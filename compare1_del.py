import tkinter as tk
from tkinter import ttk

class MultiSelectDropdown:
    def __init__(self, parent, options, **kwargs):
        self.parent = parent
        self.options = options
        self.selected_options = {self.options[0]} if options else set()

        self.var = tk.StringVar()

        self.entry = ttk.Entry(self.parent, textvariable=self.var, **kwargs)
        self.entry.grid(row=5, column=1, padx=(0, 9), pady=5, sticky="ew")

        self.dropdown_button = ttk.Button(self.parent, text=u"\u25BE", command=self.toggle_dropdown, width=1)
        self.dropdown_button.grid(row=5, column=2, padx=(0, 10), pady=1)

        self.dropdown = None
        self.listbox = None
        self.popup_opened = False

        self.refresh_entry()

    def create_dropdown(self):
        if self.dropdown:
            self.destroy_dropdown()

        self.dropdown = tk.Toplevel(self.parent)
        self.dropdown.overrideredirect(True)  # No window decorations

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
        self.dropdown.bind("<FocusOut>", self.on_focus_out)

        self.parent.bind("<1>", self.global_click)

        self.dropdown.focus_set()
        self.popup_opened = True

    def destroy_dropdown(self):
        if self.dropdown is not None:
            self.dropdown.destroy()
            self.dropdown = None
            self.parent.unbind("<1>")
        self.popup_opened = False

    def toggle_dropdown(self):
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
        pass

    def on_listbox_select(self, event=None):
        newly_selected_options = {self.options[i] for i in self.listbox.curselection()}
        self.selected_options = newly_selected_options
        self.refresh_entry()

    def refresh_entry(self):
        sorted_list = sorted(self.selected_options, key=self.options.index)
        selected_text = ', '.join(map(str, sorted_list))
        self.var.set(selected_text)

if __name__ == "__main__":
    root = tk.Tk()
    options = ["Option 1", "Option 2", "Option 3"]
    msd = MultiSelectDropdown(root, options)
    root.mainloop()
