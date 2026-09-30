import re
import pyttsx3
import speech_recognition as sr
import ollama
from ollama import chat
import os

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
    "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

class JarvisBot:
    def __init__(self):
        self.jarvi = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        # Deine Einstellungen aus dem Skript
        self.jarvi.setProperty('voice', 'com.apple.speech.synthesis.voice.sinji')
        self.jarvi.setProperty('rate', 230)
        self.recognizer.pause_threshold = 0.6
        self.recognizer.energy_threshold = 300
        self.name = "Jarvis"

    def listen_for_command(self, source):
        try:
            audio = self.recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=10
            )
            try:
                prompt = self.recognizer.recognize_google(audio)
                prompt = self.recognizer.recognize_google(audio, language="en-US")
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

    def speak(self, text):
        clean_text = remove_emojis(text)
        print(clean_text)
        self.jarvi.say(clean_text)
        self.jarvi.runAndWait()

    def run(self, camera_tracker):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Jarvis is ready")
            
            while True:
                text = self.listen_for_command(source)

                if not text:
                    continue
                if self.name.lower() not in text.lower():
                    continue
                
                command = text.lower().replace(self.name.lower(), "").strip()
                if not command:
                    self.speak("Yes?")
                    continue

                print("Command:", command)

                # Aktuell erkannte Objekte aus der Kamera abfragen
                current_objects = camera_tracker.detected_objects
                objects_str = ", ".join(current_objects) if current_objects else "nothing detected"

                # System-Prompt übergeben, damit die KI weiß, was im Bild ist
                system_context = f"You are Jarvis. Your camera currently sees: {objects_str}. Use this information when the user asks about it."

                try:
                    response = ollama.chat(
                        model='gemma3:1b',
                        messages=[
                            {'role': 'system', 'content': system_context},
                            {'role': 'user', 'content': command}
                        ],
                        options={
                            'temperature': 0.1
                        }
                    )

                    answer = response['message']['content']
                    self.speak(answer)

                except Exception as e:
                    print("Error processing command:", e)
                    self.speak("I am not sure what you mean. Please try again.")