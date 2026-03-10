"""
Fixed Globe Application - No Unicode issues, immediate continent rendering
"""
print("Starting Globe Application...")

try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import *
    from math import sin, cos, pi
    print("Imports successful")

    # Real world data using GeoPandas with SSL bypass
    def get_real_world_data():
        print("Loading real world data with GeoPandas...")

        # SSL bypass setup
        import ssl
        import urllib3
        import os
        import warnings
        import requests
        import tempfile

        warnings.filterwarnings('ignore')
        urllib3.disable_warnings()
        ssl._create_default_https_context = ssl._create_unverified_context
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''

        try:
            import geopandas as gpd

            print("Downloading Natural Earth data with requests...")
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
            os.unlink(temp_path)  # Clean up
            print(f"Successfully loaded {len(world)} countries!")

            # Process into continents
            continents = process_world_to_continents(world)
            return continents

        except Exception as e:
            print(f"Failed to load real data: {e}")
            print("Falling back to simple continent shapes...")
            return get_fallback_continents()

    def process_world_to_continents(world_gdf):
        """Process GeoPandas world data into continent groups"""
        import geopandas as gpd

        # Country to continent mapping (expanded)
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
            'Albania': 'Europe', 'North Macedonia': 'Europe', 'Moldova': 'Europe', 'Montenegro': 'Europe',

            # Asia
            'China': 'Asia', 'India': 'Asia', 'Russia': 'Asia', 'Indonesia': 'Asia',
            'Pakistan': 'Asia', 'Bangladesh': 'Asia', 'Japan': 'Asia', 'Philippines': 'Asia',
            'Vietnam': 'Asia', 'Turkey': 'Asia', 'Iran': 'Asia', 'Thailand': 'Asia',
            'Myanmar': 'Asia', 'South Korea': 'Asia', 'Iraq': 'Asia', 'Saudi Arabia': 'Asia',
            'Kazakhstan': 'Asia', 'Mongolia': 'Asia', 'Afghanistan': 'Asia', 'Uzbekistan': 'Asia',
            'Malaysia': 'Asia', 'Nepal': 'Asia', 'Sri Lanka': 'Asia', 'Cambodia': 'Asia',
            'Laos': 'Asia', 'Singapore': 'Asia', 'North Korea': 'Asia', 'Jordan': 'Asia',
            'Syria': 'Asia', 'Lebanon': 'Asia', 'Israel': 'Asia', 'Yemen': 'Asia', 'Oman': 'Asia',

            # Africa
            'Nigeria': 'Africa', 'Ethiopia': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
            'Kenya': 'Africa', 'Algeria': 'Africa', 'Morocco': 'Africa', 'Angola': 'Africa',
            'Ghana': 'Africa', 'Madagascar': 'Africa', 'Cameroon': 'Africa', 'Niger': 'Africa',
            'Mali': 'Africa', 'Zambia': 'Africa', 'Somalia': 'Africa', 'Chad': 'Africa',
            'Libya': 'Africa', 'Tunisia': 'Africa', 'Sudan': 'Africa', 'Tanzania': 'Africa',
            'Uganda': 'Africa', 'Mozambique': 'Africa', 'Burkina Faso': 'Africa', 'Malawi': 'Africa',
            'Senegal': 'Africa', 'Guinea': 'Africa', 'Rwanda': 'Africa', 'Zimbabwe': 'Africa',
            'Benin': 'Africa', 'Burundi': 'Africa', 'Togo': 'Africa', 'Sierra Leone': 'Africa',
            'Liberia': 'Africa', 'Central African Republic': 'Africa', 'Mauritania': 'Africa',

            # North America
            'United States of America': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
            'Guatemala': 'North America', 'Cuba': 'North America', 'Haiti': 'North America',
            'Dominican Republic': 'North America', 'Honduras': 'North America', 'Nicaragua': 'North America',
            'Costa Rica': 'North America', 'Panama': 'North America', 'Jamaica': 'North America',
            'El Salvador': 'North America', 'Belize': 'North America', 'Bahamas': 'North America',

            # South America
            'Brazil': 'South America', 'Argentina': 'South America', 'Chile': 'South America',
            'Peru': 'South America', 'Colombia': 'South America', 'Venezuela': 'South America',
            'Bolivia': 'South America', 'Ecuador': 'South America', 'Uruguay': 'South America',
            'Paraguay': 'South America', 'Guyana': 'South America', 'Suriname': 'South America',
            'French Guiana': 'South America',

            # Oceania
            'Australia': 'Oceania', 'Papua New Guinea': 'Oceania', 'New Zealand': 'Oceania',
            'Fiji': 'Oceania', 'Solomon Islands': 'Oceania', 'Vanuatu': 'Oceania',
            'Samoa': 'Oceania', 'Tonga': 'Oceania', 'Palau': 'Oceania'
        }

        # Add continent column
        continents_list = []
        for idx, row in world_gdf.iterrows():
            # Try different column names for country name
            country_name = None
            for col in ['NAME', 'name', 'NAME_EN', 'ADMIN', 'NAME_LONG']:
                if col in row and row[col]:
                    country_name = str(row[col])
                    break

            # Map to continent
            continent = 'Unknown'
            if country_name:
                continent = country_continent_map.get(country_name, 'Unknown')
                # Try partial matching
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
                    # Union all country geometries in the continent
                    combined = group.geometry.unary_union
                    continents[continent_name] = combined
                    print(f"Processed {continent_name}: {len(group)} countries")
                except Exception as e:
                    print(f"Error processing {continent_name}: {e}")

        return continents

    def get_fallback_continents():
        """Fallback continent shapes if real data fails"""
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

    class FixedGlobe(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            print("Panda3D initialized")

            # Dark blue background instead of black
            self.setBackgroundColor(0.1, 0.1, 0.3)

            # Add lighting so we can see the geometry
            self.setup_lighting()

            # Load continent data - now using real world data
            self.continents = get_real_world_data()
            print(f"Loaded {len(self.continents)} continents")

            # Create globe
            self.create_globe()

            # Setup camera
            self.setup_camera()
            print("Camera positioned")

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
            print("Lighting setup complete")

        def setup_camera(self):
            # Position camera further back to see the full globe
            self.camera.setPos(0, -15, 5)  # Moved much further back
            self.camera.lookAt(0, 0, 0)

            # Add mouse controls for zooming
            self.accept("wheel_up", self.zoom_in)
            self.accept("wheel_down", self.zoom_out)

            # Add rotation task
            self.taskMgr.add(self.rotate_globe, "rotate")

        def zoom_in(self):
            pos = self.camera.getPos()
            new_pos = pos * 0.9  # Move 10% closer
            self.camera.setPos(new_pos)

        def zoom_out(self):
            pos = self.camera.getPos()
            new_pos = pos * 1.1  # Move 10% further
            self.camera.setPos(new_pos)

        def rotate_globe(self, task):
            # Slowly rotate the globe
            angle = task.time * 20  # degrees per second
            self.globe.setHpr(angle, 0, 0)
            return task.cont

        def create_globe(self):
            self.globe = self.render.attachNewNode("globe")
            print("Globe node created")

            # Create ocean sphere (semi-transparent blue)
            try:
                ocean = self.create_sphere(1.0, (0.2, 0.4, 0.8, 0.5))
                ocean.reparentTo(self.globe)
                ocean.setTransparency(TransparencyAttrib.MAlpha)
                print("Ocean sphere created and attached")
            except Exception as e:
                print(f"Error creating ocean sphere: {e}")

            # Add continents with colors for all real continents
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
                try:
                    color = colors.get(name, (0.7, 0.7, 0.7, 1))
                    self.add_continent_geometry(geometry, color, name)
                    continent_count += 1
                    print(f"Successfully added continent: {name}")
                except Exception as e:
                    print(f"Error adding continent {name}: {e}")

            self.globe.setScale(2, 2, 2)  # Reduced from 3x to 2x
            print(f"Globe created with {continent_count} continents, scaled to 2x")

            # Print globe hierarchy for debugging
            print("Globe hierarchy:")
            print(f"  Globe children: {self.globe.getNumChildren()}")
            for i in range(self.globe.getNumChildren()):
                child = self.globe.getChild(i)
                print(f"    Child {i}: {child.getName()}")

        def create_sphere(self, radius, color):
            # Create a proper 3D sphere using GeomNode
            format = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData("sphere", format, Geom.UHStatic)
            vertex = GeomVertexWriter(vdata, "vertex")
            normal = GeomVertexWriter(vdata, "normal")

            segments = 32
            rings = 16

            # Generate sphere vertices
            for r in range(rings + 1):
                lat = (r / rings - 0.5) * pi  # -π/2 to π/2
                y = sin(lat) * radius
                ring_r = cos(lat) * radius

                for s in range(segments + 1):
                    lon = (s / segments) * 2 * pi  # 0 to 2π
                    x = ring_r * sin(lon)
                    z = ring_r * cos(lon)

                    vertex.addData3f(x, y, z)
                    normal.addData3f(x/radius, y/radius, z/radius)

            # Generate triangles
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

            # Handle both Polygon and MultiPolygon from real world data
            polygons = []
            if isinstance(geometry, MultiPolygon):
                polygons = list(geometry.geoms)
                print(f"Processing MultiPolygon {name} with {len(polygons)} parts")
            elif isinstance(geometry, Polygon):
                polygons = [geometry]
                print(f"Processing Polygon {name}")
            else:
                print(f"Skipping {name} - unsupported geometry type: {type(geometry)}")
                return

            # Add each polygon part
            for i, polygon in enumerate(polygons):
                if not polygon.is_valid or polygon.is_empty:
                    continue

                coords = list(polygon.exterior.coords)[:-1]  # Remove duplicate last point
                if len(coords) < 3:
                    continue

                print(f"Creating {name} part {i+1} with {len(coords)} points")

                # Create vertices for the continent part
                vertices_3d = []
                radius = 1.05

                for lon, lat in coords:
                    lat_rad = lat * pi / 180.0
                    lon_rad = lon * pi / 180.0
                    x = cos(lat_rad) * sin(lon_rad) * radius
                    y = sin(lat_rad) * radius
                    z = cos(lat_rad) * cos(lon_rad) * radius
                    vertices_3d.append((x, y, z))

                # Create geometry using Panda3D with normals
                part_name = f"{name}_part_{i}" if len(polygons) > 1 else name
                format = GeomVertexFormat.getV3n3()
                vdata = GeomVertexData(part_name, format, Geom.UHStatic)
                vdata.setNumRows(len(vertices_3d))
                vertex = GeomVertexWriter(vdata, "vertex")
                normal = GeomVertexWriter(vdata, "normal")

                for x, y, z in vertices_3d:
                    vertex.addData3f(x, y, z)
                    # Normal points outward from sphere center
                    length = (x*x + y*y + z*z) ** 0.5
                    normal.addData3f(x/length, y/length, z/length)

                # Create triangles (fan triangulation from first vertex)
                geom = Geom(vdata)
                tris = GeomTriangles(Geom.UHStatic)

                for j in range(1, len(vertices_3d) - 1):
                    tris.addVertices(0, j, j + 1)
                    tris.closePrimitive()

                geom.addPrimitive(tris)

                # Create and attach the node
                continent_node = GeomNode(f"continent_{part_name}")
                continent_node.addGeom(geom)
                continent_np = self.globe.attachNewNode(continent_node)
                continent_np.setColor(*color)
                continent_np.setTwoSided(True)  # Make visible from both sides

            print(f"Continent {name} geometry created successfully")

    print("Creating globe application...")
    app = FixedGlobe()
    print("Starting main loop...")
    print("Look for a window with:")
    print("- Colored continents on a blue sphere")
    print("- GUI buttons for manual zoom and rotation control")
    print("- No automatic rotation - fully manual control!")
    app.run()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
