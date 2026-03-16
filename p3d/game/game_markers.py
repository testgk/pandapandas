"""
Game Markers — Panda3D geometry helpers for placing visual feedback on the globe.
Creates disk, X-mark, scoring-ring and city-label nodes aligned to the globe surface.
Scoring zone configuration is fetched from the backend API (single source of truth).
"""
from math import cos, sin, pi
from typing import List, Tuple, Optional, Dict
import requests

from panda3d.core import (
    Geom, GeomNode, GeomTriangles, GeomVertexData,
    GeomVertexFormat, GeomVertexWriter, LineSegs,
    NodePath, TransparencyAttrib,
    TextNode, CardMaker
)

DISK_SEGMENTS = 48

# Visual styling for zones (rendering-engine specific, not boundaries)
ZONE_COLORS: Dict[str, Tuple[float, float, float, float]] = {
    "green": ( 0.1, 0.85, 0.15, 0.80 ),
    "yellow": ( 1.0, 0.90, 0.0, 0.70 ),
    "orange": ( 1.0, 0.55, 0.0, 0.60 ),
    "red": ( 1.0, 0.15, 0.0, 0.55 ),
}

# Depth offsets for z-ordering (higher = renders on top)
ZONE_DEPTH_OFFSETS: Dict[str, int] = {
    "green": 4,
    "yellow": 3,
    "orange": 2,
    "red": 1,
}

# Multiplier applied on top of the km→local conversion to make rings visually larger
RING_SCALE_MULTIPLIER = 4.5

# Earth radius in km — used to convert km distances to globe local-space units
EARTH_RADIUS_KM = 6371.0

# Backend API base URL
API_BASE_URL = "http://localhost:8000/api"

# Cached zone boundaries from API (fractions are global, only fetch once)
_cachedZoneBoundaries: Optional[List[Dict]] = None


def fetchZoneBoundariesFromAPI() -> Optional[List[Dict]]:
    """
    Fetch zone boundaries from the backend API.
    Note: Zone fractions are GLOBAL (same for all challenges).
    Backend is THE single source of truth.
    """
    global _cachedZoneBoundaries
    
    # Return cached if available
    if _cachedZoneBoundaries:
        return _cachedZoneBoundaries
    
    try:
        response = requests.get(f"{API_BASE_URL}/scoring/zones", timeout=5)
        if response.status_code == 200:
            data = response.json()
            _cachedZoneBoundaries = data.get("zones", None)
            return _cachedZoneBoundaries
    except Exception as e:
        print(f"Warning: Could not fetch scoring zones from API: {e}")
    return None


def getZonesConfig() -> List[Tuple[float, float, Tuple[float, float, float, float], int]]:
    """
    Get scoring zones configuration from the backend API.
    Backend defines the boundaries; we add visual styling (colors, depth).
    """
    apiZones = fetchZoneBoundariesFromAPI()
    if not apiZones:
        print("Warning: No scoring zones available from API")
        return []
    
    # Convert API response to our rendering tuple format
    zones = []
    for zone in apiZones:
        inner = zone["inner"]
        outer = zone["outer"]
        colorName = zone["color"]
        color = ZONE_COLORS.get(colorName, (1.0, 1.0, 1.0, 0.5))
        depth = ZONE_DEPTH_OFFSETS.get(colorName, 0)
        zones.append((inner, outer, color, depth))
    
    return zones


def createAnnulus(
    normal: Tuple[ float, float, float ],
    color: Tuple[ float, float, float, float ],
    innerRadius: float,
    outerRadius: float,
    segments: int = DISK_SEGMENTS
) -> NodePath:
    """Create a flat annulus (ring band) aligned to the globe surface."""
    nx, ny, nz = normal

    up = ( 0.0, 1.0, 0.0 ) if abs( ny ) < 0.9 else ( 1.0, 0.0, 0.0 )
    tx = ny * up[ 2 ] - nz * up[ 1 ]
    ty = nz * up[ 0 ] - nx * up[ 2 ]
    tz = nx * up[ 1 ] - ny * up[ 0 ]
    tLen = ( tx * tx + ty * ty + tz * tz ) ** 0.5
    tx, ty, tz = tx / tLen, ty / tLen, tz / tLen

    bx = ny * tz - nz * ty
    by = nz * tx - nx * tz
    bz = nx * ty - ny * tx

    fmt = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData( "annulus", fmt, Geom.UHStatic )
    vertexWriter = GeomVertexWriter( vdata, "vertex" )
    normalWriter = GeomVertexWriter( vdata, "normal" )

    for i in range( segments ):
        angle = ( i / segments ) * 2 * pi
        cosA = cos( angle )
        sinA = sin( angle )
        for r in ( innerRadius, outerRadius ):
            px = ( tx * cosA + bx * sinA ) * r
            py = ( ty * cosA + by * sinA ) * r
            pz = ( tz * cosA + bz * sinA ) * r
            vertexWriter.addData3f( px, py, pz )
            normalWriter.addData3f( nx, ny, nz )

    geom = Geom( vdata )
    tris = GeomTriangles( Geom.UHStatic )
    for i in range( segments ):
        inner0 = i * 2
        outer0 = i * 2 + 1
        inner1 = ( ( i + 1 ) % segments ) * 2
        outer1 = ( ( i + 1 ) % segments ) * 2 + 1
        tris.addVertices( inner0, outer0, inner1 )
        tris.closePrimitive()
        tris.addVertices( outer0, outer1, inner1 )
        tris.closePrimitive()
    geom.addPrimitive( tris )

    node = GeomNode( "annulus" )
    node.addGeom( geom )
    path = NodePath( node )
    path.setColor( *color )
    path.setTwoSided( True )
    path.setTransparency( TransparencyAttrib.MAlpha )
    return path


