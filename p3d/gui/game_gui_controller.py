"""
Game GUI Controller - Creates and manages all game-related GUI elements.
Challenge text display, Start Game, Next Question and Stats buttons.
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import TextNode
from typing import Callable, Optional

from settings.gui_settings_manager import GuiSettingsManager


class GameGuiController:
    """Owns all game-related GUI elements — buttons and challenge text."""

    def __init__(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable,
        taskManager,
    ):
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__taskManager = taskManager
        self.__challengeMaxLines: int = self.__settings.getChallengeTextSettings()[ "max_lines" ]

        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__gameStatsBtn: Optional[ DirectButton ] = None
        self.__challengeDisplay: Optional[ OnscreenText ] = None

        self.__buildButtons( onStartGame, onNextChallenge, onGameStats )
        self.__buildChallengeDisplay()

    # ── Build ─────────────────────────────────────────────────────────────────

    def __buildButtons(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable,
    ) -> None:
        self.__startGameBtn = DirectButton(
            text = self.__settings.getTextContent( "start_game" ),
            pos = self.__settings.getButtonPosition( "game", "start_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__startGameBtn ), onStartGame() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )

        self.__nextChallengeBtn = DirectButton(
            text = self.__settings.getTextContent( "next_challenge" ),
            pos = self.__settings.getButtonPosition( "game", "next_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__nextChallengeBtn ), onNextChallenge() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )
        self.__nextChallengeBtn.hide()

        self.__gameStatsBtn = DirectButton(
            text = self.__settings.getTextContent( "game_stats" ),
            pos = self.__settings.getButtonPosition( "game", "stats_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__gameStatsBtn ), onGameStats() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )

    def __buildChallengeDisplay( self ) -> None:
        challengeSettings = self.__settings.getChallengeTextSettings()
        self.__challengeDisplay = OnscreenText(
            text = "",
            pos = challengeSettings[ "pos" ],
            scale = challengeSettings[ "scale" ],
            fg = self.__settings.getTextColor( "challenge" ),
            wordwrap = challengeSettings[ "wordwrap" ],
            align = TextNode.ALeft
        )

    def __applyButtonEffect( self, button: DirectButton ) -> None:
        """Flash button darker when clicked."""
        originalColor = button[ 'frameColor' ]
        pressedColor = self.__settings.getButtonColor( "control", "pressed" )
        button[ 'frameColor' ] = pressedColor

        def resetColor( task ) -> int:
            button[ 'frameColor' ] = originalColor
            return task.done

        self.__taskManager.doMethodLater(
            self.__settings.getEffectDuration(),
            resetColor,
            f"reset_game_btn_{id( button )}"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def clearChallengeText( self ) -> None:
        """Clear the challenge display."""
        if self.__challengeDisplay:
            self.__challengeDisplay.setText( "" )

    def setChallengeText( self, message: str ) -> None:
        """Set the challenge display text, capped to max lines."""
        if not self.__challengeDisplay:
            return
        lines = message.splitlines()
        truncated = "\n".join( lines[ :self.__challengeMaxLines ] )
        self.__challengeDisplay.setText( truncated )

    def showNextChallengeButton( self ) -> None:
        """Show the Next Question button once a question has been answered."""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.show()

    def hideNextChallengeButton( self ) -> None:
        """Hide the Next Question button."""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.hide()

        self.__settings: GuiSettingsManager = settings
        self.__onButtonEffect: Callable[ [ DirectButton ], None ] = onButtonEffect
        self.__challengeMaxLines: int = settings.getChallengeTextSettings()[ "max_lines" ]

        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__gameStatsBtn: Optional[ DirectButton ] = None
        self.__challengeDisplay: Optional[ OnscreenText ] = None

        self.__buildButtons( onStartGame, onNextChallenge, onGameStats )
        self.__buildChallengeDisplay()

    # ── Build ─────────────────────────────────────────────────────────────────

    def __buildButtons(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable,
    ) -> None:
        self.__startGameBtn = DirectButton(
            text = self.__settings.getTextContent( "start_game" ),
            pos = self.__settings.getButtonPosition( "game", "start_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__onButtonEffect( self.__startGameBtn ), onStartGame() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )

        self.__nextChallengeBtn = DirectButton(
            text = self.__settings.getTextContent( "next_challenge" ),
            pos = self.__settings.getButtonPosition( "game", "next_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__onButtonEffect( self.__nextChallengeBtn ), onNextChallenge() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )
        self.__nextChallengeBtn.hide()

        self.__gameStatsBtn = DirectButton(
            text = self.__settings.getTextContent( "game_stats" ),
            pos = self.__settings.getButtonPosition( "game", "stats_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__onButtonEffect( self.__gameStatsBtn ), onGameStats() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )

    def __buildChallengeDisplay( self ) -> None:
        challengeSettings = self.__settings.getChallengeTextSettings()
        self.__challengeDisplay = OnscreenText(
            text = "",
            pos = challengeSettings[ "pos" ],
            scale = challengeSettings[ "scale" ],
            fg = self.__settings.getTextColor( "challenge" ),
            wordwrap = challengeSettings[ "wordwrap" ],
            align = TextNode.ALeft
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def clearChallengeText( self ) -> None:
        """Clear the challenge display."""
        if self.__challengeDisplay:
            self.__challengeDisplay.setText( "" )

    def setChallengeText( self, message: str ) -> None:
        """Set the challenge display text, capped to max lines."""
        if not self.__challengeDisplay:
            return
        lines = message.splitlines()
        truncated = "\n".join( lines[ :self.__challengeMaxLines ] )
        self.__challengeDisplay.setText( truncated )

    def showNextChallengeButton( self ) -> None:
        """Show the Next Question button once a question has been answered."""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.show()

    def hideNextChallengeButton( self ) -> None:
        """Hide the Next Question button."""
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.hide()

