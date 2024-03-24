#!/usr/bin/python3

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
        # Initialize the parent widget, available options, and selected options
        self.parent = parent
        self.options = options
        self.selected_options = {self.options[0]} if options else set()

        # Create a StringVar to track the entry text
        self.var = tk.StringVar()

        # Create the entry widget to display selected options
        self.entry = ttk.Entry(self.parent, textvariable=self.var, **kwargs)
        self.entry.grid(row=5, column=1, padx=(0, 9), pady=5, sticky="ew")

        # Create a button with a dropdown icon
        self.dropdown_button = ttk.Button(self.parent, text=u"\u25BE", command=self.toggle_dropdown, width=1)
        self.dropdown_button.grid(row=5, column=1, padx=(120, 0), pady=1)  # Place in column 3

        # Resize the dropdown button
        self.dropdown_button.config(style='Padded.TButton', padding=(0, 0, 0, 0))  # Adjust width and font size as needed

        # Initialize dropdown and listbox
        self.dropdown = None
        self.listbox = None
        self.popup_opened = False

        # Update the entry field with selected options
        self.refresh_entry()

    def create_dropdown(self):
        if self.dropdown:
            return  # Avoid creating multiple instances

        # Create a dropdown window
        self.dropdown = tk.Toplevel(self.parent)
        self.dropdown.overrideredirect(True)  # No window decorations

        # Position the dropdown window below the entry
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.dropdown.geometry(f"+{x}+{y}")

        # Create a listbox to display options
        self.listbox = tk.Listbox(self.dropdown, selectmode='multiple', exportselection=False)
        self.listbox.pack(fill='both', expand=True)

        # Insert available options into the listbox
        for option in self.options:
            self.listbox.insert('end', option)

            # Set the selected options in the listbox
            if option in self.selected_options:
                self.listbox.selection_set(self.options.index(option))

        # Bind events
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        self.dropdown.bind("<FocusOut>", self.on_focus_out)

        self.parent.bind("<1>", self.global_click)

        self.dropdown.focus_set()
        self.popup_opened = True
        print('create', self.dropdown)

    def destroy_dropdown(self):
        """
        Destroy the dropdown and unbind the global click event.
        """
        if self.dropdown is not None:
            self.dropdown.destroy()
            self.dropdown = None
            # Unbind the global click event to clean up
            self.parent.unbind("<1>")
        self.popup_opened = False
        print('distroy', self.dropdown)

    def toggle_dropdown(self):
        # Toggle the dropdown visibility
        print('toggle',self.dropdown)
        if self.popup_opened:
            self.destroy_dropdown()
        else:
            self.create_dropdown()

    def global_click(self, event):
        """
        Close the dropdown if the click occurred outside of it.
        """
        if self.popup_opened:
            if not (self.dropdown.winfo_containing(event.x_root, event.y_root) or 
                    self.dropdown_button.winfo_containing(event.x_root, event.y_root)):
                self.destroy_dropdown()

    def on_focus_out(self, event=None):
        # Keep the dropdown open on focus out
        pass

    def on_listbox_select(self, event=None):
        # Update selected options based on listbox selection
        newly_selected_options = {self.options[i] for i in self.listbox.curselection()}
        self.selected_options = newly_selected_options

        # Refresh the entry field to display selected options
        self.refresh_entry()

    def refresh_entry(self):
        # Update the entry field with selected options
        sorted_list = sorted(self.selected_options, key=self.options.index)  # This ensures the options are in their original order
        selected_text = ', '.join(map(str, sorted_list))  # Creates a string from the selected options
        self.var.set(selected_text)  # Updates the entry field to show the selected options


class SpellingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spell Bee App")
        self.root.geometry("800x550")  # Set window size to 800x600 for more space

        # Placeholder for existing user IDs, you might want to load these from a file or database
        self.existing_user_ids = ['Bhavi', 'Madhu', 'User']  # Example user IDs
        self.test_type_values = ["Unattended Words", "Incorrectly spelled words", "Words practiced a week ago"]
        # Loading word list and appendin all new words to master wordlist
        self.word_list = pd.read_csv("word_list.csv")
        self.word_list.to_csv("word_list_all.csv", mode='a', header=False, index=False)
        self.word_list_all = pd.read_csv("word_list_all.csv")
        self.word_list_all = self.word_list_all.drop_duplicates(ignore_index = True)
        self.word_list_all.columns = ["user", "word", "word_type", "chunked_sentence", "masked_chunked_sentence", "example_sentence", "masked_example_sentence", "openai_sentence", "masked_openai_sentence"]
        self.word_list_all.to_csv("word_list_all.csv", index=False)

        self.selected_user_var = tk.StringVar()
        self.selected_test_type_var = tk.StringVar()
        self.selected_word_type_var = tk.StringVar()
        self.words_list = []
        self.current_word = tk.StringVar()
        self.current_word_label_text = tk.StringVar()
        self.user_input = tk.StringVar()


        # Initilising the stats parameters 
        self.correct_count = 0
        self.wrong_count = 0
        self.total_correct_count = 0
        self.total_wrong_count = 0
        self.auto_advance = tk.BooleanVar(value=True)  # Default to not automatically advancing
        self.auto_hide_test_options = tk.BooleanVar(value=False)
        
        # Setting default variables
        self.selected_user_var.set("Bhavi")
        self.selected_test_type_var.set("Unattended Words")
        self.selected_word_type_var.set("All")
        self.selected_user = self.selected_user_var.get()
        self.selected_test_type = self.selected_test_type_var.get()
        self.selected_word_type = self.selected_word_type_var.get()

        # initialising the GUI
        self.setup_gui()

        self.total_correct_count = self.correct_words_df.shape[0]
        self.total_wrong_count = self.incorrect_words_df.shape[0]

    def on_enter_pressed(self, event=None):
        # This function will be called when Enter is pressed
        self.check_spelling()

    def update_words_based_on_user(self, event=None):
        # Check for selected user. If not set default user as Bhavi
        self.selected_user=self.selected_user_var.get()
        self.words_df = self.word_list
        if self.selected_user:
            if self.selected_user != 'User':
                self.words_df = self.words_df[(self.words_df['user'] == self.selected_user) | (self.words_df['user']=='User')]
            else:
                self.words_df = self.words_df  
        else:
            self.user_id_options.current(self.default_user_index)
            self.words_df = self.words_df[(self.words_df['user'] == self.selected_user) | (self.words_df['user']=='User')]
            self.selected_user=self.selected_user_var.get()

        # Loading correct and worng word list
        self.correct_words_filename = f"user_{self.selected_user}_correct_words.csv"
        self.incorrect_words_filename = f"user_{self.selected_user}_incorrect_words.csv"

        # Specify the column names since the CSV file is being appended without headers
        cols = ['user_id', 'word', 'datetime']
        # Read the CSV file into a DataFrame with the correct column names
        try:
            self.correct_words_df = pd.read_csv(self.correct_words_filename, names=cols)
        except FileNotFoundError:
            # If the file doesn't exist, there are no words to exclude
            self.correct_words_df = pd.DataFrame(columns=cols)
        try:
            self.incorrect_words_df = pd.read_csv(self.incorrect_words_filename, names=cols)
        except FileNotFoundError:
            # If the file doesn't exist, there are no words to exclude
            self.incorrect_words_df = pd.DataFrame(columns=cols)

    def update_words_based_on_test_type(self, event=None):

        self.update_words_based_on_user()
        # Filterin the DF based on the testtype
        # Unattended words means: not attempted and incorrect words
        self.selected_test_type = self.selected_test_type_var.get()
        if  self.selected_test_type != '' and  self.selected_test_type != None:
            if  self.selected_test_type == "Unattended Words":
                # Filter out the correctly answered words from self.words_df
                self.words_df = self.words_df[~(self.words_df['word'].isin(self.correct_words_df['word']))]

            # Only Previous incorrectly spelled words. unattempted words are not included
            elif self.selected_test_type == "Previous incorrectly spelled words":
                incorrect_words = self.incorrect_words_df['word']
                # Filter the words that are incorrect 
                self.words_df = self.words_df[self.words_df['word'].isin(incorrect_words)]
                # drop the words that are attempted and correct
                self.words_df = self.words_df[~(self.words_df['word'].isin(self.correct_words_df['word']))]

            # attempted words - correct & incorrect practiced morethan a week ago 
            elif self.selected_test_type == "Words practiced a week ago":

                # Step 1: Select the relevant columns from both DataFrames
                cols_to_keep = ['word', 'datetime']
                incorrect_words_subset = self.incorrect_words_df[cols_to_keep]
                correct_words_subset = self.correct_words_df[cols_to_keep]

                # Step 2: Concatenate the two DataFrames
                combined_df = pd.concat([incorrect_words_subset, correct_words_subset], ignore_index=True)

                # Step 3: Sort by 'word' and 'last_practiced' and drop duplicates
                combined_df_sorted = combined_df.sort_values(by=['word', 'datetime'], ascending=[True, True])
                unique_words_df = combined_df_sorted.drop_duplicates(subset='word', keep='last')
                unique_words_df['datetime'] = pd.to_datetime(unique_words_df['datetime'])

                # Filter the words which are practised a week back
                week_ago = datetime.now() - timedelta(weeks=1)
                unique_words_df = unique_words_df[unique_words_df['datetime'] < week_ago]
                unique_words = unique_words_df['word']
                # Filter the words that are incorrect 
                self.words_df = self.words_df[self.words_df['word'].isin(unique_words)]

        else:
            self.test_type.current(0)
            self.selected_test_type = self.selected_test_type_var.get()
            self.words_df = self.words_df[~(self.words_df['word'].isin(self.correct_words_df['word']))]
            list(self.words_df['word_type'].unique())

    def update_word_type_options(self, event=None):

        self.update_words_based_on_test_type()

        self.selected_word_type = self.selected_word_type_var.get()
        # Check for selected word type, if not set default word type as 'All'.
        if self.selected_word_type:
            word_type_list = ["All"] + list(self.words_df['word_type'].unique())
            self.word_type['values'] = word_type_list
            if self.selected_word_type in word_type_list:
                self.word_type.current(word_type_list.index(self.selected_word_type))
            else:
                self.word_type.current(0)

        else:
            # setting the default user and its word types
            self.word_type.current(0)

        self.selected_word_type = self.selected_word_type_var.get()

        # Filtering the dataframe based on word_type
        if self.selected_word_type != "All":
            self.words_df = self.words_df[(self.words_df['word_type'] == self.selected_word_type)]
        else:
            self.words_df = self.words_df

    def update_word_length_options(self, event=None):

        self.update_word_type_options()

        # Calculate the length of each word and create a set of unique lengths
        unique_lengths = set(self.words_df['word'].apply(len))
        unique_lengths_list = list(unique_lengths)
        self.length_options = ["All"] + unique_lengths_list
        self.word_length_list.options = self.length_options

        if self.length_options and "All" not in self.length_options:
            lengths = [int(length) for length in self.length_options]
            self.words_df = self.words_df[self.words_df['word'].apply(len).isin(lengths)]
        else:
            self.words_df = self.words_df

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
        self.side_panel = ttk.Frame(main_frame, width=200)  # Define the width of the side panel
        self.side_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Hide checkbox
        auto_hide_checkbox = ttk.Checkbutton(
            self.side_panel,
            text="Hide Test Options",
            variable=self.auto_hide_test_options,
            onvalue=True,
            offvalue=False,
            command=self.toggle_test_options_visibility,
            style='Bold.TCheckbutton'  # Apply the bold style
        )
        auto_hide_checkbox.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Test options frame
        self.test_options_frame = ttk.Frame(self.side_panel)
        self.test_options_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

        # Test options label
        test_options_label = ttk.Label(self.test_options_frame, text="Test Options", font=('Helvetica', 14))
        test_options_label.grid(row=0, column=0, sticky="W")

        # Auto Advance checkbox
        auto_advance_checkbox = ttk.Checkbutton(
            self.test_options_frame,
            text="Auto Advance to Next Word",
            variable=self.auto_advance,
            onvalue=True,
            offvalue=False
        )
        auto_advance_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Combobox for selecting user
        user_id_label = ttk.Label(self.test_options_frame, text="User ID:", font=('Helvetica', 10))
        user_id_label.grid(row=2, column=0, sticky="w", padx=(5, 2))
        self.user_id_options = ttk.Combobox(self.test_options_frame, textvariable=self.selected_user_var, values=self.existing_user_ids, state="readonly")
        self.user_id_options.grid(row=2, column=1, padx=(0, 5), pady=5)
        # Set default user to Bhavi
        self.default_user_index = self.existing_user_ids.index("Bhavi") if "Bhavi" in self.existing_user_ids else 0
        self.user_id_options.current(self.default_user_index)  # Set Bhavi as default if exists, otherwise first user
        self.selected_user = self.selected_user_var.get()    

        # Combobox for selecting test type
        test_type_label = ttk.Label(self.test_options_frame, text="Test Type:", font=('Helvetica', 10))
        test_type_label.grid(row=3, column=0, sticky="w", padx=(5, 2))
        self.test_type = ttk.Combobox(self.test_options_frame, textvariable=self.selected_test_type_var, values=self.test_type_values, state="readonly")
        self.test_type.grid(row=3, column=1, padx=(0, 5), pady=5)
        # Set default user to Unattended Words
        self.default_test_type_index = self.test_type_values.index("Unattended Words") if "Unattended Words" in self.test_type_values else 0
        self.test_type.current(self.default_test_type_index)  # Set Bhavi as default if exists, otherwise first user
        self.selected_test_type = self.selected_test_type_var.get()

        # Combobox for selecting word type
        word_type_label = ttk.Label(self.test_options_frame, text="Word Type:", font=('Helvetica', 10))
        word_type_label.grid(row=4, column=0, sticky="w", padx=(5, 2))
        self.word_type = ttk.Combobox(self.test_options_frame, textvariable=self.selected_word_type_var, values=["All"], state="readonly")
        self.word_type.grid(row=4, column=1, padx=(0, 5), pady=5)

        # Set default user to Unattended Words
        self.default_word_type_index = self.word_type_values.index("All") if "All" in self.test_type_values else 0
        self.word_type.current(self.default_word_type_index)  # Set Bhavi as default if exists, otherwise first user
        self.selected_word_type = self.selected_word_type_var.get()

        # length options
        length_options_label = ttk.Label(self.test_options_frame, text="Word Length:", font=('Helvetica', 10))
        length_options_label.grid(row=5, column=0, sticky="w", padx=(5, 2))

        # Define your length options, assuming you want lengths from 1 to 10
        self.length_options = ["All"] + list(range(1, 11))
        # Instantiate MultiSelectDropdown
        self.word_length_list = MultiSelectDropdown(self.test_options_frame, options=self.length_options)

        # Immediately update the word type options based on the default user
        self.update_word_length_options()

        # Bind the update function to the combobox
        self.user_id_options.bind("<<ComboboxSelected>>", self.update_word_length_options)
        self.test_type.bind("<<ComboboxSelected>>", self.update_word_length_options)
        self.word_type.bind("<<ComboboxSelected>>", self.update_word_length_options)


        # App title
        ttk.Label(main_frame, text="Welcome to Spell Bee App", font=('Helvetica', 18)).pack()

        # Instruction label
        ttk.Label(main_frame, text="Type the spelling of the pronounced word:").pack(pady=10)

        # Dedicated frame for the "Hear Word" button and status message
        self.hear_word_frame = ttk.Frame(main_frame, height=50)
        self.hear_word_frame.pack(pady=(5, 10))  # Adjust as needed

        # "Hear Word" button in the dynamic frame
        ttk.Button(self.hear_word_frame, text="Hear Word", command=self.pronounce_current_word).pack(side=tk.LEFT, padx=(10, 5))

        # Placeholder frame for status message with a fixed height
        self.status_frame = ttk.Frame(main_frame, height=10)  # Adjust height as needed
        self.status_frame.pack()#fill=tk.X, padx=10, pady=(0, 10)
        self.status_message = ttk.Label(self.status_frame, text=f"\n\n", font=('Helvetica', 14))
        self.status_message.pack()

        # Placeholder frame for current_word_label with a fixed height
        self.current_word_label_frame = ttk.Frame(main_frame, height=10)  # Adjust height as needed
        self.current_word_label_frame.pack() #fill=tk.X, padx=10, pady=(0, 10)

        # Display current word to spell
        self.current_word_label_text.set("\n\n\n\n\n\n")
        current_word_label = ttk.Label(self.current_word_label_frame, textvariable=self.current_word_label_text, font=('Helvetica', 11), width=200, anchor="center")
        current_word_label.pack()

        # Start test button
        ttk.Button(self.test_options_frame, text="Start Test", command=self.start_test).grid(row=6, column=0, padx=5, pady=5)

        # User input entry
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
        self.status_label.pack()

    def toggle_test_options_visibility(self):
        if self.auto_hide_test_options.get():
            # Hide test options
            self.test_options_frame.grid_remove()
        else:
            # Show test options
            self.test_options_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

    def start_test(self):
        self.correct_count=0
        self.wrong_count=0
        
        # Check if a user ID is selected
        if self.selected_user == 'Select User' or self.selected_user == '':
            messagebox.showerror("User ID Required", "Please select a User ID to start the test.")
            return

        # Filtering df with selected word lengths
        self.selected_lengths = self.word_length_list.selected_options
        if self.selected_lengths and "All" not in self.selected_lengths:
            lengths = [int(length) for length in self.selected_lengths]
            self.sel_words_df = self.words_df[self.words_df['word'].apply(len).isin(lengths)]
        else:
            self.sel_words_df = self.words_df


        self.words_list = self.sel_words_df['word'].tolist()

        # Update the status label
        current_scores_text = f"Current Test Scores: Correct - {self.correct_count},      Wrong - {self.wrong_count}"
        total_scores_text = f"Total     Test Scores: Correct - {self.total_correct_count},      Wrong - {self.total_wrong_count}"
        self.status_label.config(text=f"{current_scores_text}\n{total_scores_text}", font=('Helvetica', 10))

        self.next_word()

    def check_spelling(self):
        # Implementation remains the same as previous
        correct_word = self.current_word.get()
        user_word = self.user_input.get()
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if user_word.strip().lower() == correct_word.strip().lower():
            # If spelling is correct, remove the word from the list
            if correct_word in self.words_list:
                self.words_list.remove(correct_word)
            self.correct_count += 1
            self.total_correct_count += 1  # Increment total correct count
            self.update_status("Correct!\n\n ", "green", 500)
            #save file for each user
            filename = f"user_{self.selected_user}_correct_words.csv"
            pd.DataFrame({'user_id': [self.selected_user], 'word': [correct_word], 'datetime': [current_datetime]}).to_csv(filename, mode='a', header=False, index=False)
        else:
            self.wrong_count += 1
            self.total_wrong_count += 1  # Increment total wrong count
            self.update_status(f"Wrong! Correct spelling is: \n\t   {correct_word}\n", "red", 5000)
            #save file for each user
            filename = f"user_{self.selected_user}_incorrect_words.csv"
            pd.DataFrame({'user_id': [self.selected_user], 'word': [correct_word], 'datetime': [current_datetime]}).to_csv(filename, mode='a', header=False, index=False)

    def next_word(self):
        # Implementation remains the same as previous
        if self.words_list:
            # Clear any existing status messages first
            # for widget in self.status_frame.winfo_children():
            #     widget.destroy()
            # # Optionally, maintain the space with an empty label if desired
            # ttk.Label(self.status_frame).pack()
            try:
                self.status_message.destroy()
            except:
                pass
            self.status_message = ttk.Label(self.status_frame, text=f"\n\n", font=('Helvetica', 16))
            self.status_message.pack()
            
            self.current_word.set(random.choice(self.words_list))
            current_word_len = len(list(self.current_word.get()))

            # Getting masked sentance examples 
            masked_chunked_sentence_df = self.sel_words_df.loc[self.sel_words_df['word']==self.current_word.get(),"masked_chunked_sentence"]
            masked_openai_sentence_df = self.sel_words_df.loc[self.sel_words_df['word']==self.current_word.get(),"masked_openai_sentence"]
            
            if not masked_chunked_sentence_df.empty:
                masked_chunked_sentence = masked_chunked_sentence_df.iloc[0]
            else:
                masked_chunked_sentence = "-"

            if not masked_openai_sentence_df.empty:
                masked_openai_sentence = masked_openai_sentence_df.iloc[0]
            else:
                masked_openai_sentence = "-"
            
            current_word_type = self.sel_words_df.loc[self.sel_words_df['word']==self.current_word.get(),"word_type"].iloc[0]
            # #mask only word with *
            # self.current_word_label_text.set(str(current_word_len)+" letter word \n\n     "+ ("*"*current_word_len))
            mask_sent='- Topic: '+str(current_word_type)+".\n\n- "+str(masked_chunked_sentence)+".\n\n- "+str(masked_openai_sentence)+"."
            sentance_label = '- '+str(current_word_len)+" letter word. Remaining Words: "+str(len(self.words_list))+"\n\n"+ mask_sent
            self.current_word_label_text.set(sentance_label)
            self.pronounce_current_word()
        else:
            self.current_word.set("No more words for the test")
            self.current_word_label_text.set("\n\n\n\n\n\n")
            self.pronounce_current_word()
            self.status_message.destroy()
            self.status_message = ttk.Label(self.status_frame, text="No more words for the test", foreground="orange", font=('Helvetica', 16))
            self.status_message.pack()

    def update_status(self, message, color, status_time):
        # Clear the status frame of any widgets
        # for widget in self.status_frame.winfo_children():
        #     widget.destroy()
        self.status_message.destroy()

        # Create and pack a new status label within the status frame
        self.status_message = ttk.Label(self.status_frame, text=message, foreground=color, font=('Helvetica', 16))
        self.status_message.pack()

        # Schedule removal of the status message after 2 seconds
        def clear_status():
            self.status_message.destroy()
            # # Optionally create an empty label to preserve the space
            # ttk.Label(self.status_frame).pack()
            self.status_message = ttk.Label(self.status_frame, text=f"\n\n", font=('Helvetica', 16))
            self.status_message.pack()
            
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