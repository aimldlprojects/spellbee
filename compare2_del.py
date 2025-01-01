from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image

class SpellBeeApp(App):
    ...
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
