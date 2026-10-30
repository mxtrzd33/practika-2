# Dependency Visualizer

CLI-инструмент для анализа зависимостей пакетов Alpine Linux APK.
Проект реализует пять этапов задания: YAML-конфигурацию, чтение APKINDEX,
построение графа, обратные зависимости и экспорт Graphviz DOT.

## Требования

- Python 3.10+
- PyYAML (`pip install -r requirements.txt`)
- Graphviz (`dot`) для создания PNG/SVG. Без Graphviz DOT-файл всё
  равно будет сформирован.

Инструмент не запускает `apk` и не использует пакетные менеджеры или
сторонние библиотеки для получения зависимостей. Индекс загружается
обычным HTTP-запросом и разбирается средствами стандартной библиотеки
Python. PyYAML используется только для пользовательской конфигурации.

## Быстрый запуск

```bash
python -m pip install -r requirements.txt
python -m src.main --config config.yaml
```

Windows: запустить `run.bat`. Linux/macOS: `chmod +x run.sh && ./run.sh`.

## Конфигурация

`config.yaml` содержит все пять обязательных параметров:

```yaml
package_name: "A"
repository_url: ""
test_repository: true
package_version: "1.0"
filter_substring: ""
test_repository_path: "test_data/repository.txt"
output_dir: "output"
```

Для реального Alpine-репозитория укажите URL каталога репозитория,
например `https://dl-cdn.alpinelinux.org/alpine/v3.22/main/x86_64`,
установите `test_repository: false` и задайте точную версию пакета.
Путь `test_repository_path` и `output_dir` — дополнительные настройки.

## Формат тестового репозитория

Файл содержит по одной записи на строку: `ПАКЕТ:ЗАВИСИМОСТЬ1,ЗАВИСИМОСТЬ2`.
Имена пакетов тестового режима — заглавные латинские буквы.

```text
A:B,C
B:D
C:D,E
D:
E:A
```

Этот пример специально содержит цикл `A -> C -> E -> A`.

## Команды

```bash
# Полный анализ, DOT и PNG/SVG (если установлен Graphviz)
python -m src.main --config config.yaml

# Только прямые зависимости
python -m src.main --config config.yaml --direct-only

# Обратные зависимости
python -m src.main --config config.yaml --reverse

# Сменить пакет без редактирования YAML
python -m src.main --config config.yaml --package B

# Вывести DOT в консоль, не вызывая Graphviz
python -m src.main --config config.yaml --dot-only
```

## Проверки

```bash
python -m unittest discover -s tests -v
```

## Результаты

Файлы создаются в `output/`: `dependencies.dot`, `dependencies.png`
(или `dependencies.svg`, если выбран SVG). Для сравнения с Alpine
допускается использовать штатные команды `apk info -R PACKAGE` и
`apk info -r PACKAGE` только как независимый эталон на системе с apk.
Сам инструмент эти команды не вызывает.

## Этапы и коммиты

История Git содержит пять Conventional Commits — по одному на этап.
