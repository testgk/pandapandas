"""
3D Globe with continents using Panda3D and GeoPandas
"""
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from math import sin, cos, pi
import geopandas as gpd
import numpy as np


class GlobeApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load world data with GeoPandas
        self.load_world_data()

        # Create the globe
        self.setup_globe()

        # Setup camera and controls
        self.setup_camera()

        # Start rotation task
        self.taskMgr.add(self.rotate_globe_task, "rotate-globe")

    def load_world_data(self):
        """Load world continent data using Natural Earth data"""
        try:
            # Download Natural Earth data directly
            url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"
            self.world = gpd.read_file(url)
            print(f"Loaded {len(self.world)} countries/regions")
        except Exception as e:
            print(f"Error loading world data: {e}")
            # Create a simple fallback dataset with major continents
            self.create_fallback_world_data()

    def create_fallback_world_data(self):
        """Create simple continent shapes if data loading fails"""
        from shapely.geometry import Polygon

        # Simple rectangular approximations of continents
        continents_data = [
            # continent, geometry (lon_min, lat_min, lon_max, lat_max)
            ("North America", Polygon([(-170, 15), (-170, 75), (-50, 75), (-50, 15), (-170, 15)])),
            ("South America", Polygon([(-85, -55), (-85, 15), (-35, 15), (-35, -55), (-85, -55)])),
            ("Europe", Polygon([(-10, 35), (-10, 75), (40, 75), (40, 35), (-10, 35)])),
            ("Africa", Polygon([(-20, -35), (-20, 35), (50, 35), (50, -35), (-20, -35)])),
            ("Asia", Polygon([(40, 5), (40, 75), (180, 75), (180, 5), (40, 5)])),
            ("Oceania", Polygon([(110, -50), (110, 10), (180, 10), (180, -50), (110, -50)])),
            ("Antarctica", Polygon([(-180, -90), (-180, -60), (180, -60), (180, -90), (-180, -90)]))
        ]

        self.world = gpd.GeoDataFrame(
            {"continent": [c[0] for c in continents_data]},
            geometry=[c[1] for c in continents_data],
            crs="EPSG:4326"
        )
        print(f"Created fallback data with {len(self.world)} continents")

    def setup_globe(self):
        """Create the 3D globe with continents"""
        # Create clean globe node (no environment loading)
        self.globe = self.render.attachNewNode("globe")

        # Generate sphere mesh
        self.create_sphere_mesh()

        # Add continent geometries
        if self.world is not None:
            self.add_continents()

        # Setup globe properties
        self.globe.setScale(2, 2, 2)

        # Setup lighting for better visibility
        self.setup_lighting()

    def create_sphere_mesh(self):
        """Create a procedural sphere mesh"""
        # Create sphere using Panda3D's built-in geometry
        format = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData("sphere", format, Geom.UHStatic)
        vdata.setNumRows(2000)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        texcoord = GeomVertexWriter(vdata, "texcoord")

        # Generate sphere vertices
        radius = 1.0
        segments = 32
        rings = 16

        for r in range(rings + 1):
            lat = (r / rings - 0.5) * pi
            y = sin(lat) * radius
            ring_radius = cos(lat) * radius

            for s in range(segments + 1):
                lon = (s / segments) * 2 * pi
                x = cos(lon) * ring_radius
                z = sin(lon) * ring_radius

                vertex.addData3f(x, y, z)
                normal.addData3f(x/radius, y/radius, z/radius)
                texcoord.addData2f(s/segments, r/rings)

        # Create geometry
        geom = Geom(vdata)

        # Add triangles
        for r in range(rings):
            for s in range(segments):
                # Two triangles per quad
                tri1 = GeomTriangles(Geom.UHStatic)
                tri2 = GeomTriangles(Geom.UHStatic)

                v1 = r * (segments + 1) + s
                v2 = r * (segments + 1) + s + 1
                v3 = (r + 1) * (segments + 1) + s
                v4 = (r + 1) * (segments + 1) + s + 1

                tri1.addVertices(v1, v3, v2)
                tri1.closePrimitive()

                tri2.addVertices(v2, v3, v4)
                tri2.closePrimitive()

                geom.addPrimitive(tri1)
                geom.addPrimitive(tri2)

        # Create node and attach to globe
        sphere_node = GeomNode("sphere")
        sphere_node.addGeom(geom)
        sphere_np = self.globe.attachNewNode(sphere_node)

        # Set blue color for oceans
        sphere_np.setColor(0.2, 0.4, 0.8, 1.0)

    def add_continents(self):
        """Add continent geometries to the globe"""
        continent_colors = {
            'North America': (0.2, 0.8, 0.2, 1.0),
            'South America': (0.8, 0.8, 0.2, 1.0),
            'Europe': (0.8, 0.2, 0.2, 1.0),
            'Africa': (0.8, 0.4, 0.2, 1.0),
            'Asia': (0.6, 0.2, 0.8, 1.0),
            'Oceania': (0.2, 0.8, 0.8, 1.0),
            'Antarctica': (0.9, 0.9, 0.9, 1.0)
        }

        for idx, country in self.world.iterrows():
            continent = country.get('continent', 'Unknown')
            geometry = country['geometry']

            if geometry is None:
                continue

            color = continent_colors.get(continent, (0.5, 0.5, 0.5, 1.0))

            # Convert geographic coordinates to 3D sphere coordinates
            self.add_country_to_sphere(geometry, color)

    def add_country_to_sphere(self, geometry, color):
        """Convert country geometry to 3D sphere surface"""
        from shapely.geometry import MultiPolygon, Polygon

        if isinstance(geometry, MultiPolygon):
            polygons = list(geometry.geoms)
        elif isinstance(geometry, Polygon):
            polygons = [geometry]
        else:
            return

        for polygon in polygons:
            if polygon.exterior is None:
                continue

            coords = list(polygon.exterior.coords)
            if len(coords) < 3:
                continue

            # Create geometry for this polygon
            self.create_polygon_on_sphere(coords, color)

    def create_polygon_on_sphere(self, coords, color):
        """Create a polygon on the sphere surface"""
        if len(coords) < 3:
            return

        # Convert lat/lon to 3D coordinates on unit sphere
        vertices_3d = []
        radius = 1.02  # Slightly larger than sphere to avoid z-fighting

        for lon, lat in coords:
            # Convert degrees to radians
            lat_rad = lat * pi / 180.0
            lon_rad = lon * pi / 180.0

            # Convert to 3D sphere coordinates
            x = cos(lat_rad) * cos(lon_rad) * radius
            z = cos(lat_rad) * sin(lon_rad) * radius
            y = sin(lat_rad) * radius

            vertices_3d.append((x, y, z))

        if len(vertices_3d) < 3:
            return

        # Create vertex data
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData("polygon", format, Geom.UHStatic)
        vdata.setNumRows(len(vertices_3d))
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")

        for x, y, z in vertices_3d:
            vertex.addData3f(x, y, z)
            # Normal points outward from sphere center
            length = (x*x + y*y + z*z) ** 0.5
            normal.addData3f(x/length, y/length, z/length)

        # Create triangulated polygon
        geom = Geom(vdata)

        # Simple fan triangulation from first vertex
        if len(vertices_3d) >= 3:
            tris = GeomTriangles(Geom.UHStatic)
            for i in range(1, len(vertices_3d) - 1):
                tris.addVertices(0, i, i + 1)
                tris.closePrimitive()
            geom.addPrimitive(tris)

        # Create node and attach
        poly_node = GeomNode("continent_poly")
        poly_node.addGeom(geom)
        poly_np = self.globe.attachNewNode(poly_node)
        poly_np.setColor(*color)

    def setup_camera(self):
        """Setup camera position and controls"""
        self.disableMouse()

        # Position camera
        self.camera.setPos(0, -8, 0)
        self.camera.lookAt(0, 0, 0)

        # Enable mouse control for orbit
        self.accept("mouse1", self.start_orbit)
        self.accept("mouse1-up", self.stop_orbit)
        self.accept("wheel_up", self.zoom_in)
        self.accept("wheel_down", self.zoom_out)

        self.orbiting = False

    def start_orbit(self):
        self.orbiting = True

    def stop_orbit(self):
        self.orbiting = False

    def zoom_in(self):
        pos = self.camera.getPos()
        self.camera.setPos(pos * 0.9)

    def zoom_out(self):
        pos = self.camera.getPos()
        self.camera.setPos(pos * 1.1)

    def rotate_globe_task(self, task):
        """Rotate the globe continuously"""
        if not self.orbiting:
            # Auto-rotate when not manually controlling
            angle = task.time * 10  # degrees per second
            self.globe.setHpr(angle, 0, 0)
        return task.cont

    def setup_lighting(self):
        """Setup proper lighting for the globe"""
        # Clear any default lighting
        self.render.clearLight()

        # Add ambient light
        ambient_light = AmbientLight('ambient')
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)

        # Add directional light (like sun)
        directional_light = DirectionalLight('sun')
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        directional_light.setDirection((-1, -1, -1))
        directional_light_np = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_light_np)

        # Set background to space black
        self.setBackgroundColor(0, 0, 0)

if __name__ == "__main__":
    app = GlobeApp()
    app.run()

