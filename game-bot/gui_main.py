"""
Match-3 Bot GUI Application
Professional interface for game automation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import keyboard
import sys
import os

from main import GameBot

class BotGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Match-3 Auto Bot - Pukiwo")
        self.window.geometry("1000x900")
        self.window.resizable(True, True)
        
        # Bot instance
        self.bot = None
        self.bot_thread = None
        self.is_running = False
        self.is_paused = False
        
        # Setup UI
        self.setup_ui()
        
        # Setup hotkeys
        keyboard.on_press_key('space', self.toggle_pause)
        
        # Redirect stdout to text widget
        sys.stdout = TextRedirector(self.log_text)
        sys.stderr = TextRedirector(self.log_text)
    
    def setup_ui(self):
        """Setup user interface"""
        # Title
        title_frame = tk.Frame(self.window, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(
            title_frame,
            text="🎮 MATCH-3 AUTO BOT",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Calibration Frame - Chia thành 2 cột
        calib_frame = tk.LabelFrame(
            self.window,
            text="📐 Calibration (Chọn từng cái riêng biệt)",
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=10
        )
        calib_frame.pack(fill='x', padx=20, pady=10)
        
        # Column 1: Vùng (Regions)
        region_frame = tk.Frame(calib_frame)
        region_frame.grid(row=0, column=0, padx=10, sticky='n')
        
        tk.Label(
            region_frame,
            text="📍 Chọn vùng:",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w')
        
        self.game_window_btn = tk.Button(
            region_frame,
            text="🖼️  Vùng Game Window",
            command=lambda: self.select_region('game_window'),
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.game_window_btn.pack(pady=3)
        
        self.board_btn = tk.Button(
            region_frame,
            text="♟️  Vùng Board 8x8",
            command=lambda: self.select_region('board'),
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.board_btn.pack(pady=3)
        
        self.timer_btn = tk.Button(
            region_frame,
            text="⏱️  Vùng Timer",
            command=lambda: self.select_region('timer'),
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.timer_btn.pack(pady=3)
        
        # Column 2: Vị trí nút (Button Positions)
        button_pos_frame = tk.Frame(calib_frame)
        button_pos_frame.grid(row=0, column=1, padx=10, sticky='n')
        
        tk.Label(
            button_pos_frame,
            text="🖱️  Set vị trí nút:",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w')
        
        self.nhan_btn = tk.Button(
            button_pos_frame,
            text="🎁 Nút NHẬN (click)",
            command=lambda: self.select_button_position('nhan'),
            font=('Arial', 9),
            bg='#9b59b6',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.nhan_btn.pack(pady=3)
        
        self.chien_btn = tk.Button(
            button_pos_frame,
            text="🗺️  Nút CHIẾN (click)",
            command=lambda: self.select_button_position('chien'),
            font=('Arial', 9),
            bg='#9b59b6',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.chien_btn.pack(pady=3)
        
        self.batdau_btn = tk.Button(
            button_pos_frame,
            text="⚔️  Nút BẮT ĐẦU (click)",
            command=lambda: self.select_button_position('batdau'),
            font=('Arial', 9),
            bg='#9b59b6',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.batdau_btn.pack(pady=3)
        
        # Column 3: Vùng nút Nhận (để detect)
        nhan_region_frame = tk.Frame(calib_frame)
        nhan_region_frame.grid(row=0, column=2, padx=10, sticky='n')
        
        tk.Label(
            nhan_region_frame,
            text="🔍 Vùng detect nút:",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w')
        
        self.nhan_region_btn = tk.Button(
            nhan_region_frame,
            text="🎁 Vùng nút NHẬN",
            command=lambda: self.select_region('nhan_region'),
            font=('Arial', 9),
            bg='#e67e22',
            fg='white',
            width=22,
            cursor='hand2'
        )
        self.nhan_region_btn.pack(pady=3)
        
        tk.Label(
            nhan_region_frame,
            text="(Chọn vùng để quét\ntìm nút Nhận)",
            font=('Arial', 7),
            fg='#7f8c8d'
        ).pack()
        
        # Control Frame
        control_frame = tk.LabelFrame(
            self.window,
            text="⚙️ Điều khiển Bot",
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=15
        )
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Buttons
        button_frame = tk.Frame(control_frame)
        button_frame.pack()
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶️ Bắt đầu",
            command=self.start_bot,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            width=25,
            height=2,
            cursor='hand2'
        )
        self.start_btn.grid(row=0, column=0, padx=10, pady=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Dừng",
            command=self.stop_bot,
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            width=25,
            height=2,
            cursor='hand2',
            state='disabled'
        )
        self.stop_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Status Frame
        status_frame = tk.LabelFrame(
            self.window,
            text="📊 Trạng thái",
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="⏸️ Chưa chạy",
            font=('Arial', 14, 'bold'),
            fg='#95a5a6'
        )
        self.status_label.pack()
        
        self.moves_label = tk.Label(
            status_frame,
            text="Số lượt đã chơi: 0 | Điểm số: 0",
            font=('Arial', 10)
        )
        self.moves_label.pack(pady=5)
        
        # Info Frame
        info_frame = tk.LabelFrame(
            self.window,
            text="ℹ️ Hướng dẫn",
            font=('Arial', 11, 'bold'),
            padx=15,
            pady=10
        )
        info_frame.pack(fill='x', padx=20, pady=10)
        
        instructions = """
