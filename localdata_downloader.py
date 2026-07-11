import os
import sys
import threading
import time
import datetime
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import requests

class LocalDataDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("지방행정인허가데이터(LOCALDATA) 다운로더")
        self.root.geometry("620x640")
        self.root.resizable(True, True)
        
        # Color Theme (Sleek Dark Mode)
        self.bg_color = "#1e1e2e"
        self.card_color = "#252538"
        self.primary_color = "#89b4fa"  # Calm blue
        self.secondary_color = "#a6e3a1"  # Mint green
        self.text_color = "#cdd6f4"
        self.text_dim = "#a6adc8"
        self.border_color = "#45475a"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Progressbar styling
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.card_color,
            background=self.primary_color,
            lightcolor=self.primary_color,
            darkcolor=self.primary_color,
            bordercolor=self.border_color,
            thickness=15
        )
        
        self.download_targets = {
            "일반음식점": {
                "url": "https://file.localdata.go.kr/file/download/general_restaurants/info",
                "filename": "식품_일반음식점.csv",
                "var": tk.BooleanVar(value=True)
            },
            "휴게음식점": {
                "url": "https://file.localdata.go.kr/file/download/rest_cafes/info",
                "filename": "식품_휴게음식점.csv",
                "var": tk.BooleanVar(value=True)
            }
        }
        
        self.save_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.is_downloading = False
        
        self.create_widgets()
        self.toggle_filter_inputs()  # Initialize filter input state
        
    def create_widgets(self):
        # Header Label
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        title_label = tk.Label(
            header_frame, 
            text="LOCALDATA 음식점 인허가 데이터 다운로더", 
            font=("Malgun Gothic", 16, "bold"), 
            fg=self.primary_color, 
            bg=self.bg_color
        )
        title_label.pack(anchor="w")
        
        desc_label = tk.Label(
            header_frame, 
            text="공공데이터포털(data.go.kr)의 전국 일반음식점 및 휴게음식점 최신 실시간 데이터를 다운로드합니다.", 
            font=("Malgun Gothic", 9), 
            fg=self.text_dim, 
            bg=self.bg_color
        )
        desc_label.pack(anchor="w", pady=(2, 0))
        
        # Options Frame (Target Selection)
        options_frame = tk.LabelFrame(
            self.root, 
            text=" 다운로드 대상 선택 ", 
            font=("Malgun Gothic", 10, "bold"), 
            fg=self.text_color, 
            bg=self.card_color, 
            bd=1, 
            relief="solid"
        )
        options_frame.pack(fill="x", padx=20, pady=5)
        
        inner_options = tk.Frame(options_frame, bg=self.card_color)
        inner_options.pack(fill="x", padx=15, pady=8)
        
        for name, target in self.download_targets.items():
            cb = tk.Checkbutton(
                inner_options,
                text=f"{name} 인허가 데이터 ({target['filename']})",
                variable=target["var"],
                font=("Malgun Gothic", 10),
                fg=self.text_color,
                bg=self.card_color,
                activebackground=self.card_color,
                activeforeground=self.primary_color,
                selectcolor=self.bg_color,
                bd=0,
                padx=5,
                pady=2
            )
            cb.pack(anchor="w")
            
        # Path Selection Frame
        path_frame = tk.LabelFrame(
            self.root, 
            text=" 저장 경로 설정 ", 
            font=("Malgun Gothic", 10, "bold"), 
            fg=self.text_color, 
            bg=self.card_color, 
            bd=1, 
            relief="solid"
        )
        path_frame.pack(fill="x", padx=20, pady=5)
        
        inner_path = tk.Frame(path_frame, bg=self.card_color)
        inner_path.pack(fill="x", padx=15, pady=8)
        
        self.path_entry = tk.Entry(
            inner_path, 
            textvariable=self.save_dir, 
            font=("Malgun Gothic", 10), 
            fg=self.text_color, 
            bg=self.bg_color, 
            bd=1, 
            relief="solid", 
            insertbackground=self.text_color
        )
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 10))
        
        browse_btn = tk.Button(
            inner_path, 
            text="경로 선택...", 
            font=("Malgun Gothic", 9, "bold"), 
            fg=self.bg_color, 
            bg=self.primary_color, 
            activebackground="#b4befe", 
            bd=0, 
            padx=10, 
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # Date Filter Frame
        filter_frame = tk.LabelFrame(
            self.root, 
            text=" 데이터 기간 필터링 (선택 사항) ", 
            font=("Malgun Gothic", 10, "bold"), 
            fg=self.text_color, 
            bg=self.card_color, 
            bd=1, 
            relief="solid"
        )
        filter_frame.pack(fill="x", padx=20, pady=5)
        
        inner_filter = tk.Frame(filter_frame, bg=self.card_color)
        inner_filter.pack(fill="x", padx=15, pady=8)
        
        self.use_filter_var = tk.BooleanVar(value=False)
        self.filter_cb = tk.Checkbutton(
            inner_filter,
            text="인허가일자 기준 필터링 적용",
            variable=self.use_filter_var,
            font=("Malgun Gothic", 9, "bold"),
            fg=self.text_color,
            bg=self.card_color,
            activebackground=self.card_color,
            activeforeground=self.primary_color,
            selectcolor=self.bg_color,
            bd=0,
            command=self.toggle_filter_inputs
        )
        self.filter_cb.pack(side="left", padx=(0, 15))
        
        # Date inputs
        self.start_label = tk.Label(inner_filter, text="시작일:", font=("Malgun Gothic", 9), fg=self.text_dim, bg=self.card_color)
        self.start_label.pack(side="left", padx=(5, 2))
        
        # Default dates (last 30 days)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        thirty_days_ago_str = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
        self.start_entry = tk.Entry(inner_filter, width=12, font=("Malgun Gothic", 9), fg=self.text_color, bg=self.bg_color, bd=1, relief="solid", insertbackground=self.text_color)
        self.start_entry.insert(0, thirty_days_ago_str)
        self.start_entry.pack(side="left", padx=2, ipady=1)
        
        self.end_label = tk.Label(inner_filter, text="종료일:", font=("Malgun Gothic", 9), fg=self.text_dim, bg=self.card_color)
        self.end_label.pack(side="left", padx=(10, 2))
        
        self.end_entry = tk.Entry(inner_filter, width=12, font=("Malgun Gothic", 9), fg=self.text_color, bg=self.bg_color, bd=1, relief="solid", insertbackground=self.text_color)
        self.end_entry.insert(0, today_str)
        self.end_entry.pack(side="left", padx=2, ipady=1)
        
        # Progress & Console Frame
        console_frame = tk.Frame(self.root, bg=self.bg_color)
        console_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # ScrolledText for logs
        self.log_text = ScrolledText(
            console_frame, 
            font=("Consolas", 9), 
            fg="#a6e3a1", 
            bg="#11111b", 
            bd=1, 
            relief="solid",
            height=8
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 10))
        self.log_text.insert(tk.END, "[System] LOCALDATA 다운로더 준비 완료.\n")
        self.log_text.configure(state="disabled")
        
        # Progressbar
        self.progress_bar = ttk.Progressbar(
            console_frame, 
            orient="horizontal", 
            mode="determinate", 
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Control Buttons
        btn_frame = tk.Frame(console_frame, bg=self.bg_color)
        btn_frame.pack(fill="x")
        
        self.action_btn = tk.Button(
            btn_frame, 
            text="다운로드 시작", 
            font=("Malgun Gothic", 11, "bold"), 
            fg=self.bg_color, 
            bg=self.secondary_color, 
            activebackground="#a6e3a1", 
            bd=0, 
            pady=6, 
            command=self.start_download_thread
        )
        self.action_btn.pack(fill="x")
        
    def toggle_filter_inputs(self):
        state = "normal" if self.use_filter_var.get() else "disabled"
        bg = self.bg_color if self.use_filter_var.get() else self.card_color
        self.start_entry.configure(state=state, bg=bg)
        self.end_entry.configure(state=state, bg=bg)
        
    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        
    def browse_directory(self):
        selected_dir = filedialog.askdirectory(initialdir=self.save_dir.get())
        if selected_dir:
            self.save_dir.set(selected_dir)
            self.log(f"[Info] 저장 경로 변경: {selected_dir}")
            
    def start_download_thread(self):
        if self.is_downloading:
            messagebox.showwarning("경고", "이미 다운로드가 진행 중입니다.")
            return
            
        targets_to_download = []
        for name, target in self.download_targets.items():
            if target["var"].get():
                targets_to_download.append((name, target["url"], target["filename"]))
                
        if not targets_to_download:
            messagebox.showwarning("선택 누락", "다운로드할 대상을 최소 하나 이상 선택하세요.")
            return
            
        # Parse and validate dates if filter is enabled
        start_date_str = ""
        end_date_str = ""
        if self.use_filter_var.get():
            start_date_str = self.start_entry.get().strip()
            end_date_str = self.end_entry.get().strip()
            try:
                datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
                datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("날짜 형식 오류", "시작일과 종료일은 YYYY-MM-DD 형식이어야 합니다.")
                return
            if start_date_str > end_date_str:
                messagebox.showerror("날짜 범위 오류", "시작일이 종료일보다 늦을 수 없습니다.")
                return
                
        save_path = self.save_dir.get()
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("오류", f"저장 경로를 생성할 수 없습니다:\n{str(e)}")
                return
                
        self.is_downloading = True
        self.action_btn.configure(text="다운로드 중...", bg="#585b70", state="disabled")
        
        # Run download in a daemon thread
        t = threading.Thread(
            target=self.run_downloads, 
            args=(targets_to_download, save_path, self.use_filter_var.get(), start_date_str, end_date_str), 
            daemon=True
        )
        t.start()
        
    def run_downloads(self, targets, save_path, is_filtering, start_date, end_date):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.data.go.kr/"
        }
        
        try:
            for idx, (name, url, filename) in enumerate(targets):
                dest_file = os.path.join(save_path, filename)
                self.log(f"\n[시작] '{name}' 다운로드 개시...")
                self.log(f"-> URL: {url}")
                self.log(f"-> 저장: {dest_file}")
                
                if is_filtering:
                    self.log(f"-> 필터링 적용: {start_date} ~ {end_date}")
                
                start_time = time.time()
                
                # Request with stream enabled
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = int(response.headers.get("content-length", 0))
                if total_size == 0:
                    self.log("[경고] 파일 크기를 알 수 없습니다. 진행률 표시 없이 다운로드합니다.")
                    
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunk size
                
                if is_filtering:
                    # Stream and filter line-by-line
                    self.log("[진행] 스트림 파싱 및 필터링 수행 중...")
                    
                    # Decoded generator for lines
                    lines_gen = (line.decode('cp949', errors='replace') for line in response.iter_lines())
                    reader = csv.reader(lines_gen)
                    
                    try:
                        header_row = next(reader)
                    except StopIteration:
                        self.log("[에러] 빈 파일이 수신되었습니다.")
                        continue
                        
                    # Find '인허가일자' index
                    try:
                        date_idx = header_row.index("인허가일자")
                    except ValueError:
                        date_idx = 2  # Fallback
                        self.log("[경고] '인허가일자' 열을 찾지 못해 기본 열(3번째)로 필터링합니다.")
                        
                    # Open target file for writing in CP949
                    with open(dest_file, "w", encoding="cp949", newline="") as out_f:
                        writer = csv.writer(out_f)
                        writer.writerow(header_row)
                        
                        row_count = 0
                        matched_count = 0
                        
                        # Process rows
                        for row in reader:
                            row_count += 1
                            if len(row) > date_idx:
                                row_date = row[date_idx].strip()
                                if start_date <= row_date <= end_date:
                                    writer.writerow(row)
                                    matched_count += 1
                                    
                            if row_count % 20000 == 0:
                                elapsed = time.time() - start_time
                                progress_msg = f"[필터링] {row_count:,}행 처리 중... (기간내 부합 데이터: {matched_count:,}건) | 경과시간: {elapsed:.1f}초"
                                self.root.after(0, self.log_progress_update, progress_msg)
                                
                                # Rough progress bar update (estimate general restaurant ~2.1m rows, rest cafes ~600k rows)
                                est_total = 2100000 if "일반" in name else 600000
                                pct = min((row_count / est_total) * 100, 99.0)
                                self.progress_bar["value"] = pct
                                
                        self.log(f"[성공] 완료! 총 {row_count:,}개 업소 분석 중 {matched_count:,}개 신규 인허가 매장 추출 성공.")
                        
                else:
                    # Full download write block by block
                    with open(dest_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    self.progress_bar["value"] = percent
                                    
                                    elapsed = time.time() - start_time
                                    speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                                    progress_msg = f"[다운로드] {downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB ({percent:.1f}%) | 속도: {speed:.2f}MB/s"
                                    self.root.after(0, self.log_progress_update, progress_msg)
                                    
                    self.log(f"[성공] '{name}' 다운로드 완료! (소요 시간: {time.time() - start_time:.1f}초)")
                
                self.progress_bar["value"] = 100
                
            self.log("\n[완료] 선택한 모든 데이터의 다운로드 및 필터링이 끝났습니다.")
            self.root.after(0, lambda: messagebox.showinfo("완료", "모든 파일 다운로드 및 필터링이 완료되었습니다!"))
            
        except Exception as e:
            self.log(f"\n[에러] 다운로드 실패: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("오류", f"다운로드 중 오류가 발생했습니다:\n{str(e)}"))
            
        finally:
            self.is_downloading = False
            self.root.after(0, self.reset_action_button)
            
    def log_progress_update(self, msg):
        self.log(msg)
        
    def reset_action_button(self):
        self.action_btn.configure(text="다운로드 시작", bg=self.secondary_color, state="normal")
        self.progress_bar["value"] = 0

def main():
    root = tk.Tk()
    app = LocalDataDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
