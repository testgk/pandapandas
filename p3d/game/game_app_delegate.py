"""
Game App Delegate - bridges RealGlobeApplication and GameController/GameGuiController.
Owns the game entry points that the GUI buttons call into.
"""
from .game_controller import GameController
from ..gui.game_gui_controller import GameGuiController


class GameAppDelegate:
    """
    Owns the game entry-point methods so RealGlobeApplication
    stays free of any game-specific logic.
    """

    def __init__( self, gameController: GameController, gameGui: GameGuiController ):
        self.__gameController: GameController = gameController
        self.__gameGui: GameGuiController = gameGui

    def startGame( self ) -> None:
        self.__gameController.startGame()
        self.__gameGui.showEndGameButton()

    def endGame( self ) -> None:
        self.__gameController.endGame()

    def nextChallenge( self ) -> None:
        self.__gameController.nextChallenge()

    def showGameStats( self ) -> None:
        self.__gameController.showStats()

    def showDbStats( self ) -> None:
        self.__gameController.showDbStats()

    def showHint( self ) -> None:
        """Show text hint (-10% score penalty)."""
        self.__gameController.showHint()

    def showCountry( self ) -> None:
        """Show country (-20% score penalty)."""
        self.__gameController.showCountry()

    def onHelpMe( self ) -> None:
        """Camera closeup hint (-50% score penalty)."""
        self.__gameController.onHelpMe()

    def updateScores( self ) -> None:
        """Update scores to database."""
        # TODO: Implement database score update
        pass

    # Legacy compatibility
    def onHint( self ) -> None:
        self.onHelpMe()

