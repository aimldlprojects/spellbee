import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import random
from datetime import datetime, timedelta

from gtts import gTTS
from playsound import playsound
import os
import tempfile

class MultiSelectDropdown:
    def __init__(self, parent, options, **kwargs):
        self.parent = parent
        self.options = options
        self.selected_options = set()  # Use a set for easier add/remove operations

        self.var = tk.StringVar()
        self.entry = ttk.Entry(self.parent, textvariable=self.var, **kwargs)
        self.entry.grid(row=4, column=1, padx=(0, 0), pady=5)  # Set column span to 2

        # Create a button with a dropdown icon
        self.dropdown_button = ttk.Button(self.parent, text=u"\u25BE", command=self.toggle_dropdown)
        self.dropdown_button.grid(row=4, column=1, padx=(100, 0), pady=5)  # Place in column 3

        # Resize the dropdown button
        self.dropdown_button.config(width=1, style='small.TButton')  # Adjust width and font size as needed

        self.dropdown = None
        self.listbox = None

    def create_dropdown(self):
        self.dropdown = tk.Toplevel(self.parent)
        self.dropdown.transient(self.parent)
        self.dropdown.grab_set()

        # Positioning
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.dropdown.geometry(f"+{x}+{y}")

        self.listbox = tk.Listbox(self.dropdown, selectmode='multiple', exportselection=False)
        self.listbox.pack(fill='both', expand=True)

        for option in self.options:
            self.listbox.insert('end', option)
            if option in self.selected_options:
                self.listbox.selection_set(self.options.index(option))

        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        self.dropdown.bind('<FocusOut>', self.on_focus_out)

    def toggle_dropdown(self, event=None):
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
            self.dropdown = None
        else:
            self.create_dropdown()

    def on_focus_out(self, event=None):
        # Do not hide the dropdown automatically on focus out to allow manual deselection
        pass

    def on_listbox_select(self, event=None):
        # Get list of currently selected options
        newly_selected_options = {self.options[i] for i in self.listbox.curselection()}
        
        # Update the selected options based on current selection
        self.selected_options = newly_selected_options

        # Refresh the text displayed in the entry widget
        self.refresh_entry()

    def refresh_entry(self):
        sorted_list = sorted(self.selected_options, key=self.options.index)
        sorted_list_as_str = [str(item) for item in sorted_list]  # Convert all items to strings
        selected_text = ', '.join(sorted_list_as_str)
        self.var.set(selected_text)

class SpellingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spell Bee App")
        self.root.geometry("700x500")  # Set window size to 800x600 for more space

        # Placeholder for existing user IDs, you might want to load these from a file or database
        self.existing_user_ids = ['Bhavi', 'Madhu', 'User']  # Example user IDs

        # Load word list
        self.word_list = pd.read_csv("word_list.csv")
        self.word_list.to_csv("word_list_all.csv", mode='a', header=False, index=False)
        self.word_list_all = pd.read_csv("word_list_all.csv")
        self.word_list_all = self.word_list_all.drop_duplicates(ignore_index = True)
        self.word_list_all.columns = ["word", "word_type"]
        self.word_list_all.to_csv("word_list_all.csv", index=False)

        self.current_word = tk.StringVar()
        self.user_input = tk.StringVar()
        self.user_id_var = tk.StringVar()

        self.correct_count = 0
        self.wrong_count = 0
        self.total_correct_count = 0
        self.total_wrong_count = 0
        self.auto_advance = tk.BooleanVar(value=False)  # Default to not automatically advancing
        self.auto_hide_test_options = tk.BooleanVar(value=False)

        self.test_options_frame = ttk.Frame(self.root)
        self.test_options_frame.pack(padx=10, pady=10)
        # Setup the MultiSelectDropdown for Word Length options
        self.setup_gui()

    def get_user_id(self):
        # Retrieve and return the current value selected in the user ID combobox
        return self.user_id_var.get()
    
    def on_enter_pressed(self, event=None):
        # This function will be called when Enter is pressed
        self.check_spelling()

    def pronounce_current_word(self):
        current_word = self.current_word.get()  # Assuming this is how you access the word to be spelled
        tts = gTTS(text=current_word, lang='en')
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            temp_filename = fp.name + '.mp3'
            tts.save(temp_filename)
            playsound(temp_filename)
            os.remove(temp_filename)  # Clean up the temporary file

    def setup_gui(self):
        # Configure the main window's style
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # Customizing widget styles
        self.style.configure('TLabel', font=('Helvetica', 14))
        self.style.configure('TButton', font=('Helvetica', 12), background='#f0f0f0')
        self.style.configure('TEntry', font=('Helvetica', 12), fieldbackground='#f0f0f0')
        self.style.configure('TCombobox', font=('Helvetica', 12), fieldbackground='#f0f0f0')
        self.style.configure('Bold.TCheckbutton', font=('Helvetica', 12, 'bold'))  # Configure a bold style for checkbuttons

        # Main content frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar separator
        separator = ttk.Separator(main_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Side panel for test options
        side_panel = ttk.Frame(main_frame, width=200)  # Define the width of the side panel
        side_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Hide checkbox
        auto_hide_checkbox = ttk.Checkbutton(
            side_panel,
            text="Hide Test Options",
            variable=self.auto_hide_test_options,
            onvalue=True,
            offvalue=False,
            command=self.toggle_test_options_visibility,
            style='Bold.TCheckbutton'  # Apply the bold style
        )
        auto_hide_checkbox.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Test options frame
        self.test_options_frame = ttk.Frame(side_panel)
        self.test_options_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        # Test options label
        test_options_label = ttk.Label(self.test_options_frame, text="Test Options", font=('Helvetica', 14))
        test_options_label.grid(row=0, column=0, sticky="w")

        # Auto Advance checkbox
        auto_advance_checkbox = ttk.Checkbutton(
            self.test_options_frame,
            text="Auto Advance to Next Word",
            variable=self.auto_advance,
            onvalue=True,
            offvalue=False
        )
        auto_advance_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Combobox for selecting test type
        test_type_label = ttk.Label(self.test_options_frame, text="Test Type:", font=('Helvetica', 10))
        test_type_label.grid(row=2, column=0, sticky="w", padx=(5, 2))
        self.test_type = ttk.Combobox(self.test_options_frame, values=["Unattended Words", "Incorrectly spelled words", "Words practiced a week ago"], state="readonly")
        self.test_type.grid(row=2, column=1, padx=(0, 5), pady=5)
        self.test_type.current(0)


        # Combobox for selecting word type
        word_type_label = ttk.Label(self.test_options_frame, text="Word Type:", font=('Helvetica', 10))
        word_type_label.grid(row=3, column=0, sticky="w", padx=(5, 2))
        self.word_type = ttk.Combobox(self.test_options_frame, values=["All"]+list(self.word_list['word_type'].unique()))
        self.word_type.grid(row=3, column=1, padx=(0, 5), pady=5)
        self.word_type.current(0)  # Assuming you want the first item as default


        # # Combobox for length options
        # length_options_label = ttk.Label(self.test_options_frame, text="Word Length:", font=('Helvetica', 10))
        # length_options_label.grid(row=4, column=0, sticky="w", padx=(5, 2))
        # self.length_options = ttk.Combobox(self.test_options_frame, values=["All"]+list(range(1, 11)), state="normal")
        # self.length_options.grid(row=4, column=1, padx=(0, 5), pady=5)  # Adjust to use grid
        # self.length_options.current(0)  # Assuming you want the first item as default
        length_options_label = ttk.Label(self.test_options_frame, text="Word Length:", font=('Helvetica', 10))
        length_options_label.grid(row=4, column=0, sticky="w", padx=(5, 2))

        # Define your length options, assuming you want lengths from 1 to 10
        self.length_options = ["All"] + list(range(1, 11))

        # Instantiate MultiSelectDropdown
        self.length_options_dropdown = MultiSelectDropdown(self.test_options_frame, options=self.length_options)
        # Note: The MultiSelectDropdown class already handles its own layout, so no need to grid/pack it again here


        # Combobox for selecting user
        user_id_label = ttk.Label(self.test_options_frame, text="User ID:", font=('Helvetica', 10))
        user_id_label.grid(row=5, column=0, sticky="w", padx=(5, 2))
        self.user_id = ttk.Combobox(self.test_options_frame, textvariable=self.user_id_var, values=self.existing_user_ids, state="readonly")
        self.user_id.grid(row=5, column=1, padx=(0, 5), pady=5)
        self.user_id.set('Select User')  # Set a placeholder or instruction text

        # Start test button
        ttk.Button(self.test_options_frame, text="Start Test", command=self.start_test).grid(row=6, column=0, padx=5, pady=5)

        # App title
        ttk.Label(main_frame, text="Welcome to Spell Bee App", font=('Helvetica', 18)).pack(pady=20)

        # Instruction label
        ttk.Label(main_frame, text="Type the spelling of the pronounced word:").pack()

        # Dedicated frame for the "Hear Word" button and status message
        self.dynamic_frame = ttk.Frame(main_frame)
        self.dynamic_frame.pack(pady=(5, 20))  # Adjust as needed

        # "Hear Word" button in the dynamic frame
        ttk.Button(self.dynamic_frame, text="Hear Word", command=self.pronounce_current_word).pack(side=tk.LEFT, padx=(10, 5))

        # Placeholder frame for status message with a fixed height
        self.status_frame = ttk.Frame(main_frame)  # Adjust height as needed
        self.status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Display current word to spell
        #ttk.Label(main_frame, textvariable=self.current_word, font=('Helvetica', 16)).pack(pady=10)

        # User input entry
        # ttk.Entry(main_frame, textvariable=self.user_input, font=('Helvetica', 14)).pack(pady=10)
        user_input_entry = ttk.Entry(main_frame, textvariable=self.user_input, font=('Helvetica', 14))
        user_input_entry.pack(pady=10)
        user_input_entry.bind('<Return>', self.on_enter_pressed)

        # Frame for check and next buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)  # Add some padding to separate from the entry widget

        # Check button with delayed pronunciation
        ttk.Button(button_frame, text="Check", command=lambda: [self.check_spelling()]).pack(side=tk.LEFT, padx=5)

        # Next word button with delayed pronunciation
        ttk.Button(button_frame, text="Next Word", command=lambda: [self.next_word()]).pack(side=tk.LEFT)

        # Display stats
        current_scores_text = f"Current Test Scores: Correct - {self.correct_count},      Wrong - {self.wrong_count}"
        total_scores_text = f"Total     Test Scores: Correct - {self.total_correct_count},      Wrong - {self.total_wrong_count}" 
        self.status_label = ttk.Label(main_frame, text=f"{current_scores_text}\n{total_scores_text}", font=('Helvetica', 10))
        self.status_label.pack(pady=10)

    def toggle_test_options_visibility(self):
        if self.auto_hide_test_options.get():
            # Hide test options
            self.test_options_frame.grid_remove()
        else:
            # Show test options
            self.test_options_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

    def start_test(self):
        user_id = self.get_user_id()
        # Check if a user ID is selected
        if self.user_id_var.get() == 'Select User' or self.user_id_var.get() == '':
            messagebox.showerror("User ID Required", "Please select a User ID to start the test.")
            return
        #previous test scores
        tot_correct_words_filename = f"user_{user_id}_correct_words.csv"
        tot_incorrect_words_filename = f"user_{user_id}_incorrect_words.csv"
        tot_correct_words_df = pd.read_csv(tot_correct_words_filename)
        tot_incorrect_words_df = pd.read_csv(tot_incorrect_words_filename)
        self.total_correct_count = tot_correct_words_df.shape[0]
        self.total_wrong_count = tot_incorrect_words_df.shape[0]

        test_type_filter = self.test_type.get()
        # Get the selected length options
        selected_lengths = self.length_options_dropdown.selected_options

        # Check if "All" is in the selected options
        if "All" in selected_lengths:
            self.words_for_test = self.word_list
        else:
            # Filter the dataframe based on the selected length options
            self.words_for_test = self.word_list[self.word_list['word'].apply(lambda x: len(x)).isin(selected_lengths)]

        # if length_option.isdigit():
        #     selected_length = int(length_option)
        #     self.words_for_test = self.word_list[self.word_list['word'].apply(len) <= selected_length]
        # elif length_option == "All":
        #     self.words_for_test = self.word_list

        if test_type_filter == "Unattended Words":
            # Define the filename based on the user_id
            filename = f"user_{user_id}_correct_words.csv"
            # Specify the column names since the CSV file is being appended without headers
            cols = ['user_id', 'word', 'datetime']
            # Read the CSV file into a DataFrame with the correct column names
            try:
                correct_words_df = pd.read_csv(filename, names=cols)
            except FileNotFoundError:
                # If the file doesn't exist, there are no words to exclude
                correct_words_df = pd.DataFrame(columns=cols)
            # Filter out the correctly answered words from self.words_for_test
            self.words_for_test = self.words_for_test[~(self.words_for_test['word'].isin(correct_words_df['word']))]

        elif test_type_filter == "Previous incorrectly spelled words":
            # Load previous incorrect words from CSV (if any)
            try:
                self.words_for_test = pd.read_csv("previous_incorrect_words.csv")
            except FileNotFoundError:
                self.words_for_test = pd.DataFrame(columns=['word'])  # Empty DataFrame if file doesn't exist
        elif test_type_filter == "Words practiced a week ago":
            week_ago = datetime.now() - timedelta(weeks=1)
            self.words_for_test = self.word_list[self.word_list['last_practiced'] == week_ago.strftime('%Y-%m-%d')]
        else:
            self.words_for_test = pd.DataFrame()  # Empty DataFrame for default
        self.words_for_test = self.words_for_test['word'].tolist()
        self.next_word()

    def check_spelling(self):
        # Implementation remains the same as previous
        correct_word = self.current_word.get()
        user_word = self.user_input.get()
        user_id = self.get_user_id()
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if user_word.strip().lower() == correct_word.strip().lower():
            # If spelling is correct, remove the word from the list
            if correct_word in self.words_for_test:
                self.words_for_test.remove(correct_word)
            self.correct_count += 1
            self.total_correct_count += 1  # Increment total correct count
            self.update_status("Correct!", "green", 500)
            #save file for each user
            filename = f"user_{user_id}_correct_words.csv"
            pd.DataFrame({'user_id': [user_id], 'word': [correct_word], 'datetime': [current_datetime]}).to_csv(filename, mode='a', header=False, index=False)
        else:
            self.wrong_count += 1
            self.total_wrong_count += 1  # Increment total wrong count
            self.update_status(f"Wrong! Correct spelling is: \n\n\t   {correct_word}", "red", 5000)
            #save file for each user
            filename = f"user_{user_id}_incorrect_words.csv"
            pd.DataFrame({'user_id': [user_id], 'word': [correct_word], 'datetime': [current_datetime]}).to_csv(filename, mode='a', header=False, index=False)

    def next_word(self):
        # Implementation remains the same as previous
        if self.words_for_test:
            # Clear any existing status messages first
            for widget in self.status_frame.winfo_children():
                widget.destroy()
            # Optionally, maintain the space with an empty label if desired
            ttk.Label(self.status_frame).pack()
            
            self.current_word.set(random.choice(self.words_for_test))
            self.pronounce_current_word()
        else:
            self.current_word.set("No more words for the test")
            self.pronounce_current_word()

    def update_status(self, message, color, status_time):
        # Clear the status frame of any widgets
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        # Create and pack a new status label within the status frame
        self.status_message = ttk.Label(self.status_frame, text=message, foreground=color)
        self.status_message.pack()

        # Schedule removal of the status message after 2 seconds
        def clear_status():
            self.status_message.destroy()
            # Optionally create an empty label to preserve the space
            ttk.Label(self.status_frame).pack()
            
        # Update the status label
        current_scores_text = f"Current Test Scores: Correct - {self.correct_count},      Wrong - {self.wrong_count}"
        total_scores_text = f"Total     Test Scores: Correct - {self.total_correct_count},      Wrong - {self.total_wrong_count}"
        self.status_label.config(text=f"{current_scores_text}\n{total_scores_text}", font=('Helvetica', 10))

        self.user_input.set("")

        if self.auto_advance.get():  # Check if auto-advance is enabled
            # After 2 seconds, proceed to the next word
            self.root.after(status_time, clear_status)
            # Introduce a delay before advancing to the next word if needed
            self.root.after(status_time+500, self.next_word)  # Adjust the delay as needed
        else:
            # Do not automatically advance to the next word
            pass



# The main part of the program
if __name__ == "__main__":
    root = tk.Tk()
    app = SpellingTestApp(root)
    root.mainloop()