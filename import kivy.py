import kivy
import kivymd
import os
kivy.require('2.1.0')

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel

# 그라데이션 배경을 그리는 클래스
class GradientBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # 그라데이션 색상 설정 (위에서 아래로)
            Color(0.992, 0.902, 0.902, 1)  # #FDE6E6 (상단 색상)
            self.rect_top = Rectangle(size=self.size, pos=self.pos)
            Color(1, 1, 1, 1)  # #FFFFFF (하단 색상)
            self.rect_bottom = Rectangle(size=self.size, pos=self.pos)

            # 크기나 위치 변경 시 배경 업데이트
            self.bind(size=self.update_background, pos=self.update_background)

    def update_background(self, *args):
        self.rect_top.size = self.size
        self.rect_top.pos = self.pos
        self.rect_bottom.size = self.size
        self.rect_bottom.pos = self.pos


# 첫 번째 화면
class FirstScreen(Screen):
    pass

# 두 번째 화면
class SecondScreen(Screen):
    pass

class MainApp(MDApp):
    def build(self):
        # ScreenManager 생성
        self.screen_manager = ScreenManager()

        # 한글 폰트 경로 설정
        font_path = os.path.join(os.path.dirname(__file__), "/Users/macbook/Downloads/NanumGothic.ttf")

        # 첫 번째 화면에 그라데이션 배경 적용
        first_screen = FirstScreen(name="first")
        gradient_background = GradientBackground()
        first_screen.add_widget(gradient_background)

        # '세이브' 제목 추가
        first_screen.add_widget(
            MDLabel(
                text="세이브",
                halign="center",  # 중앙 정렬
                theme_text_color="Primary",
                font_style="H1",  # 굵은 글씨체
                font_name=font_path,  # 한글 폰트 경로
                pos_hint={"center_x": 0.5, "center_y": 0.7},  # 화면 중앙 상단에 배치
            )
        )

        # 첫 번째 화면에서 두 번째 화면으로 가는 버튼 추가
        first_screen.add_widget(
            MDRectangleFlatButton(
                text="Go to Second Screen",
                pos_hint={"center_x": 0.5, "center_y": 0.4},  # 제목 아래에 버튼 배치
                on_release=self.go_to_second_screen,  # 버튼 클릭 시 두 번째 화면으로 이동
            )
        )

        # 두 번째 화면
        second_screen = SecondScreen(name="second")
        second_screen.add_widget(
            MDRectangleFlatButton(
                text="Back to First Screen",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_release=self.go_to_first_screen,  # 버튼 클릭 시 첫 번째 화면으로 돌아가기
            )
        )

        # ScreenManager에 두 화면 추가
        self.screen_manager.add_widget(first_screen)
        self.screen_manager.add_widget(second_screen)

        return self.screen_manager

    def go_to_second_screen(self, instance):
        # 두 번째 화면으로 전환
        self.screen_manager.current = "second"

    def go_to_first_screen(self, instance):
        # 첫 번째 화면으로 돌아가기
        self.screen_manager.current = "first"


MainApp().run()