"""
Robust World Data Manager - Downloads and caches real world maps permanently
"""
import os
import sys
import pickle
import geopandas as gpd
from pathlib import Path
import requests
import tempfile

# GLOBAL SSL CERTIFICATE BYPASS - NO VERIFICATION
import ssl
import urllib3

# Disable ALL SSL warnings and verification
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables to bypass certificates globally
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

class WorldDataManager:
    def __init__(self):
        # Support both normal Python and PyInstaller bundle
        if getattr(sys, 'frozen', False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent
        self.__dataDir = base / "world_data"
        self.__dataDir.mkdir(exist_ok=True)
        self.__cacheFile = self.__dataDir / "world_continents.pkl"
        self.__rawFile = self.__dataDir / "countries.geojson"

    def getContinents(self):
        """Get continent data - from cache, download, or create"""
        print("🌍 WorldDataManager: Getting continent data...")

        # Try cache first
        if self.__cacheFile.exists():
            try:
                print("📁 Loading from cache...")
                with open(self.__cacheFile, 'rb') as f:
                    continents = pickle.load(f)
                print(f"✅ Loaded {len(continents)} continents from cache")
                return continents
            except Exception as e:
                print(f"❌ Cache corrupted: {e}")

        # Try to load from saved raw file
        if self.__rawFile.exists():
            try:
                print("📄 Loading from saved file...")
                world = gpd.read_file(self.raw_file)
                continents = self._process_world_data(world)
                self._save_cache(continents)
                return continents
            except Exception as e:
                print(f"❌ Saved file corrupted: {e}")

        # Download new data
        print("🌐 Downloading world data...")
        world = self._download_world_data()

        # Process the data
        continents = {}
        if world is not None:
            continents = self._process_world_data(world)

        # If we're missing major continents due to geometry issues, add them from fallback
        expected_continents = ['North America', 'South America', 'Europe', 'Africa', 'Asia', 'Oceania']
        missing_continents = [name for name in expected_continents if name not in continents]

        if missing_continents:
            print(f"⚠️ Adding fallback shapes for: {missing_continents}")
            fallback_continents = self._create_fallback_continents()
            for missing in missing_continents:
                if missing in fallback_continents:
                    continents[missing] = fallback_continents[missing]
                    print(f"✅ Added fallback {missing}")

        # If we still have no continents, use all fallback
        if not continents:
            print("⚠️ Using complete fallback continent shapes...")
            continents = self._create_fallback_continents()

        self._save_cache(continents)
        if world is not None:
            self._save_raw_data(world)
        return continents

    def _download_world_data(self):
        """Download world boundary data from reliable sources (SSL verification disabled)"""
        print("🌐 Downloading world data (SSL verification OFF)...")

        sources = [
            {
                'name': 'Natural Earth Countries',
                'url': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
            },
            {
                'name': 'RestCountries',
                'url': 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'
            },
            {
                'name': 'World Atlas',
                'url': 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'
            }
        ]

        for source in sources:
            try:
                print(f"📡 Trying {source['name']}...")

                # Try direct GeoPandas first (fastest)
                try:
                    world = gpd.read_file(source['url'])
                    print(f"✅ SUCCESS! Downloaded {len(world)} features via GeoPandas")
                    return world
                except Exception as geopandas_error:
                    print(f"   GeoPandas failed: {geopandas_error}")

                    # Fallback to manual requests download
                    print(f"   Trying manual download...")
                    response = requests.get(source['url'], verify=False, timeout=30)
                    response.raise_for_status()

                    # Save to temp file and load with GeoPandas
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False, encoding='utf-8') as f:
                        f.write(response.text)
                        temp_path = f.name

                    world = gpd.read_file(temp_path)
                    os.unlink(temp_path)
                    print(f"✅ SUCCESS! Downloaded {len(world)} features via requests")
                    return world

            except Exception as e:
                print(f"❌ {source['name']} failed completely: {e}")
                continue

        print("❌ All download sources failed - using fallback shapes")
        return None

    def _process_world_data(self, world):
        """Process world data into continent groups"""
        print("🔧 Processing world data...")

        # Add continent classification if not present
        if 'continent' not in world.columns:
            world = self._add_continent_classification(world)

        # Group by continent and combine geometries
        continents = {}
        continent_groups = world.groupby('continent')

        for continent_name, group in continent_groups:
            if continent_name != 'Unknown' and len(group) > 0:
                try:
                    # Clean and validate geometries first
                    valid_geometries = []
                    for idx, row in group.iterrows():
                        geom = row.geometry
                        if geom is not None and not geom.is_empty:
                            # Try to fix invalid geometries
                            if not geom.is_valid:
                                try:
                                    geom = geom.buffer(0)  # Common fix for invalid geometries
                                except:
                                    continue

                            # Only add if still valid
                            if geom.is_valid:
                                valid_geometries.append(geom)

                    if valid_geometries:
                        # Create GeoSeries and combine
                        geo_series = gpd.GeoSeries(valid_geometries)
                        try:
                            combined = geo_series.union_all() if hasattr(geo_series, 'union_all') else geo_series.unary_union

                            # Validate the combined result
                            if combined is not None and not combined.is_empty:
                                continents[continent_name] = combined
                                print(f"✅ Processed {continent_name}: {len(group)} countries ({len(valid_geometries)} valid)")
                            else:
                                print(f"❌ {continent_name}: Combined geometry is empty")
                        except Exception as union_error:
                            print(f"❌ {continent_name}: Union failed - {union_error}")
                    else:
                        print(f"❌ {continent_name}: No valid geometries found")

                except Exception as e:
                    print(f"❌ Failed to process {continent_name}: {e}")

        return continents

    def _add_continent_classification(self, world):
        """Add continent column to world data"""
        print("🗺️ Classifying countries by continent...")

        # Comprehensive country-to-continent mapping
        country_mapping = {
            # North America
            'United States of America': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
            'United States': 'North America', 'USA': 'North America', 'US': 'North America',
            'Guatemala': 'North America', 'Belize': 'North America', 'Honduras': 'North America',
            'El Salvador': 'North America', 'Nicaragua': 'North America', 'Costa Rica': 'North America',
            'Panama': 'North America', 'Cuba': 'North America', 'Jamaica': 'North America',
            'Haiti': 'North America', 'Dominican Republic': 'North America', 'Bahamas': 'North America',

            # South America
            'Brazil': 'South America', 'Argentina': 'South America', 'Chile': 'South America',
            'Peru': 'South America', 'Colombia': 'South America', 'Venezuela': 'South America',
            'Bolivia': 'South America', 'Ecuador': 'South America', 'Uruguay': 'South America',
            'Paraguay': 'South America', 'Guyana': 'South America', 'Suriname': 'South America',
            'French Guiana': 'South America',

            # Europe
            'Germany': 'Europe', 'France': 'Europe', 'United Kingdom': 'Europe', 'Italy': 'Europe',
            'Spain': 'Europe', 'Poland': 'Europe', 'Romania': 'Europe', 'Netherlands': 'Europe',
            'Belgium': 'Europe', 'Greece': 'Europe', 'Portugal': 'Europe', 'Czech Republic': 'Europe',
            'Hungary': 'Europe', 'Sweden': 'Europe', 'Belarus': 'Europe', 'Austria': 'Europe',
            'Serbia': 'Europe', 'Switzerland': 'Europe', 'Bulgaria': 'Europe', 'Slovakia': 'Europe',
            'Denmark': 'Europe', 'Finland': 'Europe', 'Norway': 'Europe', 'Ireland': 'Europe',
            'Bosnia and Herzegovina': 'Europe', 'Croatia': 'Europe', 'Albania': 'Europe',
            'Lithuania': 'Europe', 'Slovenia': 'Europe', 'Latvia': 'Europe', 'Estonia': 'Europe',
            'North Macedonia': 'Europe', 'Moldova': 'Europe', 'Luxembourg': 'Europe', 'Malta': 'Europe',
            'Iceland': 'Europe', 'Montenegro': 'Europe', 'Cyprus': 'Europe', 'Ukraine': 'Europe',

            # Asia
            'China': 'Asia', 'India': 'Asia', 'Russia': 'Asia', 'Russian Federation': 'Asia',
            'Indonesia': 'Asia', 'Pakistan': 'Asia', 'Bangladesh': 'Asia', 'Japan': 'Asia',
            'Philippines': 'Asia', 'Vietnam': 'Asia', 'Turkey': 'Asia', 'Iran': 'Asia',
            'Thailand': 'Asia', 'Myanmar': 'Asia', 'South Korea': 'Asia', 'Iraq': 'Asia',
            'Afghanistan': 'Asia', 'Saudi Arabia': 'Asia', 'Uzbekistan': 'Asia', 'Malaysia': 'Asia',
            'Nepal': 'Asia', 'Yemen': 'Asia', 'North Korea': 'Asia', 'Sri Lanka': 'Asia',
            'Kazakhstan': 'Asia', 'Syria': 'Asia', 'Cambodia': 'Asia', 'Jordan': 'Asia',
            'Azerbaijan': 'Asia', 'United Arab Emirates': 'Asia', 'Tajikistan': 'Asia',
            'Israel': 'Asia', 'Laos': 'Asia', 'Singapore': 'Asia', 'Oman': 'Asia',
            'Kuwait': 'Asia', 'Georgia': 'Asia', 'Mongolia': 'Asia', 'Armenia': 'Asia',
            'Qatar': 'Asia', 'Bahrain': 'Asia', 'East Timor': 'Asia', 'Maldives': 'Asia',
            'Brunei': 'Asia', 'Kyrgyzstan': 'Asia', 'Turkmenistan': 'Asia',

            # Africa
            'Nigeria': 'Africa', 'Ethiopia': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
            'Kenya': 'Africa', 'Uganda': 'Africa', 'Algeria': 'Africa', 'Sudan': 'Africa',
            'Morocco': 'Africa', 'Angola': 'Africa', 'Ghana': 'Africa', 'Mozambique': 'Africa',
            'Madagascar': 'Africa', 'Cameroon': 'Africa', 'Ivory Coast': 'Africa', 'Niger': 'Africa',
            'Burkina Faso': 'Africa', 'Mali': 'Africa', 'Malawi': 'Africa', 'Zambia': 'Africa',
            'Senegal': 'Africa', 'Somalia': 'Africa', 'Chad': 'Africa', 'Zimbabwe': 'Africa',
            'Guinea': 'Africa', 'Rwanda': 'Africa', 'Benin': 'Africa', 'Tunisia': 'Africa',
            'Burundi': 'Africa', 'Togo': 'Africa', 'Sierra Leone': 'Africa', 'Libya': 'Africa',
            'Liberia': 'Africa', 'Central African Republic': 'Africa', 'Mauritania': 'Africa',
            'Eritrea': 'Africa', 'Gambia': 'Africa', 'Botswana': 'Africa', 'Namibia': 'Africa',
            'Gabon': 'Africa', 'Lesotho': 'Africa', 'Guinea-Bissau': 'Africa',
            'Equatorial Guinea': 'Africa', 'Mauritius': 'Africa', 'Eswatini': 'Africa',
            'Djibouti': 'Africa', 'Comoros': 'Africa', 'Cape Verde': 'Africa',
            'São Tomé and Príncipe': 'Africa', 'Seychelles': 'Africa', 'Tanzania': 'Africa',
            'Democratic Republic of the Congo': 'Africa', 'Republic of the Congo': 'Africa',

            # Oceania
            'Australia': 'Oceania', 'Papua New Guinea': 'Oceania', 'New Zealand': 'Oceania',
            'Fiji': 'Oceania', 'Solomon Islands': 'Oceania', 'Vanuatu': 'Oceania',
            'Samoa': 'Oceania', 'Micronesia': 'Oceania', 'Tonga': 'Oceania',
            'Kiribati': 'Oceania', 'Palau': 'Oceania', 'Marshall Islands': 'Oceania',
            'Tuvalu': 'Oceania', 'Nauru': 'Oceania'
        }

        # Add continent column
        continents = []
        for _, row in world.iterrows():
            # Try different column names for country
            country_name = None
            for col in ['NAME', 'name', 'NAME_EN', 'ADMIN', 'NAME_LONG', 'COUNTRY', 'properties.NAME']:
                if col in row and row[col]:
                    country_name = str(row[col])
                    break

            if not country_name:
                continents.append('Unknown')
                continue

            # Direct mapping
            continent = country_mapping.get(country_name, None)

            # Partial matching if direct fails
            if not continent:
                country_lower = country_name.lower()
                for mapped_country, mapped_continent in country_mapping.items():
                    if mapped_country.lower() in country_lower or country_lower in mapped_country.lower():
                        continent = mapped_continent
                        break

            continents.append(continent or 'Unknown')

        world = world.copy()
        world['continent'] = continents
        return world

    def _create_fallback_continents(self):
        """Create high-quality fallback continent shapes"""
        from shapely.geometry import Polygon

        # High-quality continent outlines based on real coordinates
        continent_data = {
            'North America': [
                # More accurate North America with better coastlines
                (-168.0, 65.5), (-140.0, 69.6), (-120.0, 72.0), (-100.0, 70.0), (-85.0, 68.0),
                (-75.0, 62.0), (-70.0, 55.0), (-68.0, 47.0), (-70.0, 42.0), (-72.0, 38.0),
                (-75.0, 35.0), (-80.0, 30.0), (-82.0, 25.5), (-84.0, 24.0), (-87.0, 24.5),
                (-90.0, 25.0), (-95.0, 26.0), (-97.0, 25.5), (-100.0, 26.0), (-105.0, 29.0),
                (-110.0, 31.0), (-115.0, 32.5), (-118.0, 34.0), (-122.0, 37.0), (-124.0, 42.0),
                (-125.0, 46.0), (-128.0, 49.0), (-135.0, 55.0), (-140.0, 60.0), (-145.0, 61.0),
                (-155.0, 59.0), (-162.0, 61.0), (-166.0, 63.0), (-168.0, 65.5)
            ],
            'South America': [
                # More detailed South America
                (-34.8, 5.2), (-42.0, 2.0), (-50.0, -5.0), (-55.0, -15.0), (-60.0, -25.0),
                (-65.0, -35.0), (-70.0, -45.0), (-72.0, -50.0), (-68.0, -54.0), (-63.0, -54.8),
                (-58.0, -54.0), (-50.0, -52.0), (-45.0, -48.0), (-40.0, -42.0), (-37.0, -35.0),
                (-35.0, -28.0), (-34.0, -20.0), (-33.5, -12.0), (-34.0, -5.0), (-34.8, 5.2)
            ],
            'Europe': [
                # Corrected Europe with Mediterranean Sea properly defined
                # Western coastline
                (-9.5, 43.0), (-7.0, 48.0), (-2.0, 51.0), (2.0, 51.5),
                # North Sea and Baltic
                (5.0, 53.0), (8.0, 55.0), (12.0, 56.0), (15.0, 59.0), (20.0, 60.0), (25.0, 65.0),
                (30.0, 68.0), (35.0, 70.0), (45.0, 71.0), (50.0, 68.0), (48.0, 65.0),
                # Eastern Europe
                (45.0, 60.0), (40.0, 55.0), (35.0, 50.0), (30.0, 48.0), (26.0, 45.0),
                # Black Sea region
                (28.0, 42.0), (30.0, 40.0), (35.0, 36.0), (40.0, 38.0), (42.0, 42.0),
                # Mediterranean coastline - Northern shore
                (40.0, 36.0), (35.0, 36.0), (25.0, 35.0), (20.0, 38.0), (15.0, 40.0),
                (10.0, 42.0), (5.0, 43.5), (2.0, 44.0), (-2.0, 43.0), (-5.0, 42.0),
                (-7.0, 41.0), (-9.0, 42.0), (-9.5, 43.0)
            ],
            'Africa': [
                # More accurate Africa with proper Mediterranean coastline
                # Mediterranean coast (North)
                (-17.0, 35.5), (-10.0, 35.8), (-5.0, 36.0), (10.0, 37.0), (25.0, 32.0),
                (30.0, 31.5), (35.0, 31.0), (37.0, 30.0),
                # Red Sea and East coast
                (43.0, 25.0), (47.0, 15.0), (42.0, 0.0), (40.0, -10.0), (35.0, -20.0),
                (30.0, -25.0), (25.0, -30.0), (20.0, -33.0), (15.0, -34.5),
                # Southern tip
                (10.0, -34.0), (5.0, -32.0), (0.0, -30.0), (-5.0, -25.0),
                # West coast
                (-10.0, -20.0), (-15.0, -10.0), (-17.0, 0.0), (-16.0, 10.0),
                (-15.0, 20.0), (-17.0, 28.0), (-17.0, 35.5)
            ],
            'Asia': [
                # More detailed Asia
                (26.0, 72.0), (40.0, 77.0), (60.0, 81.0), (80.0, 79.0), (100.0, 76.0),
                (120.0, 73.0), (140.0, 68.0), (155.0, 65.0), (170.0, 60.0), (180.0, 55.0),
                (179.0, 50.0), (175.0, 45.0), (170.0, 40.0), (165.0, 35.0), (160.0, 30.0),
                (155.0, 25.0), (150.0, 20.0), (145.0, 15.0), (140.0, 10.0), (135.0, 8.0),
                (130.0, 9.0), (125.0, 12.0), (120.0, 15.0), (115.0, 18.0), (110.0, 20.0),
                (105.0, 22.0), (100.0, 23.0), (95.0, 22.0), (90.0, 20.0), (85.0, 18.0),
                (80.0, 16.0), (75.0, 18.0), (70.0, 22.0), (65.0, 26.0), (60.0, 30.0),
                (55.0, 35.0), (50.0, 40.0), (45.0, 45.0), (40.0, 50.0), (35.0, 55.0),
                (30.0, 60.0), (26.0, 65.0), (26.0, 72.0)
            ],
            'Oceania': [
                # More detailed Australia/Oceania
                (112.9, -21.8), (115.0, -26.0), (118.0, -30.0), (122.0, -33.0), (128.0, -35.0),
                (135.0, -36.0), (140.0, -37.0), (145.0, -38.0), (150.0, -35.0), (153.4, -28.2),
                (153.6, -24.0), (152.0, -20.0), (149.0, -16.0), (145.0, -14.0), (140.0, -12.5),
                (135.0, -12.0), (130.0, -13.0), (125.0, -16.0), (120.0, -20.0), (115.0, -22.0),
                (112.9, -21.8)
            ]
        }

        continents = {}
        for name, coords in continent_data.items():
            continents[name] = Polygon(coords)

        return continents

    def _save_cache(self, continents):
        """Save processed continent data to cache"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(continents, f)
            print(f"💾 Cached {len(continents)} continents")
        except Exception as e:
            print(f"❌ Failed to save cache: {e}")

    def _save_raw_data(self, world):
        """Save raw world data for future use"""
        try:
            world.to_file(self.raw_file, driver='GeoJSON')
            print(f"💾 Saved raw data ({len(world)} countries)")
        except Exception as e:
            print(f"❌ Failed to save raw data: {e}")

    def clear_cache(self):
        """Clear all cached data to force re-download"""
        files_to_remove = [self.cache_file, self.raw_file]
        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
                print(f"🗑️ Removed {file_path}")
        print("✅ Cache cleared - next run will re-download data")

# Convenience function
def get_world_continents():
    """Get world continent data - cached or downloaded"""
    manager = WorldDataManager()
    return manager.get_continents()

if __name__ == "__main__":
    # Test the data manager
    print("Testing WorldDataManager...")
    manager = WorldDataManager()
    continents = manager.get_continents()
    print(f"\n🌍 Available continents: {list(continents.keys())}")
    print("✅ WorldDataManager test complete!")
