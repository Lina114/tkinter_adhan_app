import tkinter as tk
from tkinter import ttk
import requests
import datetime
import time
import pygame
import arabic_reshaper
from bidi.algorithm import get_display
import customtkinter as ctk
import threading

pygame.mixer.init()

# Global variables to store timings and prayers
timings = {}
prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

# Function to fetch prayer times
def fetch_prayer_times():
    global timings
    now = datetime.datetime.today().strftime("%d-%m-%Y")
    resp = requests.get(url=f'http://api.aladhan.com/v1/timingsByCity/{now}?city=Algiers&country=Algeria&method=8')
    response_dict = resp.json()
    timings = response_dict['data']['timings']
    date2 = response_dict['data']['date']['hijri']['date']
    return now, date2, timings

# Function to display Arabic text
def display_arabic_text():
    arabic_text1 = ' اليوم '
    arabic_text2 = ' الموافق لـ'
    reshaped_text1 = arabic_reshaper.reshape(arabic_text1)
    reshaped_text2 = arabic_reshaper.reshape(arabic_text2)
    bidi_text1 = get_display(reshaped_text1)
    bidi_text2 = get_display(reshaped_text2)
    label_ar1.configure(text=bidi_text1)
    label_ar2.configure(text=bidi_text2)

# Function to update time
def update_time():
    current_time = time.strftime("%H:%M:%S")
    time_var.set(current_time)
    window.after(1000, update_time)

# Function to calculate time left for next prayer
def time_left():
    current_time = datetime.datetime.now().time()
    next_prayer_time = None
    next_prayer_name = None
    for prayer in prayers:
        prayer_time = datetime.datetime.strptime(timings[prayer], "%H:%M").time()
        if prayer_time > current_time:
            next_prayer_time = prayer_time
            next_prayer_name = prayer
            break

    if next_prayer_time:
        now = datetime.datetime.now()
        next_prayer_datetime = datetime.datetime.combine(now.date(), next_prayer_time)
        time_diff = next_prayer_datetime - now
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{next_prayer_name}: {hours:02}:{minutes:02}:{seconds:02}"
    else:
        time_left_str = "No more prayers for today"

    time_left_var.set(time_left_str)
    window.after(1000, time_left)

# Function to check time and play adhan
def check_time():
    current_time = time.strftime("%H:%M")
    if current_time in timings.values():
        show_popup()
        play_sound()
    window.after(60000, check_time)  # Check every minute

# Function to play sound
def play_sound():
    pygame.mixer.music.load("adhan.mp3")
    pygame.mixer.music.play()

# Function to stop sound
def stop_sound():
    pygame.mixer.music.stop()

# Function to show popup
def show_popup():
    popup = ctk.CTkToplevel()
    popup.title("Adhan Time")

    label = ctk.CTkLabel(popup, text='It is now time for Prayer.', font=ctk.CTkFont(size=16, weight="bold"))
    label.pack(pady=10)

    close_button = ctk.CTkButton(popup, text="Close", command=lambda: (stop_sound(), popup.destroy()))
    close_button.pack(pady=5)

# Function to run the application
def run_app():
    global now, date2
    now, date2, _ = fetch_prayer_times()

    # Initialize the main window with customtkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    global window
    window = ctk.CTk()
    window.title('Prayer Times')
    window.geometry("600x280")

    # Frame for Gregorian date labels
    gregorian_frame = ctk.CTkFrame(window)
    gregorian_frame.pack(pady=10)

    label_en1 = ctk.CTkLabel(gregorian_frame, text=f"Today is: {now} ", font=ctk.CTkFont(size=16, weight="bold"))
    label_en1.pack(side=tk.LEFT, padx=10)

    label_en2 = ctk.CTkLabel(gregorian_frame, text=f"corresponding to: {date2}", font=ctk.CTkFont(size=16, weight="bold"))
    label_en2.pack(side=tk.LEFT, padx=10)

    # Frame for Arabic date labels (Part 1)
    arabic_frame1 = ctk.CTkFrame(window)
    arabic_frame1.pack(pady=1)

    global label_ar1, label_ar2
    label_ar1 = ctk.CTkLabel(arabic_frame1, font=ctk.CTkFont(size=16, weight="bold"))
    label_ar1.pack(side=tk.RIGHT, padx=10)

    label_var1 = ctk.CTkLabel(arabic_frame1, text=f"{now} ", font=ctk.CTkFont(size=16, weight="bold"))
    label_var1.pack(side=tk.RIGHT, padx=10)

    label_ar2 = ctk.CTkLabel(arabic_frame1, font=ctk.CTkFont(size=16, weight="bold"))
    label_ar2.pack(side=tk.RIGHT, padx=10)

    label_var2 = ctk.CTkLabel(arabic_frame1, text=f"{date2} ", font=ctk.CTkFont(size=16, weight="bold"))
    label_var2.pack(side=tk.RIGHT, padx=10)

    display_arabic_text()

    global time_var
    time_var = tk.StringVar()
    time_label = ctk.CTkLabel(window, textvariable=time_var, font=ctk.CTkFont(size=45, weight="bold"), text_color="green")
    time_label.pack(pady=5)

    update_time()

    # Frame for prayer times
    prayer_frame = ctk.CTkFrame(window)
    prayer_frame.pack(pady=10, padx=10, fill="both")

    # Display prayer times in a horizontal grid layout with colors
    for index, prayer in enumerate(prayers):
        prayer_name_label = ctk.CTkLabel(prayer_frame, text=prayer, font=ctk.CTkFont(size=16, weight="bold"))
        prayer_name_label.grid(row=0, column=index, padx=10, pady=5, sticky="n")

        prayer_time_label = ctk.CTkLabel(prayer_frame, text=timings[prayer], font=ctk.CTkFont(size=16), bg_color="#D5DBDB", text_color="#000000")
        prayer_time_label.grid(row=1, column=index, padx=10, pady=5, sticky="n")

        # Ensure each column has equal width
        prayer_frame.columnconfigure(index, weight=1)

    global time_left_var
    time_left_var = tk.StringVar()

    # Frame for left time labels
    left_time_frame = ctk.CTkFrame(window)
    left_time_frame.pack(pady=10)

    time_left_label_text = ctk.CTkLabel(left_time_frame, text="Time left for : ", font=ctk.CTkFont(size=16, weight="bold"))
    time_left_label_text.pack(padx=10, side=tk.LEFT)

    time_left_label = ctk.CTkLabel(left_time_frame, textvariable=time_left_var, font=ctk.CTkFont(size=16, weight="bold"), text_color="#800000")
    time_left_label.pack(padx=10, side=tk.LEFT)

    time_left()

    check_time()

    window.mainloop()

# Function to update prayer times daily
def update_daily():
    while True:
        now = datetime.datetime.now()
        if now.hour == 0 and now.minute == 0:  # Check at midnight
            fetch_prayer_times()
        time.sleep(60)

# Main function to run the application and daily updater in separate threads
def main():
    app_thread = threading.Thread(target=run_app)
    daily_update_thread = threading.Thread(target=update_daily)

    app_thread.start()
    daily_update_thread.start()

if __name__ == "__main__":
    main()
