"""
Globe GUI Controller - Handles globe navigation GUI elements only.
Game-related GUI lives in GameGuiController.
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode
from typing import Optional

from ..interfaces.i_globe_application import IGlobeApplication
from ..settings.gui_settings_manager import GuiSettingsManager
from .globe_button_factory import GlobeButtonFactory


class GlobeGuiController:
    """Controls all globe navigation GUI elements."""

    def __init__( self, globeApp: IGlobeApplication ):
        self.__globeApp: IGlobeApplication = globeApp
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__buttonFactory: GlobeButtonFactory = GlobeButtonFactory( self.__settings )

        self.__debugDisplay: Optional[ OnscreenText ] = None
        self.__radiusDisplay: Optional[ OnscreenText ] = None

        self.__createGuiControls()

    def __createGuiControls( self ) -> None:
        """Create all globe navigation buttons and labels."""
        self.__buttonFactory.buildStepControls(
            onIncrease = self.__onIncreaseRotationIncrement,
            onDecrease = self.__onDecreaseRotationIncrement
        )
        self.__buttonFactory.buildZoomControls(
            onZoomIn = self.__onZoomIn,
            onZoomOut = self.__onZoomOut
        )
        self.__buttonFactory.buildResetButton( onReset = self.__onResetView )
        self.__buttonFactory.buildRotationButtons(
            onUp = self.__onRotateUp,
            onDown = self.__onRotateDown,
            onLeft = self.__onRotateLeft,
            onRight = self.__onRotateRight
        )
        self.__buttonFactory.buildPresetButtons( onPreset = self.__onSetPresetView )
        self.__buttonFactory.buildRadiusControls(
            onIncrease = self.__onIncreaseRadius,
            onDecrease = self.__onDecreaseRadius,
            initialValue = self.__globeApp.continentRadius
        )

        # Debug label — bottom-right, gray
        debugSettings = self.__settings.getDebugTextSettings()
        self.__debugDisplay = OnscreenText(
            text = "",
            pos = debugSettings[ "pos" ],
            scale = debugSettings[ "scale" ],
            fg = self.__settings.getTextColor( "debug" ),
            wordwrap = debugSettings[ "wordwrap" ],
            align = TextNode.ALeft
        )

        # Radius value display (hidden by default)
        self.__radiusDisplay = OnscreenText(
            text = f"{self.__globeApp.continentRadius:.2f}",
            pos = ( -0.75, 0.50 ),
            scale = 0.04,
            fg = ( 1.0, 1.0, 1.0, 1.0 ),
            align = TextNode.ACenter
        )
        self.__radiusDisplay.hide()

    def __applyButtonEffect( self, button: DirectButton ) -> None:
        """Flash button darker when clicked."""
        originalColor = button[ 'frameColor' ]
        pressedColor = self.__settings.getButtonColor( "control", "pressed" )
        button[ 'frameColor' ] = pressedColor

        def resetColor( task ) -> int:
            button[ 'frameColor' ] = originalColor
            return task.done

        self.__globeApp.taskManager.doMethodLater(
            self.__settings.getEffectDuration(),
            resetColor,
            f"reset_button_{id( button )}"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def addDebugMessage( self, message: str ) -> None:
        """Update the debug label."""
        if self.__debugDisplay:
            self.__debugDisplay.setText( message )

    def updateContinentRadiusDisplay( self, value: float ) -> None:
        """Update the continent radius value display."""
        if self.__radiusDisplay:
            self.__radiusDisplay.setText( f"{value:.3f}" )

    # ── Event handlers ────────────────────────────────────────────────────────

    def __onZoomIn( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.zoomInBtn )
        self.__globeApp.zoomIn()

    def __onZoomOut( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.zoomOutBtn )
        self.__globeApp.zoomOut()

    def __onResetView( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.resetBtn )
        self.__globeApp.resetView()

    def __onRotateUp( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.rotateUpBtn )
        self.__globeApp.rotateUp()

    def __onRotateDown( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.rotateDownBtn )
        self.__globeApp.rotateDown()

    def __onRotateLeft( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.rotateLeftBtn )
        self.__globeApp.rotateLeft()

    def __onRotateRight( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.rotateRightBtn )
        self.__globeApp.rotateRight()

    def __onIncreaseRotationIncrement( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.incrementPlusBtn )
        self.__globeApp.increaseRotationIncrement()

    def __onDecreaseRotationIncrement( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.incrementMinusBtn )
        self.__globeApp.decreaseRotationIncrement()

    def __onSetPresetView( self, index: int ) -> None:
        presets = self.__buttonFactory.presetButtons
        if 0 <= index < len( presets ):
            self.__applyButtonEffect( presets[ index ] )
        self.__globeApp.setPresetView( index )

    def __onIncreaseRadius( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.radiusPlusBtn )
        self.__globeApp.increaseContinentRadius()

    def __onDecreaseRadius( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.radiusMinusBtn )
        self.__globeApp.decreaseContinentRadius()
