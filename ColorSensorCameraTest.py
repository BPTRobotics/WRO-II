import tkinter as tk
import ColorSensor
import time

def update_color():
    r, g, b = ColorSensor.read_averaged_color()
    
    # Clamp RGB to [0.0, 1.0], then convert to 0–255 scale for tkinter
    r_255 = int(max(0, min(r, 1)) * 255)
    g_255 = int(max(0, min(g, 1)) * 255)
    b_255 = int(max(0, min(b, 1)) * 255)

    hex_color = f'#{r_255:02x}{g_255:02x}{b_255:02x}'
    canvas.configure(bg=hex_color)
    label.config(text=f"R: {r:.4f}  G: {g:.4f}  B: {b:.4f}")
    
    root.after(100, update_color)  # Update every 100 ms

# GUI setup
root = tk.Tk()
root.title("TCS34725 Color Viewer")
root.geometry("400x300")

canvas = tk.Canvas(root, width=400, height=250)
canvas.pack()

label = tk.Label(root, text="", font=("Arial", 14))
label.pack(pady=10)

update_color()
root.mainloop()
