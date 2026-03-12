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
from interfaces.i_globe_application import IGlobeApplication
from geo_challenge_game import GeoChallengeGame, DifficultyLevel


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


DISK_SEGMENTS = 24


def createDisk(
    normal: Tuple[ float, float, float ],
    color: Tuple[ float, float, float, float ],
    radius: float = 0.06,
    segments: int = DISK_SEGMENTS
) -> NodePath:
    """Create a flat disk aligned to the globe surface at the given surface normal"""
    nx, ny, nz = normal

    # Build two tangent vectors perpendicular to the normal
    up = ( 0.0, 1.0, 0.0 ) if abs( ny ) < 0.9 else ( 1.0, 0.0, 0.0 )
    tx = ny * up[ 2 ] - nz * up[ 1 ]
    ty = nz * up[ 0 ] - nx * up[ 2 ]
    tz = nx * up[ 1 ] - ny * up[ 0 ]
    tLen = ( tx * tx + ty * ty + tz * tz ) ** 0.5
    tx, ty, tz = tx / tLen, ty / tLen, tz / tLen

    bx = ny * tz - nz * ty
    by = nz * tx - nx * tz
    bz = nx * ty - ny * tx

    fmt = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData( "disk", fmt, Geom.UHStatic )
    vertexWriter = GeomVertexWriter( vdata, "vertex" )
    normalWriter = GeomVertexWriter( vdata, "normal" )

    # Centre vertex
    vertexWriter.addData3f( 0.0, 0.0, 0.0 )
    normalWriter.addData3f( nx, ny, nz )

    for i in range( segments ):
        angle = ( i / segments ) * 2 * pi
        px = ( tx * cos( angle ) + bx * sin( angle ) ) * radius
        py = ( ty * cos( angle ) + by * sin( angle ) ) * radius
        pz = ( tz * cos( angle ) + bz * sin( angle ) ) * radius
        vertexWriter.addData3f( px, py, pz )
        normalWriter.addData3f( nx, ny, nz )

    geom = Geom( vdata )
    tris = GeomTriangles( Geom.UHStatic )
    for i in range( segments ):
        tris.addVertices( 0, i + 1, ( i + 1 ) % segments + 1 )
        tris.closePrimitive()
    geom.addPrimitive( tris )

    node = GeomNode( "disk" )
    node.addGeom( geom )
    diskPath = NodePath( node )
    diskPath.setColor( *color )
    diskPath.setTwoSided( True )
    diskPath.setTransparency( TransparencyAttrib.MAlpha )
    return diskPath


