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
from kivy.clock import Clock  # for scheduling
from kivymd.uix.spinner import MDSpinner

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
    spinner = None  # 로딩 스피너를 위한 변수 추가

    def build(self):
        # kv 파일 로드
        return Builder.load_string(kv)

    def go_to_second_screen(self):
        # 첫 번째 화면에서 두 번째 화면으로 이동
        self.root.current = 'second'

        # 두 번째 화면으로 이동할 때 카메라 자동 실행
        second_screen = self.root.get_screen('second')
        camera = second_screen.ids.cam_display
        if camera:
            camera.play = True  # 카메라 실행
    
    def on_stop(self):
        # 앱 종료 시 카메라 해제
        second_screen = self.root.get_screen('second')
        camera = second_screen.ids.cam_display
        if camera:
            camera.play = False  # 카메라 정지

    def capture_and_generate_caption(self):
        # 로딩 스피너 생성 및 추가
        second_screen = self.root.get_screen('second')
        if not self.spinner:
            self.spinner = MDSpinner(
                size_hint=(None, None),
                size=(46, 46),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=True
            )
            second_screen.add_widget(self.spinner)
        
        # 비동기 메서드를 Clock을 통해 호출
        Clock.schedule_once(lambda dt: asyncio.run(self.perform_caption_generation()))

    async def perform_caption_generation(self, *args):
        # 카메라의 현재 프레임을 캡처하고 서버로 전송하여 캡션을 생성
        second_screen = self.root.get_screen('second')
        camera = second_screen.ids.cam_display
        
        if camera:
            # 캡처한 이미지를 저장
            timestr = time.strftime("%Y%m%d_%H%M%S")
            file_path = f"IMG_{timestr}.png"
            camera.export_to_png(file_path)
            print(f"Image captured and saved at {file_path}")
            
            # 이미지 파일을 FastAPI 서버로 비동기 전송
            try:
                async with httpx.AsyncClient() as client:
                    with open(file_path, "rb") as image_file:
                        response = await client.post(
                            "https://ce4df9d2-7107-4d58-98f3-196be07fe3c2.mock.pstmn.io/generate_caption",  # 서버의 엔드포인트 URL
                            files={"file": image_file}
                        )
                        
                        # 서버 응답에서 캡션 받아서 표시
                        if response.status_code == 200:
                            caption = response.json().get("caption", "")
                            caption_field = second_screen.ids.caption_text
                            caption_field.text = caption
                            
                            # debug
                            print(caption)

                            # mp3 파일도 저장
                            sound = response.json().get("mp3", "")
                            
                            # debug
                            print(sound)

                        else:
                            print("Failed to get caption from server:", response.text)
            
            except Exception as e:
                print("Error uploading image:", e)


            # # 임시 저장된 이미지 파일 삭제
            # if os.path.exists(file_path):
            #     os.remove(file_path)

            # 캡션 필드를 업데이트
            # caption_field = second_screen.ids.caption_text
            # caption_field.text = "The light is red, please stop!!"  # 이미지에 대한 캡션 설정

        else:
            print("Camera widget not found")
        
        # 로딩 스피너 제거
        if self.spinner:
            second_screen.remove_widget(self.spinner)
            self.spinner = None

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