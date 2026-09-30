from asyncio import sleep
import os
from matplotlib import text
from ultralytics import YOLO
import numpy as np
import pyttsx3
import speech_recognition as sr
import ollama
import re
from ollama import chat
def remove_emojis(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F" 
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

jarvi = pyttsx3.init()
recognizer = sr.Recognizer()
jarvi.setProperty('voice', 'com.apple.speech.synthesis.voice.sinji')
jarvi.setProperty('rate', 230)
recognizer.pause_threshold = 0.6
recognizer.energy_threshold = 300


#JARVIS

def listen_for_command():
    try:
        audio = recognizer.listen(
            source,
            timeout=None,
            phrase_time_limit=10)
        try:
            prompt = recognizer.recognize_google(audio)
            print(prompt)
            return prompt
        
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print("Error with speech recognition", e)
            return ""
    except Exception as e:
        print("Error listening for command:", e)
        return ""

name = "Jarvis"
with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Jarvis is ready")
        while True:
            text = listen_for_command()

            if not text:
                continue
            if name.lower() not in text.lower():
                continue
            command = text.lower().replace(name.lower(), "").strip()
            if not command:
                jarvi.say("Yes?")
                jarvi.runAndWait()
                continue
            print("Command:", command)

            try:
                response = ollama.chat(
                    model='gemma3:1b',
                    messages=[
                    {
                        'role': 'user',
                        'content': command,
                        }
                    ],
                    options={
                        'temperature': 0.1
                    }
                )


                answer = response['message']['content']
                real_answer = remove_emojis(answer)
                print(real_answer)
                jarvi.say(real_answer) 
                jarvi.runAndWait()

            except Exception as e:
                print("Error processing command:", e)
                jarvi.say("I am not sure what you mean. Please try again.")
                jarvi.runAndWait()