def createTargetRings(
    normal: Tuple[ float, float, float ],
    thresholdKm: float,
    parent: NodePath,
    pos: Tuple[ float, float, float ],
    globeScale: float,
) -> List[ NodePath ]:
    """
    Create concentric ring bands centred on the answer location.
    Zone boundaries are fetched from the backend API (single source of truth).
    Green (innermost) → yellow → orange → red (outermost).
    """
    maxLocalRadius = ( thresholdKm / ( EARTH_RADIUS_KM * globeScale ) ) * RING_SCALE_MULTIPLIER

    # Get zone boundaries from backend API (global, same for all challenges)
    zones = getZonesConfig()
    
    nodes: List[ NodePath ] = []
    for innerFrac, outerFrac, color, depthOffset in zones:
        innerR = maxLocalRadius * innerFrac
        outerR = maxLocalRadius * outerFrac
        ring = createAnnulus( normal, color, innerRadius = innerR, outerRadius = outerR )
        ring.reparentTo( parent )
        ring.setPos( *pos )
        ring.setDepthOffset( depthOffset )
        nodes.append( ring )

    return nodes


def createXMark(
    normal: Tuple[ float, float, float ],
    color: Tuple[ float, float, float, float ],
    size: float = 0.07,
    thickness: float = 4.0
) -> NodePath:
    """Create an X mark aligned to the globe surface at the given surface normal."""
    nx, ny, nz = normal

    up = ( 0.0, 1.0, 0.0 ) if abs( ny ) < 0.9 else ( 1.0, 0.0, 0.0 )
    tx = ny * up[ 2 ] - nz * up[ 1 ]
    ty = nz * up[ 0 ] - nx * up[ 2 ]
    tz = nx * up[ 1 ] - ny * up[ 0 ]
    tLen = ( tx * tx + ty * ty + tz * tz ) ** 0.5
    tx, ty, tz = tx / tLen, ty / tLen, tz / tLen

    bx = ny * tz - nz * ty
    by = nz * tx - nx * tz
    bz = nx * ty - ny * tx

    lines = LineSegs()
    lines.setThickness( thickness )
    lines.setColor( *color )

    lines.moveTo( ( -tx - bx ) * size, ( -ty - by ) * size, ( -tz - bz ) * size )
    lines.drawTo( (  tx + bx ) * size, (  ty + by ) * size, (  tz + bz ) * size )

    lines.moveTo( (  tx - bx ) * size, (  ty - by ) * size, (  tz - bz ) * size )
    lines.drawTo( ( -tx + bx ) * size, ( -ty + by ) * size, ( -tz + bz ) * size )

    xNode = lines.create()
    xPath = NodePath( xNode )
    xPath.setTwoSided( True )
    return xPath


def createCityLabel(
    cityName: str,
    normal: Tuple[ float, float, float ],
    pos: Tuple[ float, float, float ],
    parent: NodePath,
    offset: float = 0.35,
) -> NodePath:
    """
    Create a billboard text label floating above the surface point,
    tilted ~30° for a leaning-sign feel, with a connector line.
    """
    root = NodePath( "cityLabelRoot" )
    root.reparentTo( parent )

    nx, ny, nz = normal
    tipPos = (
        pos[ 0 ] + nx * offset,
        pos[ 1 ] + ny * offset,
        pos[ 2 ] + nz * offset,
    )

    # ── Connector line ────────────────────────────────────────────────────────
    lines = LineSegs()
    lines.setThickness( 2.0 )
    lines.setColor( 1.0, 1.0, 0.3, 0.9 )
    lines.moveTo( pos[ 0 ], pos[ 1 ], pos[ 2 ] )
    lines.drawTo( tipPos[ 0 ], tipPos[ 1 ], tipPos[ 2 ] )
    lineNP = root.attachNewNode( lines.create() )
    lineNP.setDepthOffset( 18 )

    # ── Text label ────────────────────────────────────────────────────────────
    textNode = TextNode( "cityLabel" )
    textNode.setText( cityName )
    textNode.setAlign( TextNode.ACenter )
    textNode.setTextColor( 1.0, 1.0, 0.2, 1.0 )

    labelNP = root.attachNewNode( textNode )
    labelNP.setPos( tipPos[ 0 ], tipPos[ 1 ], tipPos[ 2 ] )
    labelNP.setScale( 0.08 )
    labelNP.setDepthOffset( 19 )
    # Tilt 30° around the roll axis so it looks like a leaning sign
    labelNP.setR( 30 )
    labelNP.setBillboardPointEye()

    return root
