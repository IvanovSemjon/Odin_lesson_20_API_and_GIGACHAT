import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from langchain_gigachat.chat_models import GigaChat
import re

class CompanyInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Распознавание информации о компании")
        self.root.geometry("700x500")
        
        self.model = GigaChat(
            model="Gigachat-2-Max",
            verify_ssl_certs=False,
            credentials='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        )
        
        self.company_data = {}
        
        # Кнопки
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Выбрать файл", command=self.select_file, 
                 font=("Arial", 12), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Сохранить", command=self.save_data, 
                 font=("Arial", 12), bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Фрейм для данных компании
        data_frame = tk.LabelFrame(root, text="Информация о компании", font=("Arial", 12, "bold"))
        data_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Поля для отображения данных
        fields = [("Название компании:", "name"), ("Телефон:", "phone"), 
                 ("Email:", "email"), ("Адрес:", "address")]
        
        self.labels = {}
        for i, (label_text, key) in enumerate(fields):
            tk.Label(data_frame, text=label_text, font=("Arial", 11, "bold")).grid(
                row=i, column=0, sticky="w", padx=10, pady=8)
            
            self.labels[key] = tk.Label(data_frame, text="-", font=("Arial", 11), 
                                      wraplength=400, justify="left", bg="#f0f0f0", 
                                      relief="sunken", padx=5, pady=3)
            self.labels[key].grid(row=i, column=1, sticky="ew", padx=10, pady=5)
        
        data_frame.columnconfigure(1, weight=1)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            self.process_file(file_path)
    
    def process_file(self, file_path):
        try:
            # Показать индикатор загрузки
            for key in self.labels:
                self.labels[key].config(text="Обработка...")
            self.root.update()
            
            with open(file_path, 'rb') as image_file:
                file_uploaded_id = self.model.upload_file(image_file).id_
            
            message = {
                "role": "user",
                "content": "Распознай текст с этого изображения Найди в нем название компании 'name', номер телефона 'phone', электронная почта 'email', и почтовый адрес 'address' и выведи это все простым словарем.",
                "attachments": [file_uploaded_id]
            }
            
            response = self.model.invoke([message])
            self.parse_and_display(response.content)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            for key in self.labels:
                self.labels[key].config(text="-")
    
    def parse_and_display(self, content):
        # Простой парсинг ответа
        self.company_data = {"name": "-", "phone": "-", "email": "-", "address": "-"}
        
        # Поиск данных в ответе
        patterns = {
            "name": r"'name'\s*:\s*'([^']+)'",
            "phone": r"'phone'\s*:\s*'([^']+)'",
            "email": r"'email'\s*:\s*'([^']+)'",
            "address": r"'address'\s*:\s*'([^']+)'"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                self.company_data[key] = match.group(1)
        
        # Отображение данных
        for key, value in self.company_data.items():
            self.labels[key].config(text=value if value != "-" else "Не найдено")
    
    def save_data(self):
        if not any(v != "-" for v in self.company_data.values()):
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("ИНФОРМАЦИЯ О КОМПАНИИ\n")
                    f.write("=" * 30 + "\n\n")
                    f.write(f"Название компании: {self.company_data['name']}\n")
                    f.write(f"Телефон: {self.company_data['phone']}\n")
                    f.write(f"Email: {self.company_data['email']}\n")
                    f.write(f"Адрес: {self.company_data['address']}\n")
                
                messagebox.showinfo("Успех", "Данные сохранены успешно!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CompanyInfoApp(root)
    root.mainloop()