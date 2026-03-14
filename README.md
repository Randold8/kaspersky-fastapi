# FastAPI Report Export

Тестовое задание: реализовать `POST /public/report/export`, который принимает текстовый файл, собирает частотную статистику по словоформам и возвращает результат в формате `xlsx`.

---

## Стек

- Python 3.13
- FastAPI
- Uvicorn
- pymorphy3
- openpyxl
- SQLite

---

## Запуск проекта

### 1. Создать виртуальное окружение

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустить приложение

```bash
python -m app.main
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8080
```

Swagger UI:

```text
http://127.0.0.1:8080/docs
```