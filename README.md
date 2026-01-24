# Stock Cutter

A web application that solves the **NP-hard Cutting Stock Problem** using **linear programming**. It finds a cutting plan for linear materials that **minimizes waste** while promoting **balanced usage** of available stock materials.

## 🌐 Live Demo

Try the working version of the app here:  
👉 [https://stockcutter.onrender.com](https://stockcutter.onrender.com)

⚠️ **Note**: The app is hosted on **Render's free tier**, which comes with limitations:
- The service **sleeps after 15 minutes of inactivity**.
- The first request after sleep may take **45–60 seconds** to load (you’ll see Render’s loading screen).
- The URL uses the `onrender.com` domain due to free-tier hosting.
- Occasional delays or loading errors may occur due to resource constraints of the free plan.

## 📋 Project Overview

**Problem statement**: Cut available stock materials into required pieces such that:
- **Waste (leftover material) is minimized**,
- **Stock usage is distributed as evenly as possible** across available items.

**Technical approach**:  
The core algorithm leverages **PuLP**, a Python library for linear and integer linear programming. The frontend is built with **HTML + JavaScript**, and the backend is powered by the **Flask** web framework.

## ⭐ Key Features

- Minimizes cutting waste.
- Promotes balanced consumption of stock materials.
- Allows editing of stock lengths and quantities.
- Supports adding and removing stock items.
- Simple, intuitive UI with clear results.
- Real-time computation, no page reload needed.
- Applicable across industries: construction, manufacturing, etc.  
  Works with any linear material: pipes, metal bars, wood, profiles, etc.

## 🚀 Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/verdex4/stock-cutter.git

# Navigate into the project directory
cd stock-cutter

# (Optional) Create and activate a virtual environment
# Windows
python -m venv venv
venv\Scripts\activate
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app (visit http://127.0.0.1:5000 in your browser)
python app.py
```

### Using conda

```bash
# Clone the repository
git clone https://github.com/verdex4/stock-cutter.git

# Navigate into the project directory
cd stock-cutter

# Create the conda environment
conda env create -f environment.yml

# Activate the environment
conda activate stock-cutter

# Run the app (visit http://127.0.0.1:5000)
python app.py
```

## 📁 Project Structure

```
stock-cutter/
│
├── algorithm.py         # Core solver logic (Cutting Stock algorithm)
├── app.py               # Flask application (routing & API)
├── templates/           # HTML interface pages
└── static/              # Static assets (CSS, JS)
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

-------------------------------------------------------------------------------------------------

# Stock Cutter

Веб-приложение, решающее **NP-трудную задачу раскроя (Cutting Stock Problem)** с использованием **линейного программирования**. Находит план раскроя (разрезания) линейных материалов с **минимально возможными отходами** и способствует **равномерному использованию** имеющихся заготовок.

## 🌐 Демо

Попробуйте рабочую версию приложения здесь:  
👉 [https://stockcutter.onrender.com](https://stockcutter.onrender.com)

⚠️ **Важно**: приложение размещено на **бесплатном тарифе Render**, что накладывает ограничения:
- Сервис **отключается после 15 минут бездействия**.
- Первый запрос после отключения может занять **45–60 секунд** (вы увидите загрузочный экран Render).
- Адрес использует домен `onrender.com` из-за бесплатного хостинга.
- Возможны временные задержки или ошибки загрузки из-за ограничений бесплатного тарифа.

## 📋 Описание проекта

**Формулировка задачи**: нарезать имеющиеся заготовки на требуемые детали так, чтобы:
- **Отходы (остатки материала) были минимизированы**,
- **Использование заготовок было распределено максимально равномерно** между доступными единицами.

**Технический подход**:  
Основной алгоритм использует **PuLP** — библиотеку Python для решения задач линейного и целочисленного линейного программирования. Фронтенд реализован с помощью **HTML + JavaScript**, а бэкенд построен на веб-фреймворке **Flask**.

## ⭐ Ключевые особенности

- Минимизирует отходы при раскрое.
- Способствует сбалансированному расходу материалов.
- Позволяет редактировать длину и количество заготовок.
- Поддерживает добавление и удаление позиций материалов.
- Простой и интуитивный интерфейс с понятным отображением результатов.
- Вычисления выполняются в реальном времени — перезагрузка страницы не требуется.
- Применимо в различных отраслях: строительство, производство и др.  
  Подходит для любых линейных материалов: трубы, металлические пруты, дерево, профили и т.п.

## 🚀 Установка

### Через pip

```bash
# Клонируем репозиторий
git clone https://github.com/verdex4/stock-cutter.git

# Переходим в директорию проекта
cd stock-cutter

# (Опционально) Создаём и активируем виртуальное окружение
# Windows
python -m venv venv
venv\Scripts\activate
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем приложение (откройте http://127.0.0.1:5000 в браузере)
python app.py
```

### Через conda

```bash
# Клонируем репозиторий
git clone https://github.com/verdex4/stock-cutter.git

# Переходим в директорию проекта
cd stock-cutter

# Создаём окружение conda
conda env create -f environment.yml

# Активируем окружение
conda activate stock-cutter

# Запускаем приложение (откройте http://127.0.0.1:5000)
python app.py
```

## 📁 Структура проекта

```
stock-cutter/
│
├── algorithm.py         # Ядро решателя (алгоритм задачи раскроя)
├── app.py               # Приложение Flask (маршрутизация и API)
├── templates/           # HTML-страницы интерфейса
└── static/              # Статические файлы (CSS, JS)
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## 📄 Лицензия

Проект распространяется под лицензией **MIT License**. Подробнее см. в файле [LICENSE](LICENSE).

