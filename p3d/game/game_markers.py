"""
Game Markers — Panda3D geometry helpers for placing visual feedback on the globe.
Creates disk and X-mark nodes aligned to the globe surface.
"""
from math import cos, sin, pi
from typing import Tuple

from panda3d.core import (
    Geom, GeomNode, GeomTriangles, GeomVertexData,
    GeomVertexFormat, GeomVertexWriter, LineSegs,
    NodePath, TransparencyAttrib
)

DISK_SEGMENTS = 24


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

