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
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables to bypass certificates globally
os.environ[ 'PYTHONHTTPSVERIFY' ] = '0'
os.environ[ 'CURL_CA_BUNDLE' ] = ''
os.environ[ 'REQUESTS_CA_BUNDLE' ] = ''


class WorldDataManager:
    def __init__( self ):
        # Support both normal Python and PyInstaller bundle
        if getattr( sys, 'frozen', False ):
            base = Path( sys._MEIPASS )
        else:
            base = Path( __file__ ).parent
        self.__dataDir = base / "world_data"
        self.__dataDir.mkdir( exist_ok = True )
        self.__cacheFile = self.__dataDir / "world_continents.pkl"
        self.__rawFile = self.__dataDir / "countries.geojson"

    def getContinents( self ):
        """Get continent data - from cache or download"""
        print( "🌍 WorldDataManager: Getting continent data..." )

        # Try cache first
        if self.__cacheFile.exists():
            try:
                print( "📁 Loading from cache..." )
                with open( self.__cacheFile, 'rb' ) as f:
                    continents = pickle.load( f )
                print( f"✅ Loaded {len( continents )} continents from cache" )
                return continents
            except Exception as e:
                print( f"❌ Cache corrupted: {e}" )

        # Try to load from saved raw file
        if self.__rawFile.exists():
            try:
                print( "📄 Loading from saved file..." )
                world = gpd.read_file( self.__rawFile )
                continents = self._process_world_data( world )
                self._save_cache( continents )
                return continents
            except Exception as e:
                print( f"❌ Saved file corrupted: {e}" )

        # Download new data
        print( "🌐 Downloading world data..." )
        world = self._download_world_data()

        if world is None:
            print( "❌ Failed to obtain world data" )
            return {}

        continents = self._process_world_data( world )
        self._save_cache( continents )
        self._save_raw_data( world )
        return continents

    def _download_world_data( self ):
        """Download world boundary data from reliable sources (SSL verification disabled)"""
        print( "🌐 Downloading world data (SSL verification OFF)..." )

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
                print( f"📡 Trying {source['name']}..." )

                try:
                    world = gpd.read_file( source[ 'url' ] )
                    print( f"✅ SUCCESS! Downloaded {len( world )} features via GeoPandas" )
                    return world
                except Exception as geopandas_error:
                    print( f"   GeoPandas failed: {geopandas_error}" )
                    print( f"   Trying manual download..." )
                    response = requests.get( source[ 'url' ], verify = False, timeout = 30 )
                    response.raise_for_status()

                    with tempfile.NamedTemporaryFile( mode = 'w', suffix = '.geojson', delete = False, encoding = 'utf-8' ) as f:
                        f.write( response.text )
                        temp_path = f.name

                    world = gpd.read_file( temp_path )
                    os.unlink( temp_path )
                    print( f"✅ SUCCESS! Downloaded {len( world )} features via requests" )
                    return world

            except Exception as e:
                print( f"❌ {source['name']} failed completely: {e}" )
                continue

        print( "❌ All download sources failed" )
        return None

    def _process_world_data( self, world ):
        """Process world data into continent groups"""
        print( "🔧 Processing world data..." )

        if 'continent' not in world.columns:
            world = self._add_continent_classification( world )

        continents = {}
        continent_groups = world.groupby( 'continent' )

        for continent_name, group in continent_groups:
            if continent_name == 'Unknown' or len( group ) == 0:
                continue
            try:
                valid_geometries = []
                for idx, row in group.iterrows():
                    geom = row.geometry
                    if geom is None or geom.is_empty:
                        continue
                    if not geom.is_valid:
                        try:
                            geom = geom.buffer( 0 )
                        except Exception:
                            continue
                    if geom.is_valid:
                        valid_geometries.append( geom )

                if not valid_geometries:
                    print( f"❌ {continent_name}: No valid geometries found" )
                    continue

                geo_series = gpd.GeoSeries( valid_geometries )
                combined = geo_series.union_all() if hasattr( geo_series, 'union_all' ) else geo_series.unary_union

                if combined is not None and not combined.is_empty:
                    continents[ continent_name ] = combined
                    print( f"✅ Processed {continent_name}: {len( group )} countries ({len( valid_geometries )} valid)" )
                else:
                    print( f"❌ {continent_name}: Combined geometry is empty" )

            except Exception as e:
                print( f"❌ Failed to process {continent_name}: {e}" )

        return continents

    def _add_continent_classification( self, world ):
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

    def _save_cache( self, continents ):
        """Save processed continent data to cache"""
        try:
            with open( self.__cacheFile, 'wb' ) as f:
                pickle.dump( continents, f )
            print( f"💾 Cached {len( continents )} continents" )
        except Exception as e:
            print( f"❌ Failed to save cache: {e}" )

    def _save_raw_data( self, world ):
        """Save raw world data for future use"""
        try:
            world.to_file( self.__rawFile, driver = 'GeoJSON' )
            print( f"💾 Saved raw data ({len( world )} countries)" )
        except Exception as e:
            print( f"❌ Failed to save raw data: {e}" )

    def clear_cache( self ):
        """Clear all cached data to force re-download"""
        for filePath in [ self.__cacheFile, self.__rawFile ]:
            if filePath.exists():
                filePath.unlink()
                print( f"🗑️ Removed {filePath}" )
        print( "✅ Cache cleared - next run will re-download data" )

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
