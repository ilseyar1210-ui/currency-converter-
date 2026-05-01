# Currency Converter

**Автор:** Хабибуллин Рамазан Инсафович
 
**GitHub репозиторий:** https://github.com/ilseyar1210-UI/currency-converter

## Описание

Currency Converter — это графическое приложение на Python (Tkinter) для конвертации валют по актуальному курсу с использованием внешнего API (exchangerate-api.com). Приложение сохраняет историю конвертаций в JSON и позволяет её просматривать и очищать.

## Как получить API-ключ

**API используется бесплатно без ключа!**  
Приложение обращается к `https://api.exchangerate-api.com/v4/latest/USD` — до 1500 запросов в месяц бесплатно.

Если хотите использовать свой API-ключ (например, от openexchangerates.org), замените `API_URL` в коде.

## Установка и запуск

1. Убедитесь, что установлен Python 3.7+
2. Установите библиотеку `requests`:
   ```bash
   pip install requests
