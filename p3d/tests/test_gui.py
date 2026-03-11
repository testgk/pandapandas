"""
Test the GUI controls by running just the application to see the buttons
"""
print("Testing GUI controls visibility...")

try:
    from direct.showbase.ShowBase import ShowBase
    from direct.gui.DirectGui import DirectButton
    from direct.gui.OnscreenText import OnscreenText

    class TestGUI(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            self.setBackgroundColor(0.2, 0.2, 0.5)  # Blue background

            print("Creating GUI test...")

            # Test GUI elements
            OnscreenText(text="GUI TEST - Manual Globe Controls",
                        pos=(0, 0.8), scale=0.08, fg=(1, 1, 1, 1))

            # Zoom buttons
            DirectButton(text="ZOOM IN", pos=(-0.3, 0, 0.6), scale=0.08,
                        command=self.test_zoom_in)
            DirectButton(text="ZOOM OUT", pos=(0.3, 0, 0.6), scale=0.08,
                        command=self.test_zoom_out)

            # Rotation buttons
            DirectButton(text="UP", pos=(0, 0, 0.4), scale=0.08,
                        command=self.test_up)
            DirectButton(text="DOWN", pos=(0, 0, 0.2), scale=0.08,
                        command=self.test_down)
            DirectButton(text="LEFT", pos=(-0.2, 0, 0.3), scale=0.08,
                        command=self.test_left)
            DirectButton(text="RIGHT", pos=(0.2, 0, 0.3), scale=0.08,
                        command=self.test_right)

            OnscreenText(text="Click buttons to test - check terminal for output",
                        pos=(0, -0.8), scale=0.05, fg=(0.8, 0.8, 0.8, 1))

            print("GUI elements created successfully!")
            print("You should see 6 buttons: 2 zoom + 4 rotation")

        def test_zoom_in(self):
            print("ZOOM IN button clicked!")

        def test_zoom_out(self):
            print("ZOOM OUT button clicked!")

        def test_up(self):
            print("ROTATE UP button clicked!")

        def test_down(self):
            print("ROTATE DOWN button clicked!")

        def test_left(self):
            print("ROTATE LEFT button clicked!")

        def test_right(self):
            print("ROTATE RIGHT button clicked!")

    print("Starting GUI test application...")
    app = TestGUI()
    app.run()

except Exception as e:
    print(f"Error in GUI test: {e}")
    import traceback
    traceback.print_exc()
