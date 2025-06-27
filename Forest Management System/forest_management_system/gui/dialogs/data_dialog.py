"""
Dialog windows for data operations.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class LoadDataDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📂 Load Forest Data")
        self.dialog.geometry("800x550")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"800x550+{x}+{y}")
        
        self.last_csv_dir = '.'
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the dialog UI """
        # Title
        title_label = tk.Label(self.dialog, text="\U0001F333 Load Forest Data", font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f0f0f0')
        title_label.pack(pady=(30, 10))

        # Subtitle
        subtitle = tk.Label(self.dialog, text="Please select the tree and path CSV files to load:", font=('Segoe UI', 12), fg='#2c3e50', bg='#f0f0f0')
        subtitle.pack(pady=(0, 25))

        # Form frame
        form_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40)

        # Tree file field
        tree_frame = tk.Frame(form_frame, bg='#f0f0f0')
        tree_frame.pack(fill=tk.X, pady=(0, 18))
        tk.Label(tree_frame, text="\U0001F333  Tree Data File:", font=('Segoe UI', 13, 'bold'), fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        tree_file_frame = tk.Frame(tree_frame, bg='#f0f0f0')
        tree_file_frame.pack(fill=tk.X)
        self.tree_file_var = tk.StringVar()
        tree_file_entry = ttk.Entry(tree_file_frame, textvariable=self.tree_file_var, font=('Segoe UI', 10), width=60)
        tree_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        
        button_style = {
            'font': ('Segoe UI', 11),
            'width': 10,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        browse_tree_btn = tk.Button(tree_file_frame, text="Browse", command=self._browse_tree_file, **button_style)
        browse_tree_btn.pack(side=tk.RIGHT)
        browse_tree_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        browse_tree_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))

        # Path file field
        path_frame = tk.Frame(form_frame, bg='#f0f0f0')
        path_frame.pack(fill=tk.X, pady=(0, 18))
        tk.Label(path_frame, text="\U0001F6E4\uFE0F  Path Data File:", font=('Segoe UI', 13, 'bold'), fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        path_file_frame = tk.Frame(path_frame, bg='#f0f0f0')
        path_file_frame.pack(fill=tk.X)
        self.path_file_var = tk.StringVar()
        path_file_entry = ttk.Entry(path_file_frame, textvariable=self.path_file_var, font=('Segoe UI', 10), width=60)
        path_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_path_btn = tk.Button(path_file_frame, text="Browse", command=self._browse_path_file, **button_style)
        browse_path_btn.pack(side=tk.RIGHT)
        browse_path_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        browse_path_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))

        # Main action buttons
        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=(35, 0))
        
        
        main_button_style = {
            'font': ('Segoe UI', 12),
            'width': 20,
            'height': 2,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        cancel_btn = tk.Button(button_frame, text="← Cancel", command=self.dialog.destroy, **main_button_style)
        cancel_btn.pack(side=tk.LEFT, padx=12)
        cancel_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        cancel_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))
        
        load_btn = tk.Button(button_frame, text="📂 Load Data", command=self._on_ok, **main_button_style)
        load_btn.pack(side=tk.RIGHT)
        load_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        load_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))

    def _browse_tree_file(self):
        """Browse for tree data file"""
        filename = filedialog.askopenfilename(
            title="Select Tree Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.last_csv_dir
        )
        if filename:
            self.tree_file_var.set(filename)
            self.last_csv_dir = os.path.dirname(filename)
            
    def _browse_path_file(self):
        """Browse for path data file"""
        filename = filedialog.askopenfilename(
            title="Select Path Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.last_csv_dir
        )
        if filename:
            self.path_file_var.set(filename)
            self.last_csv_dir = os.path.dirname(filename)
            
    def _on_ok(self):
        tree_file = self.tree_file_var.get().strip()
        path_file = self.path_file_var.get().strip()
        if not tree_file or not path_file:
            messagebox.showerror("Error", "请同时选择树和路径文件")
            return
        if not os.path.exists(tree_file):
            messagebox.showerror("Error", f"Tree file not found: {tree_file}")
            return
        if not os.path.exists(path_file):
            messagebox.showerror("Error", f"Path file not found: {path_file}")
            return
        self.result = (tree_file, path_file)
        self.dialog.destroy()
        
    def show(self):
        """Show the dialog and return the result"""
        self.result = None
        self.dialog.wait_window()
        return self.result 