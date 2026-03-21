"""
Android Controller - Touch-friendly game controller for Android/mobile devices.
Replaces mouse-based GlobeGuiController and GameGuiController with:
  - Large touch buttons for game actions
  - Drag-to-rotate globe (single finger)
  - Pinch-to-zoom (two fingers)
  - Swipe gesture detection
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode, Vec2
from typing import Optional

from ..interfaces.i_globe_application import IGlobeApplication
from ..settings.gui_settings_manager import GuiSettingsManager


# ── Constants ──────────────────────────────────────────────────────────────────

TOUCH_BUTTON_SCALE: float = 0.08
TOUCH_DRAG_THRESHOLD: float = 5.0        # pixels before drag is recognised
PINCH_ZOOM_SENSITIVITY: float = 0.05     # zoom units per pixel of pinch delta
SWIPE_MIN_DISTANCE: float = 80.0         # pixels for a swipe to register
SWIPE_ROTATION_DEGREES: int = 15         # degrees rotated per swipe


class AndroidController:
    """
    Touch-optimised controller that drives an IGlobeApplication.
    Handles drag-rotate, pinch-zoom and large-button game actions.
    """

    def __init__( self, globeApp: IGlobeApplication ):
        self.__globeApp: IGlobeApplication = globeApp
        self.__settings: GuiSettingsManager = GuiSettingsManager()

        # Cache mouseWatcherNode from the ShowBase instance (globe app IS the ShowBase)
        self.__mouseWatcher = getattr( globeApp, 'mouseWatcherNode', None )

        # ── Touch state ───────────────────────────────────────────────────────
        self.__isDragging: bool = False
        self.__dragStart: Vec2 = Vec2( 0, 0 )
        self.__lastDragPos: Vec2 = Vec2( 0, 0 )

        self.__isPinching: bool = False
        self.__pinchStartDistance: float = 0.0
        self.__touch1Start: Vec2 = Vec2( 0, 0 )
        self.__touch2Start: Vec2 = Vec2( 0, 0 )

        # ── GUI elements ──────────────────────────────────────────────────────
        self.__challengeDisplay: Optional[ OnscreenText ] = None
        self.__statusDisplay: Optional[ OnscreenText ] = None

        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__hintBtn: Optional[ DirectButton ] = None
        self.__zoomInBtn: Optional[ DirectButton ] = None
        self.__zoomOutBtn: Optional[ DirectButton ] = None
        self.__resetBtn: Optional[ DirectButton ] = None

        self.__buildGui()
        self.__registerInputHandlers()

    # ── GUI construction ───────────────────────────────────────────────────────

    def __buildGui( self ) -> None:
        """Build all touch-friendly UI elements."""
        self.__buildChallengeDisplay()
        self.__buildStatusDisplay()
        self.__buildGameButtons()
        self.__buildNavigationButtons()

    def __buildChallengeDisplay( self ) -> None:
        """Large, readable challenge text at top-centre for mobile screens."""
        self.__challengeDisplay = OnscreenText(
            text = "Tap START to play",
            pos = ( 0.0, 0.85 ),
            scale = 0.06,
            fg = ( 1.0, 1.0, 0.6, 1.0 ),
            wordwrap = 18,
            align = TextNode.ACenter
        )

    def __buildStatusDisplay( self ) -> None:
        """Small status/debug text at bottom-left."""
        self.__statusDisplay = OnscreenText(
            text = "",
            pos = ( -1.2, -0.9 ),
            scale = 0.04,
            fg = ( 0.7, 0.7, 0.7, 1.0 ),
            wordwrap = 20,
            align = TextNode.ALeft
        )

    def __buildGameButtons( self ) -> None:
        """Game-action buttons — large, right side of screen."""
        self.__startGameBtn = DirectButton(
            text = "START",
            pos = ( 1.1, 0, 0.5 ),
            scale = TOUCH_BUTTON_SCALE,
            command = self.__onStartGame,
            frameColor = ( 0.2, 0.7, 0.2, 1.0 ),
            text_fg = ( 1.0, 1.0, 1.0, 1.0 ),
            pressEffect = 1, relief = 2
        )

        self.__nextChallengeBtn = DirectButton(
            text = "NEXT",
            pos = ( 1.1, 0, 0.3 ),
            scale = TOUCH_BUTTON_SCALE,
            command = self.__onNextChallenge,
            frameColor = ( 0.2, 0.5, 0.9, 1.0 ),
            text_fg = ( 1.0, 1.0, 1.0, 1.0 ),
            pressEffect = 1, relief = 2
        )
        self.__nextChallengeBtn.hide()

        self.__hintBtn = DirectButton(
            text = "HINT",
            pos = ( 1.1, 0, 0.1 ),
            scale = TOUCH_BUTTON_SCALE,
            command = self.__onHint,
            frameColor = ( 0.8, 0.6, 0.1, 1.0 ),
            text_fg = ( 1.0, 1.0, 1.0, 1.0 ),
            pressEffect = 1, relief = 2
        )
        self.__hintBtn.hide()

    def __buildNavigationButtons( self ) -> None:
        """Zoom and reset buttons — large, left side of screen."""
        self.__zoomInBtn = DirectButton(
            text = "+",
            pos = ( -1.1, 0, 0.2 ),
            scale = TOUCH_BUTTON_SCALE,
            command = self.__onZoomIn,
            frameColor = ( 0.3, 0.3, 0.3, 0.85 ),
            text_fg = ( 1.0, 1.0, 1.0, 1.0 ),
            pressEffect = 1, relief = 2
        )

        self.__zoomOutBtn = DirectButton(
            text = "-",
            pos = ( -1.1, 0, 0.0 ),
            scale = TOUCH_BUTTON_SCALE,
            command = self.__onZoomOut,
            frameColor = ( 0.3, 0.3, 0.3, 0.85 ),
            text_fg = ( 1.0, 1.0, 1.0, 1.0 ),
            pressEffect = 1, relief = 2
        )

        self.__resetBtn = DirectButton(
            text = "RESET",
            pos = ( -1.1, 0, -0.2 ),
            scale = TOUCH_BUTTON_SCALE,
            command = self.__onReset,
            frameColor = ( 0.5, 0.2, 0.2, 0.85 ),
            text_fg = ( 1.0, 1.0, 1.0, 1.0 ),
            pressEffect = 1, relief = 2
        )

    # ── Input registration ─────────────────────────────────────────────────────

    def __registerInputHandlers( self ) -> None:
        """Register touch and mouse events via Panda3D's messenger."""
        self.__handlers: dict = {
            "mouse1":     self.__onTouchBegin,
            "mouse1-up":  self.__onTouchEnd,
            "mouse3":     self.__onSecondTouchBegin,
            "mouse3-up":  self.__onSecondTouchEnd,
            "wheel_up":   self.__onZoomIn,
            "wheel_down": self.__onZoomOut,
        }

        for event, handler in self.__handlers.items():
            try:
                self.__globeApp.accept( event, handler )
            except AttributeError:
                pass

        # Register per-frame drag task
        self.__globeApp.taskManager.add(
            self.__dragTask,
            "androidDragTask"
        )

    # ── Touch / drag handlers ──────────────────────────────────────────────────

    def __onTouchBegin( self ) -> None:
        """Record drag start position."""
        if not self.__mouseWatcher or not self.__mouseWatcher.hasMouse():
            return
        mousePos = self.__mouseWatcher.getMouse()
        self.__dragStart = Vec2( mousePos.x, mousePos.y )
        self.__lastDragPos = Vec2( mousePos.x, mousePos.y )
        self.__isDragging = True

    def __onTouchEnd( self ) -> None:
        """Detect swipe on release, clear drag state."""
        if self.__isDragging:
            self.__detectSwipe()
        self.__isDragging = False

    def __onSecondTouchBegin( self ) -> None:
        """Begin pinch-zoom tracking."""
        self.__isPinching = True

    def __onSecondTouchEnd( self ) -> None:
        """End pinch-zoom."""
        self.__isPinching = False
        self.__pinchStartDistance = 0.0

    def __dragTask( self, task ) -> int:
        """Per-frame task: rotate globe while finger is dragging."""
        if not self.__isDragging:
            return task.cont

        if not self.__mouseWatcher or not self.__mouseWatcher.hasMouse():
            return task.cont

        mousePos = self.__mouseWatcher.getMouse()
        currentPos = Vec2( mousePos.x, mousePos.y )
        delta = currentPos - self.__lastDragPos
        self.__lastDragPos = currentPos

        if abs( delta.x ) > 0.001:
            if delta.x > 0:
                self.__globeApp.rotateRight()
            else:
                self.__globeApp.rotateLeft()

        if abs( delta.y ) > 0.001:
            if delta.y > 0:
                self.__globeApp.rotateUp()
            else:
                self.__globeApp.rotateDown()

        return task.cont

    def __detectSwipe( self ) -> None:
        """Check if drag qualifies as a directional swipe."""
        delta = self.__lastDragPos - self.__dragStart
        distance = delta.length() * 1000  # normalised → approximate pixels

        if distance < SWIPE_MIN_DISTANCE / 1000:
            return

        if abs( delta.x ) >= abs( delta.y ):
            if delta.x > 0:
                self.__setStatus( "Swipe → rotateRight" )
                self.__globeApp.rotateRight()
            else:
                self.__setStatus( "Swipe ← rotateLeft" )
                self.__globeApp.rotateLeft()
        else:
            if delta.y > 0:
                self.__setStatus( "Swipe ↑ rotateUp" )
                self.__globeApp.rotateUp()
            else:
                self.__setStatus( "Swipe ↓ rotateDown" )
                self.__globeApp.rotateDown()

    # ── Button handlers ────────────────────────────────────────────────────────

    def __onStartGame( self ) -> None:
        self.__applyButtonEffect( self.__startGameBtn )
        self.__globeApp.startGame()

    def __onNextChallenge( self ) -> None:
        self.__applyButtonEffect( self.__nextChallengeBtn )
        self.__globeApp.nextChallenge()

    def __onHint( self ) -> None:
        self.__applyButtonEffect( self.__hintBtn )

    def __onZoomIn( self ) -> None:
        self.__applyButtonEffect( self.__zoomInBtn )
        self.__globeApp.zoomIn()

    def __onZoomOut( self ) -> None:
        self.__applyButtonEffect( self.__zoomOutBtn )
        self.__globeApp.zoomOut()

    def __onReset( self ) -> None:
        self.__applyButtonEffect( self.__resetBtn )
        self.__globeApp.resetView()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def __applyButtonEffect( self, button: Optional[ DirectButton ] ) -> None:
        """Flash button to dark on press, restore after effect duration."""
        if button is None:
            return
        originalColor = button[ 'frameColor' ]
        button[ 'frameColor' ] = ( 0.1, 0.1, 0.1, 1.0 )

        def resetColor( task ) -> int:
            button[ 'frameColor' ] = originalColor
            return task.done

        self.__globeApp.taskManager.doMethodLater(
            self.__settings.getEffectDuration(),
            resetColor,
            f"android_btn_reset_{id( button )}"
        )

    def __setStatus( self, message: str ) -> None:
        """Update the status display."""
        if self.__statusDisplay:
            self.__statusDisplay.setText( message )

    # ── Public API ─────────────────────────────────────────────────────────────

    def setChallengeText( self, message: str ) -> None:
        """Set the challenge text displayed at the top of the screen."""
        if self.__challengeDisplay:
            self.__challengeDisplay.setText( message )

    def clearChallengeText( self ) -> None:
        """Clear the challenge display."""
        if self.__challengeDisplay:
            self.__challengeDisplay.setText( "" )

    def showNextChallengeButton( self ) -> None:
        """Show NEXT button after a question is answered."""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.show()

    def hideNextChallengeButton( self ) -> None:
        """Hide the NEXT button."""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.hide()

    def showHintButton( self ) -> None:
        """Show HINT button during an active challenge."""
        if self.__hintBtn:
            self.__hintBtn.show()

    def hideHintButton( self ) -> None:
        """Hide HINT button."""
        if self.__hintBtn:
            self.__hintBtn.hide()

    def setStatusText( self, message: str ) -> None:
        """Update bottom-left status label."""
        self.__setStatus( message )

