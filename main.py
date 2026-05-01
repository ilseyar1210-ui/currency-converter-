import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# ===== КОНФИГУРАЦИЯ =====
API_URL = "https://api.exchangerate-api.com/v4/latest/"
HISTORY_FILE = "history.json"

# ===== ОСНОВНОЕ ПРИЛОЖЕНИЕ =====
class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x550")
        self.root.resizable(False, False)

        self.history = self.load_history()
        self.currencies = self.fetch_currencies()

        self.create_widgets()
        self.update_history_display()

    # ===== ЗАГРУЗКА СПИСКА ВАЛЮТ =====
    def fetch_currencies(self):
        try:
            response = requests.get(API_URL + "USD", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return sorted(data["rates"].keys())
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить список валют")
                return ["USD", "EUR", "RUB", "KZT", "GBP"]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сети: {e}")
            return ["USD", "EUR", "RUB", "KZT", "GBP"]

    # ===== РАБОТА С JSON =====
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    # ===== ИНТЕРФЕЙС =====
    def create_widgets(self):
        # Рамка ввода
        input_frame = ttk.LabelFrame(self.root, text="Конвертация валют", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Из валюты
        ttk.Label(input_frame, text="Из валюты:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.from_currency = ttk.Combobox(input_frame, values=self.currencies, width=10)
        self.from_currency.set("USD")
        self.from_currency.grid(row=1, column=1, padx=5, pady=5)

        # В валюту
        ttk.Label(input_frame, text="В валюту:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.to_currency = ttk.Combobox(input_frame, values=self.currencies, width=10)
        self.to_currency.set("EUR")
        self.to_currency.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка конвертации
        self.convert_btn = ttk.Button(input_frame, text="🔄 Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Результат
        self.result_label = ttk.Label(input_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=4, column=0, columnspan=2, pady=5)

        # История
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.clear_btn = ttk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history)
        self.clear_btn.pack(side="left", padx=5)

        self.refresh_btn = ttk.Button(btn_frame, text="🔄 Обновить курсы", command=self.refresh_currencies)
        self.refresh_btn.pack(side="left", padx=5)

    # ===== КОНВЕРТАЦИЯ =====
    def get_exchange_rate(self, from_curr, to_curr):
        try:
            response = requests.get(API_URL + from_curr, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data["rates"].get(to_curr)
            else:
                return None
        except Exception:
            return None

    def convert(self):
        # Валидация суммы
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                messagebox.showwarning("Ошибка ввода", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Введите корректное число!")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if not from_curr or not to_curr:
            messagebox.showwarning("Ошибка", "Выберите валюты!")
            return

        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate is None:
            messagebox.showerror("Ошибка", "Не удалось получить курс. Проверьте интернет.")
            return

        result = amount * rate
        self.result_label.config(text=f"{amount} {from_curr} = {result:.2f} {to_curr} (курс: {rate:.4f})")

        # Сохраняем в историю
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "result": round(result, 2),
            "rate": round(rate, 4)
        }
        self.history.append(record)
        self.save_history()
        self.update_history_display()

    def update_history_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in reversed(self.history[-50:]):  # Показываем последние 50
            self.tree.insert("", "end", values=(
                record["timestamp"],
                record["amount"],
                record["from_currency"],
                record["to_currency"],
                f"{record['result']} {record['to_currency']}"
            ))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю конвертаций?"):
            self.history.clear()
            self.save_history()
            self.update_history_display()
            self.result_label.config(text="История очищена")

    def refresh_currencies(self):
        self.currencies = self.fetch_currencies()
        self.from_currency['values'] = self.currencies
        self.to_currency['values'] = self.currencies
        messagebox.showinfo("Обновлено", "Список валют обновлён")

# ===== ЗАПУСК =====
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
