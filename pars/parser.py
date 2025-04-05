import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import sys
import os

# Добавляем путь к корневой директории проекта, чтобы импортировать модули приложения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db, Post, create_tables

BASE_URL = "https://наука.рф"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
CHECK_INTERVAL = 600  # 30 минут в секундах
PROCESSED_FILE = "processed_urls.json"
SCIENCE_CATEGORY = 1  # Категория для научных новостей

def load_processed_urls():
    """Загружает список обработанных URL"""
    try:
        if Path(PROCESSED_FILE).exists():
            with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
    except Exception as e:
        print(f"⚠️ Ошибка загрузки {PROCESSED_FILE}: {e}")
    return set()

def save_processed_urls(urls):
    """Сохраняет новые URL в файл"""
    try:
        with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(urls), f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения {PROCESSED_FILE}: {e}")

def get_news_links():
    """Получает актуальный список ссылок с главной страницы"""
    target_url = f"{BASE_URL}/news/"
    links = []

    try:
        # Первый способ: попытка через прямой запрос
        response = requests.get(target_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Парсинг из JSON данных
        news_script = soup.find('u-news-page')
        if news_script:
            json_data = news_script.get(':initial-news-items')
            if json_data:
                news_items = json.loads(json_data.replace('&quot;', '"'))
                links = [BASE_URL + item['url'] for item in news_items]
                return links

        # Второй способ: через Selenium
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(target_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        news_section = soup.find('section', class_='u-news-list')
        if news_section:
            links = [BASE_URL + a['href'] for a in news_section.find_all('a', href=True)]

    except Exception as e:
        print(f"⚠️ Ошибка получения ссылок: {e}")

    return links

def parse_article(url):
    """Парсит содержимое статьи"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.text.strip() if soup.title else "Без заголовка"
        main_content = soup.find('div', class_='u-news-detail-page__text-content')
        
        if not main_content:
            return None

        content = main_content.get_text('\n', strip=True)

        return {
            'title': title,
            'content': content,
            'url': url,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(f"⚠️ Ошибка парсинга статьи {url}: {e}")
        return None

def save_to_database(article):
    """Сохраняет статью в базу данных"""
    try:
        db = next(get_db())
        
        # Проверяем, нет ли уже статьи с таким заголовком
        existing_post = db.query(Post).filter(Post.title == article['title']).first()
        if existing_post:
            print(f"Статья с заголовком '{article['title']}' уже существует в базе данных")
            return False
        
        # Создаем новую запись в базе данных
        new_post = Post(
            title=article['title'],
            content=article['content'],
            category=SCIENCE_CATEGORY,  # Категория "Наука"
            type="news",  # Тип "news"
            author_username=None  # Автор не указан для парсинговых новостей
        )
        
        db.add(new_post)
        db.commit()
        print(f"Статья '{article['title']}' успешно добавлена в базу данных")
        return True
        
    except Exception as e:
        print(f"⚠️ Ошибка сохранения статьи в базу данных: {e}")
        if 'db' in locals():
            db.rollback()
        return False

def update_news():
    """Основная функция обновления новостей"""
    print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} Начало проверки...")
    
    # Загрузка существующих данных
    processed_urls = load_processed_urls()

    # Получение новых ссылок
    current_links = get_news_links()
    if not current_links:
        print("Нет ссылок для обработки")
        return

    # Поиск новых URL
    new_urls = set(current_links) - processed_urls
    if not new_urls:
        print("Новых статей не найдено")
        return

    print(f"Найдено {len(new_urls)} новых статей!")
    
    # Парсинг новых статей
    new_articles_count = 0
    for url in new_urls:
        article = parse_article(url)
        if article:
            if save_to_database(article):
                new_articles_count += 1
                print(f"Добавлена статья: {article['title']}")
            processed_urls.add(url)

    # Обновление обработанных URL
    if new_articles_count > 0:
        save_processed_urls(processed_urls)
        print(f"Успешно добавлено {new_articles_count} новых статей")

def main():
    """Основной цикл выполнения"""
    print("Запуск мониторинга новостей...")
    print(f"Проверка каждые {CHECK_INTERVAL//60} минут")
    
    try:
        # Убедимся, что таблицы созданы
        create_tables()
        
        while True:
            update_news()
            print(f"Следующая проверка в {time.strftime('%H:%M:%S', time.localtime(time.time() + CHECK_INTERVAL))}\n")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен пользователем")

if __name__ == "__main__":
    # Инициализация файлов при первом запуске
    if not Path(PROCESSED_FILE).exists():
        save_processed_urls(set())
    
    main()