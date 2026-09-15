# 🎲 Scrumbler

> **WCA Speedcubing Platform** — Веб-платформа для тренировок по спидкубингу (кубик Рубика 3x3x3) с таймером в стиле Stackmat, генератором официальных скрамблов WCA, расчетом статистики и поддержкой Docker.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy)](https://sqlalchemy.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

---

## ✨ Ключевые возможности

1. **Stackmat WCA Таймер:**
   - Честная механика зажима: зажатие `Space` $\to$ оранжевая индикация удержания $\to$ через 350мс загорается зеленый сигнал готовности `Ready` $\to$ отпускание для старта.
   - Высокоточный подсчет миллисекунд на базе браузерного `performance.now()`.
   - Остановка таймера нажатием любой клавиши.
   - Горячие клавиши под рукой: `2` (штраф +2), `D` (DNF), `Backspace` (удалить последнюю сборку).

2. **WCA Генератор скрамблов 3x3x3:**
   - Алгоритмическая генерация 21 хода с исключением конфликтующих движений (никаких $R\ R'$, а также взаимно параллельных повторов $R\ L\ R$ или $U\ D\ U$).

3. **Расчет официальной WCA статистики:**
   - **PB (Personal Best):** лучшее одиночное время.
   - **ao5, ao12, ao100:** расчет средних значений с отсечением 5% лучших и 5% худших результатов.
   - **Строгий учет DNF:** 1 DNF в выборке отбрасывается как худший, 2 DNF превращают весь расчет в `DNF`.
   - **Учет +2:** корректное прибавление 2000 мс к общему времени.

4. **Два режима работы:**
   - **Режим гостя:** мгновенный доступ без регистрации, чистый таймер для разминки (сборки не засоряют базу).
   - **Авторизованный режим:** регистрация/вход с надежным JWT и bcrypt-хэшированием, сохранение всей истории, расчет прогресса и графиков.

5. **Страница истории сборок (`/history`):**
   - Полный журнал с датой, примененным скрамблом, статусом (OK / +2 / DNF) и возможностью удаления.

---

## 🚀 Быстрый старт

### Вариант 1: Локально на SQLite

1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:cooN4i/scrumbler.git
   cd scrumbler
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Для Windows Git Bash
   # .\venv\Scripts\Activate.ps1  # Для PowerShell
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустите сервер разработки:
   ```bash
   uvicorn app.main:app --reload
   ```
   Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000) в браузере.

---

### Вариант 2: В Docker с PostgreSQL

Запуск одной командой:
```bash
docker compose up --build -d
```
Сервер будет доступен на [http://localhost:8000](http://localhost:8000), а данные PostgreSQL сохраняются в docker volume.

---

## 🗄️ Миграции базы данных (Alembic)

Управление схемой базы данных осуществляется через асинхронный Alembic:

- **Применить все миграции:**
  ```bash
  alembic upgrade head
  ```
- **Создать новую автоматическую миграцию:**
  ```bash
  alembic revision --autogenerate -m "описание_изменений"
  ```
- **Откатить последнюю миграцию:**
  ```bash
  alembic downgrade -1
  ```
- **Проверить текущее состояние:**
  ```bash
  alembic current
  ```

---

## 🧪 Запуск тестов

Проект покрыт юнит-тестами скрамблера, расчета средних и интеграционными асинхронными тестами API:
```bash
python -m pytest -v
```

---

## 🛠️ Стек технологий

- **Backend:** FastAPI (Async ASGI), Pydantic v2, Pydantic-Settings
- **Database:** SQLAlchemy 2.0 (Async), `aiosqlite` (локально) / `asyncpg` (PostgreSQL в Docker)
- **Migrations:** Alembic (Async)
- **Security:** JWT (python-jose), Passlib (bcrypt)
- **Frontend:** Vanilla JS, CSS Glassmorphism & Cyberpunk Neon, Jinja2 templates
