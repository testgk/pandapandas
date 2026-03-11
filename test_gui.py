#!/usr/bin/env python3
"""
Simple test to check if the GUI launches
"""
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def test_gui():
    root = tk.Tk()
    root.title("🌍 GeoChallenge Map Test")
    root.geometry("800x600")
    
    # Create a simple test frame
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Test label
    label = ttk.Label(frame, text="🎯 GUI Test - If you see this, the GUI is working!", font=('Arial', 14))
    label.pack(pady=20)
    
    # Create a simple matplotlib plot
    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    # Simple world map outline
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Click anywhere on this test map!')
    
    # Add some basic continent shapes
    import matplotlib.patches as patches
    
    # North America (very simplified)
    na = patches.Rectangle((-160, 15), 100, 55, linewidth=2, edgecolor='green', facecolor='lightgreen', alpha=0.3)
    ax.add_patch(na)
    ax.text(-110, 42, 'North America', ha='center', fontsize=10)
    
    # Europe (very simplified)
    eu = patches.Rectangle((-10, 35), 50, 35, linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.3)
    ax.add_patch(eu)
    ax.text(15, 52, 'Europe', ha='center', fontsize=10)
    
    # Create canvas
    canvas = FigureCanvasTkAgg(fig, frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Test click handler
    clicked_coords = {'lat': None, 'lon': None}
    
    def on_click(event):
        if event.inaxes == ax:
            clicked_coords['lat'] = event.ydata
            clicked_coords['lon'] = event.xdata
            coord_label.config(text=f"Clicked: ({event.ydata:.2f}°, {event.xdata:.2f}°)")
            # Add a marker
            ax.plot(event.xdata, event.ydata, 'ro', markersize=8)
            canvas.draw()
    
    canvas.mpl_connect('button_press_event', on_click)
    
    # Coordinate display
    coord_label = ttk.Label(frame, text="Click on the map above!", font=('Arial', 12))
    coord_label.pack(pady=10)
    
    # Test button
    def test_click():
        messagebox.showinfo("Test", "GUI is working correctly! 🎉")
    
    test_button = ttk.Button(frame, text="Test Button - Click Me!", command=test_click)
    test_button.pack(pady=10)
    
    print("🎯 GUI Test launched! Window should be visible now.")
    root.mainloop()
    print("🎯 GUI Test completed.")

if __name__ == "__main__":
    test_gui()
