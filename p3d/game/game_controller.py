"""
Game Controller — owns all GeoChallenge game state and logic.
Communicates with the globe app via the IGlobeApplication interface.
"""
import math
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

            challenge_info = (
                f"🌍 GEOCHALLENGE ACTIVE!\n"
                f"\n🎯 FIND: {self.__currentChallenge.location_name}\n"
                f"🎚️  Difficulty: {self.__currentChallenge.difficulty.value}\n"
                f"🏛️  Country: {self.__currentChallenge.country}\n"
                f"🌎 Continent: {self.__currentChallenge.continent}\n"
                f"\n💡 HINT: {self.__currentChallenge.hints[ 0 ] if self.__currentChallenge.hints else 'No hints available'}\n"
                f"\n👆 CLICK ON THE GLOBE TO GUESS!"
            )
            self.__log( challenge_info )
            self.__acceptCallback( "mouse1", self.__handleClick )

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

            challenge_info = (
                f"🌍 NEW CHALLENGE!\n"
                f"📍 Find: {self.__currentChallenge.location_name}\n"
                f"🎯 Difficulty: {self.__currentChallenge.difficulty.value}\n"
                f"🏛️ Country: {self.__currentChallenge.country}\n"
                f"🌎 Continent: {self.__currentChallenge.continent}\n"
                f"💡 Hint: {self.__currentChallenge.hints[ 0 ] if self.__currentChallenge.hints else 'No hints available'}\n"
                f"\n👆 Click on the globe to make your guess!"
            )
            self.__log( challenge_info )
            self.__acceptCallback( "mouse1", self.__handleClick )

        except Exception as e:
            self.__log( f"❌ Error starting next challenge: {e}" )

    def showStats( self ) -> None:
        """Display performance analytics in the challenge log."""
        self.__log( self.__buildStatsReport() )

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

            self.__log( f"🔴 You clicked: {lat:.2f}°, {lon:.2f}°" )
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

            self.__currentChallenge = None
            self.__gameMode = False
            self.__ignoreCallback( "mouse1" )

        except Exception as e:
            self.__log( f"❌ Error scoring attempt: {e}" )

    def __focusOnCity( self, coords: Tuple[ float, float ] ) -> None:
        """Smoothly rotate the globe so the answer city faces the camera."""
        from panda3d.core import LVector3f, LQuaternionf, LMatrix4f

        lat, lon = coords
        latRad = math.radians( lat )
        lonRad = math.radians( lon )

        # City unit vector in globe local space
        cityVec = LVector3f(
            math.cos( latRad ) * math.sin( lonRad ),
            math.sin( latRad ),
            math.cos( latRad ) * math.cos( lonRad ),
        )
        cityVec.normalize()

        # Camera direction in world space (from origin toward camera)
        camPos = self.__camera.getPos()
        camDirWorld = LVector3f( camPos.x, camPos.y, camPos.z )
        camDirWorld.normalize()

        # Transform camera direction into current globe local space
        # (inverse of globe world transform = transpose of rotation part)
        globeQuat = LQuaternionf()
        self.__globe.getQuat( globeQuat )
        globeQuatInv = LQuaternionf( globeQuat )
        globeQuatInv.invertInPlace()
        camDirLocal = globeQuatInv.xform( camDirWorld )
        camDirLocal.normalize()

        # Build quaternion that rotates cityVec → camDirLocal (shortest arc)
        dot = max( -1.0, min( 1.0, cityVec.dot( camDirLocal ) ) )
        cross = cityVec.cross( camDirLocal )
        if cross.length() < 1e-6:
            # Already facing or exactly opposite
            arcQ = LQuaternionf.identQuat() if dot > 0 else LQuaternionf( 0, 0, 1, 0 )
        else:
            cross.normalize()
            angle = math.acos( dot )
            arcQ = LQuaternionf()
            arcQ.setFromAxisAngleRad( angle, cross )

        # Apply arc rotation on top of current globe rotation
        targetQ = LQuaternionf()
        targetQ = globeQuat * arcQ
        targetQ.normalize()

        startQ = LQuaternionf( globeQuat )

        # Camera zoom
        camDist = camPos.length()
        targetDist = max( camDist * 0.72, 8.0 )
        camDirNorm = LVector3f( camPos.x, camPos.y, camPos.z ) / camDist

        DURATION = 1.0
        elapsed = [ 0.0 ]

        def nlerp( a: LQuaternionf, b: LQuaternionf, t: float ) -> LQuaternionf:
            """Normalised linear interpolation between two quaternions."""
            r = LQuaternionf(
                a.getR() + ( b.getR() - a.getR() ) * t,
                a.getI() + ( b.getI() - a.getI() ) * t,
                a.getJ() + ( b.getJ() - a.getJ() ) * t,
                a.getK() + ( b.getK() - a.getK() ) * t,
            )
            r.normalize()
            return r

        def animateTask( task ):
            elapsed[ 0 ] += ClockObject.getGlobalClock().getDt()
            t = min( elapsed[ 0 ] / DURATION, 1.0 )
            t = t * t * ( 3.0 - 2.0 * t )

            self.__globe.setQuat( nlerp( startQ, targetQ, t ) )

            newDist = camDist + ( targetDist - camDist ) * t
            self.__camera.setPos( camDirNorm * newDist )
            self.__camera.lookAt( 0, 0, 0 )

            if t >= 1.0:
                return task.done
            return task.cont

        self.__taskManager.add( animateTask, "focusCityTask" )

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

