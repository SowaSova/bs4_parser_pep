# Модификация [парсера PEP](https://github.com/SowaSova/scrapy_parser_pep) с использованием bs4

Данный парсер поможет:
* узнать все о нескольких последних версиях Python
* узнать о наиболее важных изменениях между основными версиями Python
* скачать документацию последней версии
* узнать о статусах документов PEP (сколько в каком статусе)
  
## Используемые технологии

 - Python 3.7
 - requests-cache (расширенная библиотека requests, включая возможность кешировать HTTP-ответы)
 - tqdm (библиотека для визуализации прогресс-бара)
 - Beautiful Soup (библиотека для парсинга HTML и XML документов)
 
## Установка и запуск

1. Клонируйте репозиторий
```bash
git clone https://github.com/lmashik/bs4_parser_pep.git
```

2. Создайте и активируйте виртуальное окружение
```bash
python3.7 -m venv env
```

* Если у вас Linux/macOS

    ```bash
    source env/bin/activate
    ```

* Если у вас windows

    ```bash
    source env/scripts/activate
    ```

3. Обновите pip до последней версии
```bash
python3 -m pip install --upgrade pip
```

4. Установите зависимости из файла requirements.txt
```bash
pip install -r requirements.txt
```

5. Перейдите в директорию с парсером
```bash
cd src
```

6. Ознакомьтесь с информацией о парсере и доступных командах
```bash
python main.py -h
```

HTTP-ответы кешируются. 
Для очистки кеша при выполнении следующей команды добавьте "-c", например,
```bash
python main.py latest-versions -c
```

Работа парсера логируется. Логи сохраняются в папку logs.

## latest_versions

Чтобы узнать подробности о нескольких последних версиях Python, 
запустите парсер с помощью команды

```bash
python main.py latest-versions
```

С помощью этой команды информация будет выведена в консоль.
Преобразите ее, добавив "-o pretty"
```bash
python main.py latest-versions -o pretty
```

Для сохранения в файл, добавьте "-o file"
```bash
python main.py latest-versions -o file
```

Файл будет сохранен в папку results.

## whats_new

Чтобы узнать об изменениях между основными версиями, 
запустите парсер с помощью команды

```bash
python main.py whats-new
```

С помощью этой команды информация будет выведена в консоль.
Преобразите ее, добавив "-o pretty"
```bash
python main.py whats-new -o pretty
```

Для сохранения в файл, добавьте "-o file"
```bash
python main.py whats-new -o file
```

Файл будет сохранен в папку results.

## download

Чтобы скачать документацию, запустите парсер с помощью команды

```bash
python main.py download
```

Документация будет сохранена в папку downloads.

## pep

Чтобы консолидировать информацию о статусах документов PEP, 
запустите парсер с помощью команды

```bash
python main.py pep
```

С помощью этой команды информация будет выведена в консоль.
Преобразите ее, добавив "-o pretty"
```bash
python main.py pep -o pretty
```

Для сохранения в файл, добавьте "-o file"
```bash
python main.py pep -o file
```

Файл будет сохранен в папку results.
