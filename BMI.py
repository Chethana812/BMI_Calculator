import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

class BMICalculatorApp:
    # Theme colors
    THEMES = {
        'light': {
            'bg': '#ffffff',
            'fg': '#000000',
            'secondary_bg': '#f0f0f0',
            'accent': '#0078d4',
            'text': '#000000',
            'frame_bg': '#e8e8e8'
        },
        'dark': {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'secondary_bg': '#2d2d2d',
            'accent': '#0078d4',
            'text': '#ffffff',
            'frame_bg': '#3d3d3d'
        }
    }

    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")
        self.root.geometry("900x700")
        
        self.current_theme = 'light'
        self.current_profile = None
        self.profiles = {}
        
        self.setup_database()
        self.load_profiles()
        self.apply_theme()
        self.create_widgets()

    def setup_database(self):
        """Initializes SQLite database for user data storage."""
        self.conn = sqlite3.connect("bmi_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                height REAL NOT NULL,
                target_weight REAL,
                target_bmi REAL,
                created_date TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def load_profiles(self):
        """Load all profiles from database."""
        self.cursor.execute('SELECT name, height, target_weight, target_bmi FROM profiles')
        profiles = self.cursor.fetchall()
        for profile in profiles:
            self.profiles[profile[0]] = {
                'height': profile[1],
                'target_weight': profile[2],
                'target_bmi': profile[3]
            }
    
    def apply_theme(self):
        """Apply color theme to the application."""
        theme = self.THEMES[self.current_theme]
        self.root.configure(bg=theme['bg'])
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TLabel', background=theme['bg'], foreground=theme['text'])
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabelFrame', background=theme['bg'], foreground=theme['text'])
        style.configure('TButton', background=theme['secondary_bg'], foreground=theme['text'])
        style.configure('TEntry', fieldbackground=theme['secondary_bg'], foreground=theme['text'])
        
        # Custom style for the result label to make it pop
        style.configure('Result.TLabel', foreground=theme['accent'], font=("Helvetica", 13, "bold"))
        
        style.map('TButton',
                  background=[('active', theme['accent'])])
        
    def toggle_theme(self):
        """Toggle between light and dark mode."""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh all widgets with new theme."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def create_widgets(self):
        """Builds the user interface."""
        theme = self.THEMES[self.current_theme]
        
        # Top Header Frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(padx=20, pady=(15, 5), fill="x")
        
        ttk.Label(header_frame, text="BMI Calculator", font=("Helvetica", 18, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="🌓 Toggle Theme", command=self.toggle_theme).pack(side=tk.RIGHT)
        
        # Profile Management Frame
        profile_frame = ttk.LabelFrame(self.root, text="Profile Management", padding="10 10 10 10")
        profile_frame.pack(padx=20, pady=10, fill="x")
        
        ttk.Label(profile_frame, text="Profile Name:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="W")
        self.profile_entry = ttk.Entry(profile_frame, width=20)
        self.profile_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")
        
        ttk.Label(profile_frame, text="Height (cm):").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="W")
        self.profile_height_entry = ttk.Entry(profile_frame, width=15)
        self.profile_height_entry.grid(row=0, column=3, padx=5, pady=5, sticky="EW")
        
        ttk.Button(profile_frame, text="Create Profile", command=self.create_profile).grid(row=0, column=4, padx=(15, 0), pady=5)
        
        ttk.Label(profile_frame, text="Select Profile:").grid(row=1, column=0, padx=(0, 5), pady=10, sticky="W")
        self.profile_dropdown = ttk.Combobox(profile_frame, state="readonly", width=18)
        self.profile_dropdown.grid(row=1, column=1, padx=5, pady=10, sticky="EW")
        self.profile_dropdown.bind("<<ComboboxSelected>>", self.select_profile)
        
        # Configure columns so they stretch nicely
        profile_frame.columnconfigure(1, weight=1)
        profile_frame.columnconfigure(3, weight=1)
        
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="New Measurement", padding="10 10 10 10")
        input_frame.pack(padx=20, pady=10, fill="x")

        ttk.Label(input_frame, text="Weight (kg):").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="W")
        self.weight_entry = ttk.Entry(input_frame, width=20)
        self.weight_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")

        ttk.Label(input_frame, text="Date:").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="W")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="EW")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(input_frame, text="📅 Pick Date", command=self.open_date_picker).grid(row=0, column=4, padx=(15, 0), pady=5)

        calc_btn = ttk.Button(input_frame, text="Calculate & Save", command=self.process_bmi)
        calc_btn.grid(row=1, column=0, columnspan=5, pady=(15, 5))

        # Result Label
        self.result_label = ttk.Label(input_frame, text="BMI: -- | Category: -- | Status: --", style='Result.TLabel')
        self.result_label.grid(row=2, column=0, columnspan=5, pady=10)
        
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Target Settings Frame
        target_frame = ttk.LabelFrame(self.root, text="Target Settings", padding="10 10 10 10")
        target_frame.pack(padx=20, pady=10, fill="x")
        
        ttk.Label(target_frame, text="Target Weight (kg):").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="W")
        self.target_weight_entry = ttk.Entry(target_frame, width=20)
        self.target_weight_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")
        
        ttk.Label(target_frame, text="Target BMI:").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="W")
        self.target_bmi_entry = ttk.Entry(target_frame, width=15)
        self.target_bmi_entry.grid(row=0, column=3, padx=5, pady=5, sticky="EW")
        
        ttk.Button(target_frame, text="Set Targets", command=self.set_targets).grid(row=0, column=4, padx=(15, 0), pady=5)
        
        target_frame.columnconfigure(1, weight=1)
        target_frame.columnconfigure(3, weight=1)

        # History & Visualization Frame
        hist_frame = ttk.LabelFrame(self.root, text="Trend Analysis", padding="10 10 10 10")
        hist_frame.pack(padx=20, pady=(10, 20), fill="both", expand=True)

        view_btn = ttk.Button(hist_frame, text="📊 Show BMI Trend", command=self.plot_history)
        view_btn.pack(pady=(0, 10))

        # Plot Area
        self.plot_frame = ttk.Frame(hist_frame)
        self.plot_frame.pack(fill="both", expand=True)
        
        # Update profile dropdown after all widgets are created
        self.update_profile_dropdown()

    def update_profile_dropdown(self):
        """Update profile dropdown with available profiles."""
        profiles = list(self.profiles.keys())
        self.profile_dropdown['values'] = profiles
        if profiles and not self.current_profile:
            self.profile_dropdown.current(0)
            self.select_profile(None)
    
    def create_profile(self):
        """Create a new profile."""
        name = self.profile_entry.get().strip()
        height_str = self.profile_height_entry.get().strip()
        
        if not name or not height_str:
            messagebox.showerror("Input Error", "Please enter profile name and height.")
            return
        
        if name in self.profiles:
            messagebox.showerror("Error", "Profile already exists!")
            return
        
        try:
            height = float(height_str)
            if height <= 0 or height > 300:
                raise ValueError("Height must be between 0 and 300 cm")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid height: {e}")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO profiles (name, height, target_weight, target_bmi, created_date)
            VALUES (?, ?, NULL, NULL, ?)
        ''', (name, height, timestamp))
        self.conn.commit()
        
        self.profiles[name] = {'height': height, 'target_weight': None, 'target_bmi': None}
        self.profile_entry.delete(0, tk.END)
        self.profile_height_entry.delete(0, tk.END)
        self.update_profile_dropdown()
        messagebox.showinfo("Success", f"Profile '{name}' created successfully!")
    
    def select_profile(self, event):
        """Select a profile."""
        selected = self.profile_dropdown.get()
        if selected:
            self.current_profile = selected
            profile_data = self.profiles[selected]
            self.target_weight_entry.delete(0, tk.END)
            self.target_bmi_entry.delete(0, tk.END)
            if profile_data['target_weight']:
                self.target_weight_entry.insert(0, str(profile_data['target_weight']))
            if profile_data['target_bmi']:
                self.target_bmi_entry.insert(0, str(profile_data['target_bmi']))
    
    def open_date_picker(self):
        """Open a simple date picker window."""
        picker_window = tk.Toplevel(self.root)
        picker_window.title("Select Date")
        picker_window.geometry("300x150")
        
        # Quick styling to match parent theme lightly
        picker_window.configure(bg=self.THEMES[self.current_theme]['bg'])
        
        ttk.Label(picker_window, text="Select Date (YYYY-MM-DD):").pack(pady=10)
        date_var = tk.StringVar(value=self.date_entry.get())
        date_entry = ttk.Entry(picker_window, textvariable=date_var, width=20)
        date_entry.pack(pady=5)
        
        def set_date():
            try:
                datetime.strptime(date_var.get(), "%Y-%m-%d")
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date_var.get())
                picker_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        
        ttk.Button(picker_window, text="Confirm", command=set_date).pack(pady=10)
    
    def set_targets(self):
        """Set target weight/BMI for current profile."""
        if not self.current_profile:
            messagebox.showerror("Error", "Please select a profile first!")
            return
        
        target_weight_str = self.target_weight_entry.get().strip()
        target_bmi_str = self.target_bmi_entry.get().strip()
        
        try:
            target_weight = float(target_weight_str) if target_weight_str else None
            target_bmi = float(target_bmi_str) if target_bmi_str else None
            
            if target_weight and (target_weight <= 0 or target_weight > 500):
                raise ValueError("Target weight must be positive")
            if target_bmi and (target_bmi < 10 or target_bmi > 50):
                raise ValueError("Target BMI must be realistic")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid target values: {e}")
            return
        
        profile_data = self.profiles[self.current_profile]
        profile_data['target_weight'] = target_weight
        profile_data['target_bmi'] = target_bmi
        
        self.cursor.execute('''
            UPDATE profiles SET target_weight = ?, target_bmi = ? WHERE name = ?
        ''', (target_weight, target_bmi, self.current_profile))
        self.conn.commit()
        
        messagebox.showinfo("Success", "Targets set successfully!")

    def get_bmi_category(self, bmi):
        """Classifies BMI into standard health categories."""
        if bmi < 18.5: return "Underweight"
        elif 18.5 <= bmi < 24.9: return "Normal weight"
        elif 25.0 <= bmi < 29.9: return "Overweight"
        else: return "Obesity"

    def process_bmi(self):
        """Validates input, calculates BMI, updates GUI, and saves to DB."""
        if not self.current_profile:
            messagebox.showerror("Error", "Please select a profile first!")
            return
        
        weight_str = self.weight_entry.get().strip()
        date_str = self.date_entry.get().strip()
        
        if not weight_str:
            messagebox.showerror("Input Error", "Please enter weight.")
            return

        try:
            weight = float(weight_str)
            datetime.strptime(date_str, "%Y-%m-%d")
            
            if weight <= 0:
                raise ValueError("Weight must be positive.")
            if weight > 500:
                raise ValueError("Weight is out of realistic bounds.")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        # Get height from profile
        height_cm = self.profiles[self.current_profile]['height']
        
        # Calculation
        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2), 2)
        category = self.get_bmi_category(bmi)
        
        # Calculate status vs target
        target_weight = self.profiles[self.current_profile]['target_weight']
        status = ""
        if target_weight:
            diff = weight - target_weight
            if abs(diff) < 0.5:
                status = "✓ On target!"
            elif diff > 0:
                status = f"↓ {diff:.1f}kg to target"
            else:
                status = f"↑ {abs(diff):.1f}kg above target"

        # Update GUI
        self.result_label.config(text=f"BMI: {bmi} | Category: {category} | {status}")

        # Database Insertion
        timestamp = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO bmi_records (profile_name, weight, height, bmi, category, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.current_profile, weight, height_cm, bmi, category, timestamp))
        self.conn.commit()
        
        self.weight_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        messagebox.showinfo("Success", "Record saved successfully!")

    def plot_history(self):
        """Fetches historical data for a profile and embeds a Matplotlib graph with target lines."""
        if not self.current_profile:
            messagebox.showerror("Error", "Please select a profile first!")
            return

        self.cursor.execute('SELECT timestamp, bmi, weight FROM bmi_records WHERE profile_name = ? ORDER BY timestamp ASC', (self.current_profile,))
        records = self.cursor.fetchall()

        if not records:
            messagebox.showinfo("No Data", f"No records found for profile: {self.current_profile}")
            return

        dates = [row[0][:10] for row in records]
        bmis = [row[1] for row in records]
        weights = [row[2] for row in records]
        x_indices = list(range(len(dates)))

        # Clear previous plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # Get target values
        profile_data = self.profiles[self.current_profile]
        target_bmi = profile_data['target_bmi']
        target_weight = profile_data['target_weight']

        try:
            # Import Figure directly to avoid pyplot state-machine conflicts
            from matplotlib.figure import Figure
            
            # Create Matplotlib Figure with 2 subplots
            fig = Figure(figsize=(12, 4), dpi=100)
            
            # Match figure background to current theme background
            fig.patch.set_facecolor(self.THEMES[self.current_theme]['bg'])
            
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            
            # Determine text color for axes based on theme
            text_color = self.THEMES[self.current_theme]['text']
            
            # BMI Plot
            ax1.plot(x_indices, bmis, marker='o', linestyle='-', color='#0078d4', linewidth=2, label='Current BMI')
            if target_bmi:
                ax1.axhline(y=target_bmi, color='green', linestyle='--', linewidth=2, label=f'Target BMI: {target_bmi}')
            
            # Fill between normal range if we have multiple points
            if len(x_indices) > 1:
                ax1.fill_between(x_indices, 18.5, 24.9, alpha=0.1, color='green', label='Normal Range')
            
            ax1.set_title(f"BMI Trend - {self.current_profile}", fontsize=12, fontweight='bold', color=text_color)
            ax1.set_xlabel("Date", color=text_color)
            ax1.set_ylabel("BMI", color=text_color)
            
            # Set x-axis labels
            if len(x_indices) > 0:
                ax1.set_xticks(x_indices)
                ax1.set_xticklabels(dates, rotation=45, ha='right')
            
            ax1.tick_params(colors=text_color)
            ax1.grid(True, linestyle='--', alpha=0.3)
            
            # Style legend
            legend1 = ax1.legend()
            for text in legend1.get_texts():
                text.set_color('black') # Keep legend text visible across themes
            
            # Weight Plot
            ax2.plot(x_indices, weights, marker='s', linestyle='-', color='#ff6b6b', linewidth=2, label='Current Weight')
            if target_weight:
                ax2.axhline(y=target_weight, color='green', linestyle='--', linewidth=2, label=f'Target Weight: {target_weight}kg')
            
            ax2.set_title(f"Weight Trend - {self.current_profile}", fontsize=12, fontweight='bold', color=text_color)
            ax2.set_xlabel("Date", color=text_color)
            ax2.set_ylabel("Weight (kg)", color=text_color)
            
            # Set x-axis labels
            if len(x_indices) > 0:
                ax2.set_xticks(x_indices)
                ax2.set_xticklabels(dates, rotation=45, ha='right')
            
            ax2.tick_params(colors=text_color)
            ax2.grid(True, linestyle='--', alpha=0.3)
            
            # Style legend
            legend2 = ax2.legend()
            for text in legend2.get_texts():
                text.set_color('black')

            fig.tight_layout()

            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Graph Error", f"Failed to display graph: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()