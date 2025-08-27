# Импорт необходимых библиотек
from langchain_gigachat.chat_models import GigaChat  # Для работы с GigaChat API
from fastapi import FastAPI, UploadFile, File        # Для создания веб-API
import uvicorn                                       # ASGI сервер для запуска FastAPI
import tempfile                                      # Для создания временных файлов
import os                                            # Для работы с файловой системой
import json                                          # Для работы с JSON
from datetime import datetime                        # Для работы с датой и временем

'''
Требуемые зависимости:
pip install langchain>=0.3.25
pip install langchain-gigachat>=0.3.10
pip install fastapi
pip install python-multipart
'''

# Создание экземпляра FastAPI приложения
app = FastAPI()

# Инициализация модели GigaChat с учетными данными
model = GigaChat(
    model="Gigachat-2-Max",                          # Используемая модель
    verify_ssl_certs=False,                          # Отключение проверки SSL сертификатов
    credentials='ZGMxZTMyYWEtMTgyZC00NzI0LWI1ZDktMDk3MTE0ODgxMGY4OjcxODZmZmM3LTA1MTQtNDJkNi1hMjNmLWI5OTUxZTg1OTk1MA=='  # API ключ
)

# Эндпоинт для загрузки и обработки изображений
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Обрабатывает загруженное изображение через GigaChat API
    и извлекает информацию о компании
    """
    try:
        # Создаем временный файл с правильным расширением
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()  # Читаем содержимое загруженного файла
            tmp_file.write(content)      # Записываем во временный файл
            tmp_file_path = tmp_file.name
        
        # Загружаем файл в GigaChat API
        with open(tmp_file_path, 'rb') as image_file:
            file_uploaded_id = model.upload_file(image_file).id_  # Получаем ID загруженного файла
        
        # Удаляем временный файл после загрузки
        os.unlink(tmp_file_path)
        
        # Формируем запрос к GigaChat для распознавания текста
        message = {
            "role": "user",
            "content": "Распознай текст с этого изображения Найди в нем название компании 'Наименование компании'\n, номер телефона 'Номер телефона',\n электронная почта 'Электронная почта',\n и почтовый адрес 'Почтовый адрес' и верни только dict.",
            "attachments": [file_uploaded_id]  # Прикрепляем загруженное изображение
        }
        
        # Отправляем запрос и получаем ответ от GigaChat
        response = model.invoke([message])
        
        # Парсим результат из строки в JSON объект
        try:
            # Пытаемся преобразовать строку словаря в JSON
            result_dict = eval(response.content.strip())
        except:
            # Если не удалось, сохраняем как строку
            result_dict = response.content
        
        # Подготавливаем новую запись для добавления
        new_entry = {
            "timestamp": datetime.now().isoformat(),  # Временная метка
            "filename": file.filename,                # Имя исходного файла
            "result": result_dict                     # Результат обработки как объект
        }
        
        # Читаем существующие данные из result.json или создаем пустой список
        results_file = "result.json"
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_results = []
        
        # Добавляем новую запись к существующим
        all_results.append(new_entry)
        
        # Сохраняем обновленный список в result.json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # Возвращаем результат и информацию о сохранении
        return {"result": response.content, "saved_to": results_file, "total_records": len(all_results)}
    
    except Exception as e:
        # Обработка ошибок
        return {"error": str(e)}
    

# Эндпоинт для получения всех записей из result.json
@app.get("/get-records/")
async def get_records():
    """
    Возвращает все записи из result.json
    """
    try:
        # Читаем данные из result.json
        with open("result.json", 'r', encoding='utf-8') as f:
            all_results = json.load(f)
        return all_results
    except FileNotFoundError:
        # Если файл не найден, возвращаем пустой список
        return []
    

# Получить все name из result.json
@app.get("/get-names/")
async def get_names():
    """
    Возвращает все имена компаний из result.json
    """
    try:
        # Читаем данные из result.json
        with open("result.json", 'r', encoding='utf-8') as f:
            all_results = json.load(f)

        # Извлекаем имена компаний из каждой записи
        names = [entry['result']['Наименование компании'] for entry in all_results]
        return names
    except FileNotFoundError:
        # Если файл не найден, возвращаем пустой список
        return []
    

# Запуск сервера при прямом выполнении файла
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  # Запуск на localhost:8000
