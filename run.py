#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Assistant Pro
Простой запуск программы
"""

import sys
import os

def main():
    print("🎯 Game Assistant Pro")
    print("=" * 40)
    print()
    
    try:
        # Проверяем, что основной файл существует
        if not os.path.exists('main_modern.py'):
            print("❌ Ошибка: Файл main_modern.py не найден!")
            return
        
        print("✅ Запуск программы...")
        print()
        
        # Импортируем и запускаем основную программу
        from main_modern import ModernGameAssistant
        
        app = ModernGameAssistant()
        app.run()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Установите зависимости: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        print("💡 Проверьте, что Python 3.7+ установлен и доступен в PATH")

if __name__ == "__main__":
    main() 