• Chọn từng vùng và nút riêng biệt (bên trái: vùng, bên phải: nút)
• Nhấn "Bắt đầu" để bot tự động chơi
• Nhấn SPACE để tạm dừng/tiếp tục bot
• Nhấn "Dừng" để dừng hoàn toàn
        """
        
        info_label = tk.Label(
            info_frame,
            text=instructions,
            font=('Arial', 9),
            justify='left',
            fg='#34495e'
        )
        info_label.pack()
        
        # Log Frame
        log_frame = tk.LabelFrame(
            self.window,
            text="📝 Nhật ký hoạt động",
            font=('Arial', 11, 'bold'),
            padx=10,
            pady=10
        )
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            font=('Consolas', 9),
            bg='#ecf0f1',
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Footer
        footer = tk.Label(
            self.window,
            text="Made with ❤️ | Press SPACE to pause/resume",
            font=('Arial', 8),
            fg='#7f8c8d'
        )
        footer.pack(pady=5)
    
    def select_region(self, region_type):
        """Select a specific region
        
        Args:
            region_type: 'game_window', 'board', 'timer', or 'nhan_region'
        """
        region_names = {
            'game_window': 'CỬA SỔ GAME',
            'board': 'BÀN CỜ 8x8',
            'timer': 'TIMER',
            'nhan_region': 'VÙNG NÚT NHẬN'
        }
        
        print(f"\n{'='*60}")
        print(f"📐 CHỌN VÙNG {region_names[region_type]}")
        print(f"{'='*60}")
        
        def run_selection():
            from calibrate import BoardCalibrator
            import yaml
            
            calibrator = BoardCalibrator()
            
            # Capture screenshot once
            screenshot = calibrator.capture_screenshot()
            
            # Select the specific region
            region_data = calibrator.select_region(region_names[region_type], screenshot=screenshot)
            
            if region_data:
                print(f"✅ Đã chọn vùng {region_names[region_type]}:")
                print(f"   Vị trí: ({region_data['left']}, {region_data['top']})")
                print(f"   Kích thước: {region_data['width']}x{region_data['height']}")
                
                # Load current config
                try:
                    with open('config.yaml', 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                except:
                    config = {}
                
                # Update config based on region type
                if region_type == 'game_window':
                    if 'game_window' not in config:
                        config['game_window'] = {}
                    config['game_window']['top'] = region_data['top']
                    config['game_window']['left'] = region_data['left']
                    config['game_window']['width'] = region_data['width']
                    config['game_window']['height'] = region_data['height']
                    
                elif region_type == 'board':
                    if 'screen' not in config:
                        config['screen'] = {}
                    config['screen']['top'] = region_data['top']
                    config['screen']['left'] = region_data['left']
                    config['screen']['width'] = region_data['width']
                    config['screen']['height'] = region_data['height']
                    
                elif region_type == 'timer':
                    if 'turn_detection' not in config:
                        config['turn_detection'] = {}
                    if 'timer_region' not in config['turn_detection']:
                        config['turn_detection']['timer_region'] = {}
                    config['turn_detection']['timer_region']['top'] = region_data['top']
                    config['turn_detection']['timer_region']['left'] = region_data['left']
                    config['turn_detection']['timer_region']['width'] = region_data['width']
                    config['turn_detection']['timer_region']['height'] = region_data['height']
                    config['turn_detection']['enabled'] = True
                    
                elif region_type == 'nhan_region':
                    if 'button_regions' not in config:
                        config['button_regions'] = {}
                    config['button_regions']['nhan'] = {
                        'top': region_data['top'],
                        'left': region_data['left'],
                        'width': region_data['width'],
                        'height': region_data['height']
                    }
                
                # Save config
                with open('config.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"💾 Đã lưu vào config.yaml!")
            else:
                print("❌ Đã hủy chọn vùng")
        
        thread = threading.Thread(target=run_selection, daemon=True)
        thread.start()
    
    def select_button_position(self, button_type):
        """Select a specific button position
        
        Args:
            button_type: 'nhan', 'chien', or 'batdau'
        """
        button_names = {
            'nhan': 'NHẬN',
            'chien': 'CHIẾN',
            'batdau': 'BẮT ĐẦU'
        }
        
        print(f"\n{'='*60}")
        print(f"🖱️  SET VỊ TRÍ NÚT {button_names[button_type]}")
        print(f"{'='*60}")
        print(f"Hướng dẫn: Mở game đến màn có nút '{button_names[button_type]}'")
        
        def run_selection():
            from calibrate import BoardCalibrator
            import yaml
            
            calibrator = BoardCalibrator()
            
            # Capture screenshot
            screenshot = calibrator.capture_screenshot()
            
            # Select button position
            button_pos = calibrator.select_button_position(f"NÚT {button_names[button_type]}", screenshot=screenshot)
            
            if button_pos:
                print(f"✅ Đã chọn vị trí nút {button_names[button_type]}:")
                print(f"   Tọa độ: ({button_pos['x']}, {button_pos['y']})")
                
                # Load current config
                try:
                    with open('config.yaml', 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                except:
                    config = {}
                
                # Update button position
                if 'button_positions' not in config:
                    config['button_positions'] = {}
                
                config['button_positions'][button_type] = {
                    'x': button_pos['x'],
                    'y': button_pos['y']
                }
                
                # Save config
                with open('config.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                
                print(f"💾 Đã lưu vào config.yaml!")
            else:
                print("❌ Đã hủy chọn nút")
        
        thread = threading.Thread(target=run_selection, daemon=True)
        thread.start()
    
    def start_bot(self):
        """Start the bot"""
        if self.is_running:
            print("⚠️ Bot đang chạy!")
            return
        
        print("\n" + "="*60)
        print("🚀 KHỞI ĐỘNG BOT")
        print("="*60)
        
        self.is_running = True
        self.is_paused = False
        self.update_status("▶️ Đang chạy", '#27ae60')
        
        # Disable/Enable buttons
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.game_window_btn.config(state='disabled')
        self.board_btn.config(state='disabled')
        self.timer_btn.config(state='disabled')
        self.nhan_btn.config(state='disabled')
        self.chien_btn.config(state='disabled')
        self.batdau_btn.config(state='disabled')
        self.nhan_region_btn.config(state='disabled')
        
        # Run bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
    
    def stop_bot(self):
        """Stop the bot"""
        if not self.is_running:
            return
        
        print("\n🛑 Đang dừng bot...")
        
        self.is_running = False
        self.is_paused = False
        
        if self.bot:
            self.bot.running = False
        
        self.update_status("⏹️ Đã dừng", '#e74c3c')
        
        # Enable/Disable buttons
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.game_window_btn.config(state='normal')
        self.board_btn.config(state='normal')
        self.timer_btn.config(state='normal')
        self.nhan_btn.config(state='normal')
        self.chien_btn.config(state='normal')
        self.batdau_btn.config(state='normal')
        self.nhan_region_btn.config(state='normal')
        
        print("✅ Bot đã dừng!")
    
    def toggle_pause(self, e=None):
        """Toggle pause/resume with Space key"""
        if not self.is_running:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.update_status("⏸️ Tạm dừng (Nhấn SPACE để tiếp tục)", '#f39c12')
            print("\n⏸️ Bot đã tạm dừng. Nhấn SPACE để tiếp tục...")
        else:
            self.update_status("▶️ Đang chạy", '#27ae60')
            print("▶️ Bot tiếp tục chạy...")
    
    def run_bot(self):
        """Run bot main loop"""
        try:
            # Create bot instance
            self.bot = GameBot(config_path="config.yaml", auto_calibrate=False)
            
            print("✅ Bot đã khởi tạo thành công!")
            print("📌 Đảm bảo cửa sổ game hiện rõ ràng")
            print("⌨️ Nhấn SPACE để tạm dừng/tiếp tục")
            print("")
            
            iteration = 0
            
            while self.is_running:
                # Check if paused
                if self.is_paused:
                    import time
                    time.sleep(0.1)
                    continue
                
                iteration += 1
                print(f"\n--- Lượt {iteration} ---")
                
                # Run single iteration
                success = self.bot.run_single_iteration()
                
                # Update UI
                self.update_moves_label()
                
                if not success:
                    import time
                    time.sleep(1)
                    continue
                
                # Delay between moves (2-3 seconds for calculation)
                import time
                import random
                delay = random.uniform(2.0, 3.0)
                time.sleep(delay)
        
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.is_running:
                self.stop_bot()
    
    def update_status(self, text, color):
        """Update status label"""
        self.status_label.config(text=text, fg=color)
    
    def update_moves_label(self):
        """Update moves and score label"""
        if self.bot:
            text = f"Số lượt đã chơi: {self.bot.move_count} | Điểm số: {self.bot.total_score}"
            self.moves_label.config(text=text)
    
    def run(self):
        """Run the GUI"""
        print("="*60)
        print("🎮 MATCH-3 AUTO BOT - PUKIWO")
        print("="*60)
        print("Chào mừng bạn đến với công cụ tự động chơi game!")
        print("")
        
        self.window.mainloop()


class TextRedirector:
    """Redirect stdout/stderr to text widget"""
    
    def __init__(self, widget):
        self.widget = widget
    
    def write(self, text):
        self.widget.insert('end', text)
        self.widget.see('end')
        self.widget.update()
    
    def flush(self):
        pass


def main():
    """Main entry point"""
    app = BotGUI()
    app.run()


if __name__ == "__main__":
    main()
