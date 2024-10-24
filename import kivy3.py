import kivy
kivy.require('2.1.0')

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.core.audio import SoundLoader  # Import for audio playback

Window.size = (296, 536)  # 앱 창 크기 설정

# kv 파일로 정의된 UI 구조
kv = """
ScreenManager:
    FirstScreen:
    SecondScreen:

<FirstScreen>:
    name: 'first'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Rectangle:
                source: '/Users/macbook/Downloads/16.png'  # 배경 이미지 경로
                size: self.size
                pos: self.pos

        Image:
            source: "/Users/macbook/Downloads/12.png"  # PNG 파일 경로
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            size_hint: (0.8, 0.8)

        MDRectangleFlatButton:
            text: "Start"
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            on_release: app.go_to_second_screen()

<SecondScreen>:
    name: 'second'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 20
        canvas.before:
            Rectangle:
                source: '/Users/macbook/Downloads/16.png'  # 배경 이미지 경로
                size: self.size
                pos: self.pos

        Image:
            source: '/Users/macbook/Downloads/12.png'
            size_hint: (1, 0.15)
            allow_stretch: True

        BoxLayout:
            size_hint: (1, 0.5)
            Image:
                id: img_display
                source: '/Users/macbook/Downloads/13.jpg'
                allow_stretch: True
                keep_ratio: True

        MDTextField:
            id: caption_text
            hint_text: "Generated Caption"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            readonly: True

        MDRectangleFlatButton:
            text: "Generate Caption"
            pos_hint: {"center_x": 0.5}
            on_release: app.generate_caption()

        MDRectangleFlatButton:
            id: sound_btn
            text: "Play Sound"
            pos_hint: {"center_x": 0.5}
            on_release: app.play_sound()
"""

class FirstScreen(Screen):
    pass

class SecondScreen(Screen):
    pass

class MyApp(MDApp):
    sound = None
    is_playing = False  # 상태 플래그 추가

    def build(self):
        # kv 파일 로드
        return Builder.load_string(kv)

    def go_to_second_screen(self):
        # 첫 번째 화면에서 두 번째 화면으로 이동
        self.root.current = 'second'

    def generate_caption(self):
        # 두 번째 화면에서 caption_text 위젯 찾기
        second_screen = self.root.get_screen('second')

        # ids를 사용하여 caption_text를 참조
        caption_field = second_screen.ids.get('caption_text')
        if caption_field:
            caption_field.text = "The light is red, please stop!!"  # 생성된 캡션 설정
        else:
            print("MDTextField with id 'caption_text' not found")

    def play_sound(self):
        # MP3 파일 재생/정지 기능
        if not self.sound:
            self.sound = SoundLoader.load('/Users/macbook/Downloads/audio_feedback.mp3')  # MP3 파일 경로
        
        if self.sound:
            if not self.is_playing:
                self.sound.play()
                self.is_playing = True
                self.root.get_screen('second').ids.sound_btn.text = "Pause Sound"  # 버튼 텍스트 변경
            else:
                self.sound.stop()
                self.is_playing = False
                self.root.get_screen('second').ids.sound_btn.text = "Play Sound"  # 버튼 텍스트 변경
        else:
            print("Failed to load sound file")

MyApp().run()