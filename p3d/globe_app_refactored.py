"""
Real Globe Application - Refactored with proper encapsulation and structure
Loads real GeoPandas world data with GUI controls for zoom and rotation
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import sin, cos, pi
import warnings
import ssl
import urllib3
import os
import requests
import tempfile

from world_data_manager import WorldDataManager
from gui.globe_gui_controller import GlobeGuiController
from interfaces.i_globe_application import IGlobeApplication


def _create_sphere(radius, color):
    """Create a 3D sphere geometry"""
    format = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData("sphere", format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")

    segments = 32
    rings = 16

    for r in range(rings + 1):
        lat = (r / rings - 0.5) * pi
        y = sin(lat) * radius
        ring_r = cos(lat) * radius

        for s in range(segments + 1):
            lon = (s / segments) * 2 * pi
            x = ring_r * sin(lon)
            z = ring_r * cos(lon)

            vertex.addData3f(x, y, z)
            normal.addData3f(x/radius, y/radius, z/radius)

    geom = Geom(vdata)
    tris = GeomTriangles(Geom.UHStatic)

    for r in range(rings):
        for s in range(segments):
            v1 = r * (segments + 1) + s
            v2 = r * (segments + 1) + s + 1
            v3 = (r + 1) * (segments + 1) + s
            v4 = (r + 1) * (segments + 1) + s + 1

            tris.addVertices(v1, v3, v2)
            tris.closePrimitive()
            tris.addVertices(v2, v3, v4)
            tris.closePrimitive()

    geom.addPrimitive(tris)

    node = GeomNode("sphere")
    node.addGeom(geom)
    sphere_np = NodePath(node)
    sphere_np.setColor(*color)
    return sphere_np


class RealGlobeApplication(ShowBase, IGlobeApplication):
    """Main application class for the Real Globe with proper encapsulation"""

    def __init__(self):
        ShowBase.__init__(self)
        print("Panda3D initialized")

        # Initialize private fields
        self.__continents = {}
        self.__globe = None
        self.__globe_rotation_x = 105
        self.__globe_rotation_y = 0
        self.__globe_rotation_z = 0
        self.__rotation_increment = 8
        self.__default_camera_pos = (6.320225, -12.64045, 4.2134833)

        # Define preset views
        self.__preset_views = [
            {"name": "Europe/Africa View", "rotation": (0, -15, 0), "description": "Shows Europe and Mediterranean"},
            {"name": "Americas View", "rotation": (0, 0, 90), "description": "North and South America centered"},
            {"name": "Asia/Pacific View", "rotation": (0, 15, -120), "description": "Asia and Pacific region"},
            {"name": "Africa/Middle East", "rotation": (0, -30, -30), "description": "Africa and Middle East focus"},
            {"name": "Atlantic View", "rotation": (0, 10, 45), "description": "Atlantic Ocean perspective"},
            {"name": "Indian Ocean View", "rotation": (0, -20, -90), "description": "Indian Ocean and surrounding continents"}
        ]

        # Initialize application
        self.__setup_environment()
        self.__setup_lighting()
        self.__load_world_data()
        self.__create_globe()
        self.__setup_camera()

        # Create GUI controller
        self.__gui_controller = GlobeGuiController(self)

        print("Application ready with manual controls")
        print(f"INITIAL STATUS - Globe rotation: X={self.__globe_rotation_x}°, Y={self.__globe_rotation_y}°, Z={self.__globe_rotation_z}°")

    # Properties for controlled access to private fields
    @property
    def rotation_increment(self) -> int:
        """Get current rotation increment in degrees"""
        return self.__rotation_increment

    @rotation_increment.setter
    def rotation_increment(self, value: int):
        """Set rotation increment with bounds checking"""
        if 1 <= value <= 30:
            self.__rotation_increment = value
        else:
            raise ValueError("Rotation increment must be between 1 and 30 degrees")

    @property
    def globe_rotation_x(self) -> int:
        """Get globe X rotation in degrees"""
        return self.__globe_rotation_x

    @property
    def globe_rotation_y(self) -> int:
        """Get globe Y rotation in degrees"""
        return self.__globe_rotation_y

    @property
    def globe_rotation_z(self) -> int:
        """Get globe Z rotation in degrees"""
        return self.__globe_rotation_z

    @property
    def taskManager(self):
        """Get task manager for scheduling tasks"""
        return self.taskMgr

    def __setup_environment(self):
        """Setup the application environment"""
        self.setBackgroundColor(0.1, 0.1, 0.3)

    def __setup_lighting(self):
        """Setup ambient and directional lighting"""
        # Add ambient light
        ambient = AmbientLight('ambient')
        ambient.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        # Add directional light
        sun = DirectionalLight('sun')
        sun.setColor((0.8, 0.8, 0.8, 1))
        sun.setDirection((-1, -1, -1))
        self.render.setLight(self.render.attachNewNode(sun))

    def __load_world_data(self):
        """Load real world data using WorldDataManager"""
        data_manager = WorldDataManager()
        self.__continents = data_manager.getContinents()
        print(f"Loaded {len(self.__continents)} continents")

    def __create_globe(self):
        """Create the 3D globe with continents"""
        self.__globe = self.render.attachNewNode("globe")

        # Create transparent ocean sphere
        ocean = _create_sphere(1.0, (0.2, 0.4, 0.8, 0.4))
        ocean.reparentTo(self.__globe)
        ocean.setTransparency(TransparencyAttrib.MAlpha)
        print("Ocean sphere created")

        # Add continents with colors
        colors = {
            'Europe': (0.8, 0.2, 0.2, 1),       # Red
            'Africa': (0.9, 0.5, 0.1, 1),       # Orange
            'North America': (0.2, 0.8, 0.3, 1), # Green
            'South America': (0.9, 0.7, 0.1, 1), # Yellow
            'Asia': (0.6, 0.2, 0.7, 1),         # Purple
            'Oceania': (0.2, 0.7, 0.9, 1)       # Light Blue
        }

        continent_count = 0
        for name, geometry in self.__continents.items():
            color = colors.get(name, (0.7, 0.7, 0.7, 1))
            self.__add_continent_geometry(geometry, color, name)
            continent_count += 1
            print(f"Added continent: {name}")

        self.__globe.setScale(3, 3, 3)
        print(f"Globe created with {continent_count} continents")

        # Apply initial rotation
        self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)

    def __add_continent_geometry(self, geometry, color, name):
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

            vertices_3d = []
            radius = 1.05

            for lon, lat in coords:
                lat_rad = lat * pi / 180.0
                lon_rad = lon * pi / 180.0
                x = cos(lat_rad) * sin(lon_rad) * radius
                y = sin(lat_rad) * radius
                z = cos(lat_rad) * cos(lon_rad) * radius
                vertices_3d.append((x, y, z))

            # Create geometry
            part_name = f"{name}_part_{i}" if len(polygons) > 1 else name
            format = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData(part_name, format, Geom.UHStatic)
            vdata.setNumRows(len(vertices_3d))
            vertex = GeomVertexWriter(vdata, "vertex")
            normal = GeomVertexWriter(vdata, "normal")

            for x, y, z in vertices_3d:
                vertex.addData3f(x, y, z)
                length = (x*x + y*y + z*z) ** 0.5
                normal.addData3f(x/length, y/length, z/length)

            geom = Geom(vdata)
            tris = GeomTriangles(Geom.UHStatic)

            for j in range(1, len(vertices_3d) - 1):
                tris.addVertices(0, j, j + 1)
                tris.closePrimitive()

            geom.addPrimitive(tris)

            continent_node = GeomNode(f"continent_{part_name}")
            continent_node.addGeom(geom)
            continent_np = self.__globe.attachNewNode(continent_node)
            continent_np.setColor(*color)
            continent_np.setTwoSided(True)

    def __setup_camera(self):
        """Setup camera position and controls"""
        # Disable mouse control to prevent interference
        self.disableMouse()

        # Set camera position to achieve distance 15
        scale_factor = 15.0 / 35.6
        self.__default_camera_pos = (15 * scale_factor, -30 * scale_factor, 10 * scale_factor)
        self.camera.setPos(*self.__default_camera_pos)
        self.camera.lookAt(0, 0, 0)

        # Debug camera position
        pos = self.camera.getPos()
        distance = pos.length()
        print(f"Camera setup: Position {pos}, Distance: {distance:.1f}")
        print("Mouse controls disabled to prevent camera interference")

    # Public methods for GUI to call
    def zoom_in(self):
        """Move camera closer to globe center"""
        current_pos = self.camera.getPos()
        current_distance = current_pos.length()

        self.__gui_controller.add_log_message(f"ZOOM IN - Distance: {current_distance:.1f}")

        if current_distance < 0.1:
            self.__gui_controller.add_log_message("Camera reset to default position")
            self.camera.setPos(*self.__default_camera_pos)
            self.camera.lookAt(0, 0, 0)
            return

        target_distance = max(current_distance * 0.8, 8.0)

        if target_distance >= current_distance - 0.1:
            self.__gui_controller.add_log_message("Already at minimum zoom distance")
            return

        direction_x = current_pos.x / current_distance
        direction_y = current_pos.y / current_distance
        direction_z = current_pos.z / current_distance

        new_pos = (
            direction_x * target_distance,
            direction_y * target_distance,
            direction_z * target_distance
        )

        self.camera.setPos(*new_pos)
        self.camera.lookAt(0, 0, 0)

        verify_distance = self.camera.getPos().length()
        self.__gui_controller.add_log_message(f"Zoomed in to distance: {verify_distance:.1f}")

    def zoom_out(self):
        """Move camera further from globe center"""
        current_pos = self.camera.getPos()
        current_distance = current_pos.length()

        self.__gui_controller.add_log_message(f"ZOOM OUT - Distance: {current_distance:.1f}")

        if current_distance < 0.1:
            self.__gui_controller.add_log_message("Camera reset to default position")
            self.camera.setPos(*self.__default_camera_pos)
            self.camera.lookAt(0, 0, 0)
            return

        target_distance = min(current_distance * 1.25, 80.0)

        if target_distance <= current_distance + 0.1:
            self.__gui_controller.add_log_message("Already at maximum zoom distance")
            return

        direction_x = current_pos.x / current_distance
        direction_y = current_pos.y / current_distance
        direction_z = current_pos.z / current_distance

        new_pos = (
            direction_x * target_distance,
            direction_y * target_distance,
            direction_z * target_distance
        )

        self.camera.setPos(*new_pos)
        self.camera.lookAt(0, 0, 0)

        verify_distance = self.camera.getPos().length()
        self.__gui_controller.add_log_message(f"Zoomed out to distance: {verify_distance:.1f}")

    def reset_view(self):
        """Reset camera position and globe rotation to default"""
        self.camera.setPos(*self.__default_camera_pos)
        self.camera.lookAt(0, 0, 0)

        self.__globe_rotation_x = 105
        self.__globe_rotation_y = 0
        self.__globe_rotation_z = 0
        self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)

        pos = self.camera.getPos()
        distance = pos.length()
        self.__gui_controller.add_log_message(f"RESET: Distance {distance:.1f} | Rotation X=105° Y=0° Z=0°")

    def rotate_up(self):
        """Rotate globe up by increment amount"""
        self.__globe_rotation_x += self.__rotation_increment
        self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)
        self.__gui_controller.add_log_message(f"UP: X={self.__globe_rotation_x}° Y={self.__globe_rotation_y}° Z={self.__globe_rotation_z}°")

    def rotate_down(self):
        """Rotate globe down by increment amount"""
        self.__globe_rotation_x -= self.__rotation_increment
        self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)
        self.__gui_controller.add_log_message(f"DOWN: X={self.__globe_rotation_x}° Y={self.__globe_rotation_y}° Z={self.__globe_rotation_z}°")

    def rotate_left(self):
        """Rotate globe left by increment amount"""
        self.__globe_rotation_z -= self.__rotation_increment
        self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)
        self.__gui_controller.add_log_message(f"LEFT: X={self.__globe_rotation_x}° Y={self.__globe_rotation_y}° Z={self.__globe_rotation_z}°")

    def rotate_right(self):
        """Rotate globe right by increment amount"""
        self.__globe_rotation_z += self.__rotation_increment
        self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)
        self.__gui_controller.add_log_message(f"RIGHT: X={self.__globe_rotation_x}° Y={self.__globe_rotation_y}° Z={self.__globe_rotation_z}°")

    def increase_rotation_increment(self):
        """Increase rotation increment by 1 degree (max 30)"""
        if self.__rotation_increment < 30:
            self.__rotation_increment += 1
            print(f"Rotation increment: {self.__rotation_increment}°")
            self.__gui_controller.add_log_message(f"Rotation increment increased to {self.__rotation_increment}°")
        else:
            print(f"Rotation increment: {self.__rotation_increment}° (MAX)")
            self.__gui_controller.add_log_message("Maximum rotation increment reached (30°)")

    def decrease_rotation_increment(self):
        """Decrease rotation increment by 1 degree (min 1)"""
        if self.__rotation_increment > 1:
            self.__rotation_increment -= 1
            print(f"Rotation increment: {self.__rotation_increment}°")
            self.__gui_controller.add_log_message(f"Rotation increment decreased to {self.__rotation_increment}°")
        else:
            print(f"Rotation increment: {self.__rotation_increment}° (MIN)")
            self.__gui_controller.add_log_message("Minimum rotation increment reached (1°)")

    def set_preset_view(self, index):
        """Set the globe to a specific preset view"""
        if 0 <= index < len(self.__preset_views):
            chosen_view = self.__preset_views[index]
            self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y = chosen_view["rotation"]
            self.__globe.setHpr(self.__globe_rotation_z, self.__globe_rotation_x, self.__globe_rotation_y)
            self.__gui_controller.add_log_message(f"{chosen_view['name']}: X={self.__globe_rotation_x}° Y={self.__globe_rotation_y}° Z={self.__globe_rotation_z}°")


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
