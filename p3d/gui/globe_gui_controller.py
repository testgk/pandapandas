"""
Globe GUI Controller - Handles all GUI elements and user interactions
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode
from typing import Optional

from interfaces.i_globe_application import IGlobeApplication
from settings.gui_settings_manager import GuiSettingsManager
from gui.globe_button_factory import GlobeButtonFactory


class GlobeGuiController:
    """Controls all GUI elements for the globe application"""

    def __init__( self, globeApp: IGlobeApplication, showGameControls: bool = True ):
        self.__globeApp: IGlobeApplication = globeApp
        self.__showGameControls: bool = showGameControls
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__buttonFactory: GlobeButtonFactory = GlobeButtonFactory( self.__settings )
        self.__challengeMaxLines: int = self.__settings.getChallengeTextSettings()[ "max_lines" ]

        self.__logDisplay: Optional[ OnscreenText ] = None
        self.__challengeDisplay: Optional[ OnscreenText ] = None
        self.__debugDisplay: Optional[ OnscreenText ] = None
        self.__radiusDisplay: Optional[ OnscreenText ] = None

        self.__createGuiControls()

    def __createGuiControls( self ) -> None:
        """Create all GUI buttons and text labels"""
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

        if self.__showGameControls:
            self.__buttonFactory.buildGameControls(
                onStartGame = self.__onStartGame,
                onNextChallenge = self.__onNextChallenge,
                onGameStats = self.__onGameStats
            )

        self.__buttonFactory.buildRadiusControls(
            onIncrease = self.__onIncreaseRadius,
            onDecrease = self.__onDecreaseRadius,
            initialValue = self.__globeApp.continentRadius
        )

        # Challenge label — bottom-left, pale yellow (game mode only)
        if self.__showGameControls:
            challengeSettings = self.__settings.getChallengeTextSettings()
            self.__challengeDisplay = OnscreenText(
                text = "",
                pos = challengeSettings[ "pos" ],
                scale = challengeSettings[ "scale" ],
                fg = self.__settings.getTextColor( "challenge" ),
                wordwrap = challengeSettings[ "wordwrap" ],
                align = TextNode.ALeft
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

        # Radius value display (hidden)
        self.__radiusDisplay = OnscreenText(
            text = f"{self.__globeApp.continentRadius:.2f}",
            pos = ( -0.75, 0.50 ),
            scale = 0.04,
            fg = ( 1.0, 1.0, 1.0, 1.0 ),
            align = TextNode.ACenter
        )
        self.__radiusDisplay.hide()

    def __applyButtonEffect( self, button: DirectButton ) -> None:
        """Apply dark gray flash to button when clicked"""
        originalColor = button[ 'frameColor' ]
        pressedColor = self.__settings.getButtonColor( "control", "pressed" )
        button[ 'frameColor' ] = pressedColor

        def resetColor( task ) -> int:
            button[ 'frameColor' ] = originalColor
            return task.done

        effectDuration = self.__settings.getEffectDuration()
        self.__globeApp.taskManager.doMethodLater(
            effectDuration, resetColor, f"reset_button_{id( button )}"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def clearLogMessage( self ) -> None:
        """Clear the challenge display"""
        if self.__challengeDisplay:
            self.__challengeDisplay.setText( "" )

    def addLogMessage( self, message: str ) -> None:
        """Replace challenge display with a single message, capped to max lines"""
        if not self.__challengeDisplay:
            return
        lines = message.splitlines()
        truncated = "\n".join( lines[ :self.__challengeMaxLines ] )
        self.__challengeDisplay.setText( truncated )

    def addDebugMessage( self, message: str ) -> None:
        """Replace debug display with a single message"""
        if self.__debugDisplay:
            self.__debugDisplay.setText( message )

    def updateContinentRadiusDisplay( self, value: float ) -> None:
        """Update the continent radius value display"""
        if self.__radiusDisplay:
            self.__radiusDisplay.setText( f"{value:.3f}" )

    def enableNextChallenge( self ) -> None:
        """Show the Next Challenge button after question is answered"""
        btn = self.__buttonFactory.nextChallengeBtn
        if btn:
            btn.show()

    def disableNextChallenge( self ) -> None:
        """Hide the Next Challenge button until question is answered"""
        btn = self.__buttonFactory.nextChallengeBtn
        if btn:
            btn.hide()

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

    def __onStartGame( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.startGameBtn )
        self.__globeApp.startGame()

    def __onNextChallenge( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.nextChallengeBtn )
        self.__globeApp.nextChallenge()

    def __onGameStats( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.gameStatsBtn )
        self.__globeApp.showGameStats()

    def __onIncreaseRadius( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.radiusPlusBtn )
        self.__globeApp.increaseContinentRadius()

    def __onDecreaseRadius( self ) -> None:
        self.__applyButtonEffect( self.__buttonFactory.radiusMinusBtn )
        self.__globeApp.decreaseContinentRadius()

