"""
Globe GUI Controller - Handles all GUI elements and user interactions
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DGG
from panda3d.core import *
from typing import List, Tuple, Callable, Optional, Any
from interfaces.i_globe_application import IGlobeApplication
from settings.gui_settings_manager import GuiSettingsManager


class GlobeGuiController:
    """Controls all GUI elements for the globe application"""

    def __init__(self, globeApp: IGlobeApplication):
        self.__globeApp: IGlobeApplication = globeApp
        self.__logMessages: List[str] = []
        self.__allButtons: List[DirectButton] = []
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__logDisplay: Optional[OnscreenText] = None
        self.__challengeDisplay: Optional[OnscreenText] = None
        self.__debugDisplay: Optional[OnscreenText] = None
        self.__challengeMaxLines: int = self.__settings.getChallengeTextSettings()[ "max_lines" ]

        # Button references for effects
        self.__incrementPlusBtn: Optional[DirectButton] = None
        self.__incrementMinusBtn: Optional[DirectButton] = None
        self.__zoomInBtn: Optional[DirectButton] = None
        self.__zoomOutBtn: Optional[DirectButton] = None
        self.__resetBtn: Optional[DirectButton] = None
        self.__rotateUpBtn: Optional[DirectButton] = None
        self.__rotateDownBtn: Optional[DirectButton] = None
        self.__rotateLeftBtn: Optional[DirectButton] = None
        self.__rotateRightBtn: Optional[DirectButton] = None

        # Game-related buttons
        self.__startGameBtn: Optional[DirectButton] = None
        self.__nextChallengeBtn: Optional[DirectButton] = None
        self.__gameStatsBtn: Optional[DirectButton] = None

        # Continent radius controls
        self.__radiusPlusBtn: Optional[DirectButton] = None
        self.__radiusMinusBtn: Optional[DirectButton] = None
        self.__radiusDisplay: Optional[OnscreenText] = None

        self.__createGuiControls()

    def __createGuiControls(self) -> None:
        """Create all GUI buttons and controls"""
        # Rotation Step controls (top-left corner) — label + +/- buttons
        DirectButton(
            text="STEP",
            pos=self.__settings.getButtonPosition( "increment", "label_position" ),
            scale=self.__settings.getButtonScale( "increment" ),
            frameColor=self.__settings.getButtonColor( "label", "background" ),
            text_fg=self.__settings.getButtonColor( "label", "text" ),
            relief=0
        )

        self.__incrementPlusBtn = DirectButton(
            text="+",
            pos=self.__settings.getButtonPosition("increment", "plus_position"),
            scale=self.__settings.getButtonScale("increment"),
            command=self.__onIncreaseRotationIncrement,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        self.__incrementMinusBtn = DirectButton(
            text="-",
            pos=self.__settings.getButtonPosition("increment", "minus_position"),
            scale=self.__settings.getButtonScale("increment"),
            command=self.__onDecreaseRotationIncrement,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        # Zoom controls label
        DirectButton(
            text=self.__settings.getTextContent("zoom_label"),
            pos=self.__settings.getButtonPosition("zoom", "label_position"),
            scale=self.__settings.getButtonScale("zoom"),
            frameColor=self.__settings.getButtonColor("label", "background"),
            text_fg=self.__settings.getButtonColor("label", "text"),
            relief=0
        )

        self.__zoomInBtn = DirectButton(
            text="IN",
            pos=self.__settings.getButtonPosition("zoom", "in_position"),
            scale=self.__settings.getButtonScale("zoom"),
            command=self.__onZoomIn,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        self.__zoomOutBtn = DirectButton(
            text="OUT",
            pos=self.__settings.getButtonPosition("zoom", "out_position"),
            scale=self.__settings.getButtonScale("zoom"),
            command=self.__onZoomOut,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        # Reset View button
        self.__resetBtn = DirectButton(
            text="RESET VIEW",
            pos=self.__settings.getButtonPosition("reset", "position"),
            scale=self.__settings.getButtonScale("reset"),
            command=self.__onResetView,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        # Directional rotation buttons at screen edges
        self.__rotateUpBtn = DirectButton(
            text="UP",
            pos=self.__settings.getButtonPosition("rotation", "up_position"),
            scale=self.__settings.getButtonScale("rotation"),
            command=self.__onRotateUp,
            frameColor=self.__settings.getButtonColor("rotation", "background"),
            text_fg=self.__settings.getButtonColor("rotation", "text"),
            pressEffect=1, relief=2
        )

        self.__rotateDownBtn = DirectButton(
            text="DOWN",
            pos=self.__settings.getButtonPosition("rotation", "down_position"),
            scale=self.__settings.getButtonScale("rotation"),
            command=self.__onRotateDown,
            frameColor=self.__settings.getButtonColor("rotation", "background"),
            text_fg=self.__settings.getButtonColor("rotation", "text"),
            pressEffect=1, relief=2
        )

        self.__rotateLeftBtn = DirectButton(
            text="LEFT",
            pos=self.__settings.getButtonPosition("rotation", "left_position"),
            scale=self.__settings.getButtonScale("rotation"),
            command=self.__onRotateLeft,
            frameColor=self.__settings.getButtonColor("rotation", "background"),
            text_fg=self.__settings.getButtonColor("rotation", "text"),
            pressEffect=1, relief=2
        )

        self.__rotateRightBtn = DirectButton(
            text="RIGHT",
            pos=self.__settings.getButtonPosition("rotation", "right_position"),
            scale=self.__settings.getButtonScale("rotation"),
            command=self.__onRotateRight,
            frameColor=self.__settings.getButtonColor("rotation", "background"),
            text_fg=self.__settings.getButtonColor("rotation", "text"),
            pressEffect=1, relief=2
        )

        # Preset view buttons
        self.__createPresetButtons()
        
        # GeoChallenge Game buttons (right side of screen)
        self.__createGameControls()

        # Continent radius controls
        self.__createRadiusControls()

        # Store all buttons for dark gray click effect
        self.__allButtons = [
            self.__incrementMinusBtn, self.__incrementPlusBtn,
            self.__zoomInBtn, self.__zoomOutBtn, self.__resetBtn,
            self.__rotateUpBtn, self.__rotateDownBtn,
            self.__rotateLeftBtn, self.__rotateRightBtn
        ]

        # Challenge label — bottom-left, pale yellow
        challengeSettings = self.__settings.getChallengeTextSettings()
        self.__challengeDisplay = OnscreenText(
            text="",
            pos=challengeSettings[ "pos" ],
            scale=challengeSettings[ "scale" ],
            fg=self.__settings.getTextColor( "challenge" ),
            wordwrap=challengeSettings[ "wordwrap" ],
            align=TextNode.ALeft
        )

        # Debug label — bottom-right, gray
        debugSettings = self.__settings.getDebugTextSettings()
        self.__debugDisplay = OnscreenText(
            text="",
            pos=debugSettings[ "pos" ],
            scale=debugSettings[ "scale" ],
            fg=self.__settings.getTextColor( "debug" ),
            wordwrap=debugSettings[ "wordwrap" ],
            align=TextNode.ALeft
        )

    def __createPresetButtons(self) -> None:
        """Create preset view buttons for different regions (currently hidden)"""
        presetLabels = self.__settings.getPresetLabels()
        presetPositions = self.__settings.getPresetPositions()
        presetScale = self.__settings.getButtonScale("presets")

        for index, (label, position) in enumerate(zip(presetLabels, presetPositions)):
            btn = DirectButton(
                text=label,
                pos=position,
                scale=presetScale,
                command=lambda i=index: self.__onSetPresetView(i),
                frameColor=self.__settings.getButtonColor("preset", "background"),
                text_fg=self.__settings.getButtonColor("preset", "text"),
                pressEffect=1, relief=2
            )
            btn.hide()
            self.__allButtons.append(btn)

    def __createGameControls(self) -> None:
        """Create buttons for GeoChallenge game controls"""
        # Start Game button
        self.__startGameBtn = DirectButton(
            text=self.__settings.getTextContent("start_game"),
            pos=self.__settings.getButtonPosition("game", "start_position"),
            scale=self.__settings.getButtonScale("game"),
            command=self.__onStartGame,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        # Next Challenge button - hidden until question is answered
        self.__nextChallengeBtn = DirectButton(
            text=self.__settings.getTextContent("next_challenge"),
            pos=self.__settings.getButtonPosition("game", "next_position"),
            scale=self.__settings.getButtonScale("game"),
            command=self.__onNextChallenge,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )
        self.__nextChallengeBtn.hide()

        # Get Hint button
        self.__gameStatsBtn = DirectButton(
            text=self.__settings.getTextContent("game_stats"),
            pos=self.__settings.getButtonPosition("game", "stats_position"),
            scale=self.__settings.getButtonScale("game"),
            command=self.__onGameStats,
            frameColor=self.__settings.getButtonColor("control", "background"),
            text_fg=self.__settings.getButtonColor("control", "text"),
            pressEffect=1, relief=2
        )

        self.__allButtons.extend([
            self.__startGameBtn, self.__nextChallengeBtn,
            self.__gameStatsBtn
        ])

    def __createRadiusControls( self ) -> None:
        """Create buttons and value display for continent radius adjustment (hidden)"""
        # Label
        radiusLabel = DirectButton(
            text="RADIUS",
            pos=( -0.75, 0, 0.58 ),
            scale=0.04,
            frameColor=self.__settings.getButtonColor( "label", "background" ),
            text_fg=self.__settings.getButtonColor( "label", "text" ),
            relief=0
        )
        radiusLabel.hide()

        self.__radiusPlusBtn = DirectButton(
            text="+",
            pos=( -0.57, 0, 0.58 ),
            scale=0.04,
            command=self.__onIncreaseRadius,
            frameColor=self.__settings.getButtonColor( "increment", "background" ),
            text_fg=self.__settings.getButtonColor( "increment", "text" ),
            pressEffect=1, relief=2
        )
        self.__radiusPlusBtn.hide()

        self.__radiusMinusBtn = DirectButton(
            text="-",
            pos=( -0.90, 0, 0.58 ),
            scale=0.04,
            command=self.__onDecreaseRadius,
            frameColor=self.__settings.getButtonColor( "increment", "background" ),
            text_fg=self.__settings.getButtonColor( "increment", "text" ),
            pressEffect=1, relief=2
        )
        self.__radiusMinusBtn.hide()

        self.__radiusDisplay = OnscreenText(
            text=f"{self.__globeApp.continentRadius:.2f}",
            pos=( -0.75, 0.50 ),
            scale=0.04,
            fg=( 1.0, 1.0, 1.0, 1.0 ),
            align=TextNode.ACenter
        )
        self.__radiusDisplay.hide()

        self.__allButtons.extend( [ self.__radiusPlusBtn, self.__radiusMinusBtn ] )

    def __applyButtonEffect(self, button: DirectButton) -> None:
        """Apply dark gray effect to button when clicked"""
        originalColor = button['frameColor']
        pressedColor = self.__settings.getButtonColor("control", "pressed")
        button['frameColor'] = pressedColor

        def resetColor(task) -> int:
            button['frameColor'] = originalColor
            return task.done

        effectDuration = self.__settings.getEffectDuration()
        self.__globeApp.taskManager.doMethodLater(effectDuration, resetColor, f"reset_button_{id(button)}")

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
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.show()

    def disableNextChallenge( self ) -> None:
        """Hide the Next Challenge button until question is answered"""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.hide()

    # Event handlers - delegate to globe app
    def __onZoomIn(self) -> None:
        self.__applyButtonEffect(self.__zoomInBtn)
        self.__globeApp.zoomIn()

    def __onZoomOut(self) -> None:
        self.__applyButtonEffect(self.__zoomOutBtn)
        self.__globeApp.zoomOut()

    def __onResetView(self) -> None:
        self.__applyButtonEffect(self.__resetBtn)
        self.__globeApp.resetView()

    def __onRotateUp(self) -> None:
        self.__applyButtonEffect(self.__rotateUpBtn)
        self.__globeApp.rotateUp()

    def __onRotateDown(self) -> None:
        self.__applyButtonEffect(self.__rotateDownBtn)
        self.__globeApp.rotateDown()

    def __onRotateLeft(self) -> None:
        self.__applyButtonEffect(self.__rotateLeftBtn)
        self.__globeApp.rotateLeft()

    def __onRotateRight(self) -> None:
        self.__applyButtonEffect(self.__rotateRightBtn)
        self.__globeApp.rotateRight()

    def __onIncreaseRotationIncrement(self) -> None:
        self.__applyButtonEffect(self.__incrementPlusBtn)
        self.__globeApp.increaseRotationIncrement()

    def __onDecreaseRotationIncrement(self) -> None:
        self.__applyButtonEffect(self.__incrementMinusBtn)
        self.__globeApp.decreaseRotationIncrement()

    def __onSetPresetView(self, index: int) -> None:
        buttons = self.__allButtons[-6:]  # Last 6 are preset buttons
        if 0 <= index < len(buttons):
            self.__applyButtonEffect(buttons[index])
        self.__globeApp.setPresetView(index)

    def __onStartGame(self) -> None:
        self.__applyButtonEffect(self.__startGameBtn)
        self.__globeApp.startGame()

    def __onNextChallenge(self) -> None:
        self.__applyButtonEffect(self.__nextChallengeBtn)
        self.__globeApp.nextChallenge()


    def __onGameStats(self) -> None:
        self.__applyButtonEffect(self.__gameStatsBtn)
        self.__globeApp.showGameStats()

    def __onIncreaseRadius( self ) -> None:
        self.__applyButtonEffect( self.__radiusPlusBtn )
        self.__globeApp.increaseContinentRadius()

    def __onDecreaseRadius( self ) -> None:
        self.__applyButtonEffect( self.__radiusMinusBtn )
        self.__globeApp.decreaseContinentRadius()

