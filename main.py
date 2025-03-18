# -----Imports-----

import tkinter as tk # tkinter for the main window
import customtkinter as ctk # custom tkinter for styling
from PIL import Image, ImageTk # PIL for handling images
import pyautogui, keyboard # keyboard for handling key presses and pyautogui for mouse tracking
import threading, time # for other functionalities

# -----Resources-----
icon_image = Image.open("cursor.png")

# -----Logic-----
# Core functionalities
def initial_processes():
    # some initial processes that needs to be running as the application starts
    global saved_hotkey, saved_time
    # getting and showing saved attributes
    with open("attr.txt", "r") as attr_read:
        saved_attributes = attr_read.readlines()
        saved_hotkey = saved_attributes[0].strip("\n")
        saved_time = saved_attributes[1].strip()
    current_hotkey_label.configure(text=saved_hotkey)
    time_entry.delete(0, "end")
    time_entry.insert(0, saved_time)
    # start listening for the hotkey
    keyboard.add_hotkey(saved_hotkey, move_cursor_to_saved_position)

def cursor():
    global saved_cursor_position
    saved_cursor_position = None  # Variable to store the cursor position
    def track_cursor():
        global saved_cursor_position
        prev_position = pyautogui.position()
        while True:
            time.sleep(int(saved_time))
            current_position = pyautogui.position()
            if current_position == prev_position:
                saved_cursor_position = current_position  # Save position if idle
            prev_position = current_position
    threading.Thread(target=track_cursor, daemon=True).start() # start tracking in a separate thread

def move_cursor_to_saved_position():
    if saved_cursor_position:
        pyautogui.moveTo(saved_cursor_position)  # Move cursor to saved position

# Apps functions

def change_hotkey_btn_func():
    # New window
    new_hotkey_popup = tk.Toplevel(root)  # create a new top-level window
    new_hotkey_popup.geometry("300x200")  # set size
    new_hotkey_popup.resizable(False, False)
    new_hotkey_popup.title("")  # remove title
    new_hotkey_popup.configure(bg="#2b2b2b") # change background
    new_hotkey_popup.grab_set()  # force focus on new window

    # Populating our new window
    new_hotkey_label = ctk.CTkLabel(new_hotkey_popup, text="New Hot Key", font=("Segoe UI", 18, "bold"), text_color="#FFFFFF")
    new_hotkey_label.place(relx=0.05, rely=0.05)
    new_hotkey_des_label = ctk.CTkLabel(new_hotkey_popup, text="Press up to 3 keys", font=("Corbel", 14, "bold"), text_color="#FFFFFF")
    new_hotkey_des_label.place(relx=0.05, rely=0.2)
    selected_hotkey_label_var = ctk.StringVar(value="")
    selected_hotkey_label = ctk.CTkLabel(new_hotkey_popup, textvariable=selected_hotkey_label_var, font=("Consolas", 18), text_color="#6EFAFB")
    selected_hotkey_label.place(relx=0.1, rely=0.48)

    # Changing the key functionality (chatgpt helped :') )
    stop_event = threading.Event()  # event to stop listening
    recorded_keys = []  # store pressed keys
    key_aliases = {
        "left windows": "Win",
        "right windows": "Win",
        "print screen": "ps",
        "scroll lock": "sl",
        "num lock": "nl",
        "caps lock": "cl",
        "page down": "pageD",
        "page up": "pageU"
        }
    # Listen for pressed keys
    def listen_for_hotkey():
        def on_press(event):
            key = event.name.lower()
            key = key_aliases.get(key, key)  # Replace with alias if available
    
            if key not in recorded_keys and len(recorded_keys) < 3:
                recorded_keys.append(key)
                selected_hotkey_label_var.set("+".join(recorded_keys))  # Update popup UI
        keyboard.on_press(on_press)
        while not stop_event.is_set():
            keyboard.wait()
        keyboard.unhook_all()  # stop listening when done

    threading.Thread(target=listen_for_hotkey, daemon=True).start()

    # Stop listening and save hotkey to variable
    def confirm_hotkey():
        if len(recorded_keys) > 0:
            stop_event.set()  # stop key listening
            global new_hotkey, saved_hotkey
            keyboard.remove_hotkey(saved_hotkey)
            new_hotkey = selected_hotkey_label_var.get() or None  # save hotkey in variable
            saved_hotkey = new_hotkey
            keyboard.add_hotkey(saved_hotkey, move_cursor_to_saved_position)
            new_hotkey_popup.destroy()  # close popup
            with open("attr.txt", "r") as read_attr_file:
               saved_attributes = read_attr_file.readlines()
               saved_attributes[0] = f"{new_hotkey}\n"
            with open("attr.txt", "w") as update_attr_file:
                update_attr_file.writelines(saved_attributes)
            current_hotkey_label.configure(text=new_hotkey)

    new_hotkey_ok_btn = ctk.CTkButton(new_hotkey_popup, text="OK", font=("Inter", 16, "bold"), text_color="#1b1b1b", fg_color="#1ea7f7", width=300, height=30, corner_radius=0, hover_color="#77dce8", command=confirm_hotkey)
    new_hotkey_ok_btn.place(relx=0.001, rely=0.85)

