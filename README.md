# Marshmallow 4.0.1: десериализация и валидация

Автор: **Баженов Артемий 972403**. Стек: Python, backend.

Репозиторий проекта: https://github.com/Acelarin32/ppo_laba5

Исходники библиотеки: https://github.com/marshmallow-code/marshmallow/tree/4.0.1

Исследуемый механизм: сборка Schema, путь load, Field.deserialize, вложенные схемы, валидаторы и ErrorStore. На диаграммах 17 используемых классов библиотеки.

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

- `presentation/Marshmallow.pptx` — 14 слайдов с заметками.
- `diagrams/Marshmallow-DEMO17-styled.drawio` — общий draw.io, 6 страниц.
- `order_demo/schemas.py` — расширение Money, схемы и хуки.
