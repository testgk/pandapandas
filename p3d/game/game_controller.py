"""
Game Controller — owns all GeoChallenge game state and logic.
Communicates with the globe app via the IGlobeApplication interface.
"""
import math
import random
import re
from typing import List, Optional, Tuple

from panda3d.core import (
    BitMask32, CollisionHandlerQueue, CollisionNode,
    CollisionRay, CollisionTraverser, NodePath, ClockObject
)

from game.geo_challenge_game import DifficultyLevel, GeoChallengeGame
from game.game_markers import createAnnulus, createTargetRings, createXMark, createCityLabel
from gui.game_gui_controller import GameGuiController
from world_data_manager import WorldDataManager

CONTINENT_RADIUS = 1.01
DISK_OFFSET = 0.01
GLOBE_SCALE = 5
DEFAULT_CAMERA_DIST = 14.6   # matches globe_app default camera distance

# Approximate centre lat/lon for each continent
CONTINENT_CENTRES = {
    "Europe":        ( 54.0,    4.0 ),    # calibrated H=16   → lon=4
    "Asia":          ( 20.0,   78.0 ),    # India as centre of Asia
    "Africa":        (  0.0,   20.0 ),    # calibrated H=0    → lon=20
    "North America": ( 45.0, -132.0 ),   # calibrated H=152  → lon=-132
    "South America": (-15.0,  -60.0 ),   # calibrated H=80   → lon=-60
    "Oceania":       (-25.0,  140.0 ),   # calibrated H=-120 → lon=140
    "Antarctica":    (-85.0,   20.0 ),
    "Europe/Asia":   ( 41.0,   16.0 ),
}


