#!/usr/bin/env python3
"""
Скрипт для автоматической установки зависимостей Game Assistant
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Выполнение команды с выводом результата"""
    print(f"\n🔧 {description}...")
    print(f"Команда: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"✅ {description} выполнено успешно")
            if result.stdout:
                print("Вывод:", result.stdout)
        else:
            print(f"❌ {description} завершилось с ошибкой")
            if result.stderr:
                print("Ошибка:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        return False
    
    return True

def check_python_version():
    """Проверка версии Python"""
    print("🐍 Проверка версии Python...")
    
    version = sys.version_info
    print(f"Текущая версия: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Требуется Python 3.8 или выше!")
        print("Скачайте новую версию с https://python.org")
        return False
    
    print("✅ Версия Python подходит")
    return True

def upgrade_pip():
    """Обновление pip"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Обновление pip"
    )

def install_package(package, description=None):
    """Установка отдельного пакета"""
    if description is None:
        description = f"Установка {package}"
    
    return run_command(
        f"{sys.executable} -m pip install {package}",
        description
    )

def install_requirements():
    """Установка зависимостей из requirements.txt"""
    if os.path.exists('requirements.txt'):
        print("\n📦 Установка зависимостей из requirements.txt...")
        
        # Чтение файла requirements.txt
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.readlines()
        
        # Фильтрация и установка
        for line in requirements:
            line = line.strip()
            if line and not line.startswith('#'):
                # Убираем комментарии после #
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                if line:
                    package_name = line.split('==')[0] if '==' in line else line
                    install_package(line, f"Установка {package_name}")
    else:
        print("❌ Файл requirements.txt не найден!")
        return False
    
    return True

def install_system_dependencies():
    """Установка системных зависимостей"""
    system = platform.system().lower()
    
    if system == "windows":
        print("\n🪟 Windows: установка дополнительных зависимостей...")
        
        # Установка pywin32 для Windows
        install_package("pywin32==306", "Установка pywin32 для Windows")
        
    elif system == "linux":
        print("\n🐧 Linux: установка системных зависимостей...")
        
        # Установка системных пакетов для Linux
        if os.path.exists('/etc/debian_version'):
            # Debian/Ubuntu
            run_command(
                "sudo apt-get update && sudo apt-get install -y python3-dev python3-pip python3-venv",
                "Обновление системных пакетов (Debian/Ubuntu)"
            )
        elif os.path.exists('/etc/redhat-release'):
            # RedHat/CentOS
            run_command(
                "sudo yum install -y python3-devel python3-pip",
                "Установка системных пакетов (RedHat/CentOS)"
            )
    
    elif system == "darwin":
        print("\n🍎 macOS: установка дополнительных зависимостей...")
        
        # Установка через Homebrew если доступен
        if run_command("which brew", "Проверка Homebrew"):
            run_command(
                "brew install python3 opencv",
                "Установка зависимостей через Homebrew"
            )

def test_imports():
    """Тестирование импорта установленных пакетов"""
    print("\n🧪 Тестирование импорта пакетов...")
    
    packages_to_test = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('pyautogui', 'PyAutoGUI'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('matplotlib', 'Matplotlib'),
        ('sklearn', 'Scikit-learn'),
        ('tensorflow', 'TensorFlow'),
        ('psutil', 'psutil')
    ]
    
    failed_imports = []
    
    for package, name in packages_to_test:
        try:
            if package == 'cv2':
                import cv2
                print(f"✅ {name} импортирован успешно")
            elif package == 'numpy':
                import numpy
                print(f"✅ {name} импортирован успешно")
            elif package == 'PIL':
                from PIL import Image
                print(f"✅ {name} импортирован успешно")
            elif package == 'pyautogui':
                import pyautogui
                print(f"✅ {name} импортирован успешно")
            elif package == 'keyboard':
                import keyboard
                print(f"✅ {name} импортирован успешно")
            elif package == 'mouse':
                import mouse
                print(f"✅ {name} импортирован успешно")
            elif package == 'matplotlib':
                import matplotlib
                print(f"✅ {name} импортирован успешно")
            elif package == 'sklearn':
                import sklearn
                print(f"✅ {name} импортирован успешно")
            elif package == 'tensorflow':
                import tensorflow
                print(f"✅ {name} импортирован успешно")
            elif package == 'psutil':
                import psutil
                print(f"✅ {name} импортирован успешно")
                
        except ImportError as e:
            print(f"❌ {name} не может быть импортирован: {e}")
            failed_imports.append(name)
        except Exception as e:
            print(f"⚠️ {name} импортирован с предупреждениями: {e}")
    
    if failed_imports:
        print(f"\n❌ Следующие пакеты не могут быть импортированы: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ Все пакеты успешно импортированы!")
        return True

def create_virtual_environment():
    """Создание виртуального окружения"""
    print("\n🌍 Создание виртуального окружения...")
    
    venv_name = "game_assistant_env"
    
    if os.path.exists(venv_name):
        print(f"✅ Виртуальное окружение {venv_name} уже существует")
        return True
    
    try:
        # Создание виртуального окружения
        result = subprocess.run(
            f"{sys.executable} -m venv {venv_name}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Виртуальное окружение {venv_name} создано")
            
            # Активация виртуального окружения
            if platform.system().lower() == "windows":
                activate_script = os.path.join(venv_name, "Scripts", "activate.bat")
                print(f"Для активации выполните: {activate_script}")
            else:
                activate_script = os.path.join(venv_name, "bin", "activate")
                print(f"Для активации выполните: source {activate_script}")
            
            return True
        else:
            print(f"❌ Ошибка создания виртуального окружения: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка создания виртуального окружения: {e}")
        return False

def main():
    """Основная функция установки"""
    print("🎯 Game Assistant - Установка зависимостей")
    print("=" * 50)
    
    # Проверка версии Python
    if not check_python_version():
        sys.exit(1)
    
    # Создание виртуального окружения
    create_virtual_environment()
    
    # Обновление pip
    upgrade_pip()
    
    # Установка системных зависимостей
    install_system_dependencies()
    
    # Установка Python пакетов
    if not install_requirements():
        print("\n❌ Ошибка установки зависимостей!")
        sys.exit(1)
    
    # Тестирование импорта
    if not test_imports():
        print("\n❌ Некоторые пакеты не могут быть импортированы!")
        print("Попробуйте перезапустить терминал или перезагрузить компьютер")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Установка зависимостей завершена успешно!")
    print("\n📋 Следующие шаги:")
    print("1. Запустите программу: python main_modern.py")
    print("2. Или используйте классическую версию: python main.py")
    print("3. Для тестирования компонентов: python test_components.py")
    
    print("\n⚠️ Важные замечания:")
    print("- Убедитесь, что у вас есть права администратора")
    print("- Некоторые функции могут требовать дополнительной настройки")
    print("- Используйте программу ответственно")

if __name__ == "__main__":
    main() 