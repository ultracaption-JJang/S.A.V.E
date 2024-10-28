import asyncio
import httpx
import kivy
kivy.require('2.1.0')

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner
from gtts import gTTS  # gTTS 임포트
import os
import time

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
                source: '/Users/macbook/무제 폴더/S.A.V.E/S.A.V.E-3/client/assets/16.png'  # 배경 이미지 경로
                size: self.size
                pos: self.pos

        Image:
            source: "/Users/macbook/무제 폴더/S.A.V.E/S.A.V.E-3/client/assets/12.png"  # PNG 파일 경로
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            size_hint: (0.8, 0.8)

        MDRectangleFlatButton:
            text: "Start"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            on_release: app.go_to_second_screen()

<SecondScreen>:
    name: 'second'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 20
        canvas.before:
            Rectangle:
                source: '/Users/macbook/무제 폴더/S.A.V.E/S.A.V.E-3/client/assets/16.png'  # 배경 이미지 경로
                size: self.size
                pos: self.pos

        Image:
            source: '/Users/macbook/무제 폴더/S.A.V.E/S.A.V.E-3/client/assets/12.png'
            size_hint: (1, 0.15)
            allow_stretch: True

        BoxLayout:
            size_hint: (1, 0.5)
            Camera:
                id: cam_display
                resolution: (640, 480)
                play: True
                allow_stretch: True

        MDTextField:
            id: caption_text
            hint_text: "Generated Caption"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            readonly: True

        MDRectangleFlatButton:
            text: "Generate Caption"
            pos_hint: {"center_x": 0.5}
            on_release: app.capture_and_generate_caption()
"""

class FirstScreen(Screen):
    pass

class SecondScreen(Screen):
    pass

class MyApp(MDApp):
    sound = None
    is_playing = False
    spinner = None

    def build(self):
        return Builder.load_string(kv)

    def go_to_second_screen(self):
        self.root.current = 'second'
        second_screen = self.root.get_screen('second')
        camera = second_screen.ids.cam_display
        if camera:
            camera.play = True

    def on_stop(self):
        second_screen = self.root.get_screen('second')
        camera = second_screen.ids.cam_display
        if camera:
            camera.play = False

    def capture_and_generate_caption(self):
        second_screen = self.root.get_screen('second')
        if not self.spinner:
            self.spinner = MDSpinner(
                size_hint=(None, None),
                size=(46, 46),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=True
            )
            second_screen.add_widget(self.spinner)
        
        Clock.schedule_once(lambda dt: asyncio.run(self.perform_caption_generation()))

    async def perform_caption_generation(self, *args):
        second_screen = self.root.get_screen('second')
        camera = second_screen.ids.cam_display
        
        if camera:
            timestr = time.strftime("%Y%m%d_%H%M%S")
            file_path = f"IMG_{timestr}.png"
            camera.export_to_png(file_path)
            print(f"Image captured and saved at {file_path}")
            
            try:
                async with httpx.AsyncClient() as client:
                    with open(file_path, "rb") as image_file:
                        response = await client.post(
                            "http://112.161.7.178:8000/generate-caption/",
                            files={"file": image_file}
                        )
                        
                        if response.status_code == 200:
                            caption = response.json().get("caption", "")
                            caption_field = second_screen.ids.caption_text
                            caption_field.text = caption
                            print(caption)

                            # 캡션을 TTS로 변환
                            self.speak(caption, frame_count=timestr)

                        else:
                            print("Failed to get caption from server:", response.text)
            
            except Exception as e:
                print("Error uploading image:", e)

        if self.spinner:
            second_screen.remove_widget(self.spinner)
            self.spinner = None

    def speak(self, text, frame_count):
        # TTS 결과를 고유한 파일 이름으로 저장
        save_dir = "./voices"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filename = os.path.join(save_dir, f"mp3_{frame_count}.mp3")
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        # 음성 파일 재생
        os.system(f"afplay {filename}") 

MyApp().run()