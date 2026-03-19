"""
Game GUI Controller - Creates and manages all game-related GUI elements.
Challenge text display, Start Game, Next Question, Stats, End Game,
Submit Scores / No Thanks buttons, and menu integration.
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton, DirectFrame
from panda3d.core import TextNode
from typing import Callable, Optional

from settings.gui_settings_manager import GuiSettingsManager


class GameGuiController:
    """Owns all game-related GUI elements — buttons, menu and challenge text."""

    def __init__(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable,
        onHint: Callable,
        taskManager,
        onDbStats: Callable = None,
        onEndGame: Callable = None,
        onSubmitScores: Callable = None,
        onSignIn: Callable = None,
        onSignOut: Callable = None,
        onSignUp: Callable = None,
        getCurrentUsers: Callable = None,
        userEmail: str = None,
    ):
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__taskManager = taskManager
        self.__challengeMaxLines: int = self.__settings.getChallengeTextSettings()[ "max_lines" ]

        # Callbacks
        self.__onStartGame = onStartGame
        self.__onEndGame = onEndGame
        self.__onSubmitScores = onSubmitScores
        self.__onSignIn = onSignIn
        self.__onSignOut = onSignOut
        self.__onSignUp = onSignUp
        self.__getCurrentUsers = getCurrentUsers
        self.__userEmail = userEmail

        # Button references
        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__gameStatsBtn: Optional[ DirectButton ] = None
        self.__dbStatsBtn: Optional[ DirectButton ] = None
        self.__hintBtn: Optional[ DirectButton ] = None
        self.__endGameBtn: Optional[ DirectButton ] = None
        self.__returnToGameBtn: Optional[ DirectButton ] = None
        self.__submitScoresBtn: Optional[ DirectButton ] = None
        self.__noThanksBtn: Optional[ DirectButton ] = None
        self.__menuBtn: Optional[ DirectButton ] = None
        self.__challengeDisplay: Optional[ OnscreenText ] = None

        # Menu state
        self.__menuFrame: Optional[ DirectFrame ] = None
        self.__menuVisible: bool = False
        self.__isSignedIn: bool = False

        # Menu button references
        self.__menuStartBtn: Optional[ DirectButton ] = None
        self.__menuTopScoresBtn: Optional[ DirectButton ] = None
        self.__menuSignInBtn: Optional[ DirectButton ] = None
        self.__menuSignOutBtn: Optional[ DirectButton ] = None
        self.__menuSignUpBtn: Optional[ DirectButton ] = None
        self.__currentUsersBtn: Optional[ DirectButton ] = None

        self.__buildButtons( onStartGame, onNextChallenge, onGameStats, onHint, onDbStats )
        self.__buildMenu()
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
            command = self.__onStartGameClicked,
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

        # End Game button (visible during active game)
        self.__endGameBtn = DirectButton(
            text = "End Game",
            pos = ( 0.7, 0, 0.8 ),
            scale = self.__settings.getButtonScale( "game" ),
            command = self.__onEndGameClicked,
            frameColor = ( 0.7, 0.2, 0.2, 1 ),
            text_fg = ( 1, 1, 1, 1 ),
            pressEffect = 1, relief = 2
        )
        self.__endGameBtn.hide()

        # Return to Game button (visible after End Game clicked)
        self.__returnToGameBtn = DirectButton(
            text = "Return to Game",
            pos = ( 0.7, 0, 0.7 ),
            scale = self.__settings.getButtonScale( "game" ),
            command = self.__onReturnToGameClicked,
            frameColor = ( 0.2, 0.5, 0.7, 1 ),
            text_fg = ( 1, 1, 1, 1 ),
            pressEffect = 1, relief = 2
        )
        self.__returnToGameBtn.hide()

        # Submit Scores button
        self.__submitScoresBtn = DirectButton(
            text = "Submit Scores",
            pos = ( 0.7, 0, 0.6 ),
            scale = self.__settings.getButtonScale( "game" ),
            command = self.__onSubmitScoresClicked,
            frameColor = ( 0.2, 0.7, 0.2, 1 ),
            text_fg = ( 1, 1, 1, 1 ),
            pressEffect = 1, relief = 2
        )
        self.__submitScoresBtn.hide()

        # No Thanks button
        self.__noThanksBtn = DirectButton(
            text = "No Thanks",
            pos = ( 0.7, 0, 0.5 ),
            scale = self.__settings.getButtonScale( "game" ),
            command = self.__onNoThanksClicked,
            frameColor = ( 0.5, 0.5, 0.5, 1 ),
            text_fg = ( 1, 1, 1, 1 ),
            pressEffect = 1, relief = 2
        )
        self.__noThanksBtn.hide()

        # Menu button (top right)
        self.__menuBtn = DirectButton(
            text = self.__settings.getTextContent( "menu" ),
            pos = self.__settings.getButtonPosition( "game", "menu_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = self.__toggleMenu,
            frameColor = self.__settings.getButtonColor( "game", "background" ),
            text_fg = self.__settings.getButtonColor( "game", "text" ),
            pressEffect = 1, relief = 2
        )

    def __buildMenu( self ) -> None:
        """Build the dropdown menu with Start, Top Scores, Sign In/Out/Up."""
        menuScale = self.__settings.getButtonScale( "menu" ) if hasattr( self.__settings, 'getButtonScale' ) else 0.030

        self.__menuFrame = DirectFrame(
            frameColor = ( 0.1, 0.1, 0.2, 0.9 ),
            frameSize = ( -0.25, 0.25, -0.55, 0.05 ),
            pos = self.__settings.getButtonPosition( "menu", "frame_position" ),
        )
        self.__menuFrame.hide()

        # Menu Start button
        self.__menuStartBtn = DirectButton(
            text = self.__settings.getTextContent( "menu_start" ),
            pos = ( 0, 0, -0.05 ),
            scale = menuScale,
            command = self.__onMenuStart,
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            parent = self.__menuFrame,
            pressEffect = 1, relief = 2
        )

        # Menu Top Scores button
        self.__menuTopScoresBtn = DirectButton(
            text = self.__settings.getTextContent( "menu_top_scores" ),
            pos = ( 0, 0, -0.15 ),
            scale = menuScale,
            command = self.__onMenuTopScores,
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            parent = self.__menuFrame,
            pressEffect = 1, relief = 2
        )

        # Sign In button (shown when not signed in)
        self.__menuSignInBtn = DirectButton(
            text = self.__settings.getTextContent( "menu_signin" ),
            pos = ( 0, 0, -0.25 ),
            scale = menuScale,
            command = self.__onMenuSignIn,
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            parent = self.__menuFrame,
            pressEffect = 1, relief = 2
        )

        # Sign Up button (shown when not signed in)
        self.__menuSignUpBtn = DirectButton(
            text = self.__settings.getTextContent( "menu_signup" ),
            pos = ( 0, 0, -0.35 ),
            scale = menuScale,
            command = self.__onMenuSignUp,
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            parent = self.__menuFrame,
            pressEffect = 1, relief = 2
        )

        # Sign Out button (shown when signed in)
        self.__menuSignOutBtn = DirectButton(
            text = self.__settings.getTextContent( "menu_signout" ),
            pos = ( 0, 0, -0.25 ),
            scale = menuScale,
            command = self.__onMenuSignOut,
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            parent = self.__menuFrame,
            pressEffect = 1, relief = 2
        )
        self.__menuSignOutBtn.hide()

        # Current Users button (visible only for gdkln@yahoo.com)
        if self.__userEmail == "gdkln@yahoo.com" and self.__getCurrentUsers:
            self.__currentUsersBtn = DirectButton(
                text = "Current Users",
                pos = ( 0, 0, -0.45 ),
                scale = menuScale,
                command = self.__onShowCurrentUsers,
                frameColor = self.__settings.getButtonColor( "control", "background" ),
                text_fg = self.__settings.getButtonColor( "control", "text" ),
                parent = self.__menuFrame,
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
        if not button:
            return
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

    # ── Button click handlers ─────────────────────────────────────────────────

    def __onStartGameClicked( self ) -> None:
        """Start Game button: require sign-in."""
        self.__applyButtonEffect( self.__startGameBtn )
        if not self.__isSignedIn:
            self.setChallengeText( "You must sign in to play." )
            return
        if self.__onStartGame:
            self.__onStartGame()

    def __onEndGameClicked( self ) -> None:
        """End Game: show Submit Scores / No Thanks and Return to Game."""
        self.__applyButtonEffect( self.__endGameBtn )
        if self.__endGameBtn: self.__endGameBtn.hide()
        if self.__returnToGameBtn: self.__returnToGameBtn.show()
        if self.__submitScoresBtn: self.__submitScoresBtn.show()
        if self.__noThanksBtn: self.__noThanksBtn.show()
        self.hideNextChallengeButton()
        self.hideHintButton()
        self.setChallengeText( "Game ended.\nSubmit your scores?" )
        if self.__onEndGame:
            self.__onEndGame()

    def __onReturnToGameClicked( self ) -> None:
        """Return to Game: hide end-game buttons, resume."""
        self.__applyButtonEffect( self.__returnToGameBtn )
        if self.__returnToGameBtn: self.__returnToGameBtn.hide()
        if self.__submitScoresBtn: self.__submitScoresBtn.hide()
        if self.__noThanksBtn: self.__noThanksBtn.hide()
        if self.__endGameBtn: self.__endGameBtn.show()
        self.clearChallengeText()

    def __onSubmitScoresClicked( self ) -> None:
        """Submit Scores: submit and return to main."""
        self.__applyButtonEffect( self.__submitScoresBtn )
        if self.__onSubmitScores:
            self.__onSubmitScores()
        self.__exitToMainDisplay()

    def __onNoThanksClicked( self ) -> None:
        """No Thanks: exit to main display, hide all game buttons, close menu."""
        self.__applyButtonEffect( self.__noThanksBtn )
        self.__exitToMainDisplay()

    def __exitToMainDisplay( self ) -> None:
        """Return to clean main display: hide all game/end buttons, clear text, close menu."""
        if self.__endGameBtn: self.__endGameBtn.hide()
        if self.__returnToGameBtn: self.__returnToGameBtn.hide()
        if self.__submitScoresBtn: self.__submitScoresBtn.hide()
        if self.__noThanksBtn: self.__noThanksBtn.hide()
        if self.__nextChallengeBtn: self.__nextChallengeBtn.hide()
        if self.__hintBtn: self.__hintBtn.hide()
        # Show main buttons (Start Game, Stats)
        if self.__startGameBtn: self.__startGameBtn.show()
        if self.__gameStatsBtn: self.__gameStatsBtn.show()
        self.clearChallengeText()
        self.__hideMenu()

    # ── Menu callbacks ────────────────────────────────────────────────────────

    def __toggleMenu( self ) -> None:
        self.__applyButtonEffect( self.__menuBtn )
        if self.__menuVisible:
            self.__menuFrame.hide()
            self.__menuVisible = False
        else:
            self.__menuFrame.show()
            self.__menuVisible = True

    def __hideMenu( self ) -> None:
        if self.__menuFrame:
            self.__menuFrame.hide()
            self.__menuVisible = False

    def __onMenuStart( self ) -> None:
        self.__hideMenu()
        if not self.__isSignedIn:
            self.setChallengeText( "You must sign in to play." )
            return
        if self.__onStartGame:
            self.__onStartGame()

    def __onMenuTopScores( self ) -> None:
        self.__hideMenu()

    def __onMenuSignIn( self ) -> None:
        self.__hideMenu()
        if self.__onSignIn:
            self.__onSignIn()

    def __onMenuSignOut( self ) -> None:
        self.__hideMenu()
        if self.__onSignOut:
            self.__onSignOut()
        self.setSignedIn( False )

    def __onMenuSignUp( self ) -> None:
        self.__hideMenu()
        if self.__onSignUp:
            self.__onSignUp()

    def __onShowCurrentUsers( self ) -> None:
        self.__hideMenu()
        if self.__getCurrentUsers:
            users = self.__getCurrentUsers()
            msg = "Current users playing:\n" + "\n".join( users ) if users else "No users online."
            self.setChallengeText( msg )

    # ── Public API ────────────────────────────────────────────────────────────

    def setSignedIn( self, signedIn: bool ) -> None:
        """Update menu and game UI for sign-in state."""
        self.__isSignedIn = signedIn
        if signedIn:
            if self.__menuSignInBtn: self.__menuSignInBtn.hide()
            if self.__menuSignUpBtn: self.__menuSignUpBtn.hide()
            if self.__menuSignOutBtn: self.__menuSignOutBtn.show()
            if self.__startGameBtn: self.__startGameBtn.show()
            if self.__gameStatsBtn: self.__gameStatsBtn.show()
            if self.__menuBtn: self.__menuBtn.show()
        else:
            if self.__menuSignInBtn: self.__menuSignInBtn.show()
            if self.__menuSignUpBtn: self.__menuSignUpBtn.show()
            if self.__menuSignOutBtn: self.__menuSignOutBtn.hide()
            # Hide all game-related buttons and clear challenge text
            if self.__startGameBtn: self.__startGameBtn.hide()
            if self.__nextChallengeBtn: self.__nextChallengeBtn.hide()
            if self.__gameStatsBtn: self.__gameStatsBtn.hide()
            if self.__dbStatsBtn: self.__dbStatsBtn.hide()
            if self.__hintBtn: self.__hintBtn.hide()
            if self.__endGameBtn: self.__endGameBtn.hide()
            if self.__returnToGameBtn: self.__returnToGameBtn.hide()
            if self.__submitScoresBtn: self.__submitScoresBtn.hide()
            if self.__noThanksBtn: self.__noThanksBtn.hide()
            if self.__menuBtn: self.__menuBtn.hide()
            self.clearChallengeText()

    def clearChallengeText( self ) -> None:
        if self.__challengeDisplay:
            self.__challengeDisplay.setText( "" )

    def setChallengeText( self, message: str ) -> None:
        if not self.__challengeDisplay:
            return
        lines = message.splitlines()
        truncated = "\n".join( lines[ :self.__challengeMaxLines ] )
        self.__challengeDisplay.setText( truncated )

    def showNextChallengeButton( self ) -> None:
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.show()

    def hideNextChallengeButton( self ) -> None:
        if self.__nextChallengeBtn:
            self.__nextChallengeBtn.hide()

    def showHintButton( self ) -> None:
        if self.__hintBtn:
            self.__hintBtn.show()

    def hideHintButton( self ) -> None:
        if self.__hintBtn:
            self.__hintBtn.hide()

    def showEndGameButton( self ) -> None:
        """Show End Game button when a game is active."""
        if self.__endGameBtn:
            self.__endGameBtn.show()

    def hideEndGameButton( self ) -> None:
        if self.__endGameBtn:
            self.__endGameBtn.hide()

