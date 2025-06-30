import customtkinter as ctk
from global_config.project_configuration import OEM_CONFIGURATION_CLASS, OEM_CONFIGURATION_JSON, OEM_CONFIGURATION_FILE, OEM_CONFIGURATION_PACKAGE
from tkinter import messagebox, ttk
import json
import os


class SecondaryUI:
    @staticmethod
    def open(parent, callback, variable="", value=""):
        def on_ok():
            callback(variable_entry.get(), value_entry.get())
            secondary_ui.destroy()

        def on_cancel():
            secondary_ui.destroy()

        secondary_ui = ctk.CTkToplevel(parent)
        secondary_ui.title("Edit Configuration")
        secondary_ui.resizable(False, False)

        # Always on top and modal
        secondary_ui.transient(parent)
        secondary_ui.grab_set()
        secondary_ui.attributes('-topmost', True)
        secondary_ui.focus_force()

        # Center on screen based on main window
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        width, height = 320, 140
        x = parent_x + (parent_w // 2) - (width // 2)
        y = parent_y + (parent_h // 2) - (height // 2)
        secondary_ui.geometry(f"{width}x{height}+{x}+{y}")

        # Layout config
        secondary_ui.grid_columnconfigure(0, weight=2)  # 30%
        secondary_ui.grid_columnconfigure(1, weight=8)  # 70%

        variable_label = ctk.CTkLabel(secondary_ui, text="Variable:")
        variable_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        variable_entry = ctk.CTkEntry(secondary_ui)
        variable_entry.grid(row=0, column=1, padx=10, pady=8, sticky="nsew")
        variable_entry.insert(0, variable)

        value_label = ctk.CTkLabel(secondary_ui, text="Value:")
        value_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")

        value_entry = ctk.CTkEntry(secondary_ui)
        value_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")
        value_entry.insert(0, value)

        ok_button = ctk.CTkButton(secondary_ui, text="OK", command=on_ok)
        ok_button.grid(row=2, column=0, padx=10, pady=12, sticky="ew")

        cancel_button = ctk.CTkButton(secondary_ui, text="Cancel", command=on_cancel)
        cancel_button.grid(row=2, column=1, padx=10, pady=12, sticky="ew")


class MainUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OEM Configuration")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.6)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.setup_table()
        self.setup_buttons()
        self.load_existing_config()

    def setup_table(self):
        self.table_frame = ctk.CTkFrame(self, corner_radius=5)
        self.table_frame.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        style = ttk.Style(self)
        style.configure("Custom.Treeview.Heading",
                        font=("Arial", 10, "bold"),
                        background="#3399FF",
                        foreground="black")
        style.configure("Custom.Treeview", rowheight=25)

        self.table = ttk.Treeview(self.table_frame,
                                  columns=("Variable", "Value"),
                                  show="headings",
                                  height=20,
                                  style="Custom.Treeview")
        self.table.heading("Variable", text="Variable", anchor="w")
        self.table.heading("Value", text="Value", anchor="w")
        self.table.column("Variable", width=300, anchor="w")
        self.table.column("Value", width=420, anchor="w")
        self.table.pack(expand=True, fill="both", padx=7, pady=7)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def setup_buttons(self):
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(button_frame, text="New", command=self.new_entry).grid(row=0, column=0, padx=4)
        ctk.CTkButton(button_frame, text="Edit", command=self.edit_entry).grid(row=0, column=1, padx=4)
        ctk.CTkButton(button_frame, text="Delete", command=self.delete_entry).grid(row=0, column=2, padx=4)
        ctk.CTkButton(button_frame, text="Generate", command=self.generate_action).grid(row=0, column=3, padx=4)

    def new_entry(self):
        self.attributes('-topmost', True)
        SecondaryUI.open(self, self.add_to_table)
        self.attributes('-topmost', False)

    def edit_entry(self):
        selected_item = self.get_selected_item()
        if selected_item:
            variable, value = self.table.item(selected_item, "values")
            SecondaryUI.open(self, self.update_table, variable, value)
        else:
            messagebox.showwarning("Warning", "No entry selected for editing.")

    def delete_entry(self):
        selected_item = self.get_selected_item()
        if selected_item:
            self.table.delete(selected_item)
        else:
            messagebox.showwarning("Warning", "No entry selected for deletion.")

    def generate_action(self):
        rows = self.table.get_children()
        if not rows:
            messagebox.showwarning("Warning", "No data to save.")
            return

        data = []
        class_lines = [f"class {OEM_CONFIGURATION_CLASS}:"]
        for row in rows:
            variable, value = self.table.item(row, "values")
            safe_variable = variable.strip().upper().replace(" ", "_")
            if not safe_variable.isidentifier():
                messagebox.showerror("Error", f"Invalid variable name: {variable}")
                return

            data.append({"variable": variable, "value": value})
            class_lines.append(f"    {safe_variable} = {repr(value)}")

        try:
            with open(OEM_CONFIGURATION_JSON, "w") as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON: {e}")
            return

        try:
            with open(OEM_CONFIGURATION_FILE, "w") as class_file:
                class_file.write("\n".join(class_lines) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Python class: {e}")
            return

        messagebox.showinfo("Success", f"Data saved to:\n- {OEM_CONFIGURATION_JSON}\n- {OEM_CONFIGURATION_FILE}")

    def load_existing_config(self):
        try:
            if not os.path.exists(OEM_CONFIGURATION_JSON):
                print(f"[INFO] {OEM_CONFIGURATION_JSON} not found. Starting with empty table.")
                return

            with open(OEM_CONFIGURATION_JSON, "r") as json_file:
                data = json.load(json_file)

            if not isinstance(data, list):
                raise ValueError("Invalid format: expected a list of objects.")

            for item in data:
                if not isinstance(item, dict) or "variable" not in item or "value" not in item:
                    raise ValueError("Each item must contain 'variable' and 'value' keys.")
                self.add_to_table(item["variable"], item["value"])

            print(f"[INFO] Loaded {len(data)} items from {OEM_CONFIGURATION_JSON}.")

        except json.JSONDecodeError:
            messagebox.showerror("JSON Error", f"The config file {OEM_CONFIGURATION_JSON} contains invalid JSON.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config from {OEM_CONFIGURATION_JSON}:\n{str(e)}")

    def add_to_table(self, variable, value):
        self.table.insert("", "end", values=(variable, value))

    def update_table(self, variable, value):
        selected_item = self.get_selected_item()
        if selected_item:
            self.table.item(selected_item, values=(variable, value))

    def get_selected_item(self):
        selected = self.table.selection()
        return selected[0] if selected else None


if __name__ == "__main__":
    app = MainUI()
    app.mainloop()
