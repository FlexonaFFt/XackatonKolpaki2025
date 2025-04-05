import subprocess
import threading
import os
import sys
from pathlib import Path

def start_parser_service():
    parser_path = Path(__file__).parent.parent / "pars" / "parser.py"
    
    def run_parser():
        try:
            subprocess.run([sys.executable, str(parser_path)], 
                          check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при запуске парсера: {e}")
        except KeyboardInterrupt:
            print("Парсер остановлен")
    
    parser_thread = threading.Thread(target=run_parser, daemon=True)
    parser_thread.start()
    print("Сервис парсера запущен в фоновом режиме")
    
    return parser_thread