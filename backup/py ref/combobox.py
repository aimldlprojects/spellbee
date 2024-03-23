
        # Combobox for selecting test Type
        test_type_label = ttk.Label(self.test_options_frame, text="Test Type:", font=('Helvetica', 10))
        test_type_label.grid(row=2, column=0, sticky="w", padx=(5, 2))
        self.test_type = ttk.Combobox(self.test_options_frame, values=["General", "Incorrectly spelled words", "Words practiced a week ago"], state="readonly")
        self.test_type.grid(row=2, column=1, padx=(0, 5), pady=5)
        self.test_type.current(0)

        # Combobox for selecting word Type
        word_type_label = ttk.Label(self.test_options_frame, text="Word Type:", font=('Helvetica', 10))
        word_type_label.grid(row=3, column=0, sticky="w", padx=(5, 2))
        self.word_type = ttk.Combobox(self.test_options_frame, values=["All"]+list(self.word_list['word_type'].unique()))
        self.word_type.grid(row=3, column=1, padx=(0, 5), pady=5)
        self.word_type.current(0)  # Assuming you want the first item as default

        # Combobox for length options
        length_options_label = ttk.Label(self.test_options_frame, text="Word Length:", font=('Helvetica', 10))
        length_options_label.grid(row=4, column=0, sticky="w", padx=(5, 2))
        self.length_options = ttk.Combobox(self.test_options_frame, values=["All"]+list(range(1, 11)), state="normal")
        self.length_options.grid(row=4, column=1, padx=(0, 5), pady=5)  # Adjust to use grid
        self.length_options.current(0)  # Assuming you want the first item as default

        # Combobox for selecting user
        user_id_label = ttk.Label(self.test_options_frame, text="User ID:", font=('Helvetica', 10))
        user_id_label.grid(row=5, column=0, sticky="w", padx=(5, 2))
        self.user_id = ttk.Combobox(self.test_options_frame, textvariable=self.user_id_var, values=self.existing_user_ids, state="readonly")
        self.user_id.grid(row=5, column=1, padx=(0, 5), pady=5)
        self.user_id.set('Select User')  # Set a placeholder or instruction text




###############
# Multi select option - label box

        # Test type
        self.test_type = tk.Listbox(self.test_options_frame, selectmode=tk.MULTIPLE, height=len(test_type_options), width=width) #state="normal"
        for option in test_type_options:
            self.test_type.insert(tk.END, option)
        # Default select the first item
        self.test_type.selection_set(0)
        self.test_type.grid(row=2, column=1, padx=(0, 5), pady=5)


        selected_indices = self.test_type.curselection()  # Get the indices of selected items
        selected_items = [self.test_type.get(idx) for idx in selected_indices]  # Retrieve the selected items using the indices


        # Calculate the maximum width of the options
        max_width = max(len(option) for option in self.test_type)
        # Set the width of the Listbox
        width = max_width + 1  # Adjust the width as needed