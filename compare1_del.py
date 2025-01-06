from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.checkbox import CheckBox

class SelectableLabel(BoxLayout):
    def __init__(self, value, parent_widget, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.value = value
        self.parent_widget = parent_widget
        self.label = Label(text=str(value))
        self.remove_button = Button(text='X', size_hint=(None, 1), width=30)
        self.remove_button.bind(on_release=self.remove_self)
        self.add_widget(self.label)
        self.add_widget(self.remove_button)

    def remove_self(self, instance):
        self.parent_widget.selected_values.remove(self.value)
        self.parent_widget.update_display()
        for option, chk_with_label in self.parent_widget.checkboxes.items():
            if chk_with_label.text == self.value:
                chk_with_label.chkbox.active = False
                break

class CheckBoxWithLabel(BoxLayout):
    active = BooleanProperty(False)

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.lbl = Label(text=text)
        self.chkbox = CheckBox()
        self.add_widget(self.chkbox)
        self.add_widget(self.lbl)
        self.chkbox.bind(active=self.on_checkbox_active)

    def on_checkbox_active(self, instance, value):
        self.active = value

    @property
    def text(self):
        return self.lbl.text

class MultiSelectDropDown(BoxLayout):
    selected_values = ListProperty([])
    popup = None
    checkboxes = {}

    def __init__(self, options, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.options = options
        self.main_button = Button(text='Select Options', size_hint_y=None, height=44)
        self.main_button.bind(on_release=self.show_popup)
        self.add_widget(self.main_button)

        self.selected_labels_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        self.add_widget(self.selected_labels_layout)

    def show_popup(self, instance):
        if self.popup is None:
            self.popup = Popup(title='Select Options', size_hint=(0.8, 0.6))
            popup_content = BoxLayout(orientation='vertical')

            for option in self.options:
                chk_with_label = CheckBoxWithLabel(text=option)
                self.checkboxes[option] = chk_with_label
                chk_with_label.chkbox.bind(active=self.update_selected_values)
                popup_content.add_widget(chk_with_label)

            close_button = Button(text='Close', size_hint_y=None, height=44)
            close_button.bind(on_release=self.popup.dismiss)
            popup_content.add_widget(close_button)
            self.popup.content = popup_content
        else:
            for option, chk_with_label in self.checkboxes.items():
                chk_with_label.chkbox.active = option in self.selected_values
        self.popup.open()

    def update_selected_values(self, instance, value):
        for option, chk_with_label in self.checkboxes.items():
            if chk_with_label.chkbox == instance:
                text = chk_with_label.text
                if value:
                    if text not in self.selected_values:
                        self.selected_values.append(text)
                        self.update_display()
                else:
                    if text in self.selected_values:
                        self.selected_values.remove(text)
                        self.update_display()
                return

    def update_display(self):
        self.selected_labels_layout.clear_widgets()
        for value in self.selected_values:
            selectable_label = SelectableLabel(value=value, parent_widget=self)
            self.selected_labels_layout.add_widget(selectable_label)

        if not self.selected_values:
            self.main_button.text = "Select Options"
        else:
            self.main_button.text = ", ".join(self.selected_values)



class MyApp(App):
    def build(self):
        options = ["SciFi", "Action", "Comedy", "Thriller", "Animated", "Adventure"]
        return MultiSelectDropDown(options=options)

if __name__ == '__main__':
    MyApp().run()