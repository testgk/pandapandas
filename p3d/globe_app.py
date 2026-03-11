"""
Real Globe Application - Refactored with proper encapsulation and structure
Loads real GeoPandas world data with GUI controls for zoom and rotation
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import sin, cos, pi
from typing import Dict, Tuple, List, Optional

from world_data_manager import WorldDataManager
from gui.globe_gui_controller import GlobeGuiController
from interfaces.i_globe_application import IGlobeApplication


# Constants for magic numbers
SPHERE_SEGMENTS = 32
SPHERE_RINGS = 16
CONTINENT_RADIUS = 1.05
GLOBE_SCALE = 3
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
CAMERA_SCALE_FACTOR = 15.0 / 35.6


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
        print(f"INITIAL STATUS - Globe rotation: X={self.__globeRotationX}°, Y={self.__globeRotationY}°, Z={self.__globeRotationZ}°")

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

        # Create transparent ocean sphere
        oceanSphere = createSphere(1.0, (0.2, 0.4, 0.8, 0.4))
        oceanSphere.reparentTo(self.__globe)
        oceanSphere.setTransparency(TransparencyAttrib.MAlpha)
        print("Ocean sphere created")

        # Add continents with colors
        continentColors = {
            'Europe': (0.8, 0.2, 0.2, 1),       # Red
            'Africa': (0.9, 0.5, 0.1, 1),       # Orange
            'North America': (0.2, 0.8, 0.3, 1), # Green
            'South America': (0.9, 0.7, 0.1, 1), # Yellow
            'Asia': (0.6, 0.2, 0.7, 1),         # Purple
            'Oceania': (0.2, 0.7, 0.9, 1)       # Light Blue
        }

        continentCount = 0
        for name, geometry in self.__continents.items():
            color = continentColors.get(name, (0.7, 0.7, 0.7, 1))
            self.__addContinentGeometry(geometry, color, name)
            continentCount += 1
            print(f"Added continent: {name}")

        self.__globe.setScale(GLOBE_SCALE, GLOBE_SCALE, GLOBE_SCALE)
        print(f"Globe created with {continentCount} continents")

        # Apply initial rotation
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)

    def __addContinentGeometry(self, geometry, color: Tuple[float, float, float, float], name: str) -> None:
        """Add continent geometry to the globe"""
        from shapely.geometry import Polygon, MultiPolygon

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

            coords = list(polygon.exterior.coords)[:-1]
            if len(coords) < 3:
                continue

            vertices3d = []

            for lon, lat in coords:
                latRad = lat * pi / 180.0
                lonRad = lon * pi / 180.0
                x = cos(latRad) * sin(lonRad) * CONTINENT_RADIUS
                y = sin(latRad) * CONTINENT_RADIUS
                z = cos(latRad) * cos(lonRad) * CONTINENT_RADIUS
                vertices3d.append((x, y, z))

            # Create geometry
            partName = f"{name}_part_{i}" if len(polygons) > 1 else name
            format = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData(partName, format, Geom.UHStatic)
            vdata.setNumRows(len(vertices3d))
            vertex = GeomVertexWriter(vdata, "vertex")
            normal = GeomVertexWriter(vdata, "normal")

            for x, y, z in vertices3d:
                vertex.addData3f(x, y, z)
                length = (x*x + y*y + z*z) ** 0.5
                normal.addData3f(x/length, y/length, z/length)

            geom = Geom(vdata)
            triangles = GeomTriangles(Geom.UHStatic)

            for j in range(1, len(vertices3d) - 1):
                triangles.addVertices(0, j, j + 1)
                triangles.closePrimitive()

            geom.addPrimitive(triangles)

            continentNode = GeomNode(f"continent_{partName}")
            continentNode.addGeom(geom)
            continentNodePath = self.__globe.attachNewNode(continentNode)
            continentNodePath.setColor(*color)
            continentNodePath.setTwoSided(True)

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

        self.__guiController.addLogMessage(f"ZOOM IN - Distance: {currentDistance:.1f}")

        if currentDistance < 0.1:
            self.__guiController.addLogMessage("Camera reset to default position")
            self.camera.setPos(*self.__defaultCameraPos)
            self.camera.lookAt(0, 0, 0)
            return

        targetDistance = max(currentDistance * ZOOM_IN_FACTOR, MIN_ZOOM_DISTANCE)

        if targetDistance >= currentDistance - 0.1:
            self.__guiController.addLogMessage("Already at minimum zoom distance")
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
        self.__guiController.addLogMessage(f"Zoomed in to distance: {verifyDistance:.1f}")

    def zoomOut(self) -> None:
        """Move camera further from globe center"""
        currentPos = self.camera.getPos()
        currentDistance = currentPos.length()

        self.__guiController.addLogMessage(f"ZOOM OUT - Distance: {currentDistance:.1f}")

        if currentDistance < 0.1:
            self.__guiController.addLogMessage("Camera reset to default position")
            self.camera.setPos(*self.__defaultCameraPos)
            self.camera.lookAt(0, 0, 0)
            return

        targetDistance = min(currentDistance * ZOOM_OUT_FACTOR, MAX_ZOOM_DISTANCE)

        if targetDistance <= currentDistance + 0.1:
            self.__guiController.addLogMessage("Already at maximum zoom distance")
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
        self.__guiController.addLogMessage(f"Zoomed out to distance: {verifyDistance:.1f}")

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
        self.__guiController.addLogMessage(f"RESET: Distance {distance:.1f} | Rotation X={DEFAULT_ROTATION_X}° Y={DEFAULT_ROTATION_Y}° Z={DEFAULT_ROTATION_Z}°")

    def rotateUp(self) -> None:
        """Rotate globe up by increment amount"""
        self.__globeRotationX += self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addLogMessage(f"UP: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def rotateDown(self) -> None:
        """Rotate globe down by increment amount"""
        self.__globeRotationX -= self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addLogMessage(f"DOWN: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def rotateLeft(self) -> None:
        """Rotate globe left by increment amount"""
        self.__globeRotationZ -= self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addLogMessage(f"LEFT: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def rotateRight(self) -> None:
        """Rotate globe right by increment amount"""
        self.__globeRotationZ += self.__rotationIncrement
        self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
        self.__guiController.addLogMessage(f"RIGHT: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")

    def increaseRotationIncrement(self) -> None:
        """Increase rotation increment by 1 degree (max 30)"""
        if self.__rotationIncrement < MAX_ROTATION_INCREMENT:
            self.__rotationIncrement += 1
            print(f"Rotation increment: {self.__rotationIncrement}°")
            self.__guiController.addLogMessage(f"Rotation increment increased to {self.__rotationIncrement}°")
        else:
            print(f"Rotation increment: {self.__rotationIncrement}° (MAX)")
            self.__guiController.addLogMessage(f"Maximum rotation increment reached ({MAX_ROTATION_INCREMENT}°)")

    def decreaseRotationIncrement(self) -> None:
        """Decrease rotation increment by 1 degree (min 1)"""
        if self.__rotationIncrement > MIN_ROTATION_INCREMENT:
            self.__rotationIncrement -= 1
            print(f"Rotation increment: {self.__rotationIncrement}°")
            self.__guiController.addLogMessage(f"Rotation increment decreased to {self.__rotationIncrement}°")
        else:
            print(f"Rotation increment: {self.__rotationIncrement}° (MIN)")
            self.__guiController.addLogMessage(f"Minimum rotation increment reached ({MIN_ROTATION_INCREMENT}°)")

    def setPresetView(self, index: int) -> None:
        """Set the globe to a specific preset view"""
        if 0 <= index < len(self.__presetViews):
            chosenView = self.__presetViews[index]
            self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY = chosenView["rotation"]
            self.__globe.setHpr(self.__globeRotationZ, self.__globeRotationX, self.__globeRotationY)
            self.__guiController.addLogMessage(f"{chosenView['name']}: X={self.__globeRotationX}° Y={self.__globeRotationY}° Z={self.__globeRotationZ}°")


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