class GameController:
    """
    Owns all GeoChallenge game state and exposes a clean API to the globe app.
    Has no knowledge of Panda3D ShowBase internals — it receives the globe
    NodePath, the camera NodePath and the GUI controller as dependencies.
    """

    def __init__( self, globeNodePath: NodePath, cameraNodePath, camNode, mouseWatcherNode, gameGui: GameGuiController, taskManager ):
        self.__globe: NodePath = globeNodePath
        self.__camera = cameraNodePath
        self.__camNode = camNode
        self.__mouseWatcher = mouseWatcherNode
        self.__gui: GameGuiController = gameGui
        self.__taskManager = taskManager

        self.__geoGame: Optional[ GeoChallengeGame ] = None
        self.__gameMode: bool = False
        self.__currentChallenge = None
        self.__markers: List[ NodePath ] = []
        self.__hintCount: int = 0

        self.__acceptCallback = None   # set by globe app so we can register mouse1
        self.__ignoreCallback = None

    def setInputCallbacks( self, accept, ignore ) -> None:
        """Provide Panda3D accept/ignore wrappers from the ShowBase instance."""
        self.__acceptCallback = accept
        self.__ignoreCallback = ignore

    # ── Public API ────────────────────────────────────────────────────────────

    def startGame( self ) -> None:
        """Start or restart the GeoChallenge game."""
        try:
            self.__ensureGameInitialised()
            self.__gameMode = True
            self.__currentChallenge = self.__geoGame.get_challenge_by_difficulty()
            self.__hintCount = 0

            self.__clearMarkers()
            self.__gui.clearChallengeText()
            self.__gui.hideNextChallengeButton()
            self.__gui.showHintButton()

            challenge_info = (
                f"GEOCHALLENGE ACTIVE!\n"
                f"\nFIND: {self.__currentChallenge.location_name}\n"
                f"Difficulty: {self.__currentChallenge.difficulty.value}\n"
                f"Country: {self.__currentChallenge.country}\n"
                f"Continent: {self.__currentChallenge.continent}\n"
                f"\nHINT: {self.__currentChallenge.hints[ 0 ] if self.__currentChallenge.hints else 'No hints available'}\n"
                f"\nCLICK ON THE GLOBE TO GUESS!"
            )
            self.__log( challenge_info )
            self.__acceptCallback( "mouse1", self.__handleClick )

            self.__focusOnContinent( self.__currentChallenge.continent )

        except Exception as e:
            self.__log( f"❌ Error starting game: {e}" )

    def nextChallenge( self, difficulty: Optional[ str ] = None ) -> None:
        """Load the next challenge, optionally forcing a difficulty level."""
        if not self.__geoGame:
            self.startGame()
            return

        try:
            selectedDifficulty = self.__resolveDifficulty( difficulty )
            self.__currentChallenge = self.__geoGame.get_challenge_by_difficulty( selectedDifficulty )
            self.__gameMode = True
            self.__hintCount = 0

            self.__clearMarkers()
            self.__gui.clearChallengeText()
            self.__gui.hideNextChallengeButton()
            self.__gui.showHintButton()

            challenge_info = (
                f"NEW CHALLENGE!\n"
                f"Find: {self.__currentChallenge.location_name}\n"
                f"Difficulty: {self.__currentChallenge.difficulty.value}\n"
                f"Country: {self.__currentChallenge.country}\n"
                f"Continent: {self.__currentChallenge.continent}\n"
                f"Hint: {self.__currentChallenge.hints[ 0 ] if self.__currentChallenge.hints else 'No hints available'}\n"
                f"\nClick on the globe to make your guess!"
            )
            self.__log( challenge_info )
            self.__acceptCallback( "mouse1", self.__handleClick )

            self.__focusOnContinent( self.__currentChallenge.continent )

        except Exception as e:
            self.__log( f"❌ Error starting next challenge: {e}" )

    def showStats( self ) -> None:
        """Display performance analytics in the challenge log."""
        self.__log( self.__buildStatsReport() )

    def showDbStats( self ) -> None:
        """Display database scoring stats (leaderboard) in the challenge log."""
        self.__log( self.__buildDbStatsReport() )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def __stripEmoji( text: str ) -> str:
        """Remove emoji / non-BMP characters that Panda3D's default font cannot render."""
        return re.sub( r'[^\u0000-\u00FF]', '', text ).strip()

    def __log( self, message: str ) -> None:
        """Send a message to the game challenge display, emoji-free."""
        self.__gui.setChallengeText( self.__stripEmoji( message ) )

    def __ensureGameInitialised( self ) -> None:
        if self.__geoGame:
            return
        dataManager = WorldDataManager()
        self.__geoGame = GeoChallengeGame( dataManager )
        print( "🎮 GeoChallenge initialised" )

    def __resolveDifficulty( self, difficulty: Optional[ str ] ) -> Optional[ DifficultyLevel ]:
        if not difficulty:
            return None
        mapping = {
            'easy': DifficultyLevel.EASY,
            'medium': DifficultyLevel.MEDIUM,
            'hard': DifficultyLevel.HARD,
            'expert': DifficultyLevel.EXPERT,
        }
        return mapping.get( difficulty.lower() )

    def __handleClick( self ) -> None:
        """Convert a mouse click to globe coordinates and score the attempt."""

        if not self.__gameMode or not self.__currentChallenge:
            return

        if not self.__mouseWatcher.hasMouse():
            return

        mpos = self.__mouseWatcher.getMouse()

        pickerRay = CollisionRay()
        pickerRay.setFromLens( self.__camNode, mpos.getX(), mpos.getY() )

        picker = CollisionTraverser()
        pq = CollisionHandlerQueue()

        pickerNode = CollisionNode( 'mouseRay' )
        pickerNP = self.__camera.attachNewNode( pickerNode )
        pickerNode.addSolid( pickerRay )
        picker.addCollider( pickerNP, pq )

        self.__globe.setCollideMask( BitMask32.bit( 1 ) )
        picker.traverse( self.__globe )

        if pq.getNumEntries() > 0:
            pq.sortEntries()
            entry = pq.getEntry( 0 )
            localHit = entry.getSurfacePoint( self.__globe )
            sx, sy, sz = localHit.x, localHit.y, localHit.z
            sLen = ( sx * sx + sy * sy + sz * sz ) ** 0.5
            surfaceNormal = ( sx / sLen, sy / sLen, sz / sLen )

            diskPos = (
                sx + surfaceNormal[ 0 ] * DISK_OFFSET,
                sy + surfaceNormal[ 1 ] * DISK_OFFSET,
                sz + surfaceNormal[ 2 ] * DISK_OFFSET,
            )
            # Bright green X to mark exactly where the player clicked
            clickMark = createXMark( surfaceNormal, ( 0.2, 1.0, 0.2, 1.0 ), size = 0.05, thickness = 5.0 )
            clickMark.reparentTo( self.__globe )
            clickMark.setPos( *diskPos )
            clickMark.setDepthOffset( 20 )
            self.__markers.append( clickMark )

            x, y, z = sx / sLen, sy / sLen, sz / sLen
            lat = math.degrees( math.asin( max( -1.0, min( 1.0, y ) ) ) )
            lon = math.degrees( math.atan2( x, z ) )

            self.__log( f"You clicked: {lat:.2f}, {lon:.2f}" )
            self.__scoreAttempt( ( lat, lon ) )

        pickerNP.removeNode()

    def __scoreAttempt( self, clickedCoords: Tuple[ float, float ] ) -> None:
        """Score the player's click and update the UI."""
        try:
            attempt = self.__geoGame.score_attempt( clickedCoords )
            self.__placeAnswerMarker()
            self.__focusOnCity( self.__currentChallenge.actual_coordinates )

            resultText = (
                f"🎯 CHALLENGE RESULT:\n"
                f"📍 Target: {self.__currentChallenge.location_name}\n"
                f"👆 You clicked: {clickedCoords[ 0 ]:.2f}°, {clickedCoords[ 1 ]:.2f}°\n"
                f"🎯 Actual: {self.__currentChallenge.actual_coordinates[ 0 ]:.2f}°, {self.__currentChallenge.actual_coordinates[ 1 ]:.2f}°\n"
                f"📏 Distance: {attempt.distance_km:.1f} km\n"
                f"⚡ Time: {attempt.response_time_seconds:.1f}s\n"
                f"🏆 Score: {attempt.accuracy_score}%\n"
            )

            if len( self.__geoGame.player_history ) > 1:
                analytics = self.__geoGame.get_performance_analytics()
                avgScore = analytics[ 'overview' ][ 'average_score' ]
                trend = "📈 Improving" if attempt.accuracy_score > avgScore else "📉 Below average"
                resultText += f"📊 {trend} (Avg: {avgScore:.0f}%)\n"

            resultText += self.__scoreFeedback( attempt.accuracy_score )

            self.__gui.setChallengeText( self.__stripEmoji( resultText ) )
            self.__gui.showNextChallengeButton()
            self.__gui.hideHintButton()

            self.__currentChallenge = None
            self.__gameMode = False
            self.__ignoreCallback( "mouse1" )

        except Exception as e:
            self.__log( f"❌ Error scoring attempt: {e}" )

    def __focusOnCity( self, coords: Tuple[ float, float ] ) -> None:
        """Move camera above the answer city — slightly zoomed in."""
        self.__animateGlobeFocus( coords, DEFAULT_CAMERA_DIST * 0.95, taskName = "focusCityTask" )

    def __focusOnContinent( self, continentName: str ) -> None:
        """Move camera above the continent centre at default distance."""
        coords = CONTINENT_CENTRES.get( continentName )
        if not coords:
            return
        self.__animateGlobeFocus( coords, DEFAULT_CAMERA_DIST * 1.1, taskName = "focusContinentTask" )

    def onHint( self ) -> None:
        """Focus near the challenge country but with a random offset — doesn't reveal exact location."""
        if not self.__currentChallenge:
            return

        actualLat, actualLon = self.__currentChallenge.actual_coordinates

        # Random offset: 15–25 degrees in a random direction
        offsetDist = random.uniform( 15.0, 25.0 )
        offsetAngle = random.uniform( 0.0, 360.0 )
        hintLat = actualLat + offsetDist * math.cos( math.radians( offsetAngle ) )
        hintLon = actualLon + offsetDist * math.sin( math.radians( offsetAngle ) )

        # Clamp lat to valid range
        hintLat = max( -85.0, min( 85.0, hintLat ) )

        self.__animateGlobeFocus(
            ( hintLat, hintLon ),
            DEFAULT_CAMERA_DIST * 0.75,
            taskName = "focusHintTask",
        )

    def __animateGlobeFocus(
        self,
        coords: Tuple[ float, float ],
        targetCamDist: float,
        taskName: str = "focusTask",
        duration: float = 1.0,
    ) -> None:
        """Move the camera above the target lat/lon point and look down at it, north up."""
        from panda3d.core import LVector3f, LPoint3f

        lat, lon = coords
        latRad = math.radians( lat )
        lonRad = math.radians( lon )

        # Unit vector in globe local space pointing toward the target location
        localDir = LVector3f(
            math.cos( latRad ) * math.sin( lonRad ),
            math.sin( latRad ),
            math.cos( latRad ) * math.cos( lonRad ),
        )
        localDir.normalize()

        # Globe north pole in local space is +Y
        localNorth = LVector3f( 0, 1, 0 )

        # Transform both to world space via globe transform matrix
        globeMat = self.__globe.getMat( self.__globe.getParent() )
        worldDir = globeMat.xformVec( localDir )
        worldDir.normalize()
        worldNorth = globeMat.xformVec( localNorth )
        worldNorth.normalize()

        targetCamPos = worldDir * targetCamDist

        # Compute camera up vector: project worldNorth onto the plane perpendicular to worldDir
        # up = worldNorth - (worldNorth·worldDir)*worldDir  → removes component along view axis
        dot = worldNorth.dot( worldDir )
        camUp = LVector3f(
            worldNorth.x - dot * worldDir.x,
            worldNorth.y - dot * worldDir.y,
            worldNorth.z - dot * worldDir.z,
        )
        if camUp.length() < 1e-6:
            # Looking straight down at pole — use arbitrary tangent as up
            camUp = LVector3f( 1, 0, 0 )
        camUp.normalize()

        startCamPos = self.__camera.getPos()
        elapsed = [ 0.0 ]

        def animateTask( task ):
            elapsed[ 0 ] += ClockObject.getGlobalClock().getDt()
            t = min( elapsed[ 0 ] / duration, 1.0 )
            t = t * t * ( 3.0 - 2.0 * t )   # ease-in-out

            newPos = LVector3f(
                startCamPos.x + ( targetCamPos.x - startCamPos.x ) * t,
                startCamPos.y + ( targetCamPos.y - startCamPos.y ) * t,
                startCamPos.z + ( targetCamPos.z - startCamPos.z ) * t,
            )
            self.__camera.setPos( newPos )
            self.__camera.lookAt( LPoint3f( 0, 0, 0 ), camUp )

            if t >= 1.0:
                return task.done
            return task.cont

        self.__taskManager.remove( taskName )
        self.__taskManager.add( animateTask, taskName )

    def __placeAnswerMarker( self ) -> None:
        """Place scoring rings + green X at the correct answer location."""
        try:
            actualLat, actualLon = self.__currentChallenge.actual_coordinates
            latRad = math.radians( actualLat )
            lonRad = math.radians( actualLon )
            r = CONTINENT_RADIUS
            ax = math.cos( latRad ) * math.sin( lonRad ) * r
            ay = math.sin( latRad ) * r
            az = math.cos( latRad ) * math.cos( lonRad ) * r
            aLen = ( ax * ax + ay * ay + az * az ) ** 0.5
            normal = ( ax / aLen, ay / aLen, az / aLen )
            markerPos = (
                ax + normal[ 0 ] * DISK_OFFSET,
                ay + normal[ 1 ] * DISK_OFFSET,
                az + normal[ 2 ] * DISK_OFFSET,
            )

            # Scoring rings centred on the answer — outermost (red) first so inner rings
            # render on top due to z-ordering
            thresholdKm = self.__geoGame.getThresholdKm( self.__currentChallenge )
            rings = createTargetRings(
                normal = normal,
                thresholdKm = thresholdKm,
                parent = self.__globe,
                pos = markerPos,
                globeScale = GLOBE_SCALE,
            )
            self.__markers.extend( rings )

            # City name label floating above the green ring
            label = createCityLabel(
                cityName = self.__currentChallenge.location_name,
                normal = normal,
                pos = markerPos,
                parent = self.__globe,
            )
            self.__markers.append( label )



        except Exception as e:
            print( f"Error placing answer marker: {e}" )

    def __clearMarkers( self ) -> None:
        for marker in self.__markers:
            if marker and not marker.isEmpty():
                marker.removeNode()
        self.__markers = []

    def __scoreFeedback( self, score: int ) -> str:
        if score >= 90:
            return "🏆 EXCELLENT! You're a geography expert!"
        if score >= 70:
            return "👍 GOOD! Nice geographical knowledge!"
        if score >= 40:
            return "📚 Not bad, but there's room for improvement!"
        if score == 0:
            return "🚫 Too far away! Try clicking closer to the target."
        return "🗺️ Keep practicing! Geography takes time to master."

    def __buildStatsReport( self ) -> str:
        if not self.__geoGame or len( self.__geoGame.player_history ) == 0:
            return "📊 No statistics yet. Play some challenges first!"
        try:
            a = self.__geoGame.get_performance_analytics()
            report = (
                f"📊 GEOCHALLENGE STATS\n"
                f"🎮 Games: {a[ 'overview' ][ 'total_games' ]}\n"
                f"🏆 Avg Score: {a[ 'overview' ][ 'average_score' ]:.1f}%\n"
                f"🎯 Best: {a[ 'overview' ][ 'best_score' ]}%\n"
                f"📏 Avg Distance: {a[ 'distance_analysis' ][ 'average_distance_km' ]:.1f} km\n"
                f"⚡ Avg Time: {a[ 'time_analysis' ][ 'average_response_time' ]:.1f}s\n"
            )
            return report
        except Exception as e:
            return f"❌ Error generating stats: {e}"

    def __buildDbStatsReport( self ) -> str:
        """Build a report of database scoring stats (leaderboard) plus current session stats."""
        report = ""

        # Add current game session stats first
        if self.__geoGame and len( self.__geoGame.player_history ) > 0:
            try:
                a = self.__geoGame.get_performance_analytics()
                report += "CURRENT SESSION\n\n"
                report += f"Games Played: {a[ 'overview' ][ 'total_games' ]}\n"
                report += f"Avg Score: {a[ 'overview' ][ 'average_score' ]:.1f}%\n"
                report += f"Best Score: {a[ 'overview' ][ 'best_score' ]}%\n"
                report += f"Avg Distance: {a[ 'distance_analysis' ][ 'average_distance_km' ]:.1f} km\n"
                report += f"Avg Time: {a[ 'time_analysis' ][ 'average_response_time' ]:.1f}s\n"
                report += "\n"
            except Exception:
                pass
        else:
            report += "CURRENT SESSION\n\nNo games played yet.\n\n"

        # Add database leaderboard
        try:
            import sys
            from pathlib import Path
            # db module lives in the sibling geochallenge-backend project
            backend_dir = str( Path( __file__ ).resolve().parent.parent.parent.parent / "geochallenge-backend" )
            if backend_dir not in sys.path:
                sys.path.insert( 0, backend_dir )

            from db.connection import get_db_connection
            db = get_db_connection()
            db.connect()

            # Get leaderboard data
            leaderboard_query = """
                SELECT u.username, s.points, s.accuracy, s.game_mode, s.achieved_at
                FROM scores s
                JOIN users u ON s.user_id = u.id
                ORDER BY s.points DESC
                LIMIT 10
            """
            leaderboard = db.execute( leaderboard_query )

            # Get total stats
            totals_query = """
                SELECT 
                    COUNT(*) as total_games,
                    COALESCE(AVG(points), 0) as avg_points,
                    COALESCE(MAX(points), 0) as best_score,
                    COALESCE(AVG(accuracy), 0) as avg_accuracy
                FROM scores
            """
            totals = db.execute_one( totals_query )

            report += "LEADERBOARD\n\n"
            if not leaderboard:
                report += "No scores recorded yet.\n"
            else:
                report += f"Total Games: {totals[ 'total_games' ]}\n"
                report += f"Avg Score: {totals[ 'avg_points' ]:.0f} pts\n"
                report += f"Best Score: {totals[ 'best_score' ]} pts\n"
                report += f"Avg Accuracy: {totals[ 'avg_accuracy' ]:.1f}%\n"
                report += "\n--- TOP SCORES ---\n"

                for i, entry in enumerate( leaderboard, 1 ):
                    report += f"#{i} {entry[ 'username' ]}: {entry[ 'points' ]} pts\n"

            return report

        except Exception as e:
            report += f"LEADERBOARD\n\nDB Error: {e}\n\nMake sure PostgreSQL is running:\ndocker-compose up -d"
            return report
