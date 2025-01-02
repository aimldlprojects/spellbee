from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import pandas as pd
import random
import os
from datetime import datetime

class SelectableLabel(BoxLayout):
    value = ObjectProperty(None)

    def __init__(self, value, dropdown, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.value = value
        self.dropdown = dropdown
        self.label = Label(text=str(value))
        self.remove_button = Button(text="X", size_hint=(None, 1), width=30)
        self.remove_button.bind(on_release=self.remove_self)
        self.add_widget(self.label)
        self.add_widget(self.remove_button)

    def remove_self(self, instance):
        self.parent.remove_widget(self)
        self.dropdown.values.append(self.value)
        self.dropdown.values.sort()
        self.dropdown.text = "Select an option"

class SpellBeeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word_list_all = pd.DataFrame()
        self.word_list_user = pd.DataFrame()
        self.word_list_test_type = pd.DataFrame()
        self.word_list_word_type = pd.DataFrame()
        self.word_list_word_len = pd.DataFrame()
        self.current_word_list = []
        self.user_id = ""
        self.test_type = ""
        self.word_type = ""
        self.word_length = ""
        self.current_word = ""
        self.correct_words_file = ""
        self.incorrect_words_file = ""
        self.review_words_file = "review_words.csv"
        self.timer = None
        self.time_remaining = 0
        self.time_limit_per_word = 30

    def build(self):
        self.load_word_list()

        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Left panel for dropdowns
        left_panel = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
        toggle_button = ToggleButton(text="Options", size_hint=(1, 0.1), state="normal")
        dropdown_panel = BoxLayout(orientation="vertical", size_hint=(1, 0.9))

        self.dropdown = DropDown()
        self.dropdown.values = list(range(1, 11))
        self.dropdown.text = "Select an option"

        user_button = Button(text="Select User", size_hint=(1, None), height=44, background_color=(0.3, 0.6, 0.9, 1))
        user_button.bind(on_release=self.dropdown.open)

        for value in self.dropdown.values:
            btn = Button(text=str(value), size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        
        self.selected_values_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=44)

        self.dropdown.bind(on_select=lambda instance, x: self.update_selected_values(x))

        dropdown_panel.add_widget(user_button)
        dropdown_panel.add_widget(self.selected_values_layout)

        toggle_button.bind(on_press=lambda instance: self.toggle_panel(instance, dropdown_panel))
        left_panel.add_widget(toggle_button)
        left_panel.add_widget(dropdown_panel)

        # Main body
        body_layout = BoxLayout(orientation="vertical", size_hint=(0.7, 1))

        self.input_field = TextInput(hint_text="Enter the spelling here", multiline=False, size_hint=(1, 0.1))
        body_layout.add_widget(self.input_field)

        self.status_label = Label(text="Welcome to SpellBee!", size_hint=(1, 0.7))
        body_layout.add_widget(self.status_label)

        self.timer_label = Label(text="", size_hint=(1, 0.1))
        body_layout.add_widget(self.timer_label)

        # Buttons at the bottom
        button_layout = BoxLayout(size_hint=(1, 0.1))

        check_button = Button(text="Check", size_hint=(0.25, 1))
        next_button = Button(text="Next Word", size_hint=(0.25, 1))
        review_button = Button(text="Review Word", size_hint=(0.25, 1))

        check_button.bind(on_release=self.check_spelling)
        next_button.bind(on_release=self.next_word)
        review_button.bind(on_release=self.review_word)

        button_layout.add_widget(check_button)
        button_layout.add_widget(next_button)
        button_layout.add_widget(review_button)

        body_layout.add_widget(button_layout)

        # Combine left panel and main body
        app_layout = BoxLayout(orientation="horizontal")
        app_layout.add_widget(left_panel)
        app_layout.add_widget(body_layout)

        return app_layout

    def update_selected_values(self, value):
        if value != "Select an option":
            if int(value) in self.dropdown.values:
                self.dropdown.values.remove(int(value))
                self.dropdown.text = "Select an option"
                selectable_label = SelectableLabel(value=int(value), dropdown=self.dropdown)
                self.selected_values_layout.add_widget(selectable_label)


    def toggle_panel(self, instance, panel):
        panel.size_hint_y = 0 if panel.size_hint_y else 0.9

    def load_word_list(self):
        if os.path.exists("word_list_all.csv"):
            self.word_list_all = pd.read_csv("word_list_all.csv")
            required_columns = ["user", "word", "word_type"]
            for column in required_columns:
                if column not in self.word_list_all.columns:
                    raise KeyError(f"Missing required column: '{column}' in word_list_all.csv")
        else:
            self.word_list_all = pd.DataFrame(columns=["user", "word", "word_type", "chunked_sentence", "masked_chunked_sentence", "example_sentence", "masked_example_sentence", "openai_sentence", "masked_openai_sentence"])

        if not os.path.exists(self.review_words_file):
            pd.DataFrame(columns=["user", "review_word", "word_type", "chunked_sentence", "example_sentence", "openai_sentence"]).to_csv(self.review_words_file, index=False)


    def check_spelling(self, instance):
        pass

    def next_word(self, instance):
        pass

    def review_word(self, instance):
        pass

if __name__ == "__main__":
    SpellBeeApp().run()
