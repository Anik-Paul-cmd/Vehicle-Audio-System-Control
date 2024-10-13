import pyaudio
import wave
import numpy as np
import tkinter as tk
from tkinter import Scale, Label

volume_level = 1.0
left_right_balance, front_rear_fade = 0.0, 0.0 

def adjust_audio(audio_data, num_audio_channels):
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    audio_array = audio_array.reshape((-1, num_audio_channels))
    
    if num_audio_channels == 2:
        left_channel, right_channel = audio_array[:, 0] * (1 - left_right_balance), audio_array[:, 1] * (1 + left_right_balance)
        
        audio_array[:, 0], audio_array[:, 1]  = left_channel, right_channel
        
    audio_array = audio_array * (1 - np.abs(front_rear_fade))
    audio_array = audio_array * volume_level
    audio_array = np.clip(audio_array, -32768, 32767)

    return audio_array.astype(np.int16).tobytes()

def play_audio_file(audio_file_path):
    try:
        wave_file = wave.open(audio_file_path, 'rb')
        audio_stream = pyaudio.PyAudio()
        stream = audio_stream.open(format=audio_stream.get_format_from_width(wave_file.getsampwidth()),
                                   channels=wave_file.getnchannels(),
                                   rate=wave_file.getframerate(),
                                   output=True)
        
        buffer_size = 1024
        audio_data = wave_file.readframes(buffer_size)
        
        while audio_data:
            processed_audio = adjust_audio(audio_data, wave_file.getnchannels())
            stream.write(processed_audio)
            audio_data = wave_file.readframes(buffer_size)
        
        stream.stop_stream()
        stream.close()
        audio_stream.terminate()

    except FileNotFoundError:
        print(f"Error: The file {audio_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def set_volume_level(value):
    global volume_level
    volume_level = float(value) / 100

def set_left_right_balance(value):
    global left_right_balance
    left_right_balance = float(value) / 100

def set_front_rear_fade(value):
    global front_rear_fade
    front_rear_fade = float(value) / 100

def create_audio_gui():
    window = tk.Tk()
    window.title("Vehicle Audio System Control")

    volume_label = Label(window, text="Volume")
    volume_label.pack()
    volume_slider = Scale(window, from_=0, to=100, orient='horizontal', command=set_volume_level)
    volume_slider.set(100)
    volume_slider.pack()

    balance_label = Label(window, text="Balance (L-R)")
    balance_label.pack()
    balance_slider = Scale(window, from_=-100, to=100, orient='horizontal', command=set_left_right_balance)
    balance_slider.set(0)
    balance_slider.pack()

    fade_label = Label(window, text="Fade (F-R)")
    fade_label.pack()
    fade_slider = Scale(window, from_=-100, to=100, orient='horizontal', command=set_front_rear_fade)
    fade_slider.set(0)
    fade_slider.pack()

    play_button = tk.Button(window, text="Play Audio", command=lambda: play_audio_file("audio.wav")) 
    play_button.pack()

    window.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_audio_gui()
