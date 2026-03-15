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
        onHint: Callable,
        taskManager,
        onDbStats: Callable = None,
    ):
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__taskManager = taskManager
        self.__challengeMaxLines: int = self.__settings.getChallengeTextSettings()[ "max_lines" ]

        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__gameStatsBtn: Optional[ DirectButton ] = None
        self.__dbStatsBtn: Optional[ DirectButton ] = None
        self.__hintBtn: Optional[ DirectButton ] = None
        self.__challengeDisplay: Optional[ OnscreenText ] = None

        self.__buildButtons( onStartGame, onNextChallenge, onGameStats, onHint, onDbStats )
        self.__buildChallengeDisplay()

    # ── Build ─────────────────────────────────────────────────────────────────

    def __buildButtons(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable,
        onHint: Callable,
        onDbStats: Callable = None,
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

        if onDbStats:
            self.__dbStatsBtn = DirectButton(
                text = self.__settings.getTextContent( "db_stats" ),
                pos = self.__settings.getButtonPosition( "game", "db_stats_position" ),
                scale = self.__settings.getButtonScale( "game" ),
                command = lambda: ( self.__applyButtonEffect( self.__dbStatsBtn ), onDbStats() ),
                frameColor = self.__settings.getButtonColor( "control", "background" ),
                text_fg = self.__settings.getButtonColor( "control", "text" ),
                pressEffect = 1, relief = 2
            )

        self.__hintBtn = DirectButton(
            text = self.__settings.getTextContent( "hint" ),
            pos = self.__settings.getButtonPosition( "game", "hint_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__hintBtn ), onHint() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )
        self.__hintBtn.hide()

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

    def showHintButton( self ) -> None:
        """Show the Hint button during an active challenge."""
        if self.__hintBtn:
            self.__hintBtn.show()

    def hideHintButton( self ) -> None:
        """Hide the Hint button."""
        if self.__hintBtn:
            self.__hintBtn.hide()

