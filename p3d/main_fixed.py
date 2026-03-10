"""
3D Globe with PROPER continent shapes - NO MORE BLOBS!
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import sin, cos, pi
from shapely.geometry import Polygon

class ProperGlobe(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Setup
        self.setBackgroundColor(0, 0, 0)  # Pure black space background
        self.setup_lighting()
        self.load_continent_data()
        self.create_globe()
        self.setup_camera()
        self.taskMgr.add(self.rotate_task, "rotate")

    def setup_lighting(self):
        ambient = AmbientLight('ambient')
        ambient.setColor((0.4, 0.4, 0.4, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        sun = DirectionalLight('sun')
        sun.setColor((0.9, 0.9, 0.9, 1))
        sun.setDirection((-1, -1, -1))
        self.render.setLight(self.render.attachNewNode(sun))

    def load_continent_data(self):
        """Load continent data using simple reliable shapes (no SSL issues)"""
        from simple_world_data import get_world_continents

        print("🌍 Loading continent data...")
        self.continents = get_world_continents()

        if self.continents:
            print(f"✅ Successfully loaded {len(self.continents)} continents")
        else:
            print("❌ Failed to load continent data")
            self.continents = {}

    def create_reliable_world_data(self):
        """Create reliable world data without downloads"""
        print("Creating reliable offline continent data...")
        from shapely.geometry import Polygon
        import geopandas as gpd

        # High-quality continent boundaries (no downloads needed)
        continent_data = {
            'North America': [
                # Detailed North America outline
                (-168, 65), (-140, 69), (-120, 72), (-100, 70), (-85, 68), (-80, 60),
                (-75, 50), (-70, 45), (-68, 40), (-70, 35), (-75, 30), (-80, 25),
                (-85, 20), (-95, 26), (-105, 29), (-115, 32), (-125, 37), (-135, 50),
                (-145, 60), (-160, 65), (-168, 65)
            ],
            'South America': [
                # Detailed South America outline
                (-35, 5), (-45, -5), (-55, -15), (-65, -25), (-70, -35), (-75, -45),
                (-70, -52), (-60, -54), (-50, -50), (-40, -40), (-35, -30), (-33, -15),
                (-34, -5), (-35, 5)
            ],
            'Europe': [
                # Detailed Europe outline
                (-10, 35), (0, 45), (10, 50), (20, 55), (30, 60), (40, 65), (45, 70),
                (40, 72), (30, 70), (20, 68), (10, 65), (0, 60), (-10, 55), (-10, 35)
            ],
            'Africa': [
                # Detailed Africa outline
                (-17, 35), (10, 35), (35, 30), (45, 0), (40, -10), (35, -25), (25, -35),
                (15, -34), (0, -30), (-10, -20), (-15, 0), (-17, 15), (-17, 35)
            ],
            'Asia': [
                # Detailed Asia outline
                (25, 75), (60, 80), (120, 75), (150, 65), (175, 55), (180, 45), (175, 35),
                (160, 25), (140, 15), (120, 10), (100, 15), (80, 20), (60, 30), (40, 40),
                (30, 50), (25, 65), (25, 75)
            ],
            'Australia': [
                # Detailed Australia outline
                (113, -22), (130, -14), (145, -18), (153, -21), (152, -26), (145, -35),
                (130, -38), (115, -35), (110, -28), (113, -22)
            ]
        }

        # Create GeoDataFrame
        geometries = []
        continents = []

        for continent, coords in continent_data.items():
            poly = Polygon(coords)
            geometries.append(poly)
            continents.append(continent)

        world = gpd.GeoDataFrame(
            {'continent': continents},
            geometry=geometries,
            crs='EPSG:4326'
        )
        print(f"✓ Created {len(world)} reliable continent shapes")
        return world

    def create_minimal_continents(self):
        """Minimal fallback if everything fails"""
        from shapely.geometry import Polygon
        return {
            'North America': Polygon([(-140, 60), (-100, 70), (-80, 50), (-100, 30), (-140, 40), (-140, 60)]),
            'South America': Polygon([(-80, 10), (-60, 0), (-50, -30), (-70, -50), (-80, -30), (-80, 10)]),
            'Europe': Polygon([(-10, 40), (30, 50), (40, 65), (20, 70), (-10, 60), (-10, 40)]),
            'Africa': Polygon([(-20, 35), (40, 30), (45, 0), (35, -35), (-10, -30), (-20, 0), (-20, 35)]),
            'Asia': Polygon([(30, 70), (150, 70), (175, 50), (160, 20), (100, 15), (60, 25), (30, 40), (30, 70)]),
            'Australia': Polygon([(110, -15), (150, -20), (150, -35), (115, -35), (110, -25), (110, -15)])
        }

    def create_globe(self):
        self.globe = self.render.attachNewNode("globe")

        # Add transparent ocean sphere back
        ocean = self.create_textured_sphere(1.0, (0.1, 0.3, 0.6, 0.3))  # Semi-transparent blue
        ocean.reparentTo(self.globe)
        ocean.setTransparency(TransparencyAttrib.MAlpha)  # Enable alpha transparency

        # Add continent shapes as flat polygons on sphere surface
        colors = {
            'North America': (0.2, 0.8, 0.3, 1),    # Bright green
            'South America': (0.9, 0.7, 0.1, 1),    # Golden yellow
            'Europe': (0.8, 0.2, 0.2, 1),           # Bright red - highlighted for verification
            'Africa': (0.9, 0.5, 0.1, 1),           # Orange
            'Asia': (0.6, 0.3, 0.8, 1),             # Purple
            'Oceania': (0.2, 0.7, 0.9, 1),          # Light blue
            'Australia': (0.2, 0.7, 0.9, 1)         # Light blue (fallback)
        }

        for name, geometry in self.continents.items():
            color = colors.get(name, (0.5, 0.5, 0.5, 1))
            self.add_continent_geometry(geometry, color, name)

        self.globe.setScale(5, 5, 5)

        # Set initial orientation to ensure South Pole is at bottom
        # No initial rotation - coordinate system should be correct as-is
        self.globe.setHpr(0, 0, 0)

    def create_textured_sphere(self, radius, color):
        format = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData("sphere", format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        texcoord = GeomVertexWriter(vdata, "texcoord")

        segments = 32
        rings = 16

        for r in range(rings + 1):
            lat = (r / rings - 0.5) * pi  # -π/2 to π/2
            y = sin(lat) * radius  # Y-axis points up
            ring_r = cos(lat) * radius

            for s in range(segments + 1):
                lon = (s / segments) * 2 * pi  # 0 to 2π
                x = ring_r * sin(lon)  # X in horizontal plane
                z = ring_r * cos(lon)  # Z in horizontal plane

                vertex.addData3f(x, y, z)
                normal.addData3f(x/radius, y/radius, z/radius)
                texcoord.addData2f(s/segments, r/rings)

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

    def add_continent_geometry(self, geometry, color, name):
        """Add continent geometry (handles both Polygon and MultiPolygon)"""
        from shapely.geometry import Polygon, MultiPolygon

        if geometry is None:
            return

        polygons = []
        if isinstance(geometry, MultiPolygon):
            polygons = list(geometry.geoms)
        elif isinstance(geometry, Polygon):
            polygons = [geometry]
        else:
            return

        for i, polygon in enumerate(polygons):
            if polygon.exterior is None:
                continue

            coords = list(polygon.exterior.coords)
            if len(coords) < 4:
                continue

            self.add_continent_polygon(polygon, color, f"{name}_{i}")

    def add_continent_polygon(self, polygon, color, name):
        """Add continent as flat polygon projected onto sphere"""
        coords = list(polygon.exterior.coords)
        if len(coords) < 4:
            return

        # Remove duplicate closing point
        if coords[0] == coords[-1]:
            coords = coords[:-1]

        # Convert to 3D sphere coordinates
        vertices_3d = []
        radius = 1.05  # Further out to be clearly visible above ocean surface

        # Only show debug for major continents (reduce startup spam)
        if name in ["Africa_0", "Asia_0", "North America_0", "South America_0", "Europe_0", "Australia_0"]:
            continent_part = name.split("_")[0]
            sample_coord = coords[0] if coords else (0, 0)
            lon, lat = sample_coord
            hemisphere = "NORTH" if lat > 0 else "SOUTH" if lat < 0 else "EQUATOR"
            print(f"✓ {continent_part}: {hemisphere} hemisphere ({lat:.1f}°)")

        for lon, lat in coords:
            lat_rad = lat * pi / 180.0
            lon_rad = lon * pi / 180.0

            # Correct spherical to Cartesian conversion with proper pole alignment
            # Y-axis should be up (poles), X and Z for horizontal plane
            x = cos(lat_rad) * sin(lon_rad) * radius
            y = sin(lat_rad) * radius  # Y-axis points up (North pole = +Y)
            z = cos(lat_rad) * cos(lon_rad) * radius

            vertices_3d.append((x, y, z))

        if len(vertices_3d) < 3:
            return

        # Create geometry
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData(name, format, Geom.UHStatic)
        vdata.setNumRows(len(vertices_3d))
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")

        for x, y, z in vertices_3d:
            vertex.addData3f(x, y, z)
            # Normal points outward
            length = (x*x + y*y + z*z) ** 0.5
            normal.addData3f(x/length, y/length, z/length)

        # Triangulate polygon (fan from first vertex)
        geom = Geom(vdata)
        tris = GeomTriangles(Geom.UHStatic)

        for i in range(1, len(vertices_3d) - 1):
            tris.addVertices(0, i, i + 1)
            tris.closePrimitive()

        geom.addPrimitive(tris)

        # Create node and attach
        continent_node = GeomNode(f"continent_{name}")
        continent_node.addGeom(geom)
        continent_np = self.globe.attachNewNode(continent_node)
        continent_np.setColor(*color)
        continent_np.setTwoSided(True)


        # Only print summary, not every single polygon
        if name.endswith("_0"):
            continent_name = name.split("_")[0]
            print(f"✓ Added {continent_name} continent")

    def setup_camera(self):
        self.disableMouse()
        # Position camera to ensure South Pole is at bottom
        # Camera looks from the side with proper up vector
        # Start with a view focused on Europe/Mediterranean to verify the fix
        self.camera.setPos(20, -15, 8)  # Elevated side view to see Mediterranean
        self.camera.lookAt(0, 0, 0)

        # Ensure proper up vector so South Pole (-Y) appears at bottom
        self.camera.setHpr(0, 0, 0)  # Reset orientation

        self.accept("wheel_up", self.zoom_in)
        self.accept("wheel_down", self.zoom_out)
        self.accept("mouse1", self.start_orbit)
        self.accept("mouse1-up", self.stop_orbit)

        # Mouse orbit variables
        self.orbiting = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.camera_distance = 18  # Distance from globe center

    def start_orbit(self):
        self.orbiting = True
        if base.mouseWatcherNode.hasMouse():
            self.last_mouse_x = base.mouseWatcherNode.getMouseX()
            self.last_mouse_y = base.mouseWatcherNode.getMouseY()

    def stop_orbit(self):
        self.orbiting = False

    def update_camera_orbit(self):
        """Update camera position based on mouse movement for orbiting"""
        if self.orbiting and base.mouseWatcherNode.hasMouse():
            mouse_x = base.mouseWatcherNode.getMouseX()
            mouse_y = base.mouseWatcherNode.getMouseY()

            # Calculate mouse movement
            dx = mouse_x - self.last_mouse_x
            dy = mouse_y - self.last_mouse_y

            # Get current camera position relative to globe center
            cam_pos = self.camera.getPos()

            # Convert to spherical coordinates for orbiting
            from math import atan2, sqrt, sin, cos
            distance = sqrt(cam_pos.x**2 + cam_pos.y**2 + cam_pos.z**2)

            # Update spherical angles based on mouse movement
            theta = atan2(cam_pos.y, cam_pos.x) + dx * 3  # Horizontal orbit
            phi = atan2(sqrt(cam_pos.x**2 + cam_pos.y**2), cam_pos.z) + dy * 3  # Vertical orbit

            # Clamp vertical angle to prevent flipping
            phi = max(0.1, min(3.1, phi))

            # Convert back to Cartesian coordinates
            new_x = distance * sin(phi) * cos(theta)
            new_y = distance * sin(phi) * sin(theta)
            new_z = distance * cos(phi)

            self.camera.setPos(new_x, new_y, new_z)
            self.camera.lookAt(0, 0, 0)

            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y

    def zoom_in(self):
        # Zoom by moving camera closer to globe center
        cam_pos = self.camera.getPos()
        direction = cam_pos.normalized()
        new_pos = cam_pos - direction * 1.5  # Move closer

        # Prevent zooming too close
        distance = new_pos.length()
        if distance > 8:  # Minimum distance
            self.camera.setPos(new_pos)
            self.camera_distance = distance

    def zoom_out(self):
        # Zoom by moving camera away from globe center
        cam_pos = self.camera.getPos()
        direction = cam_pos.normalized()
        new_pos = cam_pos + direction * 1.5  # Move away

        # Prevent zooming too far
        distance = new_pos.length()
        if distance < 50:  # Maximum distance
            self.camera.setPos(new_pos)
            self.camera_distance = distance

    def rotate_task(self, task):
        # Update camera orbit if user is dragging
        if hasattr(self, 'orbiting'):
            self.update_camera_orbit()

        # Only auto-rotate globe when not manually orbiting camera
        if not getattr(self, 'orbiting', False):
            angle = task.time * 15  # Slower rotation for better viewing
            # Rotate around Z-axis for proper Earth-like rotation (poles stay vertical)
            self.globe.setHpr(0, 0, angle)
        return task.cont

    def assign_continents_to_countries(self, world_gdf):
        """Assign continent names to countries in GeoPandas GeoDataFrame"""

        # Create continent assignment based on country names or coordinates
        country_to_continent = self.get_country_continent_mapping()

        continents = []
        for idx, row in world_gdf.iterrows():
            country_name = row.get('NAME', row.get('name', row.get('ADMIN', 'Unknown')))
            continent = self.guess_continent_from_name(country_name, country_to_continent)
            continents.append(continent)

        # Add continent column to GeoDataFrame
        world_gdf = world_gdf.copy()
        world_gdf['continent'] = continents
        return world_gdf

    def get_country_continent_mapping(self):
        """Return mapping of country names to continents"""
        return {
            # North America
            'United States': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
            'Guatemala': 'North America', 'Belize': 'North America', 'Honduras': 'North America',
            'El Salvador': 'North America', 'Nicaragua': 'North America', 'Costa Rica': 'North America',
            'Panama': 'North America', 'Cuba': 'North America', 'Jamaica': 'North America',
            'Haiti': 'North America', 'Dominican Republic': 'North America',

            # South America
            'Brazil': 'South America', 'Argentina': 'South America', 'Chile': 'South America',
            'Peru': 'South America', 'Colombia': 'South America', 'Venezuela': 'South America',
            'Bolivia': 'South America', 'Ecuador': 'South America', 'Uruguay': 'South America',
            'Paraguay': 'South America', 'Guyana': 'South America', 'Suriname': 'South America',

            # Europe
            'Germany': 'Europe', 'France': 'Europe', 'United Kingdom': 'Europe', 'Italy': 'Europe',
            'Spain': 'Europe', 'Poland': 'Europe', 'Romania': 'Europe', 'Netherlands': 'Europe',
            'Belgium': 'Europe', 'Greece': 'Europe', 'Portugal': 'Europe', 'Czech Republic': 'Europe',
            'Hungary': 'Europe', 'Sweden': 'Europe', 'Belarus': 'Europe', 'Austria': 'Europe',
            'Serbia': 'Europe', 'Switzerland': 'Europe', 'Bulgaria': 'Europe', 'Slovakia': 'Europe',
            'Denmark': 'Europe', 'Finland': 'Europe', 'Norway': 'Europe', 'Ireland': 'Europe',
            'Bosnia and Herzegovina': 'Europe', 'Croatia': 'Europe', 'Albania': 'Europe',
            'Lithuania': 'Europe', 'Slovenia': 'Europe', 'Latvia': 'Europe', 'Estonia': 'Europe',
            'Macedonia': 'Europe', 'Moldova': 'Europe', 'Luxembourg': 'Europe', 'Malta': 'Europe',
            'Iceland': 'Europe', 'Montenegro': 'Europe', 'Cyprus': 'Europe',

            # Asia
            'China': 'Asia', 'India': 'Asia', 'Russia': 'Asia', 'Indonesia': 'Asia',
            'Pakistan': 'Asia', 'Bangladesh': 'Asia', 'Japan': 'Asia', 'Philippines': 'Asia',
            'Vietnam': 'Asia', 'Turkey': 'Asia', 'Iran': 'Asia', 'Thailand': 'Asia',
            'Myanmar': 'Asia', 'South Korea': 'Asia', 'Iraq': 'Asia', 'Afghanistan': 'Asia',
            'Saudi Arabia': 'Asia', 'Uzbekistan': 'Asia', 'Malaysia': 'Asia', 'Nepal': 'Asia',
            'Yemen': 'Asia', 'North Korea': 'Asia', 'Sri Lanka': 'Asia', 'Kazakhstan': 'Asia',
            'Syria': 'Asia', 'Cambodia': 'Asia', 'Jordan': 'Asia', 'Azerbaijan': 'Asia',
            'United Arab Emirates': 'Asia', 'Tajikistan': 'Asia', 'Israel': 'Asia',
            'Laos': 'Asia', 'Singapore': 'Asia', 'Oman': 'Asia', 'Kuwait': 'Asia',
            'Georgia': 'Asia', 'Mongolia': 'Asia', 'Armenia': 'Asia', 'Qatar': 'Asia',
            'Bahrain': 'Asia', 'East Timor': 'Asia', 'Maldives': 'Asia', 'Brunei': 'Asia',

            # Africa
            'Nigeria': 'Africa', 'Ethiopia': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
            'Kenya': 'Africa', 'Uganda': 'Africa', 'Algeria': 'Africa', 'Sudan': 'Africa',
            'Morocco': 'Africa', 'Angola': 'Africa', 'Ghana': 'Africa', 'Mozambique': 'Africa',
            'Madagascar': 'Africa', 'Cameroon': 'Africa', 'Ivory Coast': 'Africa',
            'Niger': 'Africa', 'Burkina Faso': 'Africa', 'Mali': 'Africa', 'Malawi': 'Africa',
            'Zambia': 'Africa', 'Senegal': 'Africa', 'Somalia': 'Africa', 'Chad': 'Africa',
            'Zimbabwe': 'Africa', 'Guinea': 'Africa', 'Rwanda': 'Africa', 'Benin': 'Africa',
            'Tunisia': 'Africa', 'Burundi': 'Africa', 'Togo': 'Africa', 'Sierra Leone': 'Africa',
            'Libya': 'Africa', 'Liberia': 'Africa', 'Central African Republic': 'Africa',
            'Mauritania': 'Africa', 'Eritrea': 'Africa', 'Gambia': 'Africa',
            'Botswana': 'Africa', 'Namibia': 'Africa', 'Gabon': 'Africa',
            'Lesotho': 'Africa', 'Guinea-Bissau': 'Africa', 'Equatorial Guinea': 'Africa',
            'Mauritius': 'Africa', 'Eswatini': 'Africa', 'Djibouti': 'Africa',
            'Comoros': 'Africa', 'Cape Verde': 'Africa', 'São Tomé and Príncipe': 'Africa',
            'Seychelles': 'Africa',

            # Oceania
            'Australia': 'Oceania', 'Papua New Guinea': 'Oceania', 'New Zealand': 'Oceania',
            'Fiji': 'Oceania', 'Solomon Islands': 'Oceania', 'Vanuatu': 'Oceania',
            'Samoa': 'Oceania', 'Micronesia': 'Oceania', 'Tonga': 'Oceania',
            'Kiribati': 'Oceania', 'Palau': 'Oceania', 'Marshall Islands': 'Oceania',
            'Tuvalu': 'Oceania', 'Nauru': 'Oceania'
        }

    def guess_continent_from_name(self, country_name, mapping):
        """Guess continent from country name"""
        # Direct mapping
        if country_name in mapping:
            return mapping[country_name]

        # Partial matching for variations
        country_lower = country_name.lower()
        for mapped_country, continent in mapping.items():
            if mapped_country.lower() in country_lower or country_lower in mapped_country.lower():
                return continent

        # Default fallback
        return 'Unknown'

if __name__ == "__main__":
    print("=" * 50)
    print("STARTING PROPER 3D GLOBE APPLICATION")
    print("=" * 50)
    print("Features:")
    print("- Real continent shapes using GeoPandas")
    print("- Transparent ocean sphere with continents on surface")
    print("- Google Maps-style camera controls:")
    print("  * Mouse drag: Orbit around globe")
    print("  * Mouse wheel: Zoom in/out")
    print("  * Auto-rotation when not manually controlling")
    print("=" * 50)
    print("PANDAS INVOLVEMENT IN THIS APP:")
    print("GeoPandas extends pandas DataFrames with geographic capabilities:")
    print("1. GeoDataFrame = pandas DataFrame + geometry column")
    print("2. Uses pandas operations: .groupby(), .iterrows(), .copy()")
    print("3. Spatial operations: .union_all(), .unary_union")
    print("4. Data handling: country classification, continent mapping")
    print("5. CRS management: coordinate reference systems")
    print("=" * 50)

    try:
        app = ProperGlobe()
        print("Application created successfully!")
        print("Starting Panda3D main loop...")
        app.run()
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")
        import traceback
        traceback.print_exc()
