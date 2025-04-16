import tkinter as tk

# Create the main application window
root = tk.Tk()
root.title("Simple Tkinter App")
root.geometry("300x150")

# Function to update the label text
def update_label():
    user_input = entry.get()
    label.config(text=f"Hello, {user_input}!")

# Create a label
label = tk.Label(root, text="Enter your name:", font=("Comic Sans MS", 12))
label.pack(pady=10)

# Create an entry widget
entry = tk.Entry(root, width=25)
entry.pack()

# Create a button that triggers the update_label function
button = tk.Button(root, text="Greet", command=update_label)
button.pack(pady=10)

# Start the main loop
root.mainloop()