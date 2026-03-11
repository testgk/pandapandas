"""
Globe GUI Controller - Handles all GUI elements and user interactions
"""
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectButton
from panda3d.core import *
from interfaces.i_globe_application import IGlobeApplication


class GlobeGuiController:
    """Controls all GUI elements for the globe application"""

    def __init__(self, globe_app: IGlobeApplication):
        self.__globe_app = globe_app
        self.__log_messages = []
        self.__all_buttons = []
        self.__create_gui_controls()

    def __create_gui_controls(self):
        """Create all GUI buttons and controls"""
        # Rotation Step controls (top-left corner, vertical layout)
        # + button
        self.__increment_plus_btn = DirectButton(
            text="+", pos=(-0.75, 0, 0.8), scale=0.04,
            command=self.__on_increase_rotation_increment,
            frameColor=(0.2, 0.8, 0.2, 1), text_fg=(0, 0, 0, 1), relief=2
        )

        # - button
        self.__increment_minus_btn = DirectButton(
            text="-", pos=(-0.75, 0, 0.7), scale=0.04,
            command=self.__on_decrease_rotation_increment,
            frameColor=(0.2, 0.8, 0.2, 1), text_fg=(0, 0, 0, 1), relief=2
        )

        # Zoom controls
        DirectButton(
            text="ZOOM", pos=(-0.1, 0, 0.8), scale=0.05,
            frameColor=(0, 0, 0, 0), text_fg=(1, 1, 1, 1), relief=0
        )

        self.__zoom_in_btn = DirectButton(
            text="IN", pos=(0.1, 0, 0.8), scale=0.05,
            command=self.__on_zoom_in,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__zoom_out_btn = DirectButton(
            text="OUT", pos=(0.3, 0, 0.8), scale=0.05,
            command=self.__on_zoom_out,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        # Reset View button
        self.__reset_btn = DirectButton(
            text="RESET VIEW", pos=(0, 0, 0.65), scale=0.05,
            command=self.__on_reset_view,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        # Directional rotation buttons at screen edges
        self.__rotate_up_btn = DirectButton(
            text="UP", pos=(0, 0, 0.9), scale=0.05,
            command=self.__on_rotate_up,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__rotate_down_btn = DirectButton(
            text="DOWN", pos=(0, 0, -0.8), scale=0.05,
            command=self.__on_rotate_down,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__rotate_left_btn = DirectButton(
            text="LEFT", pos=(-0.95, 0, 0), scale=0.05,
            command=self.__on_rotate_left,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        self.__rotate_right_btn = DirectButton(
            text="RIGHT", pos=(0.95, 0, 0), scale=0.05,
            command=self.__on_rotate_right,
            frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
            pressEffect=1, relief=2
        )

        # Preset view buttons
        self.__create_preset_buttons()

        # Store all buttons for dark gray click effect
        self.__all_buttons = [
            self.__increment_minus_btn, self.__increment_plus_btn,
            self.__zoom_in_btn, self.__zoom_out_btn, self.__reset_btn,
            self.__rotate_up_btn, self.__rotate_down_btn,
            self.__rotate_left_btn, self.__rotate_right_btn
        ]

        # Log display at bottom
        self.__log_display = OnscreenText(
            text="SYSTEM READY",
            pos=(0, -0.75), scale=0.04,
            fg=(1, 1, 1, 1), wordwrap=80
        )

        # Bottom status text
        OnscreenText(
            text="REAL WORLD DATA • MANUAL CONTROLS ONLY",
            pos=(0, -0.85), scale=0.04, fg=(0, 1, 0, 1)
        )

    def __create_preset_buttons(self):
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
                command=lambda i=index: self.__on_set_preset_view(i),
                frameColor=(0.1, 0.3, 0.1, 1), text_fg=(0, 1, 0, 1),
                pressEffect=1, relief=2
            )
            self.__all_buttons.append(btn)

    def __apply_button_effect(self, button):
        """Apply dark gray effect to button when clicked"""
        original_color = button['frameColor']
        button['frameColor'] = (0.3, 0.3, 0.3, 1)  # Dark gray

        def reset_color(task):
            button['frameColor'] = original_color
            return task.done

        self.__globe_app.taskManager.doMethodLater(0.1, reset_color, f"reset_button_{id(button)}")

    def add_log_message(self, message):
        """Add message to log display"""
        self.__log_messages.append(message)
        if len(self.__log_messages) > 3:
            self.__log_messages.pop(0)
        log_text = " | ".join(self.__log_messages)
        self.__log_display.setText(log_text)

    # Event handlers - delegate to globe app
    def __on_zoom_in(self):
        self.__apply_button_effect(self.__zoom_in_btn)
        self.__globe_app.zoomIn()

    def __on_zoom_out(self):
        self.__apply_button_effect(self.__zoom_out_btn)
        self.__globe_app.zoomOut()

    def __on_reset_view(self):
        self.__apply_button_effect(self.__reset_btn)
        self.__globe_app.resetView()

    def __on_rotate_up(self):
        self.__apply_button_effect(self.__rotate_up_btn)
        self.__globe_app.rotateUp()

    def __on_rotate_down(self):
        self.__apply_button_effect(self.__rotate_down_btn)
        self.__globe_app.rotateDown()

    def __on_rotate_left(self):
        self.__apply_button_effect(self.__rotate_left_btn)
        self.__globe_app.rotateLeft()

    def __on_rotate_right(self):
        self.__apply_button_effect(self.__rotate_right_btn)
        self.__globe_app.rotateRight()

    def __on_increase_rotation_increment(self):
        self.__apply_button_effect(self.__increment_plus_btn)
        self.__globe_app.increaseRotationIncrement()

    def __on_decrease_rotation_increment(self):
        self.__apply_button_effect(self.__increment_minus_btn)
        self.__globe_app.decreaseRotationIncrement()

    def __on_set_preset_view(self, index):
        buttons = self.__all_buttons[-6:]  # Last 6 are preset buttons
        if 0 <= index < len(buttons):
            self.__apply_button_effect(buttons[index])
        self.__globe_app.setPresetView(index)
