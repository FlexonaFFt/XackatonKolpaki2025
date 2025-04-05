import json
import time
from pathlib import Path
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class BaseNewsPlugin(ABC):
    
    @abstractmethod
    def __init__(self, config: dict):
        pass
    
    @abstractmethod
    def check_updates(self) -> list:
        pass
    
    @abstractmethod
    def get_processed_urls(self) -> set:
        pass
    
    @abstractmethod
    def save_state(self):
        pass

class NaukaRFPlugin(BaseNewsPlugin):
    
    def __init__(self, config: dict):
        self.config = {
            'base_url': "https://наука.рф",
            'check_interval': 1800,
            'processed_file': "processed_urls.json",
            'news_file': "science_news.json",
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            'headless_browser': True
        }
        self.config.update(config)
        
        self.processed_urls = self._load_processed_urls()
        self.driver = None
        self.last_check = None

    def _load_processed_urls(self) -> set:
        try:
            if Path(self.config['processed_file']).exists():
                with open(self.config['processed_file'], 'r', encoding='utf-8') as f:
                    return set(json.load(f))
        except Exception as e:
            print(f"Ошибка загрузки URL: {e}")
        return set()

    def _get_news_links(self) -> list:
        target_url = f"{self.config['base_url']}/news/"
        
        try:
            response = requests.get(target_url, headers={
                "User-Agent": self.config['user_agent']
            })
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_script = soup.find('u-news-page')
            if news_script:
                json_data = news_script.get(':initial-news-items')
                if json_data:
                    news_items = json.loads(json_data.replace('&quot;', '"'))
                    return [self.config['base_url'] + item['url'] for item in news_items]

            if not self.driver:
                options = Options()
                options.headless = self.config['headless_browser']
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.get(target_url)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            return [
                self.config['base_url'] + a['href'] 
                for a in soup.select('.u-news-list a[href]')
            ]

        except Exception as e:
            print(f"Ошибка получения ссылок: {e}")
            return []

    def _parse_article(self, url: str) -> dict:
        try:
            response = requests.get(url, headers={
                "User-Agent": self.config['user_agent']
            }, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            return {
                'title': soup.title.text.strip() if soup.title else "Без заголовка",
                'content': '\n'.join([p.text for p in soup.select('.u-news-detail-page__text-content p')]),
                'url': url,
                'source': 'nauka-rf',
                'timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        except Exception as e:
            print(f"Ошибка парсинга статьи: {e}")
            return None

        def check_updates(self) -> list:
            new_articles = []
        
            try:
                current_links = self._get_news_links()
                new_urls = set(current_links) - self.processed_urls
                
                for url in new_urls:
                    if article := self._parse_article(url):
                        new_articles.append(article)
                        self.processed_urls.add(url)
                
                self.last_check = time.time()
                self.save_state()
                
            except Exception as e:
                print(f"Ошибка при проверке обновлений: {e}")
        
            return new_articles

        def get_processed_urls(self) -> set:
            return self.processed_urls.copy()

        def save_state(self):
            try:
                with open(self.config['processed_file'], 'w', encoding='utf-8') as f:
                    json.dump(list(self.processed_urls), f, ensure_ascii=False)
                
            except Exception as e:
                print(f"Ошибка сохранения состояния: {e}")

        def __del__(self):
            """Деструктор для очистки ресурсов"""
            if self.driver:
                self.driver.quit()

    if __name__ == "__main__":
        config = {
            'processed_file': 'nauka_processed.json',
            'news_file': 'nauka_articles.json',
            'check_interval': 300  # 5 минут
        }
        
        plugin = NaukaRFPlugin(config)
        
        while True:
            new_articles = plugin.check_updates()
            if new_articles:
                print(f"Найдено {len(new_articles)} новых статей:")
                for article in new_articles:
                    print(f" - {article['title']}")
            
            time.sleep(config['check_interval'])