def createXMark(
    normal: Tuple[ float, float, float ],
    color: Tuple[ float, float, float, float ],
    size: float = 0.07,
    thickness: float = 4.0
) -> NodePath:
    """Create an X mark aligned to the globe surface at the given surface normal"""
    nx, ny, nz = normal

    # Build two tangent vectors perpendicular to the normal
    up = ( 0.0, 1.0, 0.0 ) if abs( ny ) < 0.9 else ( 1.0, 0.0, 0.0 )
    tx = ny * up[ 2 ] - nz * up[ 1 ]
    ty = nz * up[ 0 ] - nx * up[ 2 ]
    tz = nx * up[ 1 ] - ny * up[ 0 ]
    tLen = ( tx * tx + ty * ty + tz * tz ) ** 0.5
    tx, ty, tz = tx / tLen, ty / tLen, tz / tLen

    bx = ny * tz - nz * ty
    by = nz * tx - nx * tz
    bz = nx * ty - ny * tx

    lines = LineSegs()
    lines.setThickness( thickness )
    lines.setColor( *color )

    # First diagonal: (-t-b) to (+t+b)
    lines.moveTo( ( -tx - bx ) * size, ( -ty - by ) * size, ( -tz - bz ) * size )
    lines.drawTo( (  tx + bx ) * size, (  ty + by ) * size, (  tz + bz ) * size )

    # Second diagonal: (+t-b) to (-t+b)
    lines.moveTo( (  tx - bx ) * size, (  ty - by ) * size, (  tz - bz ) * size )
    lines.drawTo( ( -tx + bx ) * size, ( -ty + by ) * size, ( -tz + bz ) * size )

    xNode = lines.create()
    xPath = NodePath( xNode )
    xPath.setTwoSided( True )
    return xPath


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

    def __init__(self):
        ShowBase.__init__(self)
        print("Panda3D initialized")

        # Initialize private fields with proper typing
        self.__continents: Dict = {}
        self.__globe: Optional[NodePath] = None
        self.__globeRotationX: int = DEFAULT_ROTATION_X
        self.__globeRotationY: int = DEFAULT_ROTATION_Y
        self.__globeRotationZ: int = DEFAULT_ROTATION_Z
        self.__rotationIncrement: int = DEFAULT_ROTATION_INCREMENT
        self.__defaultCameraPos: Tuple[float, float, float] = (6.320225, -12.64045, 4.2134833)

        # Initialize GeoChallenge Game
        self.__geoGame: Optional[GeoChallengeGame] = None
        self.__gameMode: bool = False
        self.__currentChallenge = None
        self.__gameMarkers: List[NodePath] = []
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

        # Create GUI controller
        self.__guiController = GlobeGuiController(self)

        print("Application ready with manual controls")
        print(f"INITIAL STATUS - Globe rotation: X={self.__globeRotationX}, Y={self.__globeRotationY}, Z={self.__globeRotationZ}")
        
        # Auto-start a geography challenge for immediate play
        print("🎮 Auto-starting GeoChallenge for immediate play...")
        self.startGeoChallenge()

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
    def globeRotationX(self) -> int:
        """Get globe X rotation in degrees"""
        return self.__globeRotationX

    @property
    def globeRotationY(self) -> int:
        """Get globe Y rotation in degrees"""
        return self.__globeRotationY

    @property
    def globeRotationZ(self) -> int:
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

        self.__globeRotationX = DEFAULT_ROTATION_X
        self.__globeRotationY = DEFAULT_ROTATION_Y
        self.__globeRotationZ = DEFAULT_ROTATION_Z
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)

        pos = self.camera.getPos()
        distance = pos.length()
        self.__guiController.addDebugMessage(f"RESET: Distance {distance:.1f} | Rotation X={DEFAULT_ROTATION_X}° Y={DEFAULT_ROTATION_Y}° Z={DEFAULT_ROTATION_Z}°")

    def rotateUp(self) -> None:
        """Rotate globe up by increment amount"""
        self.__globeRotationX += self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addDebugMessage(f"UP: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def rotateDown(self) -> None:
        """Rotate globe down by increment amount"""
        self.__globeRotationX -= self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addDebugMessage(f"DOWN: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def rotateLeft(self) -> None:
        """Rotate globe left by increment amount"""
        self.__globeRotationZ -= self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addDebugMessage(f"LEFT: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def rotateRight(self) -> None:
        """Rotate globe right by increment amount"""
        self.__globeRotationZ += self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addDebugMessage(f"RIGHT: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

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
        """Set the globe to a specific preset view"""
        if 0 <= index < len(self.__presetViews):
            chosenView = self.__presetViews[index]
            self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY = chosenView["rotation"]
            self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
            self.__guiController.addDebugMessage(f"{chosenView['name']}: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

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

    # GeoChallenge Game Methods - Professional GeoPandas/Pandas Showcase
    def startGeoChallenge(self) -> None:
        """
        Start the GeoChallenge game mode
        Demonstrates professional GeoPandas and Pandas usage for interactive learning
        """
        try:
            if not self.__geoGame:
                # Initialize game with world data manager
                dataManager = WorldDataManager()
                self.__geoGame = GeoChallengeGame(dataManager)
                print("🎮 GeoChallenge Game initialized with professional GeoPandas backend")
            
            self.__gameMode = True
            self.__currentChallenge = self.__geoGame.get_challenge_by_difficulty()

            self.__clearGameMarkers()
            self.__guiController.clearLogMessage()
            self.__guiController.disableNextChallenge()

            # Display challenge information prominently
            challenge_info = (
                f"🌍 GEOCHALLENGE ACTIVE!\n"
                f"\n🎯 FIND: {self.__currentChallenge.location_name}\n"
                f"🎚️  Difficulty: {self.__currentChallenge.difficulty.value}\n"
                f"🏛️  Country: {self.__currentChallenge.country}\n"
                f"🌎 Continent: {self.__currentChallenge.continent}\n"
                f"\n💡 HINT: {self.__currentChallenge.hints[0] if self.__currentChallenge.hints else 'No hints available'}\n"
                f"\n👆 CLICK ON THE GLOBE TO GUESS!"
                f"\n🔴 Red dot shows where you clicked"
            )
            
            self.__guiController.addLogMessage("🎮 GeoChallenge Mode ACTIVE")
            self.__guiController.addLogMessage(challenge_info)
            
            # Enable mouse clicking for game interaction
            self.accept("mouse1", self.__handleGameClick)
            
            print(f"🎯 Challenge: Find {self.__currentChallenge.location_name} in {self.__currentChallenge.country}")
            
        except Exception as e:
            print(f"Error starting GeoChallenge: {e}")
            self.__guiController.addLogMessage(f"❌ Error starting game: {e}")

    def __handleGameClick(self) -> None:
        """
        Handle mouse clicks during game mode - Convert 3D click to geographic coordinates
        Shows red disk where clicked and automatically derives coordinates
        """
        if not self.__gameMode or not self.__currentChallenge:
            return

        # Get mouse position and convert to 3D world coordinates
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()

            # Create picker ray from camera through mouse position
            pickerRay = CollisionRay()
            pickerRay.setFromLens( self.camNode, mpos.getX(), mpos.getY() )

            # Create collision traverser and handler
            picker = CollisionTraverser()
            pq = CollisionHandlerQueue()

            # Create collision node for the globe
            pickerNode = CollisionNode( 'mouseRay' )
            pickerNP = self.camera.attachNewNode( pickerNode )
            pickerNode.addSolid( pickerRay )
            picker.addCollider( pickerNP, pq )

            # Enable collision detection on the globe
            self.__globe.setCollideMask( BitMask32.bit( 1 ) )

            # Traverse and find collision
            picker.traverse( self.__globe )

            if pq.getNumEntries() > 0:
                # Get the closest intersection point
                pq.sortEntries()
                entry = pq.getEntry( 0 )

                # Get hit point in globe LOCAL space (accounts for rotation + scale)
                localHit = entry.getSurfacePoint( self.__globe )
                sx = localHit.x
                sy = localHit.y
                sz = localHit.z

                # Compute surface normal (unit vector from globe centre to hit point)
                sLen = ( sx * sx + sy * sy + sz * sz ) ** 0.5
                surfaceNormal = ( sx / sLen, sy / sLen, sz / sLen )

                # Place disk just above the surface to avoid z-fighting
                DISK_OFFSET = 0.01
                diskPos = (
                    sx + surfaceNormal[ 0 ] * DISK_OFFSET,
                    sy + surfaceNormal[ 1 ] * DISK_OFFSET,
                    sz + surfaceNormal[ 2 ] * DISK_OFFSET,
                )

                # Create fully opaque red disk marker conforming to the globe curvature
                clickDisk = createDisk( surfaceNormal, ( 1.0, 0.0, 0.0, 1.0 ) )
                clickDisk.reparentTo( self.__globe )
                clickDisk.setPos( *diskPos )
                self.__gameMarkers.append( clickDisk )

                # Convert local-space position to geographic coordinates
                # Normalise to unit sphere to get direction vector
                x = sx / sLen
                y = sy / sLen
                z = sz / sLen

                # Calculate latitude and longitude from 3D coordinates
                lat = math.degrees( math.asin( max( -1, min( 1, y ) ) ) )
                lon = math.degrees( math.atan2( x, z ) )

                # Display click coordinates immediately
                self.__guiController.addLogMessage( f"🔴 You clicked: {lat:.2f}°, {lon:.2f}°" )

                # Process the game attempt
                self.__processGameAttempt( ( lat, lon ) )

            # Clean up collision nodes
            pickerNP.removeNode()

    def __processGameAttempt(self, clicked_coords: Tuple[float, float]) -> None:
        """
        Process a game attempt using professional GeoPandas/Pandas analytics
        Demonstrates advanced spatial analysis and statistical performance tracking
        """
        if not self.__geoGame or not self.__currentChallenge:
            return
        
        try:
            # Score the attempt using advanced spatial calculations
            attempt = self.__geoGame.score_attempt(clicked_coords)
            
            # Create visual feedback on the globe
            self.__visualizeGameResult(clicked_coords, attempt)
            
            # Generate comprehensive result analysis
            result_analysis = (
                f"🎯 CHALLENGE RESULT:\n"
                f"📍 Target: {self.__currentChallenge.location_name}\n"
                f"👆 You clicked: {clicked_coords[0]:.2f}°, {clicked_coords[1]:.2f}°\n"
                f"🎯 Actual location: {self.__currentChallenge.actual_coordinates[0]:.2f}°, {self.__currentChallenge.actual_coordinates[1]:.2f}°\n"
                f"📏 Distance off: {attempt.distance_km:.1f} km\n"
                f"⚡ Response time: {attempt.response_time_seconds:.1f} seconds\n"
                f"🏆 Score: {attempt.accuracy_score}% accuracy\n"
                f"🎲 Difficulty: {self.__currentChallenge.difficulty.value}\n"
            )
            
            # Add performance context using Pandas analytics
            if len(self.__geoGame.player_history) > 1:
                analytics = self.__geoGame.get_performance_analytics()
                avg_score = analytics['overview']['average_score']
                performance_trend = "📈 Improving" if attempt.accuracy_score > avg_score else "📉 Below average"
                result_analysis += f"📊 Performance: {performance_trend} (Avg: {avg_score:.0f}%)\n"

            # Scoring feedback (percentage-based thresholds)
            if attempt.accuracy_score >= 90:
                result_analysis += "🏆 EXCELLENT! You're a geography expert!"
            elif attempt.accuracy_score >= 70:
                result_analysis += "👍 GOOD! Nice geographical knowledge!"
            elif attempt.accuracy_score >= 40:
                result_analysis += "📚 Not bad, but there's room for improvement!"
            elif attempt.accuracy_score == 0:
                result_analysis += "🚫 Too close to be realistic! Try clicking further away."
            else:
                result_analysis += "🗺️ Keep practicing! Geography takes time to master."
            
            self.__guiController.addLogMessage(result_analysis)
            self.__guiController.enableNextChallenge()

            # End current challenge and prepare for next
            self.__currentChallenge = None
            self.__gameMode = False
            self.ignore("mouse1")
            
            print(f"🎮 Challenge completed! Score: {attempt.accuracy_score}%, Distance: {attempt.distance_km:.1f}km")
            
        except Exception as e:
            print(f"Error processing game attempt: {e}")
            self.__guiController.addLogMessage(f"❌ Error processing attempt: {e}")

    def __visualizeGameResult(self, clicked_coords: Tuple[float, float], attempt) -> None:
        """
        Visualize game results on the 3D globe
        Demonstrates GeoPandas-style spatial visualization techniques
        """
        try:
            actual_lat, actual_lon = self.__currentChallenge.actual_coordinates

            # Convert geographic coordinates to globe LOCAL space (unit sphere)
            def geo_to_local( latitude: float, longitude: float ) -> Tuple[ float, float, float ]:
                latRad = math.radians( latitude )
                lonRad = math.radians( longitude )
                r = CONTINENT_RADIUS
                x = math.cos( latRad ) * math.sin( lonRad ) * r
                y = math.sin( latRad ) * r
                z = math.cos( latRad ) * math.cos( lonRad ) * r
                return ( x, y, z )

            # X mark for the correct location (green)
            actualLocal = geo_to_local( actual_lat, actual_lon )
            ax, ay, az = actualLocal
            aLen = ( ax * ax + ay * ay + az * az ) ** 0.5
            actualNormal = ( ax / aLen, ay / aLen, az / aLen )

            OFFSET = 0.01
            xPos = (
                ax + actualNormal[ 0 ] * OFFSET,
                ay + actualNormal[ 1 ] * OFFSET,
                az + actualNormal[ 2 ] * OFFSET,
            )

            xMark = createXMark( actualNormal, ( 0.0, 1.0, 0.0, 1.0 ) )
            xMark.reparentTo( self.__globe )
            xMark.setPos( *xPos )
            self.__gameMarkers.append( xMark )

        except Exception as e:
            print( f"Error creating game visualization: {e}" )

    def __clearGameMarkers( self ) -> None:
        """Remove all game visualization markers from the globe"""
        for marker in self.__gameMarkers:
            if marker and not marker.isEmpty():
                marker.removeNode()
        self.__gameMarkers = []

    def getGameStatistics(self) -> str:
        """
        Get comprehensive game statistics using Pandas analytics
        Demonstrates professional data analysis capabilities
        """
        if not self.__geoGame or len(self.__geoGame.player_history) == 0:
            return "📊 No game statistics available yet. Play some challenges first!"
        
        try:
            analytics = self.__geoGame.get_performance_analytics()
            
            # Format comprehensive statistics report
            stats_report = (
                f"📊 GEOCHALLENGE PERFORMANCE ANALYTICS\n"
                f"🎮 Total Games: {analytics['overview']['total_games']}\n"
                f"🏆 Average Score: {analytics['overview']['average_score']:.1f}/1000\n"
                f"🎯 Best Score: {analytics['overview']['best_score']}/1000\n"
                f"📏 Average Distance: {analytics['distance_analysis']['average_distance_km']:.1f} km\n"
                f"⚡ Average Response Time: {analytics['time_analysis']['average_response_time']:.1f} seconds\n"
                f"🚀 Fastest Response: {analytics['time_analysis']['fastest_response']:.1f} seconds\n"
            )
            
            # Add difficulty breakdown if available
            if 'difficulty_breakdown' in analytics:
                stats_report += "\n🎲 DIFFICULTY BREAKDOWN:\n"
                for difficulty, stats in analytics['difficulty_breakdown'].items():
                    if isinstance(stats, dict) and 'count' in stats:
                        count = stats['count']
                        avg_score = stats.get('mean', 0)
                        stats_report += f"   {difficulty}: {count} games, {avg_score:.1f} avg score\n"
            
            # Add geographic performance
            if 'geographic_analysis' in analytics and analytics['geographic_analysis']:
                geo_analysis = analytics['geographic_analysis']
                if geo_analysis.get('best_continent'):
                    stats_report += f"\n🌍 Best Continent: {geo_analysis['best_continent']}\n"
                if geo_analysis.get('worst_continent'):
                    stats_report += f"🌍 Challenging Continent: {geo_analysis['worst_continent']}\n"
            
            # Add performance trend
            if 'performance_trends' in analytics:
                trends = analytics['performance_trends']
                if isinstance(trends, dict) and 'score_trend' in trends:
                    trend_emoji = "📈" if trends['score_trend'] == 'improving' else "📉" if trends['score_trend'] == 'declining' else "➡️"
                    stats_report += f"\n{trend_emoji} Performance Trend: {trends['score_trend'].title()}\n"
            
            return stats_report
            
        except Exception as e:
            return f"❌ Error generating statistics: {e}"

    def nextGeoChallenge(self, difficulty: str = None) -> None:
        """
        Start the next GeoChallenge with optional difficulty selection
        Showcases adaptive difficulty based on player performance analytics
        """
        if not self.__geoGame:
            self.startGeoChallenge()
            return
        
        try:
            # Convert difficulty string to enum if provided
            selected_difficulty = None
            if difficulty:
                difficulty_map = {
                    'easy': DifficultyLevel.EASY,
                    'medium': DifficultyLevel.MEDIUM,
                    'hard': DifficultyLevel.HARD,
                    'expert': DifficultyLevel.EXPERT
                }
                selected_difficulty = difficulty_map.get(difficulty.lower())
            
            # Get next challenge with intelligent difficulty selection
            self.__currentChallenge = self.__geoGame.get_challenge_by_difficulty(selected_difficulty)
            self.__gameMode = True

            self.__clearGameMarkers()
            self.__guiController.clearLogMessage()
            self.__guiController.disableNextChallenge()
            self._hint_count = 0

            # Display new challenge
            challenge_info = (
                f"🌍 NEW CHALLENGE!\n"
                f"📍 Find: {self.__currentChallenge.location_name}\n"
                f"🎯 Difficulty: {self.__currentChallenge.difficulty.value}\n"
                f"🏛️ Country: {self.__currentChallenge.country}\n"
                f"🌎 Continent: {self.__currentChallenge.continent}\n"
                f"💡 Hint: {self.__currentChallenge.hints[0] if self.__currentChallenge.hints else 'No hints available'}\n"
                f"\n👆 Click on the globe to make your guess!"
            )
            
            self.__guiController.addLogMessage(challenge_info)
            
            # Enable mouse clicking
            self.accept("mouse1", self.__handleGameClick)
            
            print(f"🎯 New Challenge: Find {self.__currentChallenge.location_name}")
            
        except Exception as e:
            print(f"Error starting next challenge: {e}")
            self.__guiController.addLogMessage(f"❌ Error starting next challenge: {e}")

    def getGameHint(self) -> None:
        """
        Get additional hints for the current challenge
        Demonstrates intelligent hint system using geographic data analysis
        """
        if not self.__gameMode or not self.__currentChallenge:
            self.__guiController.addLogMessage("❌ No active challenge for hints")
            return

        try:
            # Get progressive hints
            hint_count = getattr(self, '_hint_count', 0)
            hint = self.__geoGame.get_hint(hint_count)

            hint_message = (
                f"💡 HINT #{hint_count + 1}:\n"
                f"{hint}\n"
                f"🎯 Still looking for: {self.__currentChallenge.location_name}"
            )

            self.__guiController.addLogMessage(hint_message)
            self._hint_count = hint_count + 1
            
        except Exception as e:
            self.__guiController.addLogMessage(f"❌ Error getting hint: {e}")

    # Method aliases for GUI controller compatibility
    def startGame(self) -> None:
        """Alias for startGeoChallenge - for GUI controller compatibility"""
        self.startGeoChallenge()
    
    def nextChallenge(self) -> None:
        """Alias for nextGeoChallenge - for GUI controller compatibility"""
        self.nextGeoChallenge()
    
    def getHint(self) -> None:
        """Alias for getGameHint - for GUI controller compatibility"""
        self.getGameHint()
    
    def showGameStats(self) -> None:
        """Show game statistics in log - for GUI controller compatibility"""
        stats = self.getGameStatistics()
        self.__guiController.addLogMessage(stats)


def main():
    """Main entry point"""
    print("Starting Real Globe Application with Manual Controls...")
    try:
        app = RealGlobeApplication()
        print("Starting application with real world data and manual controls...")
        app.run()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
