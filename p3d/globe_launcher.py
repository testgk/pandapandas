#!/usr/bin/env python3
"""
Globe Launcher — launches the globe in globe-viewer or game mode.

Usage:
  python globe_launcher.py              # defaults to game mode
  python globe_launcher.py --mode game  # full GeoChallenge game
  python globe_launcher.py --mode globe # pure globe viewer, no game
"""
import sys
from pathlib import Path

sys.path.append( str( Path( __file__ ).parent ) )

from app_mode import AppMode


def parseMode() -> AppMode:
    if "--mode" in sys.argv:
        idx = sys.argv.index( "--mode" )
        if idx + 1 < len( sys.argv ):
            arg = sys.argv[ idx + 1 ].lower()
            if arg == "globe":
                return AppMode.GLOBE
    return AppMode.GAME


def launch( mode: AppMode ) -> None:
    modeLabel = "Globe Viewer" if mode == AppMode.GLOBE else "GeoChallenge Game"
    print( f"Launching 3D Globe — {modeLabel}" )
    print( "=" * 50 )

    if mode == AppMode.GAME:
        print( "How to play:" )
        print( "  1. Read the challenge question on screen" )
        print( "  2. Click the globe where you think the location is" )
        print( "  3. Get instant score and feedback" )
        print( "  4. Press NEXT QUESTION for the next challenge" )
    else:
        print( "Globe viewer mode — use the controls to rotate and zoom." )

    print( "=" * 50 )

    try:
        from globe_app import RealGlobeApplication
        app = RealGlobeApplication( appMode = mode )
        app.run()
    except Exception as e:
        print( f"Error: {e}" )
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    launch( parseMode() )
