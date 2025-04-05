import subprocess
import threading
import os
import sys
from pathlib import Path

def start_parser_service():
    """Запускает парсер как отдельный процесс"""
    parser_path = Path(__file__).parent.parent / "pars" / "parser.py"
    
    def run_parser():
        try:
            # Запускаем парсер в отдельном процессе
            subprocess.run([sys.executable, str(parser_path)], 
                          check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при запуске парсера: {e}")
        except KeyboardInterrupt:
            print("Парсер остановлен")
    
    # Запускаем парсер в отдельном потоке, чтобы не блокировать основное приложение
    parser_thread = threading.Thread(target=run_parser, daemon=True)
    parser_thread.start()
    print("Сервис парсера запущен в фоновом режиме")
    
    return parser_thread