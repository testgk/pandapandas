u"""
Test real data loading separately to debug the issue
"""
print("Testing GeoPandas real data loading...")

# SSL bypass setup
import ssl
import urllib3
import os
import warnings

warnings.filterwarnings('ignore')
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

try:
    import geopandas as gpd
    print("GeoPandas imported successfully")

    # Try to load real world data
    print("Attempting to download Natural Earth country data...")
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"

    world = gpd.read_file(url)
    print(f"SUCCESS! Loaded {len(world)} countries")
    print(f"Columns: {list(world.columns)}")
    print(f"Sample countries: {world['NAME'].head().tolist()}")

    # Test continent processing
    print("\nProcessing continents...")
    continents = {}

    # Simple continent assignment for testing
    for idx, row in world.iterrows():
        country_name = row.get('NAME', 'Unknown')

        # Simple continent assignment
        continent = 'Unknown'
        if any(x in country_name for x in ['Germany', 'France', 'Spain', 'Italy', 'United Kingdom']):
            continent = 'Europe'
        elif any(x in country_name for x in ['United States', 'Canada', 'Mexico']):
            continent = 'North America'
        elif any(x in country_name for x in ['Brazil', 'Argentina', 'Chile']):
            continent = 'South America'
        elif any(x in country_name for x in ['China', 'India', 'Japan', 'Russia']):
            continent = 'Asia'
        elif any(x in country_name for x in ['Nigeria', 'Egypt', 'South Africa']):
            continent = 'Africa'
        elif any(x in country_name for x in ['Australia', 'New Zealand']):
            continent = 'Oceania'

        if continent not in continents:
            continents[continent] = []
        continents[continent].append(country_name)

    print(f"Continent assignment results:")
    for cont, countries in continents.items():
        print(f"  {cont}: {len(countries)} countries")
        if len(countries) <= 5:
            print(f"    -> {countries}")

    print(f"\nSUCCESS: Real data loading works!")

except Exception as e:
    print(f"ERROR loading real data: {e}")
    import traceback
    traceback.print_exc()
