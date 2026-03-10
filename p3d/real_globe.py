"""
Real Globe Application with Manual Controls - Final Version
Loads real GeoPandas world data with GUI controls for zoom and rotation
"""
print("Starting Real Globe Application with Manual Controls...")

try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import *
    from direct.gui.OnscreenText import OnscreenText
    from direct.gui.DirectGui import DirectButton
    from math import sin, cos, pi
    import warnings
    import ssl
    import urllib3
    import os
    import requests
    import tempfile
    import random

    print("All imports successful")

    class RealGlobe(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            print("Panda3D initialized")

            # Setup environment
            self.setBackgroundColor(0.1, 0.1, 0.3)
            self.setup_lighting()

            # Manual rotation variables - NO auto-rotation
            self.globe_rotation_x = 0
            self.globe_rotation_y = 0
            self.globe_rotation_z = 0

            # Define interesting natural views
            self.preset_views = [
                {"name": "Europe/Africa View", "rotation": (0, -15, 0), "description": "Shows Europe and Mediterranean"},
                {"name": "Americas View", "rotation": (0, 0, 90), "description": "North and South America centered"},
                {"name": "Asia/Pacific View", "rotation": (0, 15, -120), "description": "Asia and Pacific region"},
                {"name": "Africa/Middle East", "rotation": (0, -30, -30), "description": "Africa and Middle East focus"},
                {"name": "Atlantic View", "rotation": (0, 10, 45), "description": "Atlantic Ocean perspective"},
                {"name": "Indian Ocean View", "rotation": (0, -20, -90), "description": "Indian Ocean and surrounding continents"}
            ]

            # Load REAL world data
            self.continents = self.load_real_world_data()
            print(f"Loaded {len(self.continents)} continents")

            # Create the globe with real data
            self.create_globe()

            # Setup camera
            self.setup_camera()

            # Create GUI controls
            self.create_gui_controls()
            print("Application ready with manual controls")

        def setup_lighting(self):
            # Add ambient light
            ambient = AmbientLight('ambient')
            ambient.setColor((0.4, 0.4, 0.4, 1))
            self.render.setLight(self.render.attachNewNode(ambient))

            # Add directional light
            sun = DirectionalLight('sun')
            sun.setColor((0.8, 0.8, 0.8, 1))
            sun.setDirection((-1, -1, -1))
            self.render.setLight(self.render.attachNewNode(sun))

        def load_real_world_data(self):
            """Load real world data using GeoPandas with SSL bypass"""
            print("Loading REAL world data...")

            # SSL bypass setup
            warnings.filterwarnings('ignore')
            urllib3.disable_warnings()
            ssl._create_default_https_context = ssl._create_unverified_context
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''

            try:
                import geopandas as gpd

                print("Downloading Natural Earth country data...")
                url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

                # Download with requests (bypassing SSL)
                response = requests.get(url, verify=False, timeout=30)
                response.raise_for_status()
                print(f"Downloaded {len(response.content)} bytes")

                # Save to temporary file and load with GeoPandas
                with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False, encoding='utf-8') as f:
                    f.write(response.text)
                    temp_path = f.name

                world = gpd.read_file(temp_path)
                os.unlink(temp_path)
                print(f"Successfully loaded {len(world)} countries!")

                # Process into continents
                continents = self.process_world_to_continents(world)
                return continents

            except Exception as e:
                print(f"Failed to load real data: {e}")
                print("Using fallback continent shapes...")
                return self.get_fallback_continents()

        def process_world_to_continents(self, world_gdf):
            """Process real GeoPandas data into continent groups"""
            import geopandas as gpd

            # Comprehensive country to continent mapping
            country_continent_map = {
                # Europe
                'Germany': 'Europe', 'France': 'Europe', 'United Kingdom': 'Europe', 'Italy': 'Europe',
                'Spain': 'Europe', 'Poland': 'Europe', 'Romania': 'Europe', 'Netherlands': 'Europe',
                'Belgium': 'Europe', 'Greece': 'Europe', 'Portugal': 'Europe', 'Czech Republic': 'Europe',
                'Hungary': 'Europe', 'Sweden': 'Europe', 'Austria': 'Europe', 'Switzerland': 'Europe',
                'Denmark': 'Europe', 'Finland': 'Europe', 'Norway': 'Europe', 'Ireland': 'Europe',
                'Croatia': 'Europe', 'Bulgaria': 'Europe', 'Slovakia': 'Europe', 'Slovenia': 'Europe',
                'Estonia': 'Europe', 'Latvia': 'Europe', 'Lithuania': 'Europe', 'Ukraine': 'Europe',
                'Belarus': 'Europe', 'Serbia': 'Europe', 'Bosnia and Herzegovina': 'Europe',
                'Albania': 'Europe', 'North Macedonia': 'Europe', 'Moldova': 'Europe',

                # Asia
                'China': 'Asia', 'India': 'Asia', 'Russia': 'Asia', 'Indonesia': 'Asia',
                'Pakistan': 'Asia', 'Bangladesh': 'Asia', 'Japan': 'Asia', 'Philippines': 'Asia',
                'Vietnam': 'Asia', 'Turkey': 'Asia', 'Iran': 'Asia', 'Thailand': 'Asia',
                'Myanmar': 'Asia', 'South Korea': 'Asia', 'Iraq': 'Asia', 'Saudi Arabia': 'Asia',
                'Kazakhstan': 'Asia', 'Mongolia': 'Asia', 'Afghanistan': 'Asia', 'Malaysia': 'Asia',
                'Nepal': 'Asia', 'Sri Lanka': 'Asia', 'Cambodia': 'Asia', 'North Korea': 'Asia',
                'Jordan': 'Asia', 'Syria': 'Asia', 'Lebanon': 'Asia', 'Israel': 'Asia',

                # Africa
                'Nigeria': 'Africa', 'Ethiopia': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
                'Kenya': 'Africa', 'Algeria': 'Africa', 'Morocco': 'Africa', 'Angola': 'Africa',
                'Ghana': 'Africa', 'Madagascar': 'Africa', 'Cameroon': 'Africa', 'Niger': 'Africa',
                'Mali': 'Africa', 'Zambia': 'Africa', 'Somalia': 'Africa', 'Chad': 'Africa',
                'Libya': 'Africa', 'Tunisia': 'Africa', 'Sudan': 'Africa', 'Tanzania': 'Africa',
                'Uganda': 'Africa', 'Mozambique': 'Africa', 'Burkina Faso': 'Africa',

                # North America
                'United States of America': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
                'Guatemala': 'North America', 'Cuba': 'North America', 'Haiti': 'North America',
                'Dominican Republic': 'North America', 'Honduras': 'North America', 'Nicaragua': 'North America',
                'Costa Rica': 'North America', 'Panama': 'North America', 'Jamaica': 'North America',

                # South America
                'Brazil': 'South America', 'Argentina': 'South America', 'Chile': 'South America',
                'Peru': 'South America', 'Colombia': 'South America', 'Venezuela': 'South America',
                'Bolivia': 'South America', 'Ecuador': 'South America', 'Uruguay': 'South America',
                'Paraguay': 'South America', 'Guyana': 'South America', 'Suriname': 'South America',

                # Oceania
                'Australia': 'Oceania', 'Papua New Guinea': 'Oceania', 'New Zealand': 'Oceania',
                'Fiji': 'Oceania', 'Solomon Islands': 'Oceania'
            }

            # Add continent column
            continents_list = []
            for idx, row in world_gdf.iterrows():
                country_name = None
                for col in ['NAME', 'name', 'NAME_EN', 'ADMIN', 'NAME_LONG']:
                    if col in row and row[col]:
                        country_name = str(row[col])
                        break

                continent = 'Unknown'
                if country_name:
                    continent = country_continent_map.get(country_name, 'Unknown')
                    if continent == 'Unknown':
                        for mapped_country, mapped_continent in country_continent_map.items():
                            if mapped_country.lower() in country_name.lower():
                                continent = mapped_continent
                                break

                continents_list.append(continent)

            world_gdf = world_gdf.copy()
            world_gdf['continent'] = continents_list

            # Group by continent and union geometries
            continents = {}
            continent_groups = world_gdf.groupby('continent')

            for continent_name, group in continent_groups:
                if continent_name != 'Unknown' and len(group) > 0:
                    try:
                        combined = group.geometry.unary_union
                        continents[continent_name] = combined
                        print(f"Processed {continent_name}: {len(group)} countries")
                    except Exception as e:
                        print(f"Error processing {continent_name}: {e}")

            return continents

        def get_fallback_continents(self):
            """High-quality fallback continent shapes"""
            from shapely.geometry import Polygon
            return {
                'Europe': Polygon([
                    (-9.5, 43.0), (-2.0, 51.0), (5.0, 53.0), (15.0, 59.0), (25.0, 65.0),
                    (35.0, 70.0), (40.0, 55.0), (35.0, 50.0), (30.0, 48.0), (28.0, 42.0),
                    (25.0, 35.0), (15.0, 40.0), (5.0, 43.5), (-2.0, 43.0), (-9.5, 43.0)
                ]),
                'Africa': Polygon([
                    (-17.0, 35.5), (10.0, 37.0), (35.0, 31.0), (40.0, -10.0), (25.0, -30.0),
                    (0.0, -30.0), (-15.0, -10.0), (-17.0, 28.0), (-17.0, 35.5)
                ]),
                'North America': Polygon([
                    (-168.0, 65.5), (-120.0, 72.0), (-85.0, 68.0), (-70.0, 55.0), (-80.0, 30.0),
                    (-95.0, 26.0), (-115.0, 32.5), (-125.0, 46.0), (-140.0, 60.0), (-168.0, 65.5)
                ]),
                'South America': Polygon([
                    (-70.0, 12.0), (-55.0, -15.0), (-70.0, -50.0), (-60.0, -54.0), (-50.0, -40.0),
                    (-40.0, -20.0), (-35.0, 5.0), (-50.0, 10.0), (-70.0, 12.0)
                ]),
                'Asia': Polygon([
                    (26.0, 70.0), (60.0, 80.0), (120.0, 75.0), (150.0, 65.0), (175.0, 50.0),
                    (160.0, 20.0), (120.0, 15.0), (80.0, 20.0), (60.0, 30.0), (40.0, 45.0),
                    (26.0, 60.0), (26.0, 70.0)
                ]),
                'Oceania': Polygon([
                    (113.0, -22.0), (145.0, -18.0), (153.0, -25.0), (145.0, -35.0), (130.0, -38.0),
                    (115.0, -35.0), (110.0, -28.0), (113.0, -22.0)
                ])
            }

        def create_globe(self):
            self.globe = self.render.attachNewNode("globe")

            # Create transparent ocean sphere
            ocean = self.create_sphere(1.0, (0.2, 0.4, 0.8, 0.4))
            ocean.reparentTo(self.globe)
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
            for name, geometry in self.continents.items():
                color = colors.get(name, (0.7, 0.7, 0.7, 1))
                self.add_continent_geometry(geometry, color, name)
                continent_count += 1
                print(f"Added continent: {name}")

            self.globe.setScale(3, 3, 3)
            print(f"Globe created with {continent_count} continents")

        def create_sphere(self, radius, color):
            # Create proper 3D sphere
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

        def add_continent_geometry(self, geometry, color, name):
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
                continent_np = self.globe.attachNewNode(continent_node)
                continent_np.setColor(*color)
                continent_np.setTwoSided(True)

        def setup_camera(self):
            # Default position - more zoomed out
            self.default_camera_pos = (0, -25, 8)  # Further back and higher
            self.camera.setPos(*self.default_camera_pos)
            self.camera.lookAt(0, 0, 0)

        def create_gui_controls(self):
            """Create GUI buttons for manual control"""

            # Title
            OnscreenText(text="Real Globe Manual Controls", pos=(0, 0.9), scale=0.07,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5))

            # Zoom buttons
            DirectButton(text="Zoom In", pos=(-0.3, 0, 0.8), scale=0.05,
                        command=self.zoom_in, text_scale=1.2)
            DirectButton(text="Zoom Out", pos=(0.3, 0, 0.8), scale=0.05,
                        command=self.zoom_out, text_scale=1.2)

            # Reset View button
            DirectButton(text="Reset View", pos=(0, 0, 0.8), scale=0.05,
                        command=self.reset_view, text_scale=1.0)

            # Random View button
            DirectButton(text="Random View", pos=(0.5, 0, 0.8), scale=0.05,
                        command=self.random_view, text_scale=1.0)

            # Rotation buttons in cross pattern
            DirectButton(text="Up", pos=(0, 0, 0.6), scale=0.05,
                        command=self.rotate_up, text_scale=1.0)
            DirectButton(text="Down", pos=(0, 0, 0.4), scale=0.05,
                        command=self.rotate_down, text_scale=1.0)
            DirectButton(text="Left", pos=(-0.15, 0, 0.5), scale=0.05,
                        command=self.rotate_left, text_scale=1.0)
            DirectButton(text="Right", pos=(0.15, 0, 0.5), scale=0.05,
                        command=self.rotate_right, text_scale=1.0)

            # Preset view buttons
            DirectButton(text="Europe", pos=(-0.6, 0, 0.3), scale=0.04,
                        command=lambda: self.set_preset_view(0), text_scale=1.0)
            DirectButton(text="Americas", pos=(-0.6, 0, 0.2), scale=0.04,
                        command=lambda: self.set_preset_view(1), text_scale=1.0)
            DirectButton(text="Asia", pos=(-0.6, 0, 0.1), scale=0.04,
                        command=lambda: self.set_preset_view(2), text_scale=1.0)

            DirectButton(text="Africa", pos=(0.6, 0, 0.3), scale=0.04,
                        command=lambda: self.set_preset_view(3), text_scale=1.0)
            DirectButton(text="Atlantic", pos=(0.6, 0, 0.2), scale=0.04,
                        command=lambda: self.set_preset_view(4), text_scale=1.0)
            DirectButton(text="Pacific", pos=(0.6, 0, 0.1), scale=0.04,
                        command=lambda: self.set_preset_view(5), text_scale=1.0)

            OnscreenText(text="Real world data • Manual controls only",
                        pos=(0, -0.9), scale=0.05, fg=(0.8, 0.8, 0.8, 1))

        # Control functions
        def zoom_in(self):
            pos = self.camera.getPos()
            new_pos = pos * 0.9
            self.camera.setPos(new_pos)

        def zoom_out(self):
            pos = self.camera.getPos()
            new_pos = pos * 1.1
            self.camera.setPos(new_pos)

        def reset_view(self):
            """Reset camera position and globe rotation to default"""
            # Reset camera to default position
            self.camera.setPos(*self.default_camera_pos)
            self.camera.lookAt(0, 0, 0)

            # Reset globe rotation to default (no rotation)
            self.globe_rotation_x = 0
            self.globe_rotation_y = 0
            self.globe_rotation_z = 0
            self.globe.setHpr(0, 0, 0)

            print("View reset to default position and rotation")

        def random_view(self):
            """Set the globe to a random interesting angle"""
            chosen_view = random.choice(self.preset_views)
            self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y = chosen_view["rotation"]
            self.globe.setHpr(self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y)
            print(f"Random view: {chosen_view['name']} - {chosen_view['description']}")

        def set_preset_view(self, index):
            """Set the globe to a specific preset view"""
            if 0 <= index < len(self.preset_views):
                chosen_view = self.preset_views[index]
                self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y = chosen_view["rotation"]
                self.globe.setHpr(self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y)
                print(f"Set view: {chosen_view['name']} - {chosen_view['description']}")

        def rotate_up(self):
            self.globe_rotation_x += 15
            self.globe.setHpr(self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y)

        def rotate_down(self):
            self.globe_rotation_x -= 15
            self.globe.setHpr(self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y)

        def rotate_left(self):
            self.globe_rotation_z -= 15
            self.globe.setHpr(self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y)

        def rotate_right(self):
            self.globe_rotation_z += 15
            self.globe.setHpr(self.globe_rotation_z, self.globe_rotation_x, self.globe_rotation_y)

    print("Creating Real Globe application...")
    app = RealGlobe()
    print("Starting application with real world data and manual controls...")
    app.run()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
