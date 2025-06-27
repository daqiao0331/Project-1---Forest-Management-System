"""
Dialog windows for tree-related operations.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ...components.health_status import HealthStatus

class AddTreeDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("➕ Add New Tree")
        self.dialog.geometry("540x480")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (540 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (480 // 2)
        self.dialog.geometry(f"540x480+{x}+{y}")
        
        # UI Setup
        form_frame = tk.Frame(self.dialog, bg='#f0f0f0', padx=45, pady=35)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(form_frame, text="Add New Tree", font=('Segoe UI', 16, 'bold'), 
                fg='#2c3e50', bg='#f0f0f0').grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Species field
        tk.Label(form_frame, text="Species:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=12)
        self.species_var = tk.StringVar(value="Pine")
        ttk.Entry(form_frame, textvariable=self.species_var, font=('Segoe UI', 12), width=35).grid(row=1, column=1, sticky='w', pady=12)

        # Age field
        tk.Label(form_frame, text="Age:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=12)
        self.age_var = tk.StringVar(value="10")
        ttk.Entry(form_frame, textvariable=self.age_var, font=('Segoe UI', 12), width=35).grid(row=2, column=1, sticky='w', pady=12)

        # Health Status field
        tk.Label(form_frame, text="Health Status:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=3, column=0, sticky='w', pady=12)
        self.health_var = tk.StringVar(value="HEALTHY")
        ttk.Combobox(form_frame, textvariable=self.health_var, values=["HEALTHY", "INFECTED", "AT_RISK"], 
                     font=('Segoe UI', 12), width=32).grid(row=3, column=1, sticky='w', pady=12)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.grid(row=4, columnspan=2, pady=(35, 0))
        
        # 创建柔和的绿色按钮样式
        button_style = {
            'font': ('Segoe UI', 12),
            'width': 20,
            'height': 2,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        add_button = tk.Button(button_frame, text="✚ Add Tree", command=self._on_ok, **button_style)
        add_button.pack(side=tk.LEFT, padx=12)
        
        # 鼠标悬停效果
        add_button.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        add_button.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))
        
        cancel_button = tk.Button(button_frame, text="✖ Cancel", command=self.dialog.destroy, **button_style)
        cancel_button.pack(side=tk.LEFT, padx=12)
        
        # 鼠标悬停效果
        cancel_button.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        cancel_button.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))

        # Configure grid
        form_frame.grid_columnconfigure(1, weight=1)

        self.result = None

    def _on_ok(self):
        try:
            self.result = {
                "species": self.species_var.get(),
                "age": int(self.age_var.get()),
                "health": HealthStatus[self.health_var.get()]
            }
            self.dialog.destroy()
        except (ValueError, KeyError):
            messagebox.showerror("Invalid Input", "Please check your inputs.", parent=self.dialog)

    def show(self):
        self.dialog.wait_window()
        return self.result

class DeleteTreeDialog:
    def __init__(self, parent, tree_ids):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("✖ Delete Tree")
        self.dialog.geometry("540x480")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (540 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (480 // 2)
        self.dialog.geometry(f"540x480+{x}+{y}")
        
        # UI Setup
        form_frame = tk.Frame(self.dialog, bg='#f0f0f0', padx=45, pady=35)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(form_frame, text="Delete Tree", font=('Segoe UI', 16, 'bold'), 
                fg='#2c3e50', bg='#f0f0f0').grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Tree Selection
        tk.Label(form_frame, text="Select Tree:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=12)
        self.tree_var = tk.StringVar()
        self.tree_combobox = ttk.Combobox(form_frame, textvariable=self.tree_var, values=tree_ids, 
                                         font=('Segoe UI', 12), width=32)
        self.tree_combobox.grid(row=1, column=1, sticky='w', pady=12)
        
        # Warning Message
        warning_frame = tk.Frame(form_frame, bg='#f0f0f0')
        warning_frame.grid(row=2, column=0, columnspan=2, pady=(20, 30))
        
        warning_icon = tk.Label(warning_frame, text="⚠", font=('Segoe UI', 24), fg='#ff9800', bg='#f0f0f0')
        warning_icon.pack(pady=(0, 10))
        
        warning_text = tk.Label(warning_frame, text="Are you sure you want to delete this tree?\nThis action cannot be undone.",
                              font=('Segoe UI', 12), fg='#666', bg='#f0f0f0', justify=tk.CENTER)
        warning_text.pack()
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.grid(row=3, columnspan=2, pady=(35, 0))
        
        # 创建柔和的绿色按钮样式
        button_style = {
            'font': ('Segoe UI', 12),
            'width': 20,
            'height': 2,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        delete_button = tk.Button(button_frame, text="✖ Delete Tree", command=self._on_ok, **button_style)
        delete_button.pack(side=tk.LEFT, padx=12)
        
        delete_button.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        delete_button.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))
        
        cancel_button = tk.Button(button_frame, text="← Cancel", command=self.dialog.destroy, **button_style)
        cancel_button.pack(side=tk.LEFT, padx=12)
        
        cancel_button.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        cancel_button.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        self.result = None

    def _on_ok(self):
        if self.tree_var.get():
            self.result = int(self.tree_var.get())
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Please select a tree to delete.", parent=self.dialog)

    def show(self):
        self.dialog.wait_window()
        return self.result

class ModifyHealthDialog:
    def __init__(self, parent, tree_ids):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔄 Modify Tree Health")
        self.dialog.geometry("540x480")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (540 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (480 // 2)
        self.dialog.geometry(f"540x480+{x}+{y}")
        
        # UI Setup
        form_frame = tk.Frame(self.dialog, bg='#f0f0f0', padx=45, pady=35)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(form_frame, text="Modify Tree Health", font=('Segoe UI', 16, 'bold'), 
                fg='#2c3e50', bg='#f0f0f0').grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Tree Selection
        tk.Label(form_frame, text="Select Tree:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=1, column=0, sticky='w', pady=12)
        self.tree_var = tk.StringVar()
        self.tree_combobox = ttk.Combobox(form_frame, textvariable=self.tree_var, values=tree_ids, 
                                         font=('Segoe UI', 12), width=32)
        self.tree_combobox.grid(row=1, column=1, sticky='w', pady=12)
        
        # Health Status
        tk.Label(form_frame, text="New Health Status:", font=('Segoe UI', 12), bg='#f0f0f0').grid(row=2, column=0, sticky='w', pady=12)
        self.health_var = tk.StringVar(value="HEALTHY")
        health_combobox = ttk.Combobox(form_frame, textvariable=self.health_var, 
                                      values=["HEALTHY", "INFECTED", "AT_RISK"],
                                      font=('Segoe UI', 12), width=32)
        health_combobox.grid(row=2, column=1, sticky='w', pady=12)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.grid(row=3, columnspan=2, pady=(35, 0))
        
        # 创建柔和的绿色按钮样式
        button_style = {
            'font': ('Segoe UI', 12),
            'width': 20,
            'height': 2,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        modify_button = tk.Button(button_frame, text="🔄 Update Health", command=self._on_ok, **button_style)
        modify_button.pack(side=tk.LEFT, padx=12)
        
        modify_button.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        modify_button.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))
        
        cancel_button = tk.Button(button_frame, text="← Cancel", command=self.dialog.destroy, **button_style)
        cancel_button.pack(side=tk.LEFT, padx=12)
        
        cancel_button.bind('<Enter>', lambda e: e.widget.configure(bg='#45a049'))
        cancel_button.bind('<Leave>', lambda e: e.widget.configure(bg='#4CAF50'))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        self.result = None

    def _on_ok(self):
        if self.tree_var.get():
            try:
                tree_id = int(self.tree_var.get())
                health = HealthStatus[self.health_var.get()]
                self.result = {
                    "tree_id": tree_id,
                    "health": health
                }
                self.dialog.destroy()
            except (ValueError, KeyError):
                messagebox.showerror("Error", "Invalid input values.", parent=self.dialog)
        else:
            messagebox.showerror("Error", "Please select a tree.", parent=self.dialog)

    def show(self):
        self.dialog.wait_window()
        return self.result 