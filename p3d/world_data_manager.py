"""
Robust World Data Manager - Downloads and caches real world maps permanently
"""
import os
import pickle
import geopandas as gpd
from pathlib import Path
import requests
import tempfile
import ssl
import urllib3

class WorldDataManager:
    def __init__(self):
        self.data_dir = Path(__file__).parent / "world_data"
        self.data_dir.mkdir(exist_ok=True)
        self.cache_file = self.data_dir / "world_continents.pkl"
        self.raw_file = self.data_dir / "countries.geojson"

    def get_continents(self):
        """Get continent data - from cache, download, or create"""
        print("🌍 WorldDataManager: Getting continent data...")

        # Try cache first
        if self.cache_file.exists():
            try:
                print("📁 Loading from cache...")
                with open(self.cache_file, 'rb') as f:
                    continents = pickle.load(f)
                print(f"✅ Loaded {len(continents)} continents from cache")
                return continents
            except Exception as e:
                print(f"❌ Cache corrupted: {e}")

        # Try to load from saved raw file
        if self.raw_file.exists():
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
        """Download world boundary data from reliable sources"""
        # Disable SSL warnings
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        sources = [
            {
                'name': 'Natural Earth Countries',
                'url': 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson',
                'method': 'direct'
            },
            {
                'name': 'RestCountries',
                'url': 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json',
                'method': 'direct'
            },
            {
                'name': 'World Atlas',
                'url': 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json',
                'method': 'requests'
            }
        ]

        for source in sources:
            try:
                print(f"📡 Trying {source['name']}...")

                if source['method'] == 'direct':
                    # Direct GeoPandas download
                    world = gpd.read_file(source['url'])
                    print(f"✅ Success! Downloaded {len(world)} features")
                    return world

                elif source['method'] == 'requests':
                    # Manual download with requests
                    response = requests.get(source['url'], verify=False, timeout=30)
                    response.raise_for_status()

                    # Save to temp file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False, encoding='utf-8') as f:
                        f.write(response.text)
                        temp_path = f.name

                    world = gpd.read_file(temp_path)
                    os.unlink(temp_path)
                    print(f"✅ Success! Downloaded {len(world)} features")
                    return world

            except Exception as e:
                print(f"❌ {source['name']} failed: {e}")
                continue

        print("❌ All download sources failed")
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
                (-168, 65), (-140, 69), (-120, 72), (-100, 70), (-85, 68), (-80, 60),
                (-75, 50), (-70, 45), (-68, 40), (-70, 35), (-75, 30), (-80, 25),
                (-85, 20), (-95, 26), (-105, 29), (-115, 32), (-125, 37), (-135, 50),
                (-145, 60), (-160, 65), (-168, 65)
            ],
            'South America': [
                (-35, 5), (-45, -5), (-55, -15), (-65, -25), (-70, -35), (-75, -45),
                (-70, -52), (-60, -54), (-50, -50), (-40, -40), (-35, -30), (-33, -15),
                (-34, -5), (-35, 5)
            ],
            'Europe': [
                (-10, 35), (0, 45), (10, 50), (20, 55), (30, 60), (40, 65), (45, 70),
                (40, 72), (30, 70), (20, 68), (10, 65), (0, 60), (-10, 55), (-10, 35)
            ],
            'Africa': [
                (-17, 35), (10, 35), (35, 30), (45, 0), (40, -10), (35, -25), (25, -35),
                (15, -34), (0, -30), (-10, -20), (-15, 0), (-17, 15), (-17, 35)
            ],
            'Asia': [
                (25, 75), (60, 80), (120, 75), (150, 65), (175, 55), (180, 45), (175, 35),
                (160, 25), (140, 15), (120, 10), (100, 15), (80, 20), (60, 30), (40, 40),
                (30, 50), (25, 65), (25, 75)
            ],
            'Oceania': [
                (113, -22), (130, -14), (145, -18), (153, -21), (152, -26), (145, -35),
                (130, -38), (115, -35), (110, -28), (113, -22)
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
