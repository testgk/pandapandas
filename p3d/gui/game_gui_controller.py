"""
Game GUI Controller - Creates and manages all game-related GUI elements.
Challenge text display, Start Game, Next Question, Stats, Menu and Hint buttons.
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
        onShowCountry: Callable,
        onShowHint: Callable,
        onHelpMe: Callable,
        taskManager,
        onDbStats: Callable = None,
        onUpdateScores: Callable = None,
        onSignIn: Callable = None,
        onSignOut: Callable = None,
        onSignUp: Callable = None,
        getCurrentUsers: Callable = None,
        userEmail: str = None,
    ):
        self.__settings: GuiSettingsManager = GuiSettingsManager()
        self.__taskManager = taskManager
        self.__challengeMaxLines: int = self.__settings.getChallengeTextSettings()[ "max_lines" ]

        # Button references
        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__gameStatsBtn: Optional[ DirectButton ] = None
        self.__dbStatsBtn: Optional[ DirectButton ] = None
        self.__updateScoresBtn: Optional[ DirectButton ] = None
        self.__showCountryBtn: Optional[ DirectButton ] = None
        self.__hintBtn: Optional[ DirectButton ] = None
        self.__helpMeBtn: Optional[ DirectButton ] = None
        self.__menuBtn: Optional[ DirectButton ] = None
        self.__challengeDisplay: Optional[ OnscreenText ] = None

        # Menu state
        self.__menuFrame: Optional[ DirectFrame ] = None
        self.__menuVisible: bool = False
        self.__isSignedIn: bool = False
        self.__userEmail: str = userEmail
        self.__getCurrentUsers: Callable = getCurrentUsers

        # Menu button references
        self.__menuStartBtn: Optional[ DirectButton ] = None
        self.__menuTopScoresBtn: Optional[ DirectButton ] = None
        self.__menuSignInBtn: Optional[ DirectButton ] = None
        self.__menuSignOutBtn: Optional[ DirectButton ] = None
        self.__menuSignUpBtn: Optional[ DirectButton ] = None

        # Store callbacks
        self.__onStartGame = onStartGame
        self.__onDbStats = onDbStats
        self.__onSignIn = onSignIn
        self.__onSignOut = onSignOut
        self.__onSignUp = onSignUp

        self.__buildButtons( onStartGame, onNextChallenge, onGameStats, onShowCountry, onShowHint, onHelpMe, onDbStats, onUpdateScores )
        self.__buildMenu()
        self.__buildChallengeDisplay()

    # ── Build ─────────────────────────────────────────────────────────────────

    def __buildButtons(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable,
        onShowCountry: Callable,
        onShowHint: Callable,
        onHelpMe: Callable,
        onDbStats: Callable = None,
        onUpdateScores: Callable = None,
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

        if onUpdateScores:
            self.__updateScoresBtn = DirectButton(
                text = self.__settings.getTextContent( "update_scores" ),
                pos = self.__settings.getButtonPosition( "game", "update_scores_position" ),
                scale = self.__settings.getButtonScale( "game" ),
                command = lambda: ( self.__applyButtonEffect( self.__updateScoresBtn ), onUpdateScores() ),
                frameColor = self.__settings.getButtonColor( "control", "background" ),
                text_fg = self.__settings.getButtonColor( "control", "text" ),
                pressEffect = 1, relief = 2
            )

        # Show Hint button (shows text hint, -10% score penalty)
        self.__hintBtn = DirectButton(
            text = self.__settings.getTextContent( "hint" ),
            pos = self.__settings.getButtonPosition( "game", "hint_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__hintBtn ), onShowHint() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )
        self.__hintBtn.hide()

        # Show Country button (reveals country, -20% score penalty)
        self.__showCountryBtn = DirectButton(
            text = self.__settings.getTextContent( "show_country" ),
            pos = self.__settings.getButtonPosition( "game", "show_country_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__showCountryBtn ), onShowCountry() ),
            frameColor = self.__settings.getButtonColor( "control", "background" ),
            text_fg = self.__settings.getButtonColor( "control", "text" ),
            pressEffect = 1, relief = 2
        )
        self.__showCountryBtn.hide()

        # Help Me button (camera closeup, -50% score penalty)
        self.__helpMeBtn = DirectButton(
            text = self.__settings.getTextContent( "help_me" ),
            pos = self.__settings.getButtonPosition( "game", "help_me_position" ),
            scale = self.__settings.getButtonScale( "game" ),
            command = lambda: ( self.__applyButtonEffect( self.__helpMeBtn ), onHelpMe() ),
            frameColor = self.__settings.getButtonColor( "game", "background" ),
            text_fg = self.__settings.getButtonColor( "game", "text" ),
            pressEffect = 1, relief = 2
        )
        self.__helpMeBtn.hide()

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

        # Menu frame background
        self.__menuFrame = DirectFrame(
            frameColor = ( 0.1, 0.1, 0.2, 0.9 ),
            frameSize = ( -0.25, 0.25, -0.45, 0.05 ),
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

        # Custom button for current users (visible only to gdkln@yahoo.com)
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
    def __onShowCurrentUsers(self):
        self.__hideMenu()
        if self.__getCurrentUsers:
            users = self.__getCurrentUsers()
            msg = "Current users playing:\n" + "\n".join(users) if users else "No users online."
            self.setChallengeText(msg)

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

    # ── Menu callbacks ────────────────────────────────────────────────────────

    def __toggleMenu( self ) -> None:
        """Toggle menu visibility."""
        self.__applyButtonEffect( self.__menuBtn )
        if self.__menuVisible:
            self.__menuFrame.hide()
            self.__menuVisible = False
        else:
            self.__menuFrame.show()
            self.__menuVisible = True

    def __hideMenu( self ) -> None:
        """Hide the menu."""
        if self.__menuFrame:
            self.__menuFrame.hide()
            self.__menuVisible = False

    def __onMenuStart( self ) -> None:
        """Handle menu Start button click."""
        self.__hideMenu()
        if not self.__isSignedIn:
            self.setChallengeText("You must sign in to play.")
            return
        if self.__onStartGame:
            self.__onStartGame()

    def __onMenuTopScores( self ) -> None:
        """Handle menu Top Scores button click."""
        self.__hideMenu()
        if self.__onDbStats:
            self.__onDbStats()

    def __onMenuSignIn( self ) -> None:
        """Handle menu Sign In button click."""
        self.__hideMenu()
        if self.__onSignIn:
            self.__onSignIn()

    def __onMenuSignOut( self ) -> None:
        """Handle menu Sign Out button click."""
        self.__hideMenu()
        if self.__onSignOut:
            self.__onSignOut()
        self.setSignedIn( False )

    def __onMenuSignUp( self ) -> None:
        """Handle menu Sign Up button click."""
        self.__hideMenu()
        if self.__onSignUp:
            self.__onSignUp()

    # ── Public API ────────────────────────────────────────────────────────────

    def setSignedIn( self, signedIn: bool ) -> None:
        """Update menu to show Sign Out when signed in, Sign In/Up when not."""
        self.__isSignedIn = signedIn
        if signedIn:
            self.__menuSignInBtn.hide()
            self.__menuSignUpBtn.hide()
            self.__menuSignOutBtn.show()
        else:
            self.__menuSignInBtn.show()
            self.__menuSignUpBtn.show()
            self.__menuSignOutBtn.hide()

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

    def showHintButtons( self ) -> None:
        """Show Country, Hint and Zoom In buttons during an active challenge."""
        if self.__showCountryBtn:
            self.__showCountryBtn.show()
        if self.__hintBtn:
            self.__hintBtn.show()
        if self.__helpMeBtn:
            self.__helpMeBtn.show()

    def hideHintButtons( self ) -> None:
        """Hide Country, Hint and Zoom In buttons."""
        if self.__showCountryBtn:
            self.__showCountryBtn.hide()
        if self.__hintBtn:
            self.__hintBtn.hide()
        if self.__helpMeBtn:
            self.__helpMeBtn.hide()

    # Legacy compatibility
    def showHintButton( self ) -> None:
        """Show both Hint and Help Me buttons."""
        self.showHintButtons()

    def hideHintButton( self ) -> None:
        """Hide both Hint and Help Me buttons."""
        self.hideHintButtons()

