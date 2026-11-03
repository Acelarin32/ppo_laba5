# Marshmallow 4.0.1: десериализация и валидация

Автор: **Баженов Артемий 972403**. Стек: Python, backend.

Репозиторий проекта: https://github.com/Acelarin32/ppo_laba5

Исходники библиотеки: https://github.com/marshmallow-code/marshmallow/tree/4.0.1

Исследуемый механизм: сборка Schema, путь load, Field.deserialize, вложенные схемы, валидаторы и ErrorStore. На диаграммах ровно 17 реально используемых классов библиотеки. Пользовательские Money/ItemSchema/OrderSchema/Order находятся только в демо.

## Запуск

Нужен Python 3.9+. В Windows из корня этой папки:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m order_demo --case valid --trace
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

В Linux/macOS используйте python3 и .venv/bin/python. Сервер, Docker и БД не нужны.

Другие сценарии: меняйте `--case valid` на `--case field-error`, `--case total-error`, `--case unknown`. Для последнего добавьте `--exclude-unknown`, чтобы сравнить политику. Собственный JSON: `--file examples/order.json`. Демонстрационные ошибки печатаются как данные, а не ненулевой код завершения CLI.

## Что открывать

- `presentation/Marshmallow17-clean.pptx` — 15 слайдов с заметками.
- `diagrams/Marshmallow-DEMO17-native.drawio` — общий draw.io, пять страниц; диаграммы также лежат отдельными файлами.
- `docs/RESEARCH.md` — исследование архитектуры, решения, ограничения и альтернативы.
- `docs/DEMO17_CLASSES.md` — полные поля, сигнатуры и связи 17 классов.
- `docs/DEFENSE.md` — порядок демонстрации, дебаггер и практические упражнения.
- `docs/SOURCE_MAP.md` — ссылки на исходники и точки останова.
- `order_demo/schemas.py` — расширение Money, схемы и хуки.
