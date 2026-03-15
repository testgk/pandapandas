#!/usr/bin/env python3
"""
Globe Launcher — launches the globe in globe-viewer, game or android mode.

Usage:
  python globe_launcher.py                # defaults to game mode
  python globe_launcher.py --mode game    # full GeoChallenge game
  python globe_launcher.py --mode globe   # pure globe viewer, no game
  python globe_launcher.py --mode android # touch-optimised Android mode
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
            if arg == "android":
                return AppMode.ANDROID
    return AppMode.GAME


def launch( mode: AppMode ) -> None:
    modeLabels = {
        AppMode.GLOBE:   "Globe Viewer",
        AppMode.GAME:    "GeoChallenge Game",
        AppMode.ANDROID: "GeoChallenge Android (Touch Mode)",
    }
    print( f"Launching 3D Globe — {modeLabels[ mode ]}" )
    print( "=" * 50 )

    if mode == AppMode.GAME:
        print( "How to play:" )
        print( "  1. Read the challenge question on screen" )
        print( "  2. Click the globe where you think the location is" )
        print( "  3. Get instant score and feedback" )
        print( "  4. Press NEXT QUESTION for the next challenge" )
    elif mode == AppMode.ANDROID:
        print( "Android touch mode:" )
        print( "  • Drag  — rotate the globe" )
        print( "  • +/-   — zoom in / out" )
        print( "  • START — begin a GeoChallenge" )
        print( "  • NEXT  — next question after answering" )
        print( "  • HINT  — focus camera on the answer region" )
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
