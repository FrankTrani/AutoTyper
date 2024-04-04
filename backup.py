import pyautogui
import threading
import time
import sys
import tkinter as tk
from tkinter import filedialog
from pynput import keyboard
import random
import re
import unicodedata

# Flag to control the typing thread
typing_thread_running = False
countdown_running = False
countdown_time = 5
typing_speed = 0.1
typing_file = ""
current_line = 0
current_char = 0
total_lines = 0
error_rate = 0
start_time = 0
end_time = 0
total_characters = 0
total_errors = 0
random_speed = False
language = "English"
preprocess_text = False
lines = []  # Add this line to make lines accessible globally

def typing_thread():
    global typing_thread_running, current_line, current_char, total_lines, start_time, end_time, total_characters, total_errors, lines
    while countdown_running:
        time.sleep(0.1)  # Wait for the countdown to finish
    with open(typing_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
        total_lines = len(lines)
        start_time = time.time()
        previous_time = start_time
        for i in range(current_line, total_lines):
            line = lines[i]
            if preprocess_text:
                line = preprocess_line(line)
            for j in range(current_char, len(line)):
                character = line[j]
                if not typing_thread_running:
                    current_line = i
                    current_char = j
                    return  # Stop the thread if the flag is set to False
                current_time = time.time()
                keystroke_delay = current_time - previous_time
                previous_time = current_time
                if random.random() < error_rate:
                    # Introduce a typing error
                    error_character = random.choice(list('abcdefghijklmnopqrstuvwxyz'))
                    pyautogui.typewrite(error_character, interval=get_typing_speed())
                    total_errors += 1
                else:
                    pyautogui.typewrite(character, interval=get_typing_speed())
                total_characters += 1
                progress = ((i + 1) / total_lines) * 100
                progress_label.config(text=f"Progress: {progress:.2f}%")
                if not random_speed:
                    update_estimated_time(keystroke_delay)
            current_char = 0  # Reset character position for the next line
        end_time = time.time()
        update_statistics()

def update_estimated_time(keystroke_delay):
    if not random_speed:
        remaining_characters = sum(len(line) for line in lines[current_line:])
        estimated_time = remaining_characters * (typing_speed +( keystroke_delay - 0.09))
        estimated_time_label.config(text=f"Estimated Time: {estimated_time:.2f}s")
        

def on_key_release(key):
    global typing_thread_running
    if key == keyboard.Key.esc:
        typing_thread_running = False
        print("Stopping typing...")
        sys.exit()  # Exit the script when the Escape key is released

def select_file():
    global typing_file
    typing_file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    file_label.config(text=f"Selected File: {typing_file}")

def start_typing():
    global typing_thread_running, countdown_running, current_line, current_char
    if typing_file:
        countdown_running = True
        countdown(countdown_time)
        typing_thread_running = True
        typing_thread_obj = threading.Thread(target=typing_thread)
        typing_thread_obj.start()
    else:
        countdown_label.config(text="Please select a file first.")

def pause_typing():
    global typing_thread_running
    typing_thread_running = False
    countdown_label.config(text="Typing paused.")

def resume_typing():
    global typing_thread_running, countdown_running
    if typing_file:
        countdown_running = True
        countdown(countdown_time)
        typing_thread_running = True
        typing_thread_obj = threading.Thread(target=typing_thread)
        typing_thread_obj.start()
    else:
        countdown_label.config(text="Please select a file first.")

def kill_typing():
    global typing_thread_running
    typing_thread_running = False
    countdown_label.config(text="Typing killed.")
    sys.exit()

def update_speed(value):
    global typing_speed
    typing_speed = float(value)

def update_error_rate(value):
    global error_rate
    error_rate = float(value)

def countdown(seconds):
    global countdown_running
    countdown_label.config(text=f"Typing starts in {seconds} seconds...")
    if seconds > 0:
        root.after(1000, countdown, seconds - 1)
    else:
        countdown_label.config(text="Typing started!")
        countdown_running = False

def update_statistics():
    duration = end_time - start_time
    wpm = (total_characters / 5) / (duration / 60)
    accuracy = ((total_characters - total_errors) / total_characters) * 100
    statistics_label.config(text=f"WPM: {wpm:.2f} | Accuracy: {accuracy:.2f}% | Time: {duration:.2f}s")

def toggle_random_speed():
    global random_speed
    random_speed = random_speed_var.get()
    if random_speed:
        estimated_time_label.config(text="Estimated Time: N/A")
    else:
        update_estimated_time()

def get_typing_speed():
    if random_speed:
        return random.uniform(0.01, 1.0)  # Choose a random speed between 0.01 and 1.0 for each letter
    else:
        return typing_speed


def update_language(lang):
    global language
    language = lang

def toggle_preprocess_text():
    global preprocess_text
    preprocess_text = not preprocess_text

def preprocess_line(line):
    # Remove URLs
    line = re.sub(r'http\S+', '', line)
    # Remove special characters
    line = re.sub(r'[^\w\s]', '', line)
    # Convert to lowercase
    line = line.lower()
    # Normalize Unicode characters
    line = unicodedata.normalize('NFKD', line).encode('ascii', 'ignore').decode('utf-8')
    return line

root = tk.Tk()
root.title("Auto Typer")

# Make the GUI window appear in front of everything else
root.attributes("-topmost", True)

random_speed_var = tk.BooleanVar()
file_button = tk.Button(root, text="Select File", command=select_file)
file_label = tk.Label(root, text="No file selected.")
speed_label = tk.Label(root, text="Typing Speed:")
speed_slider = tk.Scale(root, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, command=update_speed)
error_label = tk.Label(root, text="Error Rate:")
error_slider = tk.Scale(root, from_=0.0, to=0.2, resolution=0.01, orient=tk.HORIZONTAL, command=update_error_rate)
start_button = tk.Button(root, text="Start", command=start_typing)
pause_button = tk.Button(root, text="Pause", command=pause_typing)
resume_button = tk.Button(root, text="Resume", command=resume_typing)
kill_button = tk.Button(root, text="Kill", command=kill_typing)
language_label = tk.Label(root, text="Language:")
language_var = tk.StringVar(value=language)
language_menu = tk.OptionMenu(root, language_var, "English", "Spanish", "French", "German", command=update_language)
preprocess_button = tk.Button(root, text="Preprocess Text", command=toggle_preprocess_text)
random_speed_checkbox = tk.Checkbutton(root, text="Random Speed", variable=random_speed_var, command=toggle_random_speed)
countdown_label = tk.Label(root, text="")
progress_label = tk.Label(root, text="Progress: 0%")
statistics_label = tk.Label(root, text="WPM: 0.00 | Accuracy: 0.00% | Time: 0.00s")
estimated_time_label = tk.Label(root, text="Estimated Time: 0.00s")


file_button.pack()
file_label.pack()
speed_label.pack()
speed_slider.pack()
error_label.pack()
error_slider.pack()
start_button.pack()
pause_button.pack()
resume_button.pack()
kill_button.pack()
language_label.pack()
language_menu.pack()
preprocess_button.pack()
random_speed_checkbox.pack()
countdown_label.pack()
progress_label.pack()
statistics_label.pack()
estimated_time_label.pack()

if __name__ == "__main__":
    listener = keyboard.Listener(on_release=on_key_release)
    listener.start()
    root.mainloop()