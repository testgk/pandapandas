"""
Real Globe Application - Refactored with proper encapsulation and structure
Loads real GeoPandas world data with GUI controls for zoom and rotation
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import math
from math import sin, cos, pi
from typing import Dict, Tuple, List, Optional

from world_data_manager import WorldDataManager
from gui.globe_gui_controller import GlobeGuiController
from gui.game_gui_controller import GameGuiController
from interfaces.i_globe_application import IGlobeApplication
from game.game_controller import GameController
from game.game_app_delegate import GameAppDelegate
from app_mode import AppMode


# Constants for magic numbers
SPHERE_SEGMENTS = 32
SPHERE_RINGS = 16
CONTINENT_RADIUS = 1.01
GLOBE_SCALE = 5
DEFAULT_ROTATION_X = 105
DEFAULT_ROTATION_Y = 0
DEFAULT_ROTATION_Z = 0
DEFAULT_ROTATION_INCREMENT = 8
MIN_ROTATION_INCREMENT = 1
MAX_ROTATION_INCREMENT = 30
MIN_ZOOM_DISTANCE = 8.0
MAX_ZOOM_DISTANCE = 80.0
ZOOM_IN_FACTOR = 0.8
ZOOM_OUT_FACTOR = 1.25
CAMERA_SCALE_FACTOR = 15.0 / 21.0
SMOOTH_ROTATION_SPEED = 120.0   # degrees per second for smooth rotation
SMOOTH_ROTATION_TASK = "smooth_globe_rotation"



def createSphere(radius: float, color: Tuple[float, float, float, float]) -> NodePath:
    """Create a 3D sphere geometry with specified radius and color"""
    format = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData("sphere", format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")

    for r in range(SPHERE_RINGS + 1):
        lat = (r / SPHERE_RINGS - 0.5) * pi
        y = sin(lat) * radius
        ringRadius = cos(lat) * radius

        for s in range(SPHERE_SEGMENTS + 1):
            lon = (s / SPHERE_SEGMENTS) * 2 * pi
            x = ringRadius * sin(lon)
            z = ringRadius * cos(lon)

            vertex.addData3f(x, y, z)
            normal.addData3f(x/radius, y/radius, z/radius)

    geom = Geom(vdata)
    triangles = GeomTriangles(Geom.UHStatic)

    for r in range(SPHERE_RINGS):
        for s in range(SPHERE_SEGMENTS):
            v1 = r * (SPHERE_SEGMENTS + 1) + s
            v2 = r * (SPHERE_SEGMENTS + 1) + s + 1
            v3 = (r + 1) * (SPHERE_SEGMENTS + 1) + s
            v4 = (r + 1) * (SPHERE_SEGMENTS + 1) + s + 1

            triangles.addVertices(v1, v3, v2)
            triangles.closePrimitive()
            triangles.addVertices(v2, v3, v4)
            triangles.closePrimitive()

    geom.addPrimitive(triangles)

    node = GeomNode("sphere")
    node.addGeom(geom)
    sphereNodePath = NodePath(node)
    sphereNodePath.setColor(*color)
    sphereNodePath.setAttrib( CullFaceAttrib.make( CullFaceAttrib.MCullClockwise ) )
    return sphereNodePath


class RealGlobeApplication(ShowBase, IGlobeApplication):
    """Main application class for the Real Globe with proper encapsulation"""

    def __init__( self, appMode: AppMode = AppMode.GAME ):
        ShowBase.__init__(self)
        print("Panda3D initialized")

        self.__appMode: AppMode = appMode

        # Initialize private fields with proper typing
        self.__continents: Dict = {}
        self.__globe: Optional[NodePath] = None
        self.__globeRotationX: float = DEFAULT_ROTATION_X
        self.__globeRotationY: float = DEFAULT_ROTATION_Y
        self.__globeRotationZ: float = DEFAULT_ROTATION_Z
        # Target rotation (smooth movement destination)
        self.__targetRotationX: float = DEFAULT_ROTATION_X
        self.__targetRotationY: float = DEFAULT_ROTATION_Y
        self.__targetRotationZ: float = DEFAULT_ROTATION_Z
        self.__rotationIncrement: int = DEFAULT_ROTATION_INCREMENT
        self.__defaultCameraPos: Tuple[float, float, float] = (6.320225, -12.64045, 4.2134833)

        # Initialize GeoChallenge Game
        self.__continentRadius: float = CONTINENT_RADIUS

        # Define preset views with proper typing
        self.__presetViews: List[Dict] = [
            {"name": "Europe/Africa View", "rotation": (0, -15, 0), "description": "Shows Europe and Mediterranean"},
            {"name": "Americas View", "rotation": (0, 0, 90), "description": "North and South America centered"},
            {"name": "Asia/Pacific View", "rotation": (0, 15, -120), "description": "Asia and Pacific region"},
            {"name": "Africa/Middle East", "rotation": (0, -30, -30), "description": "Africa and Middle East focus"},
            {"name": "Atlantic View", "rotation": (0, 10, 45), "description": "Atlantic Ocean perspective"},
            {"name": "Indian Ocean View", "rotation": (0, -20, -90), "description": "Indian Ocean and surrounding continents"}
        ]

        # Initialize application
        self.__setupEnvironment()
        self.__setupLighting()
        self.__loadWorldData()
        self.__createGlobe()
        self.__setupCamera()
        self.taskMgr.add( self.__smoothRotationTask, SMOOTH_ROTATION_TASK )

        # Globe navigation GUI — always present
        isGameMode: bool = self.__appMode == AppMode.GAME
        self.__guiController: GlobeGuiController = GlobeGuiController( self )

        # Game GUI + logic — game mode only
        self.__gameDelegate: Optional[ GameAppDelegate ] = None
        if isGameMode:
            gameGui = GameGuiController(
                onStartGame = lambda: self.__gameDelegate.startGame(),
                onNextChallenge = lambda: self.__gameDelegate.nextChallenge(),
                onGameStats = lambda: self.__gameDelegate.showGameStats(),
                onHint = lambda: self.__gameDelegate.onHint(),
                taskManager = self.taskMgr,
            )
            gameController = GameController(
                globeNodePath = self.__globe,
                cameraNodePath = self.camera,
                camNode = self.camNode,
                mouseWatcherNode = self.mouseWatcherNode,
                gameGui = gameGui,
                taskManager = self.taskMgr
            )
            gameController.setInputCallbacks(
                accept = self.accept,
                ignore = self.ignore
            )
            self.__gameDelegate = GameAppDelegate( gameController, gameGui )

        print("Application ready with manual controls")
        print(f"INITIAL STATUS - Globe rotation: X={self.__globeRotationX}, Y={self.__globeRotationY}, Z={self.__globeRotationZ}")

        if isGameMode:
            print("Auto-starting GeoChallenge for immediate play...")
            self.__gameDelegate.startGame()

    # Properties for controlled access to private fields
    @property
    def rotationIncrement(self) -> int:
        """Get current rotation increment in degrees"""
        return self.__rotationIncrement

    @rotationIncrement.setter
    def rotationIncrement(self, value: int) -> None:
        """Set rotation increment with bounds checking"""
        if MIN_ROTATION_INCREMENT <= value <= MAX_ROTATION_INCREMENT:
            self.__rotationIncrement = value
        else:
            raise ValueError(f"Rotation increment must be between {MIN_ROTATION_INCREMENT} and {MAX_ROTATION_INCREMENT} degrees")

    @property
    def globeRotationX(self) -> float:
        """Get globe X rotation in degrees"""
        return self.__globeRotationX

    @property
    def globeRotationY(self) -> float:
        """Get globe Y rotation in degrees"""
        return self.__globeRotationY

    @property
    def globeRotationZ(self) -> float:
        """Get globe Z rotation in degrees"""
        return self.__globeRotationZ

    @property
    def taskManager(self):
        """Get task manager for scheduling tasks"""
        return self.taskMgr

    def __setupEnvironment(self) -> None:
        """Setup the application environment"""
        self.setBackgroundColor(0.1, 0.1, 0.3)

    def __setupLighting(self) -> None:
        """Setup ambient and directional lighting"""
        # Add ambient light
        ambientLight = AmbientLight('ambient')
        ambientLight.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambientLight))

        # Add directional light
        sunLight = DirectionalLight('sun')
        sunLight.setColor((0.8, 0.8, 0.8, 1))
        sunLight.setDirection((-1, -1, -1))
        self.render.setLight(self.render.attachNewNode(sunLight))

    def __loadWorldData(self) -> None:
        """Load real world data using WorldDataManager"""
        dataManager = WorldDataManager()
        self.__continents = dataManager.getContinents()
        print(f"Loaded {len(self.__continents)} continents")

    def __createGlobe(self) -> None:
        """Create the 3D globe with continents"""
        self.__globe = self.render.attachNewNode("globe")

        # Create opaque ocean sphere
        oceanSphere = createSphere( 1.0, ( 0.1, 0.3, 0.65, 1.0 ) )
        oceanSphere.reparentTo( self.__globe )
        print( "Ocean sphere created" )

        # Add collision sphere for click detection
        collisionSphere = CollisionSphere( 0, 0, 0, self.__continentRadius )
        collisionNode = CollisionNode( 'globe-collision' )
        collisionNode.addSolid( collisionSphere )
        self.__collisionNP = self.__globe.attachNewNode( collisionNode )
        self.__collisionNP.setCollideMask( BitMask32.bit( 1 ) )

        # Add continents with colors
        continentColors = {
            'Europe': (0.8, 0.2, 0.2, 1),       # Red
            'Africa': (0.9, 0.5, 0.1, 1),       # Orange
            'North America': (0.2, 0.8, 0.3, 1), # Green
            'South America': (0.9, 0.7, 0.1, 1), # Yellow
            'Asia': (0.6, 0.2, 0.7, 1),         # Purple
            'Oceania': (0.2, 0.7, 0.9, 1)       # Light Blue
        }
        self.__continentColors = continentColors

        continentCount = 0
        for name, geometry in self.__continents.items():
            color = self.__continentColors.get(name, (0.7, 0.7, 0.7, 1))
            radius = self.__continentRadius
            self.__addContinentGeometry(geometry, color, name, radius)
            continentCount += 1
            print(f"Added continent: {name}")

        self.__globe.setScale(GLOBE_SCALE, GLOBE_SCALE, GLOBE_SCALE)
        print(f"Globe created with {continentCount} continents")

        # Draw latitude / longitude grid lines
        self.__createGraticule()

        # Apply initial rotation
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)

    def __createGraticule( self ) -> None:
        """Draw latitude and longitude grid lines on the globe surface"""
        GRID_RADIUS = self.__continentRadius + 0.005   # just above continents
        GRID_STEP   = 15          # degrees between lines
        GRID_SEGMENTS = 120       # smoothness of each circle
        LINE_COLOR  = ( 0.55, 0.75, 0.95, 0.45 )   # pale blue, semi-transparent
        EQUATOR_COLOR  = ( 0.9, 0.9, 0.4, 0.7 )    # yellow equator / prime meridian
        THICK_NORMAL   = 1.0
        THICK_MAJOR    = 2.0

        lines = LineSegs()
        lines.setThickness( THICK_NORMAL )

        # --- Latitude lines (parallels) ---
        for latDeg in range( -90, 91, GRID_STEP ):
            isMajor = ( latDeg == 0 )
            lines.setThickness( THICK_MAJOR if isMajor else THICK_NORMAL )
            lines.setColor( *( EQUATOR_COLOR if isMajor else LINE_COLOR ) )
            latRad = math.radians( latDeg )
            ringR  = math.cos( latRad ) * GRID_RADIUS
            y      = math.sin( latRad ) * GRID_RADIUS
            first  = True
            for s in range( GRID_SEGMENTS + 1 ):
                lonRad = ( s / GRID_SEGMENTS ) * 2 * pi
                x = ringR * math.sin( lonRad )
                z = ringR * math.cos( lonRad )
                if first:
                    lines.moveTo( x, y, z )
                    first = False
                else:
                    lines.drawTo( x, y, z )

        # --- Longitude lines (meridians) ---
        for lonDeg in range( 0, 360, GRID_STEP ):
            isMajor = ( lonDeg == 0 )
            lines.setThickness( THICK_MAJOR if isMajor else THICK_NORMAL )
            lines.setColor( *( EQUATOR_COLOR if isMajor else LINE_COLOR ) )
            lonRad = math.radians( lonDeg )
            first  = True
            for s in range( GRID_SEGMENTS + 1 ):
                latRad = ( s / GRID_SEGMENTS ) * pi - pi / 2
                x = math.cos( latRad ) * math.sin( lonRad ) * GRID_RADIUS
                y = math.sin( latRad ) * GRID_RADIUS
                z = math.cos( latRad ) * math.cos( lonRad ) * GRID_RADIUS
                if first:
                    lines.moveTo( x, y, z )
                    first = False
                else:
                    lines.drawTo( x, y, z )

        graticuleNode = lines.create()
        graticulePath = self.__globe.attachNewNode( graticuleNode )
        graticulePath.setTransparency( TransparencyAttrib.MAlpha )
        graticulePath.setDepthOffset( 1 )

    def __addContinentGeometry(self, geometry, color: Tuple[float, float, float, float], name: str, radius: float = CONTINENT_RADIUS) -> None:
        """Add continent geometry to the globe"""
        from shapely.geometry import Polygon, MultiPolygon
        from shapely.ops import triangulate

        polygons = []
        if isinstance(geometry, MultiPolygon):
            polygons = list(geometry.geoms)
        elif isinstance(geometry, Polygon):
            polygons = [geometry]
        else:
            return

        for i, polygon in enumerate(polygons):
            if not polygon.is_valid or polygon.is_empty:
                continue

            # Proper Delaunay triangulation — only keep triangles whose centroid
            # lies inside the original polygon (filters out outside triangles)
            triangles = [
                t for t in triangulate( polygon )
                if polygon.contains( t.centroid )
            ]

            if not triangles:
                continue

            partName = f"{name}_part_{i}" if len(polygons) > 1 else name
            fmt = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData( partName, fmt, Geom.UHStatic )
            vertexWriter = GeomVertexWriter( vdata, "vertex" )
            normalWriter = GeomVertexWriter( vdata, "normal" )

            vertexIndex = 0
            triIndices = GeomTriangles( Geom.UHStatic )

            for tri in triangles:
                triCoords = list( tri.exterior.coords )[ :3 ]
                for lon, lat in triCoords:
                    latRad = lat * pi / 180.0
                    lonRad = lon * pi / 180.0
                    x = cos( latRad ) * sin( lonRad ) * radius
                    y = sin( latRad ) * radius
                    z = cos( latRad ) * cos( lonRad ) * radius
                    length = ( x*x + y*y + z*z ) ** 0.5
                    vertexWriter.addData3f( x, y, z )
                    normalWriter.addData3f( x / length, y / length, z / length )

                triIndices.addVertices( vertexIndex, vertexIndex + 1, vertexIndex + 2 )
                triIndices.closePrimitive()
                vertexIndex += 3

            geom = Geom( vdata )
            geom.addPrimitive( triIndices )

            continentNode = GeomNode( f"continent_{partName}" )
            continentNode.addGeom( geom )
            continentNodePath = self.__globe.attachNewNode( continentNode )
            continentNodePath.setColor( *color )

    def __setupCamera(self) -> None:
        """Setup camera position and controls"""
        # Disable mouse control to prevent interference
        self.disableMouse()

        # Set camera position using constant
        self.__defaultCameraPos = (
            15 * CAMERA_SCALE_FACTOR,
            -30 * CAMERA_SCALE_FACTOR,
            10 * CAMERA_SCALE_FACTOR
        )
        self.camera.setPos(*self.__defaultCameraPos)
        self.camera.lookAt(0, 0, 0)

        # Debug camera position
        pos = self.camera.getPos()
        distance = pos.length()
        print(f"Camera setup: Position {pos}, Distance: {distance:.1f}")
        print("Mouse controls disabled to prevent camera interference")

    # ��─ Smooth rotation task ────��─────────────────────────────────────────────

    @staticmethod
    def __lerpAngle( current: float, target: float, speed: float, dt: float ) -> float:
        """Step current angle toward target at given speed (deg/s), shortest arc."""
        diff = target - current
        # Normalise to [-180, 180]
        diff = ( diff + 180 ) % 360 - 180
        maxStep = speed * dt
        if abs( diff ) <= maxStep:
            return target
        return current + maxStep * ( 1.0 if diff > 0 else -1.0 )

    def __smoothRotationTask( self, task ) -> int:
        """Per-frame task: smoothly move globe rotation toward target values."""
        if self.__globe is None:
            return task.cont

        dt = globalClock.getDt()  # type: ignore[name-defined]
        speed = SMOOTH_ROTATION_SPEED

        self.__globeRotationX = self.__lerpAngle(
            self.__globeRotationX, self.__targetRotationX, speed, dt )
        self.__globeRotationY = self.__lerpAngle(
            self.__globeRotationY, self.__targetRotationY, speed, dt )
        self.__globeRotationZ = self.__lerpAngle(
            self.__globeRotationZ, self.__targetRotationZ, speed, dt )

        self.__globe.setHpr(
            self.__globeRotationZ,
            self.__globeRotationX,
            self.__globeRotationY
        )
        return task.cont

    # Public methods for GUI to call
    def zoomIn(self) -> None:
        """Move camera closer to globe center"""
        currentPos = self.camera.getPos()
        currentDistance = currentPos.length()

        self.__guiController.addDebugMessage(f"ZOOM IN - Distance: {currentDistance:.1f}")

        if currentDistance < 0.1:
            self.__guiController.addDebugMessage("Camera reset to default position")
            self.camera.setPos(*self.__defaultCameraPos)
            self.camera.lookAt(0, 0, 0)
            return

        targetDistance = max(currentDistance * ZOOM_IN_FACTOR, MIN_ZOOM_DISTANCE)

        if targetDistance >= currentDistance - 0.1:
            self.__guiController.addDebugMessage("Already at minimum zoom distance")
            return

        directionX = currentPos.x / currentDistance
        directionY = currentPos.y / currentDistance
        directionZ = currentPos.z / currentDistance

        newPos = (
            directionX * targetDistance,
            directionY * targetDistance,
            directionZ * targetDistance
        )

        self.camera.setPos(*newPos)
        self.camera.lookAt(0, 0, 0)

        verifyDistance = self.camera.getPos().length()
        self.__guiController.addDebugMessage(f"Zoomed in to distance: {verifyDistance:.1f}")

    def zoomOut(self) -> None:
        """Move camera further from globe center"""
        currentPos = self.camera.getPos()
        currentDistance = currentPos.length()

        self.__guiController.addDebugMessage(f"ZOOM OUT - Distance: {currentDistance:.1f}")

        if currentDistance < 0.1:
            self.__guiController.addDebugMessage("Camera reset to default position")
            self.camera.setPos(*self.__defaultCameraPos)
            self.camera.lookAt(0, 0, 0)
            return

        targetDistance = min(currentDistance * ZOOM_OUT_FACTOR, MAX_ZOOM_DISTANCE)

        if targetDistance <= currentDistance + 0.1:
            self.__guiController.addDebugMessage("Already at maximum zoom distance")
            return

        directionX = currentPos.x / currentDistance
        directionY = currentPos.y / currentDistance
        directionZ = currentPos.z / currentDistance

        newPos = (
            directionX * targetDistance,
            directionY * targetDistance,
            directionZ * targetDistance
        )

        self.camera.setPos(*newPos)
        self.camera.lookAt(0, 0, 0)

        verifyDistance = self.camera.getPos().length()
        self.__guiController.addDebugMessage(f"Zoomed out to distance: {verifyDistance:.1f}")

    def resetView(self) -> None:
        """Reset camera position and globe rotation to default"""
        self.camera.setPos(*self.__defaultCameraPos)
        self.camera.lookAt(0, 0, 0)

        self.__targetRotationX = DEFAULT_ROTATION_X
        self.__targetRotationY = DEFAULT_ROTATION_Y
        self.__targetRotationZ = DEFAULT_ROTATION_Z

        pos = self.camera.getPos()
        distance = pos.length()
        self.__guiController.addDebugMessage(f"RESET: Distance {distance:.1f} | Rotation X={DEFAULT_ROTATION_X}° Y={DEFAULT_ROTATION_Y}° Z={DEFAULT_ROTATION_Z}°")

    def rotateUp(self) -> None:
        """Rotate globe up by increment amount (smooth)"""
        self.__targetRotationX += self.__rotationIncrement
        self.__guiController.addDebugMessage(f"UP: target X={self.__targetRotationX:.1f}°")

    def rotateDown(self) -> None:
        """Rotate globe down by increment amount (smooth)"""
        self.__targetRotationX -= self.__rotationIncrement
        self.__guiController.addDebugMessage(f"DOWN: target X={self.__targetRotationX:.1f}°")

    def rotateLeft(self) -> None:
        """Rotate globe left by increment amount (smooth)"""
        self.__targetRotationZ -= self.__rotationIncrement
        self.__guiController.addDebugMessage(f"LEFT: target Z={self.__targetRotationZ:.1f}°")

    def rotateRight(self) -> None:
        """Rotate globe right by increment amount (smooth)"""
        self.__targetRotationZ += self.__rotationIncrement
        self.__guiController.addDebugMessage(f"RIGHT: target Z={self.__targetRotationZ:.1f}°")

    def increaseRotationIncrement(self) -> None:
        """Increase rotation increment by 1 degree (max 30)"""
        if self.__rotationIncrement < MAX_ROTATION_INCREMENT:
            self.__rotationIncrement += 1
            self.__guiController.addDebugMessage(f"Rotation increment increased to {self.__rotationIncrement}°")
        else:
            self.__guiController.addDebugMessage(f"Maximum rotation increment reached ({MAX_ROTATION_INCREMENT}°)")

    def decreaseRotationIncrement(self) -> None:
        """Decrease rotation increment by 1 degree (min 1)"""
        if self.__rotationIncrement > MIN_ROTATION_INCREMENT:
            self.__rotationIncrement -= 1
            self.__guiController.addDebugMessage(f"Rotation increment decreased to {self.__rotationIncrement}°")
        else:
            self.__guiController.addDebugMessage(f"Minimum rotation increment reached ({MIN_ROTATION_INCREMENT}°)")

    def setPresetView(self, index: int) -> None:
        """Set the globe to a specific preset view (smooth transition)"""
        if 0 <= index < len(self.__presetViews):
            chosenView = self.__presetViews[index]
            self.__targetRotationZ, self.__targetRotationX, self.__targetRotationY = chosenView["rotation"]
            self.__guiController.addDebugMessage(f"{chosenView['name']}: target X={self.__targetRotationX}° Y={self.__targetRotationY}° Z={self.__targetRotationZ}°")

    @property
    def continentRadius( self ) -> float:
        """Get current continent radius"""
        return self.__continentRadius

    def __rebuildContinents( self ) -> None:
        """Remove and rebuild all continent geometry at the current radius"""
        # Remove existing continent nodes and graticule
        for child in self.__globe.getChildren():
            nodeName = child.getName()
            if nodeName.startswith( "continent_" ) or nodeName == "line_segs":
                child.removeNode()

        # Rebuild continents with new radius
        for name, geometry in self.__continents.items():
            color = self.__continentColors.get( name, ( 0.7, 0.7, 0.7, 1 ) )
            self.__addContinentGeometry( geometry, color, name, self.__continentRadius )

        # Update collision sphere to match new radius
        self.__collisionNP.removeNode()
        collisionSphere = CollisionSphere( 0, 0, 0, self.__continentRadius )
        collisionNode = CollisionNode( 'globe-collision' )
        collisionNode.addSolid( collisionSphere )
        self.__collisionNP = self.__globe.attachNewNode( collisionNode )
        self.__collisionNP.setCollideMask( BitMask32.bit( 1 ) )

        # Rebuild graticule above new continent surface
        self.__createGraticule()

    def increaseContinentRadius( self ) -> None:
        """Increase continent radius by 0.01"""
        self.__continentRadius = self.__continentRadius + 0.001
        self.__rebuildContinents()
        self.__guiController.updateContinentRadiusDisplay( self.__continentRadius )

    def decreaseContinentRadius( self ) -> None:
        """Decrease continent radius by 0.01"""
        self.__continentRadius = self.__continentRadius - 0.001
        self.__rebuildContinents()
        self.__guiController.updateContinentRadiusDisplay( self.__continentRadius )

    # ── Game delegation ───────────────────────────────────────────────────────

    def startGame( self ) -> None:
        if self.__gameDelegate:
            self.__gameDelegate.startGame()

    def nextChallenge( self ) -> None:
        if self.__gameDelegate:
            self.__gameDelegate.nextChallenge()

    def showGameStats( self ) -> None:
        if self.__gameDelegate:
            self.__gameDelegate.showGameStats()


def main():
    """Main entry point"""
    import sys
    mode = AppMode.GAME
    if "--mode" in sys.argv:
        idx = sys.argv.index( "--mode" )
        if idx + 1 < len( sys.argv ):
            modeArg = sys.argv[ idx + 1 ].lower()
            mode = AppMode.GLOBE if modeArg == "globe" else AppMode.GAME

    print( f"Starting Real Globe Application (mode: {mode.value})..." )
    try:
        app = RealGlobeApplication( appMode = mode )
        app.run()
    except Exception as e:
        print( f"ERROR: {e}" )
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