def change_time_btn_func():
    global saved_time
    main_canvas.focus_set()
    new_time = time_entry.get().strip()
    if new_time.isdigit():
        saved_time = new_time
        time_entry.delete(0, "end")
        time_entry.insert(0, new_time)
        with open("attr.txt", "r") as read_attr_file:
           saved_attributes = read_attr_file.readlines()
           saved_attributes[1] = new_time
        with open("attr.txt", "w") as update_attr_file:
            update_attr_file.writelines(saved_attributes)
        cursor()
    

# -----Design-----
root = tk.Tk() # main window
root.geometry("360x450") # resizing the main window
root.resizable(False, False) # user cant resize the window
root.iconphoto(True, ImageTk.PhotoImage(icon_image)) # custom icon
root.title("") # removing title it doesnt look good

main_canvas = ctk.CTkCanvas(root, bg="#2f384b", highlightthickness=0) # a canvas where we will place all our widgets instead of the main window
main_canvas.pack(fill="both", expand=True) 

# Populating our canvas
# Title
title_label = ctk.CTkLabel(main_canvas, text="Cursor Snap", font=("Quicksand", 16, "bold"), text_color="#04d3f7")
title_label.place(relx=0.36, rely=0.01)

# Main features

# Hot Key
hotkey_frame = ctk.CTkFrame(main_canvas, width=320, height=45, fg_color="#1b1b1b", corner_radius=5)
hotkey_frame.place(relx=0.06, rely=0.18)
hotkey_line = ctk.CTkFrame(hotkey_frame, width=5, height=44, fg_color="#1ea7f7", corner_radius=500)
hotkey_line.place(relx=0.001, rely=0.001)
hotkey_label = ctk.CTkLabel(hotkey_frame, text="HotKey", font=("Quicksand", 13, "bold"), text_color="#1ea7f7")
hotkey_label.place(relx=0.05, rely=0.15)
current_hotkey_label = ctk.CTkLabel(hotkey_frame, text="", font=("Consolas", 13), text_color="#FFFFFF", bg_color="#343638", width=150)
current_hotkey_label.place(relx=0.28, rely=0.15)
change_hotkey_btn = ctk.CTkButton(hotkey_frame, text="►", font=("Arial", 18), width=30, height=15, fg_color="#1b1b1b", text_color="#1ea7f7", hover_color="#3d5a80", anchor="left", command=change_hotkey_btn_func)
change_hotkey_btn.place(relx=0.86, rely=0.2)

# Wait Time
time_frame = ctk.CTkFrame(main_canvas, width=320, height=45, fg_color="#1b1b1b", corner_radius=5)
time_frame.place(relx=0.06, rely=0.31)
time_line = ctk.CTkFrame(time_frame, width=5, height=44, fg_color="#00dcb8", corner_radius=500)
time_line.place(relx=0.001, rely=0.001)
time_label = ctk.CTkLabel(time_frame, text="Wait Time", font=("Quicksand", 13, "bold"), text_color="#00dcb8")
time_label.place(relx=0.05, rely=0.15)
time_entry = ctk.CTkEntry(time_frame, height=25, width=80)
time_entry.place(relx=0.35, rely=0.2)
seconds_label = ctk.CTkLabel(time_frame, text="s", font=("Helvetica", 14, "bold"), text_color="#00dcb8")
seconds_label.place(relx=0.62, rely=0.23)
change_time_btn = ctk.CTkButton(time_frame, text="►", font=("Arial", 18), width=30, height=15, fg_color="#1b1b1b", text_color="#00dcb8", hover_color="#3d5a80", anchor="left", command=change_time_btn_func)
change_time_btn.place(relx=0.86, rely=0.2)

# Other functionalities
# placeholder frames for additional functionalities that we might add in the future
placeholder_frame_1 = ctk.CTkFrame(main_canvas, width=320, height=45, fg_color="#242933", corner_radius=5)
placeholder_frame_1.place(relx=0.06, rely=0.44)
placeholder_1_line = ctk.CTkFrame(placeholder_frame_1, width=6, height=44, fg_color="#1b1b1b", corner_radius=500)
placeholder_1_line.place(relx=0.001, rely=0.001)

placeholder_frame_2 = ctk.CTkFrame(main_canvas, width=320, height=45, fg_color="#242933", corner_radius=5)
placeholder_frame_2.place(relx=0.06, rely=0.57)
placeholder_2_line = ctk.CTkFrame(placeholder_frame_2, width=6, height=44, fg_color="#1b1b1b", corner_radius=500)
placeholder_2_line.place(relx=0.001, rely=0.001)

placeholder_frame_3 = ctk.CTkFrame(main_canvas, width=320, height=45, fg_color="#242933", corner_radius=5)
placeholder_frame_3.place(relx=0.06, rely=0.7)
placeholder_3_line = ctk.CTkFrame(placeholder_frame_3, width=6, height=44, fg_color="#1b1b1b", corner_radius=500)
placeholder_3_line.place(relx=0.001, rely=0.001)

initial_processes()
cursor()

root.mainloop()
