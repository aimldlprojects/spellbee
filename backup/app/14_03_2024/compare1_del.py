
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