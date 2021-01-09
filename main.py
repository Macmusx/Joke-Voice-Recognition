from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import os
from random import randint

Builder.load_file('interface.kv')  # incarcam fisierul .kv ce contine layout-ul


class PlayAudio(Button):
    def playAudio(self):
        audio_files = os.listdir('audio_files')  # obtinem lista de fisiere audio
        if audio_files.__len__() == 0:  # in caz ca nu gasim nici un fisier audio dam eroare
            print('nup')  # todo create error handler
            return
        file_chosen = audio_files[randint(0, audio_files.__len__())]  # alegem un fisier audio random
        sound = SoundLoader.load('audio_files' + file_chosen)
        if sound:
            sound.play()
        else:
            print('nu mere')
            return


class Core(BoxLayout, App):
    def build(self):  # construim interfata
        return self

    def playAudio(self):
        PlayAudio.playAudio(self)


if __name__ == '__main__':  # ruleaza numai atunci cand asta e fisierul principal
    Core().run()  # rulam kivy
