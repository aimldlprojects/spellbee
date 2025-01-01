from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
import pandas as pd
import random
import os
from datetime import datetime

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

    def build(self):
        self.load_word_list()

        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Left panel for dropdowns
        left_panel = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
        toggle_button = ToggleButton(text="Options", size_hint=(1, 0.1), state="normal")
        dropdown_panel = BoxLayout(orientation="vertical", size_hint=(1, 0.9))

        self.user_dropdown = DropDown()
        self.test_type_dropdown = DropDown()
        self.word_type_dropdown = DropDown()
        self.word_length_dropdown = DropDown()

        user_button = Button(text="Select User", size_hint=(1, None), height=44, background_color=(0.3, 0.6, 0.9, 1))
        test_type_button = Button(text="Select Test Type", size_hint=(1, None), height=44, background_color=(0.3, 0.6, 0.9, 1))
        word_type_button = Button(text="Select Word Type", size_hint=(1, None), height=44, background_color=(0.3, 0.6, 0.9, 1))
        word_length_button = Button(text="Select Word Length", size_hint=(1, None), height=44, background_color=(0.3, 0.6, 0.9, 1))
        start_test_button = Button(text="Start Test", size_hint=(1, None), height=44, background_color=(0.3, 0.7, 0.5, 1))

        user_button.bind(on_release=self.user_dropdown.open)
        test_type_button.bind(on_release=self.test_type_dropdown.open)
        word_type_button.bind(on_release=self.word_type_dropdown.open)
        word_length_button.bind(on_release=self.word_length_dropdown.open)
        start_test_button.bind(on_release=self.start_test)

        self.populate_dropdown(self.user_dropdown, self.word_list_all['user'].unique(), self.set_user)
        self.populate_dropdown(self.test_type_dropdown, ["Unattended Words", "Previous Incorrectly Spelled Words", "Words Practiced a Week Ago"], self.set_test_type)

        dropdown_panel.add_widget(user_button)
        dropdown_panel.add_widget(test_type_button)
        dropdown_panel.add_widget(word_type_button)
        dropdown_panel.add_widget(word_length_button)
        dropdown_panel.add_widget(start_test_button)

        scroll_view = ScrollView()
        scroll_view.add_widget(dropdown_panel)

        toggle_button.bind(on_press=lambda instance: self.toggle_panel(instance, dropdown_panel))
        left_panel.add_widget(toggle_button)
        left_panel.add_widget(scroll_view)

        # Main body
        body_layout = BoxLayout(orientation="vertical", size_hint=(0.7, 1))

        self.input_field = TextInput(hint_text="Enter the spelling here", multiline=False, size_hint=(1, 0.1))
        body_layout.add_widget(self.input_field)

        self.status_label = Label(text="Welcome to SpellBee!", size_hint=(1, 0.8))
        body_layout.add_widget(self.status_label)

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

    def populate_dropdown(self, dropdown, items, callback):
        for item in items:
            btn = Button(text=str(item), size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.on_dropdown_select(dropdown, btn.text, callback))
            dropdown.add_widget(btn)

    def on_dropdown_select(self, dropdown, text, callback):
        dropdown.dismiss()
        callback(text)

    def set_user(self, user_id):
        self.user_id = user_id
        self.correct_words_file = f"user_{user_id}_correct_words.csv"
        self.incorrect_words_file = f"user_{user_id}_incorrect_words.csv"
        self.ensure_user_files()
        self.load_user_data()

        # Display selected user with cross mark
        self.update_selected_user_display(user_id)

    def update_selected_user_display(self, user_id):
        self.user_dropdown.clear_widgets()  # Clear the dropdown menu
        grid = GridLayout(cols=2, size_hint_y=None, height=44)  # User name and cross icon layout
        label = Label(text=user_id, size_hint_x=0.9)
        cross_button = Button(text="❌", size_hint_x=0.1, on_press=lambda instance: self.clear_selected_user())

        grid.add_widget(label)
        grid.add_widget(cross_button)
        self.user_dropdown.add_widget(grid)

    def clear_selected_user(self):
        self.user_id = ""
        self.user_dropdown.clear_widgets()  # Reset dropdown to original state
        self.populate_dropdown(self.user_dropdown, self.word_list_all['user'].unique(), self.set_user)

    def set_test_type(self, test_type):
        self.test_type = test_type
        self.apply_filters()

    def load_user_data(self):
        self.word_list_user = self.word_list_all[self.word_list_all['user'] == self.user_id]

    def ensure_user_files(self):
        if not os.path.exists(self.correct_words_file):
            pd.DataFrame(columns=["user", "word", "timestamp", "word_type"]).to_csv(self.correct_words_file, index=False)
        if not os.path.exists(self.incorrect_words_file):
            pd.DataFrame(columns=["user", "word", "timestamp", "word_type"]).to_csv(self.incorrect_words_file, index=False)

    def apply_filters(self):
        if self.test_type == "Unattended Words":
            correct_words = pd.read_csv(self.correct_words_file)
            review_words = pd.read_csv(self.review_words_file)
            self.word_list_test_type = self.word_list_user[~self.word_list_user['word'].isin(correct_words['word']) & ~self.word_list_user['word'].isin(review_words['review_word'])]
        elif self.test_type == "Previous Incorrectly Spelled Words":
            incorrect_words = pd.read_csv(self.incorrect_words_file)
            review_words = pd.read_csv(self.review_words_file)
            self.word_list_test_type = incorrect_words[~incorrect_words['word'].isin(review_words['review_word'])]
        elif self.test_type == "Words Practiced a Week Ago":
            correct_words = pd.read_csv(self.correct_words_file)
            incorrect_words = pd.read_csv(self.incorrect_words_file)
            review_words = pd.read_csv(self.review_words_file)
            one_week_ago = datetime.now() - pd.Timedelta(days=7)
            practiced_words = pd.concat([correct_words, incorrect_words])
            practiced_words['timestamp'] = pd.to_datetime(practiced_words['timestamp'])
            self.word_list_test_type = practiced_words[(practiced_words['timestamp'] < one_week_ago) & ~practiced_words['word'].isin(review_words['review_word'])]

        if 'word_type' in self.word_list_test_type.columns:
            self.populate_dropdown(self.word_type_dropdown, self.word_list_test_type['word_type'].unique(), self.set_word_type)
        else:
            self.word_list_test_type = pd.DataFrame()

    def set_word_type(self, word_type):
        self.word_type = word_type
        self.word_list_word_type = self.word_list_test_type[self.word_list_test_type['word_type'] == word_type]
        self.populate_dropdown(self.word_length_dropdown, self.word_list_word_type['word'].str.len().unique(), self.set_word_length)

    def set_word_length(self, word_length):
        self.word_length = int(word_length)
        self.word_list_word_len = self.word_list_word_type[self.word_list_word_type['word'].str.len() == self.word_length]
        self.current_word_list = self.word_list_word_len['word'].unique().tolist()

    def start_test(self, instance):
        random.shuffle(self.current_word_list)
        self.next_word()

    def next_word(self, instance=None):
        if self.current_word_list:
            self.current_word = self.current_word_list.pop()
            masked_word = '*' * len(self.current_word)
            self.status_label.text = f"Spell this word: {masked_word}"
            sound_file = f"{self.current_word}.mp3"
            if os.path.exists(sound_file):
                sound = SoundLoader.load(sound_file)
                if sound:
                    sound.play()
        else:
            self.status_label.text = "No more words to practice!"

    def check_spelling(self, instance):
        user_input = self.input_field.text.strip()
        if user_input.lower() == self.current_word.lower():
            self.status_label.text = "Correct!"
            self.update_correct_words()
        else:
            self.status_label.text = f"Incorrect! The correct spelling is: {self.current_word}"
            self.update_incorrect_words()
        self.input_field.text = ""

    def update_correct_words(self):
        correct_words = pd.read_csv(self.correct_words_file)
        new_entry = pd.DataFrame({"user": [self.user_id], "word": [self.current_word], "timestamp": [datetime.now()], "word_type": [self.word_type]})
        correct_words = pd.concat([correct_words, new_entry], ignore_index=True)
        correct_words.to_csv(self.correct_words_file, index=False)

    def update_incorrect_words(self):
        incorrect_words = pd.read_csv(self.incorrect_words_file)
        new_entry = pd.DataFrame({"user": [self.user_id], "word": [self.current_word], "timestamp": [datetime.now()], "word_type": [self.word_type]})
        incorrect_words = pd.concat([incorrect_words, new_entry], ignore_index=True)
        incorrect_words.to_csv(self.incorrect_words_file, index=False)

    def review_word(self, instance):
        review_words = pd.read_csv(self.review_words_file)
        new_entry = pd.DataFrame({"user": [self.user_id], "review_word": [self.current_word], "word_type": [self.word_type]})
        review_words = pd.concat([review_words, new_entry], ignore_index=True)
        review_words.to_csv(self.review_words_file, index=False)

if __name__ == "__main__":
    SpellBeeApp().run()
