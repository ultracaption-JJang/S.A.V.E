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
from kivy.graphics.texture import Texture
from kivy.clock import Clock  # for scheduling
from kivymd.uix.spinner import MDSpinner
from kivy.core.text import LabelBase
import cv2
from ultralytics import YOLO
import numpy as np
import os
import time
from collections import defaultdict
from gtts import gTTS  # Import gTTS for text-to-speech

# Register the custom font
LabelBase.register(name="NanumGothic", fn_regular="../assets/NanumGothic.ttf")

Window.size = (296, 536)  # 앱 창 크기 설정

# UI 구조 정의
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
                source: '../assets/16.png'
                size: self.size
                pos: self.pos

        Image:
            source: "../assets/12.png"
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            size_hint: (0.8, 0.8)

        MDRectangleFlatButton:
            text: "Start"
            font_name: "NanumGothic"
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            on_release: app.go_to_second_screen()

<SecondScreen>:
    name: 'second'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 20

        Image:
            id: cam_display
            size_hint: (1, 0.5)
            allow_stretch: True

        MDTextField:
            id: caption_text
            hint_text: "Generated Caption"
            font_name: "NanumGothic"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            readonly: True

        MDRectangleFlatButton:
            text: "Generate Caption"
            font_name: "NanumGothic"
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
    capture = None
    memory = {'previous_track_ids': []}  # 이전 track ID를 저장할 memory 변수 추가

    def build(self):
        return Builder.load_string(kv)

    def go_to_second_screen(self):
        self.root.current = 'second'
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

    def update_camera(self, dt):
        ret, frame = self.capture.read()
        track_history = defaultdict(lambda: [])
        if ret:
            model = YOLO("./checkpoints/yolo11n.pt")
            results = model.track(frame, persist=True)

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xywh.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
            else:
                boxes = []
                track_ids = []
            annotated_frame = results[0].plot()
            
            # 현재 프레임에서 새로운 객체를 찾기 위해 이전 트랙과 비교
            new_detections = list(set(track_ids) - set(self.memory['previous_track_ids']))
            
            if new_detections:
                warning_list = new_detections
                self.capture_and_generate_caption()  # 캡셔닝 생성

            # 현재 track_ids를 memory에 저장
            self.memory['previous_track_ids'] = track_ids

            # 트랙을 그려서 화면에 표시
            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))
                if len(track) > 30:
                    track.pop(0)

                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(
                    annotated_frame,
                    [points],
                    isClosed=False,
                    color=(230, 230, 230),
                    thickness=10,
                )

            buf = annotated_frame.tobytes()
            texture = Texture.create(size=(annotated_frame.shape[1], annotated_frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            texture.flip_vertical()
            self.root.get_screen('second').ids.cam_display.texture = texture

    def on_stop(self):
        if self.capture:
            self.capture.release()

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
            # frames 폴더가 없으면 생성
            os.makedirs("frames", exist_ok=True)
            # file_path를 frames 폴더 안에 저장되도록 설정
            file_path = f"./frames/IMG_{timestr}.png"
            camera.export_to_png(file_path)
            print(f"Image captured and saved at {file_path}")
            
            try:
                async with httpx.AsyncClient() as client:
                    with open(file_path, "rb") as image_file:
                        response = await client.post(
                            "https://ce4df9d2-7107-4d58-98f3-196be07fe3c2.mock.pstmn.io/generate_caption",
                            files={"file": image_file}
                        )
                        
                        if response.status_code == 200:
                            caption = response.json().get("caption", "")
                            caption_field = second_screen.ids.caption_text
                            caption_field.text = caption
                            print("Generated caption:", caption)

                            # Generate audio with gTTS and load it for immediate playback                            
                            tts = gTTS(text=caption, lang='en')

                            # frames 폴더가 없으면 생성
                            os.makedirs("voices", exist_ok=True)

                            audio_file = f"./voices/{timestr}_audio.mp3"
                            tts.save(audio_file)
                            self.sound = SoundLoader.load(audio_file)
                            print(f"Audio saved and loaded from {audio_file}")

                            # Automatically play the generated sound if successfully loaded
                            if self.sound:
                                self.sound.play()
                                self.is_playing = True
                                second_screen.ids.sound_btn.text = "Pause Sound"
                            else:
                                print("Error: Sound failed to load")
            
            except Exception as e:
                print("Error uploading image:", e)
        
        if self.spinner:
            second_screen.remove_widget(self.spinner)
            self.spinner = None

    def play_sound(self):
        if self.sound:
            if not self.is_playing:
                self.sound.play()
                self.is_playing = True
                self.root.get_screen('second').ids.sound_btn.text = "Pause Sound"
            else:
                self.sound.stop()
                self.is_playing = False
                self.root.get_screen('second').ids.sound_btn.text = "Play Sound"
        else:
            print("No sound loaded to play")

MyApp().run()