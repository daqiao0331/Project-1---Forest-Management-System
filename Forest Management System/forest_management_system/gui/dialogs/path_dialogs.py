"""
Dialogs for path-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox

class ShortestPathDialog:
    def __init__(self, parent, tree_ids):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Find Shortest Path")
        self.dialog.geometry("400x200")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()

        form_frame = tk.Frame(self.dialog, bg='#f0f0f0', padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(form_frame, text="Start Tree ID:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=0, column=0, sticky='w', pady=5)
        self.start_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.start_var, values=tree_ids, font=('Segoe UI', 11)).grid(row=0, column=1, sticky='we', pady=5)

        tk.Label(form_frame, text="End Tree ID:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=5)
        self.end_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.end_var, values=tree_ids, font=('Segoe UI', 11)).grid(row=1, column=1, sticky='we', pady=5)

        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.grid(row=2, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Find Path", command=self._on_ok, style='Modern.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)

        self.result = None

    def _on_ok(self):
        start_id_str = self.start_var.get()
        end_id_str = self.end_var.get()

        if not start_id_str or not end_id_str:
            messagebox.showerror("Invalid Input", "Please select both start and end trees.", parent=self.dialog)
            return

        try:
            start_id = int(start_id_str)
            end_id = int(end_id_str)
            if start_id == end_id:
                messagebox.showwarning("Invalid Input", "Start and end trees cannot be the same.", parent=self.dialog)
                return
            self.result = (start_id, end_id)
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid tree ID selected.", parent=self.dialog)

    def show(self):
        self.dialog.wait_window()
        return self.result 