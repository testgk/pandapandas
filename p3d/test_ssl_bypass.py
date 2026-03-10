"""
Simple SSL Bypass Test - No Certificate Verification
"""
import os
import ssl
import urllib3
import warnings

# DISABLE ALL SSL WARNINGS AND VERIFICATION
warnings.filterwarnings('ignore')
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Environment variables
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

def test_ssl_bypass():
    print("🔓 Testing SSL certificate bypass...")

    try:
        import requests
        response = requests.get('https://httpbin.org/get', verify=False, timeout=10)
        print(f"✅ Basic HTTPS test: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic HTTPS failed: {e}")
        return False

    try:
        import geopandas as gpd
        print("🌍 Testing GeoPandas download with SSL bypass...")
        url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
        world = gpd.read_file(url)
        print(f"✅ GeoPandas download successful: {len(world)} countries")
        return True
    except Exception as e:
        print(f"❌ GeoPandas download failed: {e}")
        return False

def test_fallback_continents():
    print("🗺️ Testing fallback continent shapes...")
    from shapely.geometry import Polygon

    # Use the improved continent shapes directly
    continents = {
        'Europe': Polygon([
            # Europe with Mediterranean coastline
            (-9.5, 43.0), (-2.0, 51.0), (5.0, 53.0), (15.0, 59.0), (25.0, 65.0),
            (35.0, 70.0), (45.0, 71.0), (40.0, 55.0), (35.0, 50.0), (30.0, 48.0),
            (28.0, 42.0), (35.0, 36.0), (25.0, 35.0), (15.0, 40.0), (5.0, 43.5),
            (-2.0, 43.0), (-7.0, 41.0), (-9.5, 43.0)
        ]),
        'Africa': Polygon([
            (-17.0, 35.5), (10.0, 37.0), (35.0, 31.0), (43.0, 25.0), (40.0, -10.0),
            (25.0, -30.0), (15.0, -34.5), (0.0, -30.0), (-15.0, -10.0), (-17.0, 28.0), (-17.0, 35.5)
        ])
    }

    print(f"✅ Created {len(continents)} fallback continents")
    for name, geom in continents.items():
        bounds = geom.bounds
        print(f"   {name}: {bounds[0]:.1f}° to {bounds[2]:.1f}°E, {bounds[1]:.1f}° to {bounds[3]:.1f}°N")

    return continents

if __name__ == "__main__":
    print("🚀 SSL Bypass and Continent Test")
    print("=" * 50)

    # Test SSL bypass
    ssl_works = test_ssl_bypass()

    # Test fallback shapes
    fallback_continents = test_fallback_continents()

    if ssl_works:
        print("\n✅ SSL bypass working - can download real data!")
    else:
        print("\n⚠️ SSL issues remain - using fallback shapes")

    print(f"\n🌍 Ready for 3D globe with {len(fallback_continents)} continents")
    print("Run 'python main_fixed.py' to see the globe!")
