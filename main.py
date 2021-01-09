from bokeh.models import TextInput
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import os
from random import randint

Builder.load_file('interface.kv')  # incarcam fisierul .kv ce contine layout-ul


class CheckResponse:
    pass


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

    def build(self):  # construim interfata
        return self

    # mapam butoanele
    def playAudio(self):
        self.audio = PlayAudio.playAudio(self, self.audio)

    def stopAudio(self):
        self.audio = StopAudio.stopAudio(self, self.audio)


if __name__ == '__main__':  # ruleaza numai atunci cand asta e fisierul principal
    Core().run()  # rulam kivy
