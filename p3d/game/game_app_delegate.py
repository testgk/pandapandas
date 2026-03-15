"""
Game App Delegate - bridges RealGlobeApplication and GameController/GameGuiController.
Owns the three game entry points that the GUI buttons call into.
"""
from game.game_controller import GameController
from gui.game_gui_controller import GameGuiController


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

    def nextChallenge( self ) -> None:
        self.__gameController.nextChallenge()

    def showGameStats( self ) -> None:
        self.__gameController.showStats()

    def showDbStats( self ) -> None:
        self.__gameController.showDbStats()

    def onHint( self ) -> None:
        self.__gameController.onHint()

