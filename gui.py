import os
import threading
import tempfile
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
from text_extraction import extract_text
from chunking import chunk_text
from tts_engine import TTSEngine
from audio_utils import concatenate_wavs, cleanup_files, get_chunk_cache_path

# Set theme and color
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class Doc2VoiceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("doc2voice - Personal TTS")
        self.geometry("700x600")

        # UI State
        self.input_file = ctk.StringVar()
        self.voice_file = ctk.StringVar()
        self.language = ctk.StringVar(value="en")
        self.output_format = ctk.StringVar(value="wav")
        self.temperature = ctk.DoubleVar(value=0.75)
        self.top_p = ctk.DoubleVar(value=0.85)
        self.voice_library = []
        self.is_processing = False

        self.setup_ui()

    def setup_ui(self):
        # Title
        self.header = ctk.CTkLabel(self, text="doc2voice", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=20)

        # File Selection Frame
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=40, fill="x")

        # Input Document
        self.input_label = ctk.CTkLabel(self.file_frame, text="Document (PDF/TXT/DOCX):")
        self.input_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_entry = ctk.CTkEntry(self.file_frame, textvariable=self.input_file, width=300)
        self.input_entry.grid(row=0, column=1, padx=10, pady=10)
        self.input_btn = ctk.CTkButton(self.file_frame, text="Browse", width=80, command=self.browse_input)
        self.input_btn.grid(row=0, column=2, padx=10, pady=10)

        self.voice_label = ctk.CTkLabel(self.file_frame, text="Voice Sample (WAV):")
        self.voice_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.voice_entry = ctk.CTkEntry(self.file_frame, textvariable=self.voice_file, width=300)
        self.voice_entry.grid(row=1, column=1, padx=10, pady=10)
        self.voice_btn = ctk.CTkButton(self.file_frame, text="Browse", width=80, command=self.browse_voice)
        self.voice_btn.grid(row=1, column=2, padx=10, pady=10)

        # Voice Library Dropdown
        self.lib_label = ctk.CTkLabel(self.file_frame, text="Or choose from Library:")
        self.lib_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.update_voice_library()
        self.lib_option = ctk.CTkOptionMenu(self.file_frame, values=["Custom..."] + [v[0] for v in self.voice_library], command=self.select_library_voice)
        self.lib_option.grid(row=2, column=1, padx=10, pady=10)
        self.refresh_btn = ctk.CTkButton(self.file_frame, text="Refresh", width=80, command=self.update_voice_library_ui)
        self.refresh_btn.grid(row=2, column=2, padx=10, pady=10)

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=40, fill="x")

        # Language
        self.lang_label = ctk.CTkLabel(self.settings_frame, text="Language:")
        self.lang_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.lang_option = ctk.CTkOptionMenu(self.settings_frame, values=["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "hu", "ko", "hi"], variable=self.language)
        self.lang_option.grid(row=0, column=1, padx=10, pady=10)

        # Format
        self.format_label = ctk.CTkLabel(self.settings_frame, text="Format:")
        self.format_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.format_option = ctk.CTkOptionMenu(self.settings_frame, values=["wav", "mp3"], variable=self.output_format)
        self.format_option.grid(row=0, column=3, padx=10, pady=10)

        # Expressiveness Sliders
        self.temp_label = ctk.CTkLabel(self.settings_frame, text="Temperature (0.1 - 1.0):")
        self.temp_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.temp_slider = ctk.CTkSlider(self.settings_frame, from_=0.1, to=1.0, variable=self.temperature)
        self.temp_slider.grid(row=1, column=1, padx=10, pady=10)

        self.top_p_label = ctk.CTkLabel(self.settings_frame, text="Top P (0.1 - 1.0):")
        self.top_p_label.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.top_p_slider = ctk.CTkSlider(self.settings_frame, from_=0.1, to=1.0, variable=self.top_p)
        self.top_p_slider.grid(row=1, column=3, padx=10, pady=10)

        # Action Button
        self.convert_btn = ctk.CTkButton(self, text="Start Conversion", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.start_conversion)
        self.convert_btn.pack(pady=20)

        # Progress Frame
        self.progress_label = ctk.CTkLabel(self, text="Status: Ready")
        self.progress_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        # Log Area
        self.log_area = ctk.CTkTextbox(self, height=150, width=600)
        self.log_area.pack(pady=10)

    def log(self, message):
        self.log_area.insert("end", f"{message}\n")
        self.log_area.see("end")
        self.progress_label.configure(text=f"Status: {message}")

    def browse_input(self):
        f = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.docx *.txt")])
        if f: self.input_file.set(f)

    def browse_voice(self):
        f = filedialog.askopenfilenames(filetypes=[("Audio", "*.wav")])
        if f: 
            self.voice_file.set(", ".join(f))
            self.lib_option.set("Custom...")

    def update_voice_library(self):
        """Scans the voices/ directory for WAV files."""
        lib_path = os.path.join(os.getcwd(), "voices")
        if not os.path.exists(lib_path):
            os.makedirs(lib_path, exist_ok=True)
        
        self.voice_library = []
        for file in os.listdir(lib_path):
            if file.lower().endswith(".wav"):
                name = os.path.splitext(file)[0].replace("_", " ")
                self.voice_library.append((name, os.path.abspath(os.path.join(lib_path, file))))
    
    def update_voice_library_ui(self):
        self.update_voice_library()
        names = ["Custom..."] + [v[0] for v in self.voice_library]
        self.lib_option.configure(values=names)

    def select_library_voice(self, selected_name):
        if selected_name == "Custom...":
            self.voice_file.set("")
        else:
            for name, path in self.voice_library:
                if name == selected_name:
                    self.voice_file.set(path)
                    break

    def start_conversion(self):
        if not self.input_file.get() or not self.voice_file.get():
            messagebox.showerror("Error", "Please select both a document and a voice sample.")
            return
        
        if self.is_processing:
            return

        self.is_processing = True
        self.convert_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.log_area.delete("1.0", "end")
        
        # Run in thread
        threading.Thread(target=self.process_logic, daemon=True).start()

    def process_logic(self):
        try:
            input_path = self.input_file.get()
            voice_path = self.voice_file.get()
            lang = self.language.get()
            fmt = self.output_format.get()
            temp = self.temperature.get()
            top_p = self.top_p.get()
            out_path = filedialog.asksaveasfilename(defaultextension=f".{fmt}", filetypes=[("Audio", f"*.{fmt}")])
            
            if not out_path:
                self.reset_ui("Cancelled")
                return

            self.log(f"Extracting text (Temp: {temp:.2f}, Top P: {top_p:.2f})...")
            raw_text = extract_text(input_path)
            
            self.log(f"Chunking text...")
            chunks = chunk_text(raw_text)
            num_chunks = len(chunks)
            self.log(f"Total chunks: {num_chunks}")

            if not chunks:
                self.reset_ui("No text found.")
                return

            self.log("Initializing TTS Engine...")
            engine = TTSEngine()

            tmp_files = [] # Will store list of {"path": ..., "type": ...}
            for i, chunk_data in enumerate(chunks):
                text = chunk_data["text"]
                chunk_type = chunk_data["type"]
                
                self.log(f"Processing Chunk {i+1}/{num_chunks}...")
                self.progress_bar.set((i + 1) / num_chunks)
                
                # Support multiple voices (comma separated in the UI)
                voice_paths = [v.strip() for v in voice_path.split(",")] if "," in voice_path else voice_path
                
                # Caching logic
                cache_path = get_chunk_cache_path(
                    text=text,
                    voice_path=str(voice_paths),
                    language=lang,
                    temperature=temp,
                    top_p=top_p
                )
                
                if os.path.exists(cache_path):
                    self.log(f"   [Chunk {i+1}] Using cached audio...")
                    tmp_files.append({"path": cache_path, "type": chunk_type})
                    continue

                self.log(f"   [Chunk {i+1}] Generating speech...")
                engine.generate_speech(text, voice_paths, lang, cache_path, temperature=temp, top_p=top_p)
                tmp_files.append({"path": cache_path, "type": chunk_type})

            if tmp_files:
                self.log(f"Merging audio chunks into {os.path.basename(out_path)}...")
                concatenate_wavs(tmp_files, out_path, format=fmt)
                cleanup_files([f["path"] for f in tmp_files])
                
            self.reset_ui("Conversion Successful!")
            messagebox.showinfo("Success", f"Audio saved to:\n{out_path}")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.reset_ui("Failed")
            messagebox.showerror("Error", str(e))

    def reset_ui(self, status):
        self.is_processing = False
        self.convert_btn.configure(state="normal")
        self.progress_label.configure(text=f"Status: {status}")

if __name__ == "__main__":
    app = Doc2VoiceGUI()
    app.mainloop()
