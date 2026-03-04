# Flask Authentication & RBAC System

## Описание
Проект представляет собой REST API на базе Flask с реализованной системой аутентификации и авторизации (RBAC).

## Реализованный функционал:
- ✅ Регистрация и вход пользователей (JWT токены).
- ✅ Защита маршрутов через декораторы (@require_auth).
- ✅ Система ролей (@require_role) для проверки принадлежности к группе.
- ✅ Система прав доступа (@require_permission) для детального контроля действий.
- ✅ Архитектура: Factory Pattern + Blueprints.
- ✅ База данных: SQLAlchemy (SQLite).

## Установка и запуск:
1. Создайте виртуальное окружение: `python -m venv .venv`
2. Активируйте его: `source .venv/Scripts/activate` (Windows: `.venv\Scripts\activate`)
3. Установите зависимости: `pip install -r requirements.txt`
4. Запустите приложение: `python main.py`

## Структура БД
- Users (пользователи)
- Roles (роли)
- Permissions (права доступа)
- Связи: Many-to-Many между таблицами.
