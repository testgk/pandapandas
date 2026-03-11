"""
Globe GUI Controller - Handles all GUI elements and user interactions
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import *
from interfaces.i_globe_application import IGlobeApplication


class GlobeGuiController:
    """Controls all GUI elements for the globe application"""

    def __init__(self, globeApp: IGlobeApplication):
        self.__globeApp = globeApp
        self.__logMessages = []
        self.__allButtons = []
        self.__createGuiControls()

    def __createGuiControls(self):
        """Create all GUI buttons and controls"""
        # Rotation Step controls (top-left corner, vertical layout)
        # + button
        self.__incrementPlusBtn = DirectButton(
            text="+", pos=(-0.75, 0, 0.8), scale=0.04,
            command=self.__onIncreaseRotationIncrement,
            frameColor=(0.2, 0.8, 0.2, 1), text_fg=(0, 0, 0, 1), relief=2
        )

        # - button
        self.__incrementMinusBtn = DirectButton(
            text="-", pos=(-0.75, 0, 0.7), scale=0.04,
            command=self.__onDecreaseRotationIncrement,
            frameColor=(0.2, 0.8, 0.2, 1), text_fg=(0, 0, 0, 1), relief=2
        )

        # Zoom controls
        DirectButton(
            text="ZOOM", pos=(-0.1, 0, 0.8), scale=0.05,
            frameColor=(0, 0, 0, 0), text_fg=(1, 1, 1, 1), relief=0
        )

        self.__zoomInBtn = DirectButton(
            text="IN", pos=(0.1, 0, 0.8), scale=0.05,
            command=self.__onZoomIn,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__zoomOutBtn = DirectButton(
            text="OUT", pos=(0.3, 0, 0.8), scale=0.05,
            command=self.__onZoomOut,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        # Reset View button
        self.__resetBtn = DirectButton(
            text="RESET VIEW", pos=(0, 0, 0.65), scale=0.05,
            command=self.__onResetView,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        # Directional rotation buttons at screen edges
        self.__rotateUpBtn = DirectButton(
            text="UP", pos=(0, 0, 0.9), scale=0.05,
            command=self.__onRotateUp,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__rotateDownBtn = DirectButton(
            text="DOWN", pos=(0, 0, -0.8), scale=0.05,
            command=self.__onRotateDown,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__rotateLeftBtn = DirectButton(
            text="LEFT", pos=(-0.95, 0, 0), scale=0.05,
            command=self.__onRotateLeft,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__rotateRightBtn = DirectButton(
            text="RIGHT", pos=(0.95, 0, 0), scale=0.05,
            command=self.__onRotateRight,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        # Preset view buttons
        self.__createPresetButtons()

        # Store all buttons for dark gray click effect
        self.__allButtons = [
            self.__incrementMinusBtn, self.__incrementPlusBtn,
            self.__zoomInBtn, self.__zoomOutBtn, self.__resetBtn,
            self.__rotateUpBtn, self.__rotateDownBtn,
            self.__rotateLeftBtn, self.__rotateRightBtn
        ]

        # Log display at bottom
        self.__logDisplay = OnscreenText(
            text="SYSTEM READY",
            pos=(0, -0.75), scale=0.04,
            fg=(1, 1, 1, 1), wordwrap=80
        )

        # Bottom status text
        OnscreenText(
            text="REAL WORLD DATA • MANUAL CONTROLS ONLY",
            pos=(0, -0.85), scale=0.04, fg=(0, 1, 0, 1)
        )

    def __createPresetButtons(self):
        """Create preset view buttons for different regions"""
        presets = [
            ("EUROPE", 0, (-0.6, 0, 0.2)),
            ("AMERICAS", 1, (-0.6, 0, 0.1)),
            ("ASIA", 2, (-0.6, 0, 0.0)),
            ("AFRICA", 3, (0.6, 0, 0.2)),
            ("ATLANTIC", 4, (0.6, 0, 0.1)),
            ("PACIFIC", 5, (0.6, 0, 0.0))
        ]

        for name, index, pos in presets:
            btn = DirectButton(
                text=name, pos=pos, scale=0.04,
                command=lambda i=index: self.__onSetPresetView(i),
                frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
                pressEffect=1, relief=2
            )
            self.__allButtons.append(btn)

    def __applyButtonEffect(self, button):
        """Apply dark gray effect to button when clicked"""
        originalColor = button['frameColor']
        button['frameColor'] = (0.3, 0.3, 0.3, 1)  # Dark gray

        def resetColor(task):
            button['frameColor'] = originalColor
            return task.done

        self.__globeApp.taskManager.doMethodLater(0.1, resetColor, f"reset_button_{id(button)}")

    def addLogMessage(self, message):
        """Add message to log display"""
        self.__logMessages.append(message)
        if len(self.__logMessages) > 3:
            self.__logMessages.pop(0)
        logText = " | ".join(self.__logMessages)
        self.__logDisplay.setText(logText)

    # Event handlers - delegate to globe app
    def __onZoomIn(self):
        self.__applyButtonEffect(self.__zoomInBtn)
        self.__globeApp.zoomIn()

    def __onZoomOut(self):
        self.__applyButtonEffect(self.__zoomOutBtn)
        self.__globeApp.zoomOut()

    def __onResetView(self):
        self.__applyButtonEffect(self.__resetBtn)
        self.__globeApp.resetView()

    def __onRotateUp(self):
        self.__applyButtonEffect(self.__rotateUpBtn)
        self.__globeApp.rotateUp()

    def __onRotateDown(self):
        self.__applyButtonEffect(self.__rotateDownBtn)
        self.__globeApp.rotateDown()

    def __onRotateLeft(self):
        self.__applyButtonEffect(self.__rotateLeftBtn)
        self.__globeApp.rotateLeft()

    def __onRotateRight(self):
        self.__applyButtonEffect(self.__rotateRightBtn)
        self.__globeApp.rotateRight()

    def __onIncreaseRotationIncrement(self):
        self.__applyButtonEffect(self.__incrementPlusBtn)
        self.__globeApp.increaseRotationIncrement()

    def __onDecreaseRotationIncrement(self):
        self.__applyButtonEffect(self.__incrementMinusBtn)
        self.__globeApp.decreaseRotationIncrement()

    def __onSetPresetView(self, index):
        buttons = self.__allButtons[-6:]  # Last 6 are preset buttons
        if 0 <= index < len(buttons):
            self.__applyButtonEffect(buttons[index])
        self.__globeApp.setPresetView(index)
