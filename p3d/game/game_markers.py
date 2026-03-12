"""
Game Markers — Panda3D geometry helpers for placing visual feedback on the globe.
Creates disk, X-mark and scoring-ring nodes aligned to the globe surface.
"""
from math import cos, sin, pi
from typing import List, Tuple

from panda3d.core import (
    Geom, GeomNode, GeomTriangles, GeomVertexData,
    GeomVertexFormat, GeomVertexWriter, LineSegs,
    NodePath, TransparencyAttrib
)

DISK_SEGMENTS = 48

# Scoring zones as fractions of the total threshold radius (outermost → innermost)
# Each tuple: ( fraction_of_threshold, RGBA )
SCORING_ZONES: List[ Tuple[ float, Tuple[ float, float, float, float ] ] ] = [
    ( 1.00, ( 1.0, 0.15, 0.0,  0.55 ) ),   # red    — worst  (outer)
    ( 0.75, ( 1.0, 0.55, 0.0,  0.60 ) ),   # orange
    ( 0.50, ( 1.0, 0.90, 0.0,  0.65 ) ),   # yellow
    ( 0.25, ( 0.1, 0.85, 0.15, 0.75 ) ),   # green  — best   (inner)
]

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
    # km → globe local-space radius
    # globe local unit sphere = 1.0 = EARTH_RADIUS_KM km (before globeScale is applied)
    # but disks are children of the globe node which is already scaled,
    # so we work in pre-scale units: local_r = km / (EARTH_RADIUS_KM * globeScale)
    maxLocalRadius = thresholdKm / ( EARTH_RADIUS_KM * globeScale )

    nodes: List[ NodePath ] = []
    for fraction, color in SCORING_ZONES:
        radius = maxLocalRadius * fraction
        disk = createDisk( normal, color, radius = radius )
        disk.reparentTo( parent )
        disk.setPos( *pos )
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

