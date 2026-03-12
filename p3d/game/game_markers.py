"""
Game Markers — Panda3D geometry helpers for placing visual feedback on the globe.
Creates disk, X-mark, scoring-ring and city-label nodes aligned to the globe surface.
"""
from math import cos, sin, pi
from typing import List, Tuple

from panda3d.core import (
    Geom, GeomNode, GeomTriangles, GeomVertexData,
    GeomVertexFormat, GeomVertexWriter, LineSegs,
    NodePath, TransparencyAttrib,
    TextNode, CardMaker
)

DISK_SEGMENTS = 48

# Scoring zones: outermost→innermost — ( fraction_of_threshold, RGBA, depth_offset )
# Keep offsets LOW so the click X (depthOffset=20) always renders above them.
SCORING_ZONES: List[ Tuple[ float, Tuple[ float, float, float, float ], int ] ] = [
    ( 1.00, ( 1.0, 0.15, 0.0,  0.55 ), -4 ),   # red    — worst  (outer)
    ( 0.75, ( 1.0, 0.55, 0.0,  0.60 ), -3 ),   # orange
    ( 0.50, ( 1.0, 0.90, 0.0,  0.65 ), -2 ),   # yellow
    ( 0.25, ( 0.1, 0.85, 0.15, 0.75 ), -1 ),   # green  — best   (inner)
]

# Multiplier applied on top of the km→local conversion to make rings visually larger
RING_SCALE_MULTIPLIER = 3.5

# Earth radius in km — used to convert km distances to globe local-space units
EARTH_RADIUS_KM = 6371.0


def createDisk(
    normal: Tuple[ float, float, float ],
    color: Tuple[ float, float, float, float ],
    radius: float = 0.06,
    segments: int = DISK_SEGMENTS
) -> NodePath:
    """Create a flat disk aligned to the globe surface at the given surface normal."""
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
    vdata = GeomVertexData( "disk", fmt, Geom.UHStatic )
    vertexWriter = GeomVertexWriter( vdata, "vertex" )
    normalWriter = GeomVertexWriter( vdata, "normal" )

    vertexWriter.addData3f( 0.0, 0.0, 0.0 )
    normalWriter.addData3f( nx, ny, nz )

    for i in range( segments ):
        angle = ( i / segments ) * 2 * pi
        px = ( tx * cos( angle ) + bx * sin( angle ) ) * radius
        py = ( ty * cos( angle ) + by * sin( angle ) ) * radius
        pz = ( tz * cos( angle ) + bz * sin( angle ) ) * radius
        vertexWriter.addData3f( px, py, pz )
        normalWriter.addData3f( nx, ny, nz )

    geom = Geom( vdata )
    tris = GeomTriangles( Geom.UHStatic )
    for i in range( segments ):
        tris.addVertices( 0, i + 1, ( i + 1 ) % segments + 1 )
        tris.closePrimitive()
    geom.addPrimitive( tris )

    node = GeomNode( "disk" )
    node.addGeom( geom )
    diskPath = NodePath( node )
    diskPath.setColor( *color )
    diskPath.setTwoSided( True )
    diskPath.setTransparency( TransparencyAttrib.MAlpha )
    return diskPath


def createTargetRings(
    normal: Tuple[ float, float, float ],
    thresholdKm: float,
    parent: NodePath,
    pos: Tuple[ float, float, float ],
    globeScale: float,
) -> List[ NodePath ]:
    """
    Create 4 concentric scoring-zone disks centred on the answer location.
    Drawn outermost→innermost so inner zones render on top.

    Args:
        normal:       surface normal at the answer point (unit vector, globe local space)
        thresholdKm:  full scoring radius in km (maps to the outermost red ring)
        parent:       NodePath to attach the disks to (the globe node)
        pos:          disk centre position in globe local space
        globeScale:   the globe's uniform scale factor (used to convert km → local units)
    Returns:
        list of NodePaths (one per zone, outermost first)
    """
    # km → globe local-space radius, then scale up so rings are clearly visible
    maxLocalRadius = ( thresholdKm / ( EARTH_RADIUS_KM * globeScale ) ) * RING_SCALE_MULTIPLIER

    nodes: List[ NodePath ] = []
    for fraction, color, depthOffset in SCORING_ZONES:
        radius = maxLocalRadius * fraction
        disk = createDisk( normal, color, radius = radius )
        disk.reparentTo( parent )
        disk.setPos( *pos )
        disk.setDepthOffset( depthOffset )
        nodes.append( disk )

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
