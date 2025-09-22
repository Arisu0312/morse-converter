import tkinter as tk
import pygame
import time
import threading
import sys
import os

morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',  'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--', 'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-','R': '.-.', 'S': '...',  'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--','Z': '--..',
    '1': '.----','2': '..---','3': '...--','4': '....-','5': '.....',
    '6': '-....','7': '--...','8': '---..','9': '----.','0': '-----',
    ' ': '/'
}
reverse_dict = {v: k for k, v in morse_dict.items()}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS 
    except AttributeError:
        base_path = os.path.abspath(".") 
    return os.path.join(base_path, relative_path)

pygame.mixer.init()
try:
    short_path = resource_path("short.wav")
    long_path = resource_path("long.wav")
    short_sound = pygame.mixer.Sound(short_path)
    long_sound = pygame.mixer.Sound(long_path)
except pygame.error:
    short_sound = None
    long_sound = None

mode = "text_to_morse"
press_start_time = None
space_timer = None 

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def update_output(text):
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, text)
    output_text.config(state="disabled")

def to_morse(text):
    return ' '.join(morse_dict.get(char.upper(), '?') for char in text)

def to_text(morse_code):
    return ''.join(reverse_dict.get(code, '?') for code in morse_code.strip().split())

def on_input(event=None):
    text = input_entry.get()
    if mode == "text_to_morse":
        converted = to_morse(text)
    else:
        converted = to_text(text)
    update_output(converted)

def copy_to_clipboard():
    morse_text = output_text.get("1.0", tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(morse_text)
    root.update()

def play_morse_sound():
    if not short_sound or not long_sound:
        return
    morse = output_text.get("1.0", tk.END).strip()
    sound_button.config(state="disabled")

    def play():
        for symbol in morse:
            if symbol == '.':
                short_sound.play()
                time.sleep(0.2)
            elif symbol == '-':
                long_sound.play()
                time.sleep(0.4)
            elif symbol == '/':
                time.sleep(0.4)
            elif symbol == ' ':
                time.sleep(0.2)
        sound_button.config(state="normal")

    threading.Thread(target=play).start()

def toggle_mode():
    global mode
    if mode == "text_to_morse":
        mode = "morse_to_text"
        mode_label.config(text="現在のモード：モールス → 英語")
        sound_button.pack_forget()
        key_button.pack(pady=5)
    else:
        mode = "text_to_morse"
        mode_label.config(text="現在のモード：英語 → モールス")
        sound_button.pack(pady=5)
        key_button.pack_forget()

    input_entry.delete(0, tk.END)
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.config(state="disabled")

def insert_space():
    input_entry.insert(tk.END, " ")
    on_input()

def reset_space_timer():
    global space_timer
    if space_timer:
        root.after_cancel(space_timer)
    space_timer = root.after(650, insert_space) 

def on_key_press(event):
    global press_start_time
    press_start_time = time.time()
    if space_timer:
        root.after_cancel(space_timer)

def on_key_release(event):
    global press_start_time
    if press_start_time is None:
        return
    duration = time.time() - press_start_time
    press_start_time = None
    if duration < 0.2:
        input_entry.insert(tk.END, ".")
    else:
        input_entry.insert(tk.END, "-")
    on_input()
    reset_space_timer()

def clear_column():
    input_entry.delete(0, tk.END)
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.config(state="disabled")

root = tk.Tk()
root.title("MorseConvert")
root.geometry("800x500")
root.iconbitmap(resource_path("ico.ico"))

mode_label = tk.Label(root, text="現在のモード：英語 → モールス", font=("Arial", 12))
mode_label.pack(pady=5)

input_entry = tk.Entry(root, font=("Arial", 16), width=40)
input_entry.pack(pady=10)
input_entry.bind("<KeyRelease>", on_input)

output_frame = tk.Frame(root)
output_frame.pack(pady=10)

output_text = tk.Text(output_frame, font=("Courier", 14), wrap="word", height=7, width=40)
output_text.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(output_frame, command=output_text.yview)
scrollbar.pack(side="right", fill="y")
output_text.config(yscrollcommand=scrollbar.set)
output_text.config(state="disabled")

toggle_button = tk.Button(root, text="モード切替", font=("Arial", 12), width=15, command=toggle_mode)
toggle_button.pack(pady=10)

copy_button = tk.Button(root, text="コピー", font=("Arial", 12), width=15, command=copy_to_clipboard)
copy_button.pack(pady=5)

clear_button = tk.Button(root, text="入力欄リセット", font=("Arial", 12), width=15, command=clear_column)
clear_button.pack(pady=5)

sound_button = tk.Button(root, text="音声再生", font=("Arial", 12), width=15, command=play_morse_sound)
sound_button.pack(pady=5)

key_button = tk.Button(root, text="Push (. / -)", font=("Arial", 12), width=15)
key_button.bind("<ButtonPress-1>", on_key_press)
key_button.bind("<ButtonRelease-1>", on_key_release)

key_button.pack_forget()

root.mainloop()
