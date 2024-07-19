import os
import customtkinter as ctk
from googletrans import Translator
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import csv
import datetime
import asyncio

# Initialize application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Constants
MAX_CHARS = 100
MAX_DESC_CHARS = 5000

# Custom colors
RESET_BUTTON_COLOR = "#e74c3c"
RESET_BUTTON_HOVER_COLOR = "#c0392b"
INPUT_FRAME_COLOR = "#333333"
SCROLL_COLOR = "#1d1e1e"
OVER_LIMIT_COLOR = "#e74c3c"
TRANSLATE_BUTTON_COLOR = "#1f8b4c"
TRANSLATE_BUTTON_HOVER_COLOR = "#176839"

class YouTubeBulkTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1450x800")
        self.root.title("YouTube Bulk Translator (High Paying)")

        # Set custom icon
        icon_path = os.path.join(os.path.dirname(__file__), "translate.ico")
        self.root.iconbitmap(icon_path)

        self.translator = Translator()
        self.translations = {}
        self.char_count_labels = {}
        self.progress_bar = None

        self.create_widgets()

    def create_widgets(self):
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.pack(padx=10, pady=10, fill="both", expand=True)

        self.input_tab = self.tab_view.add("Input Text")
        self.checker_tab = self.tab_view.add("Checker")

        # Create input section for Input Text tab
        self.create_input_section(self.input_tab)

        # Create sections for each language in Checker tab
        languages = [
            ("Arab", 'ar'), ("Belanda", 'nl'), ("Inggris", 'en'), ("Indonesia", 'id'),
            ("Italia", 'it'), ("Jepang", 'ja'), ("Jerman", 'de'), ("Prancis", 'fr'),
            ("Rusia", 'ru'), ("Spanyol", 'es')
        ]

        for label, code in languages:
            textbox, char_count_label = self.create_language_section(self.checker_tab, label, code)
            self.translations[code] = textbox
            self.char_count_labels[textbox] = char_count_label

        # Add directory input with Browse button at the bottom
        self.create_directory_input()

    def create_input_section(self, parent):
        main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        main_frame.pack(padx=10, pady=5, fill='both', expand=True)

        # Title input
        title_frame = ctk.CTkFrame(main_frame, fg_color=INPUT_FRAME_COLOR)
        title_frame.pack(padx=10, pady=5, fill='x')

        ctk.CTkLabel(title_frame, text="Title").pack(side='left', padx=10, pady=10)
        self.title_textbox = ctk.CTkTextbox(title_frame, height=30)
        self.title_textbox.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        self.title_char_count_label = ctk.CTkLabel(title_frame, text=f"0/{MAX_CHARS}")
        self.title_char_count_label.pack(side='left', padx=10, pady=10)

        # Description input
        desc_frame = ctk.CTkFrame(main_frame, fg_color=INPUT_FRAME_COLOR)
        desc_frame.pack(padx=10, pady=5, fill='both', expand=True)

        ctk.CTkLabel(desc_frame, text="Description").pack(anchor='w', padx=10, pady=(10, 0))
        self.desc_textbox = ctk.CTkTextbox(desc_frame, height=400)
        self.desc_textbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.desc_char_count_label = ctk.CTkLabel(desc_frame, text=f"0/{MAX_DESC_CHARS}")
        self.desc_char_count_label.pack(pady=(0, 10))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        translate_button = ctk.CTkButton(button_frame, text="Translate", command=self.start_translation, 
                                         width=105, fg_color=TRANSLATE_BUTTON_COLOR, 
                                         hover_color=TRANSLATE_BUTTON_HOVER_COLOR)
        translate_button.pack(side='left', padx=5)

        reset_button = ctk.CTkButton(button_frame, text="Reset", command=self.reset_input, 
                                     fg_color=RESET_BUTTON_COLOR, hover_color=RESET_BUTTON_HOVER_COLOR,
                                     width=70)
        reset_button.pack(side='left', padx=5)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill='x', padx=10, pady=(5, 10))
        self.progress_bar.set(0)

        # Bind character count update
        self.title_textbox.bind("<KeyRelease>", self.update_character_counts)
        self.desc_textbox.bind("<KeyRelease>", self.update_character_counts)

    def create_language_section(self, parent, label_text, lang_code):
        outer_frame = ctk.CTkFrame(parent)
        outer_frame.pack(padx=10, pady=5, fill='x')

        try:
            icon_path = os.path.join(os.path.dirname(__file__), f"{lang_code}.png")
            icon = ctk.CTkImage(Image.open(icon_path).resize((20, 20)))
            ctk.CTkLabel(outer_frame, image=icon, text="").pack(side='left', padx=(10, 5), pady=5)
        except FileNotFoundError:
            ctk.CTkLabel(outer_frame, text="", width=20).pack(side='left', padx=(10, 5), pady=5)

        ctk.CTkLabel(outer_frame, text=label_text, width=80).pack(side='left', padx=(0, 10), pady=5)

        textbox_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        textbox_frame.pack(side='left', padx=10, pady=5, fill='x', expand=True)

        textbox = ctk.CTkTextbox(textbox_frame, height=25)  # Single line for title
        textbox.pack(fill='both', expand=True)
        
        textbox.configure(scrollbar_button_color=SCROLL_COLOR)

        button_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        button_frame.pack(side='left', padx=10, pady=5)

        char_count_label = ctk.CTkLabel(button_frame, text=f"0/{MAX_CHARS}", width=70)
        char_count_label.pack(side='left', padx=5)

        copy_button = ctk.CTkButton(button_frame, text="Copy", 
                                    command=lambda: self.copy_to_clipboard(textbox, copy_button),
                                    width=70)
        copy_button.pack(side='left', padx=5)

        return textbox, char_count_label

    def start_translation(self):
        asyncio.run(self.translate_text())

    async def translate_text(self):
        title_text = self.title_textbox.get("1.0", "end-1c")
        desc_text = self.desc_textbox.get("1.0", "end-1c")

        # Detect input language
        input_lang = self.translator.detect(title_text).lang

        # Update progress bar
        total_languages = len(self.translations)
        translated_data = []

        for i, (lang, textbox) in enumerate(self.translations.items(), 1):
            try:
                if lang != input_lang:
                    translated_title = self.translator.translate(title_text, dest=lang).text
                    translated_desc = self.translator.translate(desc_text, dest=lang).text
                    
                    translated_data.append((lang, translated_title, translated_desc))
                else:
                    translated_title = title_text
                    translated_desc = desc_text
                
                # Display translated or original title in Checker tab
                self.insert_text_with_alignment(textbox, translated_title, lang)
            except Exception as e:
                self.insert_text_with_alignment(textbox, f"Error: {str(e)}", lang)
            
            # Update progress bar smoothly
            for j in range(10):
                progress = (i - 1 + (j + 1) / 10) / total_languages
                self.progress_bar.set(progress)
                self.root.update_idletasks()
                await asyncio.sleep(0.01)

        # Reset progress bar after translation is complete
        self.root.after(1000, lambda: self.progress_bar.set(0))
        
        self.update_character_counts()
        
        directory = self.directory_entry.get().strip()
        if directory:
            self.generate_csv_file(translated_data, directory, input_lang)

    def reset_input(self):
        self.title_textbox.delete("1.0", ctk.END)
        self.desc_textbox.delete("1.0", ctk.END)
        self.update_character_counts()

    def update_character_counts(self, event=None):
        title_text = self.title_textbox.get("1.0", "end-1c")
        desc_text = self.desc_textbox.get("1.0", "end-1c")

        if len(title_text) > MAX_CHARS:
            title_text = self.limit_input_chars(title_text, MAX_CHARS)
            self.title_textbox.delete("1.0", ctk.END)
            self.title_textbox.insert(ctk.END, title_text)
        self.title_char_count_label.configure(text=f"{len(title_text)}/{MAX_CHARS}")

        if len(desc_text) > MAX_DESC_CHARS:
            desc_text = self.limit_input_chars(desc_text, MAX_DESC_CHARS)
            self.desc_textbox.delete("1.0", ctk.END)
            self.desc_textbox.insert(ctk.END, desc_text)
        self.desc_char_count_label.configure(text=f"{len(desc_text)}/{MAX_DESC_CHARS}")

        for textbox, label in self.char_count_labels.items():
            text = textbox.get("1.0", "end-1c")
            char_count = len(text)
            label.configure(text=f"{char_count}/{MAX_CHARS}")
            
            if char_count > MAX_CHARS:
                label.configure(text_color=OVER_LIMIT_COLOR)
                textbox.configure(text_color=OVER_LIMIT_COLOR)
            else:
                label.configure(text_color="white")
                textbox.configure(text_color="white")

    def generate_csv_file(self, translated_data, directory, input_lang):
        current_datetime = datetime.datetime.now().strftime("%H%M_%d%m%Y")
        filename = os.path.join(directory, f"translated_{current_datetime}.csv")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write translations without headers, excluding the input language
            for lang, title, description in translated_data:
                if lang != input_lang:
                    writer.writerow([title, description])

    def limit_input_chars(self, text, max_chars):
        return text[:max_chars]

    def copy_to_clipboard(self, textbox, copy_button):
        text_to_copy = textbox.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text_to_copy)
        self.root.update()
        
        original_text = copy_button.cget("text")
        copy_button.configure(text="Copied!")
        self.root.after(2000, lambda: copy_button.configure(text=original_text))

    def insert_text_with_alignment(self, textbox, text, lang):
        textbox.delete("1.0", tk.END)
        if lang == 'ar':
            textbox.insert(tk.END, text.rjust(len(text) + 2))
        else:
            textbox.insert(tk.END, text)
        
        if len(text) > MAX_CHARS:
            textbox.configure(text_color=OVER_LIMIT_COLOR)
        else:
            textbox.configure(text_color="white")

    def create_directory_input(self):
        directory_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        directory_frame.pack(padx=10, pady=5, fill='x')

        directory_inner_frame = ctk.CTkFrame(directory_frame, fg_color="transparent")
        directory_inner_frame.pack(expand=True)

        ctk.CTkLabel(directory_inner_frame, text="CSV Save Directory").pack(side='left', padx=(0, 5), pady=10)

        self.directory_entry = ctk.CTkEntry(directory_inner_frame, width=300)
        self.directory_entry.pack(side='left', padx=5, pady=10)

        browse_button = ctk.CTkButton(directory_inner_frame, text="Browse", command=self.browse_directory, width=70)
        browse_button.pack(side='left', padx=5, pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)

# Run the application
if __name__ == "__main__":
    app = ctk.CTk()
    translator_app = YouTubeBulkTranslatorApp(app)
    app.mainloop()