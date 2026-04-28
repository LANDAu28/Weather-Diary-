import customtkinter as ctk # type: ignore
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weather Diary")
        self.geometry("800x600")
        self.db_file = "diary.json"
        self.data = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- Левая панель: Ввод данных ---
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Новая запись", font=("Arial", 20, "bold")).pack(pady=10)

        self.entry_date = ctk.CTkEntry(self.sidebar, placeholder_text="Дата (ДД.ММ.ГГГГ)")
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.entry_date.pack(pady=5, padx=10, fill="x")

        self.entry_temp = ctk.CTkEntry(self.sidebar, placeholder_text="Температура (°C)")
        self.entry_temp.pack(pady=5, padx=10, fill="x")

        self.entry_desc = ctk.CTkEntry(self.sidebar, placeholder_text="Описание погоды")
        self.entry_desc.pack(pady=5, padx=10, fill="x")

        self.precip_var = ctk.BooleanVar()
        self.check_precip = ctk.CTkCheckBox(self.sidebar, text="Осадки", variable=self.precip_var)
        self.check_precip.pack(pady=10)

        self.add_btn = ctk.CTkButton(self.sidebar, text="Добавить запись", command=self.add_record)
        self.add_btn.pack(pady=10, padx=10, fill="x")

        # --- Верхняя панель: Фильтры ---
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(side="top", fill="x", padx=10, pady=10)

        self.filter_date = ctk.CTkEntry(self.filter_frame, placeholder_text="Фильтр по дате", width=150)
        self.filter_date.grid(row=0, column=0, padx=5)

        self.filter_temp = ctk.CTkEntry(self.filter_frame, placeholder_text="Мин. темп-ра", width=120)
        self.filter_temp.grid(row=0, column=1, padx=5)

        ctk.CTkButton(self.filter_frame, text="Фильтр", width=80, command=self.apply_filter).grid(row=0, column=2, padx=5)
        ctk.CTkButton(self.filter_frame, text="Сброс", width=80, fg_color="gray", command=self.refresh_table).grid(row=0, column=3, padx=5)

        # --- Центр: Таблица ---
        self.create_table()

    def create_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        
        cols = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Темп. (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

    def validate(self, d, t, desc):
        try:
            datetime.strptime(d, "%d.%m.%Y")
            float(t)
            if not desc.strip(): raise ValueError
            return True
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте данные!\nФормат даты: ДД.ММ.ГГГГ\nТемпература: число\nОписание: не пустое")
            return False

    def add_record(self):
        d, t, desc = self.entry_date.get(), self.entry_temp.get(), self.entry_desc.get()
        prec = "Есть" if self.precip_var.get() else "Нет"

        if self.validate(d, t, desc):
            record = {"date": d, "temp": float(t), "desc": desc, "precip": prec}
            self.data.append(record)
            self.save_data()
            self.refresh_table()
            self.entry_temp.delete(0, 'end')
            self.entry_desc.delete(0, 'end')

    def apply_filter(self):
        f_date = self.filter_date.get()
        f_temp = self.filter_temp.get()

        filtered = self.data
        if f_date:
            filtered = [r for r in filtered if f_date in r['date']]
        if f_temp:
            try:
                filtered = [r for r in filtered if r['temp'] >= float(f_temp)]
            except: pass
        
        self.refresh_table(filtered)

    def refresh_table(self, dataset=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        display_data = dataset if dataset is not None else self.data
        for r in display_data:
            self.tree.insert("", "end", values=(r['date'], r['temp'], r['desc'], r['precip']))

    def save_data(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.refresh_table()

if __name__ == "__main__":
    app = WeatherDiary()
    app.mainloop()
