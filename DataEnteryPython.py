import os
import datetime
import csv
from tkinter import Tk, Label, Entry, Button, Listbox, END, messagebox, Scrollbar, Menu, Toplevel, Frame
from tkinter.simpledialog import askstring
from tkinter.ttk import Style
from tkinter import StringVar, Canvas

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + event.x + 25
        y = self.widget.winfo_rooty() + event.y + 25
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes('-alpha', 0.0)
        tw.after(0, lambda: tw.attributes('-alpha', 1.0))  # Fade-in effect
        label = Label(tw, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.attributes('-alpha', 1.0)
            tw.after(0, lambda: tw.attributes('-alpha', 0.0))  # Fade-out effect
            tw.destroy()

class AnimatedButton(Button):
    """Custom Button with hover and click animations."""
    def __init__(self, master=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)
        self.default_bg = self["background"]
        self.hover_bg = "#0056b3"  # Darker shade for hover
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress>", self.on_click)

    def on_enter(self, e):
        self.animate_color(self.default_bg, self.hover_bg)

    def on_leave(self, e):
        self.animate_color(self.hover_bg, self.default_bg)

    def on_click(self, e):
        self.ripple_effect()

    def animate_color(self, start_color, end_color, step=0):
        if step > 10:  # Number of steps for the transition
            return
        start_rgb = self.winfo_rgb(start_color)
        end_rgb = self.winfo_rgb(end_color)
        new_color = (
            int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * step / 10),
            int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * step / 10),
            int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * step / 10),
        )
        hex_color = f"#{new_color[0] // 256:02x}{new_color[1] // 256:02x}{new_color[2] // 256:02x}"
        self.config(background=hex_color)
        self.after(20, lambda: self.animate_color(start_color, end_color, step + 1))

    def ripple_effect(self):
        canvas = Canvas(self, width=self.winfo_width(), height=self.winfo_height(), bg=self["background"], highlightthickness=0)
        canvas.place(x=0, y=0)
        x, y = self.winfo_width() // 2, self.winfo_height() // 2
        ripple = canvas.create_oval(x, y, x, y, outline=self["background"], width=2)
        for i in range(10, 60, 2):
            self.after(i, lambda i=i: canvas.coords(ripple, x - i, y - i, x + i, y + i))
        self.after(500, canvas.destroy)

class ResearchDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Research Data Management System")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Define color schemes
        self.light_mode_colors = {
            "bg": "#F7F9FC",
            "fg": "#333",
            "entry_bg": "#FFF",
            "button_bg": "#007BFF",
            "button_fg": "#FFF",
            "listbox_bg": "#FFF",
            "listbox_fg": "#000"
        }
        
        self.dark_mode_colors = {
            "bg": "#2E2E2E",
            "fg": "#FFF",
            "entry_bg": "#3C3F41",
            "button_bg": "#007BFF",
            "button_fg": "#FFF",
            "listbox_bg": "#3C3F41",
            "listbox_fg": "#FFF"
        }
        
        self.current_colors = self.light_mode_colors
        
        # Style Configuration
        self.style = Style()
        self.apply_styles()

        # UI Setup
        self.setup_ui()

        # Load existing entries
        self.load_entries_from_file()

    def apply_styles(self):
        """Apply the current color scheme to the UI."""
        colors = self.current_colors
        
        self.root.configure(bg=colors["bg"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TButton", padding=6, relief="flat", background=colors["button_bg"], foreground=colors["button_fg"])
        self.style.configure("TEntry", padding=5, fieldbackground=colors["entry_bg"], foreground=colors["fg"])

    def toggle_dark_mode(self):
        """Toggle between light mode and dark mode with animation."""
        def animate_bg(color1, color2, step=0):
            if step > 10: return
            r1, g1, b1 = self.root.winfo_rgb(color1)
            r2, g2, b2 = self.root.winfo_rgb(color2)
            r = int(r1 + (r2 - r1) * step / 10)
            g = int(g1 + (g2 - g1) * step / 10)
            b = int(b1 + (b2 - b1) * step / 10)
            color = f"#{r // 256:02x}{g // 256:02x}{b // 256:02x}"
            self.root.configure(bg=color)
            self.root.after(20, lambda: animate_bg(color1, color2, step + 1))

        if self.current_colors == self.light_mode_colors:
            self.current_colors = self.dark_mode_colors
            animate_bg("#F7F9FC", "#2E2E2E")
        else:
            self.current_colors = self.light_mode_colors
            animate_bg("#2E2E2E", "#F7F9FC")
        self.apply_styles()
        self.update_widget_styles()

    def update_widget_styles(self):
        """Update the styles of individual widgets after a mode switch."""
        for widget in self.root.winfo_children():
            widget_type = widget.winfo_class()
            if widget_type == 'TLabel':
                widget.configure(foreground=self.current_colors["fg"])
            elif widget_type == 'TEntry':
                widget.configure(background=self.current_colors["entry_bg"], foreground=self.current_colors["fg"])
            elif widget_type == 'TListbox':
                widget.configure(background=self.current_colors["listbox_bg"], foreground=self.current_colors["listbox_fg"])

    def setup_ui(self):
        # Header
        Label(self.root, text="Research Data Management System", font=("Helvetica", 16, "bold"), bg=self.current_colors["bg"], fg=self.current_colors["fg"]).pack(pady=10)

        # Input Fields
        self.input_frame = Frame(self.root)
        self.input_frame.pack(padx=20, pady=10)

        Label(self.input_frame, text="Experiment Name:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = Entry(self.input_frame, width=40, bg=self.current_colors["entry_bg"], fg=self.current_colors["fg"])
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(self.name_entry, "Enter the name of the experiment.")

        Label(self.input_frame, text="Researcher Name:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.researcher_entry = Entry(self.input_frame, width=40, bg=self.current_colors["entry_bg"], fg=self.current_colors["fg"])
        self.researcher_entry.grid(row=1, column=1, padx=5, pady=5)
        ToolTip(self.researcher_entry, "Enter the name of the researcher.")

        Label(self.input_frame, text="Date (YYYY-MM-DD):", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = Entry(self.input_frame, width=40, bg=self.current_colors["entry_bg"], fg=self.current_colors["fg"])
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        ToolTip(self.date_entry, "Enter the date of the experiment.")

        Label(self.input_frame, text="Description:", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.description_entry = Entry(self.input_frame, width=40, bg=self.current_colors["entry_bg"], fg=self.current_colors["fg"])
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)
        ToolTip(self.description_entry, "Enter a brief description of the experiment.")

        # Buttons
        self.button_frame = Frame(self.root)
        self.button_frame.pack(pady=10)

        self.add_button = AnimatedButton(self.button_frame, text="Add Entry", command=self.add_entry, bg=self.current_colors["button_bg"], fg=self.current_colors["button_fg"])
        self.add_button.grid(row=0, column=0, padx=10)
        ToolTip(self.add_button, "Click to add the entry.")

        self.clear_button = AnimatedButton(self.button_frame, text="Clear Fields", command=self.clear_fields, bg=self.current_colors["button_bg"], fg=self.current_colors["button_fg"])
        self.clear_button.grid(row=0, column=1, padx=10)
        ToolTip(self.clear_button, "Click to clear all input fields.")

        self.save_button = AnimatedButton(self.button_frame, text="Save to CSV", command=self.save_entries_to_file, bg=self.current_colors["button_bg"], fg=self.current_colors["button_fg"])
        self.save_button.grid(row=0, column=2, padx=10)
        ToolTip(self.save_button, "Click to save entries to a CSV file.")

        # Entry List
        self.list_frame = Frame(self.root)
        self.list_frame.pack(pady=10)

        self.scrollbar = Scrollbar(self.list_frame, orient="vertical")
        self.entry_listbox = Listbox(self.list_frame, yscrollcommand=self.scrollbar.set, width=80, height=10, bg=self.current_colors["listbox_bg"], fg=self.current_colors["listbox_fg"])
        self.scrollbar.config(command=self.entry_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.entry_listbox.pack(side="left", fill="both", expand=True)
        ToolTip(self.entry_listbox, "List of all entries.")

        # Menu
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.mode_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Options", menu=self.mode_menu)
        self.mode_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.mode_menu.add_command(label="Exit", command=self.root.quit)

    def add_entry(self):
        name = self.name_entry.get()
        researcher = self.researcher_entry.get()
        date = self.date_entry.get()
        description = self.description_entry.get()

        if not name or not researcher or not date or not description:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        entry = f"{name} - {researcher} - {date} - {description}"
        self.entry_listbox.insert(END, entry)
        self.clear_fields()

    def clear_fields(self):
        self.name_entry.delete(0, END)
        self.researcher_entry.delete(0, END)
        self.date_entry.delete(0, END)
        self.description_entry.delete(0, END)

    def save_entries_to_file(self):
        entries = self.entry_listbox.get(0, END)
        if not entries:
            messagebox.showwarning("Save Error", "There are no entries to save.")
            return

        file_name = f"research_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(file_name, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Experiment Name", "Researcher Name", "Date", "Description"])
            for entry in entries:
                writer.writerow(entry.split(" - "))

        messagebox.showinfo("Save Successful", f"Entries have been saved to {file_name}.")

    def load_entries_from_file(self):
        if not os.path.exists("entries.csv"):
            return

        with open("entries.csv", mode="r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                entry = " - ".join(row)
                self.entry_listbox.insert(END, entry)


if __name__ == "__main__":
    root = Tk()
    app = ResearchDataApp(root)
    root.mainloop()
