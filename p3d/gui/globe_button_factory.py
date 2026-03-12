"""
Globe Button Factory - Creates and owns all DirectButton instances for the globe GUI
"""
from direct.gui.DirectGui import DirectButton, DGG
from panda3d.core import TextNode
from typing import List, Callable, Optional

from settings.gui_settings_manager import GuiSettingsManager


class GlobeButtonFactory:
    """Creates and holds all DirectButton instances for the globe GUI"""

    def __init__( self, settings: GuiSettingsManager ):
        self.__settings: GuiSettingsManager = settings

        self.__incrementPlusBtn: Optional[ DirectButton ] = None
        self.__incrementMinusBtn: Optional[ DirectButton ] = None
        self.__zoomInBtn: Optional[ DirectButton ] = None
        self.__zoomOutBtn: Optional[ DirectButton ] = None
        self.__resetBtn: Optional[ DirectButton ] = None
        self.__rotateUpBtn: Optional[ DirectButton ] = None
        self.__rotateDownBtn: Optional[ DirectButton ] = None
        self.__rotateLeftBtn: Optional[ DirectButton ] = None
        self.__rotateRightBtn: Optional[ DirectButton ] = None
        self.__startGameBtn: Optional[ DirectButton ] = None
        self.__nextChallengeBtn: Optional[ DirectButton ] = None
        self.__gameStatsBtn: Optional[ DirectButton ] = None
        self.__radiusPlusBtn: Optional[ DirectButton ] = None
        self.__radiusMinusBtn: Optional[ DirectButton ] = None
        self.__presetButtons: List[ DirectButton ] = []

    # ── Creation ──────────────────────────────────────────────────────────────

    def buildStepControls(
        self,
        onIncrease: Callable,
        onDecrease: Callable
    ) -> None:
        """Create the STEP label and +/- buttons"""
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
            pos=self.__settings.getButtonPosition( "increment", "plus_position" ),
            scale=self.__settings.getButtonScale( "increment" ),
            command=onIncrease,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

        self.__incrementMinusBtn = DirectButton(
            text="-",
            pos=self.__settings.getButtonPosition( "increment", "minus_position" ),
            scale=self.__settings.getButtonScale( "increment" ),
            command=onDecrease,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

    def buildZoomControls(
        self,
        onZoomIn: Callable,
        onZoomOut: Callable
    ) -> None:
        """Create the ZOOM label, IN and OUT buttons"""
        DirectButton(
            text=self.__settings.getTextContent( "zoom_label" ),
            pos=self.__settings.getButtonPosition( "zoom", "label_position" ),
            scale=self.__settings.getButtonScale( "zoom" ),
            frameColor=self.__settings.getButtonColor( "label", "background" ),
            text_fg=self.__settings.getButtonColor( "label", "text" ),
            relief=0
        )

        self.__zoomInBtn = DirectButton(
            text="IN",
            pos=self.__settings.getButtonPosition( "zoom", "in_position" ),
            scale=self.__settings.getButtonScale( "zoom" ),
            command=onZoomIn,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

        self.__zoomOutBtn = DirectButton(
            text="OUT",
            pos=self.__settings.getButtonPosition( "zoom", "out_position" ),
            scale=self.__settings.getButtonScale( "zoom" ),
            command=onZoomOut,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

    def buildResetButton( self, onReset: Callable ) -> None:
        """Create the RESET VIEW button"""
        self.__resetBtn = DirectButton(
            text="RESET VIEW",
            pos=self.__settings.getButtonPosition( "reset", "position" ),
            scale=self.__settings.getButtonScale( "reset" ),
            command=onReset,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

    def buildRotationButtons(
        self,
        onUp: Callable,
        onDown: Callable,
        onLeft: Callable,
        onRight: Callable
    ) -> None:
        """Create the four directional rotation buttons"""
        self.__rotateUpBtn = DirectButton(
            text="UP",
            pos=self.__settings.getButtonPosition( "rotation", "up_position" ),
            scale=self.__settings.getButtonScale( "rotation" ),
            command=onUp,
            frameColor=self.__settings.getButtonColor( "rotation", "background" ),
            text_fg=self.__settings.getButtonColor( "rotation", "text" ),
            pressEffect=1, relief=2
        )

        self.__rotateDownBtn = DirectButton(
            text="DOWN",
            pos=self.__settings.getButtonPosition( "rotation", "down_position" ),
            scale=self.__settings.getButtonScale( "rotation" ),
            command=onDown,
            frameColor=self.__settings.getButtonColor( "rotation", "background" ),
            text_fg=self.__settings.getButtonColor( "rotation", "text" ),
            pressEffect=1, relief=2
        )

        self.__rotateLeftBtn = DirectButton(
            text="LEFT",
            pos=self.__settings.getButtonPosition( "rotation", "left_position" ),
            scale=self.__settings.getButtonScale( "rotation" ),
            command=onLeft,
            frameColor=self.__settings.getButtonColor( "rotation", "background" ),
            text_fg=self.__settings.getButtonColor( "rotation", "text" ),
            pressEffect=1, relief=2
        )

        self.__rotateRightBtn = DirectButton(
            text="RIGHT",
            pos=self.__settings.getButtonPosition( "rotation", "right_position" ),
            scale=self.__settings.getButtonScale( "rotation" ),
            command=onRight,
            frameColor=self.__settings.getButtonColor( "rotation", "background" ),
            text_fg=self.__settings.getButtonColor( "rotation", "text" ),
            pressEffect=1, relief=2
        )

    def buildPresetButtons( self, onPreset: Callable[ [ int ], None ] ) -> None:
        """Create preset view buttons (hidden by default)"""
        presetLabels = self.__settings.getPresetLabels()
        presetPositions = self.__settings.getPresetPositions()
        presetScale = self.__settings.getButtonScale( "presets" )

        for index, ( label, position ) in enumerate( zip( presetLabels, presetPositions ) ):
            btn = DirectButton(
                text=label,
                pos=position,
                scale=presetScale,
                command=lambda i=index: onPreset( i ),
                frameColor=self.__settings.getButtonColor( "preset", "background" ),
                text_fg=self.__settings.getButtonColor( "preset", "text" ),
                pressEffect=1, relief=2
            )
            btn.hide()
            self.__presetButtons.append( btn )

    def buildGameControls(
        self,
        onStartGame: Callable,
        onNextChallenge: Callable,
        onGameStats: Callable
    ) -> None:
        """Create game control buttons"""
        self.__startGameBtn = DirectButton(
            text=self.__settings.getTextContent( "start_game" ),
            pos=self.__settings.getButtonPosition( "game", "start_position" ),
            scale=self.__settings.getButtonScale( "game" ),
            command=onStartGame,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

        self.__nextChallengeBtn = DirectButton(
            text=self.__settings.getTextContent( "next_challenge" ),
            pos=self.__settings.getButtonPosition( "game", "next_position" ),
            scale=self.__settings.getButtonScale( "game" ),
            command=onNextChallenge,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )
        self.__nextChallengeBtn.hide()

        self.__gameStatsBtn = DirectButton(
            text=self.__settings.getTextContent( "game_stats" ),
            pos=self.__settings.getButtonPosition( "game", "stats_position" ),
            scale=self.__settings.getButtonScale( "game" ),
            command=onGameStats,
            frameColor=self.__settings.getButtonColor( "control", "background" ),
            text_fg=self.__settings.getButtonColor( "control", "text" ),
            pressEffect=1, relief=2
        )

    def buildRadiusControls(
        self,
        onIncrease: Callable,
        onDecrease: Callable,
        initialValue: float
    ) -> None:
        """Create continent radius controls (hidden by default)"""
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
            command=onIncrease,
            frameColor=self.__settings.getButtonColor( "increment", "background" ),
            text_fg=self.__settings.getButtonColor( "increment", "text" ),
            pressEffect=1, relief=2
        )
        self.__radiusPlusBtn.hide()

        self.__radiusMinusBtn = DirectButton(
            text="-",
            pos=( -0.90, 0, 0.58 ),
            scale=0.04,
            command=onDecrease,
            frameColor=self.__settings.getButtonColor( "increment", "background" ),
            text_fg=self.__settings.getButtonColor( "increment", "text" ),
            pressEffect=1, relief=2
        )
        self.__radiusMinusBtn.hide()

    # ── Accessors ─────────────────────────────────────────────────────────────

    @property
    def incrementPlusBtn( self ) -> Optional[ DirectButton ]:
        return self.__incrementPlusBtn

    @property
    def incrementMinusBtn( self ) -> Optional[ DirectButton ]:
        return self.__incrementMinusBtn

    @property
    def zoomInBtn( self ) -> Optional[ DirectButton ]:
        return self.__zoomInBtn

    @property
    def zoomOutBtn( self ) -> Optional[ DirectButton ]:
        return self.__zoomOutBtn

    @property
    def resetBtn( self ) -> Optional[ DirectButton ]:
        return self.__resetBtn

    @property
    def rotateUpBtn( self ) -> Optional[ DirectButton ]:
        return self.__rotateUpBtn

    @property
    def rotateDownBtn( self ) -> Optional[ DirectButton ]:
        return self.__rotateDownBtn

    @property
    def rotateLeftBtn( self ) -> Optional[ DirectButton ]:
        return self.__rotateLeftBtn

    @property
    def rotateRightBtn( self ) -> Optional[ DirectButton ]:
        return self.__rotateRightBtn

    @property
    def startGameBtn( self ) -> Optional[ DirectButton ]:
        return self.__startGameBtn

    @property
    def nextChallengeBtn( self ) -> Optional[ DirectButton ]:
        return self.__nextChallengeBtn

    @property
    def gameStatsBtn( self ) -> Optional[ DirectButton ]:
        return self.__gameStatsBtn

    @property
    def radiusPlusBtn( self ) -> Optional[ DirectButton ]:
        return self.__radiusPlusBtn

    @property
    def radiusMinusBtn( self ) -> Optional[ DirectButton ]:
        return self.__radiusMinusBtn

    @property
    def presetButtons( self ) -> List[ DirectButton ]:
        return list( self.__presetButtons )

    def getAllButtons( self ) -> List[ DirectButton ]:
        """Return all non-None interactive buttons as a flat list"""
        candidates = [
            self.__incrementMinusBtn, self.__incrementPlusBtn,
            self.__zoomInBtn, self.__zoomOutBtn,
            self.__resetBtn,
            self.__rotateUpBtn, self.__rotateDownBtn,
            self.__rotateLeftBtn, self.__rotateRightBtn,
            self.__startGameBtn, self.__nextChallengeBtn,
            self.__gameStatsBtn,
            self.__radiusPlusBtn, self.__radiusMinusBtn,
        ] + self.__presetButtons
        return [ btn for btn in candidates if btn is not None ]

