from bokeh.models import TextInput
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget

import os
import json
import re
from threading import Timer
from random import randint
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

Builder.load_file('interface.kv')

class Engine:
    def checkResponse(self, audio, rec):
        if 'audio_files' in audio.source:
            jsonParam = 'audio_files' + audio.source.split('audio_files')[-1]
            response = json.load(open('responseMap.json'))[jsonParam]
            sf.write('temp.wav', rec, 44000)
            recognizer = sr.Recognizer()

            while True:
                if os.path.exists('temp.wav'):
                    break

            file_read = sr.AudioFile('temp.wav')
            with file_read:
                source = recognizer.record(file_read)
                try:
                    text = recognizer.recognize_google(source,
                                                       language='ro-RO')
                    Terminal.showText(self, 'Ati spus: ' + text)
                    text = re.sub(r'/șȘ/gm', 's', text)
                    text = re.sub(r'/ăĂ/gm', 'a', text)
                    text = re.sub(r'/îÎ/gm', 'i', text)
                    text = re.sub(r'/âÂ/gm', 'a', text)
                    text = re.sub(r'/țȚ/gm', 't', text)

                    if response.lower() in text.lower():
                        Terminal.showText(self, 'Raspuns Corect!!')
                    else:
                        Terminal.showText(self, 'Raspuns Gresit!!')
                except:
                    Terminal.showText(self, 'Nu s-a putut recunoaste ce ati spus')
        else:
            Terminal.showText(self, 'ERROR: Fisierul nu se afla in locul bun')


class Respond(Button, Widget):
    def respond(self, audio):
        if audio:
            if self.recording:
                Terminal.showText(self, 'WARNING: Deja se inregistreaza!')
                return

            Terminal.showText(self, 'A inceput inregistrarea')
            self.ids.respond.color = (0, 1, 0, 1)
            audio.stop()
            self.recording = True

            duration = 3
            fs = 44000

            rec = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            Timer(3.0, Respond.finished, (self, audio, rec)).start()
        else:
            Terminal.showText(self, 'ERROR: Nu s-a redat nici un fisier audio!')

    def finished(self, audio, rec):
        self.ids.respond.color = (1, 1, 1, 1)
        sd.wait()
        self.recording = False
        Terminal.showText(self, 'S-a terminat inregistrarea')
        Engine.checkResponse(self, audio, rec)


class StopAudio(Button):
    def stopAudio(self, audio):
        if audio:
            if audio.state == 'play':
                audio.stop()
            else:
                Terminal.showText(self, 'WARNING: In momentul de fata nu este redat nici un fisier audio!')
        else:
            Terminal.showText(self, 'WARNING: In momentul de fata nu este redat nici un fisier audio!')
        return audio


class Terminal(TextInput):
    def showText(self, text):
        if self.ids.terminal.text == '':
            self.ids.terminal.text = text
        else:
            self.ids.terminal.text = self.ids.terminal.text + '\n' + text


class PlayAudio(Button):
    def playAudio(self, audio):
        if audio:
            audio.stop()
        files = os.listdir('audio_files')

        audio_files = []
        for file in files:
            if ('.wav' in file) | ('.ogg' in file):
                audio_files.append(file)

        if audio_files.__len__() == 0:
            Terminal.showText(self, 'ERROR: Nu exista fisiere audio in folder-ul audio_files!')
            return audio

        file_chosen = audio_files[randint(0, audio_files.__len__() - 1)]
        audio = SoundLoader.load('audio_files/' + file_chosen)
        if audio:
            audio.play()
            Terminal.showText(self, 'S-a dat play la fisierul audio ' + file_chosen)
            return audio
        else:
            Terminal.showText(self, 'ERROR: Nu s-a putut incarca fisierul audio ' + file_chosen + '!')
            return audio


class Core(BoxLayout, App):
    audio = None
    recording = False

    def build(self):
        return self

    def playAudio(self):
        if self.recording:
            Terminal.showText(self, 'WARNING: Se inregistreaza!')
            return
        self.audio = PlayAudio.playAudio(self, self.audio)

    def stopAudio(self):
        if self.recording:
            Terminal.showText(self, 'WARNING: Se inregistreaza!')
            return
        self.audio = StopAudio.stopAudio(self, self.audio)

    def respond(self):
        Respond.respond(self, self.audio)


if __name__ == '__main__':
    Core().run()
