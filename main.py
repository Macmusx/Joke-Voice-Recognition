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

Builder.load_file('interface.kv')  # incarcam fisierul .kv ce contine layout-ul


class Engine:
    def checkResponse(self, audio, rec):
        if 'audio_files' in audio.source:  # o verificare probabil inutila (verific daca se afla in folderul care
            # trebuie)
            jsonParam = 'audio_files' + audio.source.split('audio_files')[-1]  # obtin denumirea lui (cum a fost numit
            # in json)
            response = json.load(open('responseMap.json'))[jsonParam]  # citesc fisierul json si iau valoarea care imi
            # trebuie
            sf.write('temp.wav', rec, 44000)  # creez un fisier audio temporal cu ce am zis -> deoarece nu stiu cum se
            # poate transforma in tipul Audio Data
            recognizer = sr.Recognizer()  # initializez o instanta de Recognizer

            while True:
                if os.path.exists('temp.wav'):  # astept pana se termina fisierul de generat
                    break

            file_read = sr.AudioFile('temp.wav')  # citesc fisierul -> astfel devenint de tipul Audio Data
            with file_read:
                source = recognizer.record(file_read)  # inregistrez ce e in fisierul audio
                try:
                    text = recognizer.recognize_google(source,
                                                       language='ro-RO')  # folosesc serviciile de la google pentru
                    # a vedea ce am zis
                    Terminal.showText(self, 'Ati spus: ' + text)  # afisam text-ul
                    # transformam diacriticile in litere normale pentru a putea compara cu raspunsul trecut in json
                    # am decis de la inceput sa nu folosim diacritice pentru a detecta cu mai multa precizie raspunsul
                    text = re.sub(r'/șȘ/gm', 's', text)
                    text = re.sub(r'/ăĂ/gm', 'a', text)
                    text = re.sub(r'/îÎ/gm', 'i', text)
                    text = re.sub(r'/âÂ/gm', 'a', text)
                    text = re.sub(r'/țȚ/gm', 't', text)

                    # verificam daca e raspunsul bun
                    if response.lower() in text.lower():  # transformam toate literele mari in litere mici si verificam
                        # daca raspunsul spus contine raspunsul corect pentru a asigura o mai mare corectitudine
                        Terminal.showText(self, 'Raspuns Corect!!')
                    else:
                        Terminal.showText(self, 'Raspuns Gresit!!')
                except:
                    Terminal.showText(self, 'Nu s-a putut recunoaste ce ati spus')  # afisam text-ul
        else:
            Terminal.showText(self, 'ERROR: Fisierul nu se afla in locul bun')


class Respond(Button, Widget):
    def respond(self, audio):
        if audio:
            if self.recording:  # verific daca nu cumva se inregistreaza deja
                Terminal.showText(self, 'WARRNING: Deja se inregistreaza!')
                return

            Terminal.showText(self, 'A inceput inregistrarea')
            self.ids.respond.color = (0, 1, 0, 1)  # fac textul verde
            audio.stop()  # opresc orice audio care mai rula
            self.recording = True

            duration = 3  # secunde
            fs = 44000  # frecventa

            rec = sd.rec(int(duration * fs), samplerate=fs, channels=2)  # ma apuc sa inregistrez
            Timer(3.0, Respond.finished, (self, audio, rec)).start()  # pornesc un timer de 3 secunde dupa care sa zic
            # ca inregistrarea s-a terminat
        else:
            Terminal.showText(self, 'ERROR: Nu s-a redat nici un fisier audio!')

    def finished(self, audio, rec):
        self.ids.respond.color = (1, 1, 1, 1)  # fac textul butonului inapoi
        sd.wait()  # astept putin in caz ca nu a apucat inregistrarea sa se termine
        self.recording = False
        Terminal.showText(self, 'S-a terminat inregistrarea')
        Engine.checkResponse(self, audio, rec)  # verific raspunsul


class StopAudio(Button):
    def stopAudio(self, audio):
        if audio:
            if audio.state == 'play':  # daca este redat ceva audio opresc
                audio.stop()
            else:
                Terminal.showText(self, 'WARNING: In momentul de fata nu este redat nici un fisier audio!')
        else:
            Terminal.showText(self, 'WARNING: In momentul de fata nu este redat nici un fisier audio!')
        return audio


class Terminal(TextInput):
    def showText(self, text):  # metoda pentru afisarea unui text in input text
        if self.ids.terminal.text == '':  # verific daca exista ceva pentru a nu adauga un rand gol la inceput
            self.ids.terminal.text = text  # pun textul sa se afiseze in consola
        else:
            self.ids.terminal.text = self.ids.terminal.text + '\n' + text  # afisez textul pe urmatorul rand


class PlayAudio(Button):
    def playAudio(self, audio):
        if audio:
            audio.stop()  # in cazul in care inca se da play la un fisier audio il oprim
        audio_files = os.listdir('audio_files')  # obtinem lista de fisiere audio
        if audio_files.__len__() == 0:  # in caz ca nu gasim nici un fisier audio dam eroare
            Terminal.showText(self, 'ERROR: Nu exista fisiere audio in folder-ul audio_files!')  # afisez mesaj de
            # eroare in terminal
            return audio
        file_chosen = audio_files[randint(0, audio_files.__len__() - 1)]  # alegem un fisier audio random
        audio = SoundLoader.load('audio_files/' + file_chosen)  # incarcam fisierul audio in kivy
        if audio:
            audio.play()  # dam play la fisierul audio daca s-a incarcat corect
            Terminal.showText(self, 'S-a dat play la fisierul audio ' + file_chosen)
            return audio
        else:
            Terminal.showText(self, 'ERROR: Nu s-a putut incarca fisierul audio ' + file_chosen + '!')  # afisam
            # mesaj de eroare in caz ca nu s-a incarcat fisierul audio corect
            return audio


class Core(BoxLayout, App):
    audio = None
    recording = False

    def build(self):  # construim interfata
        return self

    # mapam butoanele
    def playAudio(self):
        if self.recording:  # verificam daca nu cumva se inregistreaza, in cazul caruia nu avem voie sa facem alte
            # modificari
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


if __name__ == '__main__':  # ruleaza numai atunci cand asta e fisierul principal
    Core().run()  # rulam kivy
