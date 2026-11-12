import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import cv2
import numpy as np
import pyautogui
import keyboard
import mouse
import threading
import time
import json
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys
import platform

# Проверка и установка зависимостей
def check_dependencies():
    """Проверка и установка необходимых зависимостей"""
    missing_packages = []
    
    required_packages = [
        'cv2', 'numpy', 'PIL', 'pyautogui', 'keyboard', 
        'mouse', 'matplotlib', 'sklearn', 'tensorflow'
    ]
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'numpy':
                import numpy
            elif package == 'PIL':
                from PIL import Image
            elif package == 'pyautogui':
                import pyautogui
            elif package == 'keyboard':
                import keyboard
            elif package == 'mouse':
                import mouse
            elif package == 'matplotlib':
                import matplotlib
            elif package == 'sklearn':
                import sklearn
            elif package == 'tensorflow':
                import tensorflow
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"Отсутствуют необходимые пакеты: {', '.join(missing_packages)}\n\n"
        error_msg += "Установите их командой:\npip install -r requirements.txt"
        messagebox.showerror("Ошибка зависимостей", error_msg)
        return False
    
    return True

class ModernGameAssistant:
    def __init__(self):
        # Проверка зависимостей
        if not check_dependencies():
            sys.exit(1)
        
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Настройки по умолчанию
        self.settings = {
            'screen_width': 1920,
            'screen_height': 1080,
            'trigger_key': 'shift',
            'click_key': 'left',  # left, right, middle для мыши
            'detection_radius': 1,  # Фиксированный радиус = 1 пиксель
            'color_tolerance': 15,
            'click_duration': 0.1,
            'aim_speed': 100.0,
            'aim_accuracy_radius': 10,
            'aim_key': 'alt',
            'aim_target': 'Enemy_Head',
            'output_mode': 'virtual',  # virtual | hardware
            'hardware_port': '',
            'hardware_baud': 115200,
            'target_body_part': 'head',
            'team_to_detect': 'both',
            'model_path': 'models/',
            'theme': 'dark'
        }
        
        # Состояние программы
        self.is_running = False
        self.trigger_bot_running = False
        self.aim_active = False
        self.detection_active = False
        
        # Модель машинного зрения
        self.model = None
        self.model_trained = False
        # Аппаратная мышь (серийный порт)
        self.hardware_serial = None
        
        # Создание интерфейса
        self.create_modern_interface()
        self.load_settings()
        
        # Применение темы
        self.apply_theme()
        
        # Инициализация мониторинга
        if hasattr(self, 'monitor_canvas'):
            self.update_monitor_screen()
        
        # Запускаем предпросмотр триггер-бота после полной инициализации
        self.root.after(2000, self.start_trigger_preview_update)
    
    def setup_main_window(self):
        """Настройка главного окна"""
        self.root.title("🎯 Game Assistant Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Иконка (если есть)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Центрирование окна
        self.center_window()
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_modern_interface(self):
        """Создание современного интерфейса"""
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Заголовок
        self.create_header(main_container)
        
        # Создание вкладок
        self.create_notebook(main_container)
        
        # Статус бар (создаем после всех вкладок)
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Создание заголовка"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Логотип и название
        title_label = ttk.Label(
            header_frame, 
            text="🎯 Game Assistant Pro", 
            font=('Segoe UI', 24, 'bold')
        )
        title_label.pack(side='left')
        
        # Информация о системе
        system_info = f"Python {platform.python_version()} | {platform.system()} {platform.release()}"
        system_label = ttk.Label(
            header_frame, 
            text=system_info, 
            font=('Segoe UI', 10)
        )
        system_label.pack(side='right')
        
        # Разделитель
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill='x', pady=10)
    
    def create_notebook(self, parent):
        """Создание вкладок"""
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='#2b2b2b')
        style.configure('Custom.TNotebook.Tab', padding=[20, 10])
        
        self.notebook = ttk.Notebook(parent, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Вкладка дашборда
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Дашборд")
        self.create_dashboard_tab(dashboard_frame)
        
        # Вкладка настроек
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Настройки")
        self.create_settings_tab(settings_frame)
        
        # Вкладка триггер-бота
        trigger_frame = ttk.Frame(self.notebook)
        self.notebook.add(trigger_frame, text="🎯 Триггер-бот")
        self.create_trigger_tab(trigger_frame)
        
        # Вкладка машинного зрения
        vision_frame = ttk.Frame(self.notebook)
        self.notebook.add(vision_frame, text="👁️ Машинное зрение")
        self.create_vision_tab(vision_frame)
        
        # Вкладка авто-наводки
        aim_frame = ttk.Frame(self.notebook)
        self.notebook.add(aim_frame, text="🎯 Авто-наводка")
        self.create_aim_tab(aim_frame)
        
        # Вкладка мониторинга
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="📺 Мониторинг")
        self.create_monitor_tab(monitor_frame)
        
        # Вкладка логов
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 Логи")
        self.create_logs_tab(logs_frame)
    
    def create_dashboard_tab(self, parent):
        """Создание вкладки дашборда"""
        # Основная информация
        info_frame = ttk.LabelFrame(parent, text="📊 Общая информация", padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        # Статистика
        stats_frame = ttk.Frame(info_frame)
        stats_frame.pack(fill='x')
        
        # Колонки статистики
        col1 = ttk.Frame(stats_frame)
        col1.pack(side='left', expand=True, padx=(0, 20))
        
        col2 = ttk.Frame(stats_frame)
        col2.pack(side='left', expand=True, padx=(0, 20))
        
        col3 = ttk.Frame(stats_frame)
        col3.pack(side='left', expand=True)
        
        # Колонка 1
        ttk.Label(col1, text="🖥️ Система", font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        self.system_info_label = ttk.Label(col1, text="Загрузка...")
        self.system_info_label.pack(anchor='w', pady=5)
        
        # Колонка 2
        ttk.Label(col2, text="🎯 Статистика", font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        self.stats_info_label = ttk.Label(col2, text="Загрузка...")
        self.stats_info_label.pack(anchor='w', pady=5)
        
        # Колонка 3
        ttk.Label(col3, text="⚡ Производительность", font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        self.perf_info_label = ttk.Label(col3, text="Загрузка...")
        self.perf_info_label.pack(anchor='w', pady=5)
        
        # Быстрые действия
        actions_frame = ttk.LabelFrame(parent, text="🚀 Быстрые действия", padding=20)
        actions_frame.pack(fill='x', padx=20, pady=20)
        
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.pack(fill='x')
        
        # Кнопки быстрых действий
        ttk.Button(
            buttons_frame, 
            text="🎯 Запустить всё", 
            command=self.start_all_features,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="⏹️ Остановить всё", 
            command=self.stop_all_features,
            style='Danger.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="🔄 Обновить статистику", 
            command=self.update_dashboard_stats
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="💾 Сохранить настройки", 
            command=self.save_settings
        ).pack(side='left')
        
        # Обновление статистики
        self.update_dashboard_stats()
    
    def create_settings_tab(self, parent):
        """Создание вкладки настроек"""
        # Основные настройки
        main_settings = ttk.LabelFrame(parent, text="🔧 Основные настройки", padding=20)
        main_settings.pack(fill='x', padx=20, pady=20)
        
        # Сетка настроек
        settings_grid = ttk.Frame(main_settings)
        settings_grid.pack(fill='x')
        
        # Разрешение экрана
        ttk.Label(settings_grid, text="🖥️ Разрешение экрана:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        resolution_frame = ttk.Frame(settings_grid)
        resolution_frame.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        ttk.Label(resolution_frame, text="Ширина:").pack(side='left')
        self.width_entry = ttk.Entry(resolution_frame, width=10)
        self.width_entry.pack(side='left', padx=(5, 10))
        
        ttk.Label(resolution_frame, text="Высота:").pack(side='left')
        self.height_entry = ttk.Entry(resolution_frame, width=10)
        self.height_entry.pack(side='left', padx=(5, 0))
        
        # Клавиша триггера
        ttk.Label(settings_grid, text="⌨️ Клавиша триггера:", font=('Segoe UI', 11, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.trigger_key_entry = ttk.Entry(settings_grid, width=15)
        self.trigger_key_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        # Радиус обнаружения
        ttk.Label(settings_grid, text="📏 Радиус обнаружения:", font=('Segoe UI', 11, 'bold')).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.radius_scale = ttk.Scale(settings_grid, from_=10, to=200, orient='horizontal', length=200)
        self.radius_scale.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        # Толерантность цвета
        ttk.Label(settings_grid, text="🎨 Толерантность цвета:", font=('Segoe UI', 11, 'bold')).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.tolerance_scale = ttk.Scale(settings_grid, from_=10, to=100, orient='horizontal', length=200)
        self.tolerance_scale.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        
        # Длительность клика
        ttk.Label(settings_grid, text="⏱️ Длительность клика:", font=('Segoe UI', 11, 'bold')).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.duration_entry = ttk.Entry(settings_grid, width=15)
        self.duration_entry.grid(row=4, column=1, padx=10, pady=10, sticky='w')
        
        # Скорость наводки
        ttk.Label(settings_grid, text="🚀 Скорость наводки:", font=('Segoe UI', 11, 'bold')).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.aim_speed_entry = ttk.Entry(settings_grid, width=15)
        self.aim_speed_entry.grid(row=5, column=1, padx=10, pady=10, sticky='w')
        
        # Цель для стрельбы
        ttk.Label(settings_grid, text="🎯 Цель для стрельбы:", font=('Segoe UI', 11, 'bold')).grid(row=6, column=0, padx=10, pady=10, sticky='w')
        self.body_part_var = tk.StringVar(value='head')
        body_part_combo = ttk.Combobox(settings_grid, textvariable=self.body_part_var, values=['head', 'body'], width=15, state='readonly')
        body_part_combo.grid(row=6, column=1, padx=10, pady=10, sticky='w')
        
        # Команда для обнаружения
        ttk.Label(settings_grid, text="👥 Команда для обнаружения:", font=('Segoe UI', 11, 'bold')).grid(row=7, column=0, padx=10, pady=10, sticky='w')
        self.team_var = tk.StringVar(value='both')
        team_combo = ttk.Combobox(settings_grid, textvariable=self.team_var, values=['ct', 't', 'both'], width=15, state='readonly')
        team_combo.grid(row=7, column=1, padx=10, pady=10, sticky='w')
        
        # Тема интерфейса
        ttk.Label(settings_grid, text="🎨 Тема интерфейса:", font=('Segoe UI', 11, 'bold')).grid(row=8, column=0, padx=10, pady=10, sticky='w')
        self.theme_var = tk.StringVar(value='dark')
        theme_combo = ttk.Combobox(settings_grid, textvariable=self.theme_var, values=['dark', 'light'], width=15, state='readonly')
        theme_combo.grid(row=8, column=1, padx=10, pady=10, sticky='w')
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        
        # Кнопки
        buttons_frame = ttk.Frame(main_settings)
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            buttons_frame, 
            text="💾 Сохранить настройки", 
            command=self.save_settings,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="🔄 Сбросить к умолчаниям", 
            command=self.reset_settings
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="📁 Импорт настроек", 
            command=self.import_settings
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="📤 Экспорт настроек", 
            command=self.export_settings
        ).pack(side='left')
        
        # Заполнение значений по умолчанию
        self.populate_settings_fields()
    
    def create_trigger_tab(self, parent):
        """Создание вкладки триггер-бота"""
        # Настройки триггер-бота
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Настройки триггер-бота", padding=20)
        settings_frame.pack(fill='x', padx=20, pady=20)
        
        # Сетка настроек
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill='x')
        
        # Клавиша триггера
        ttk.Label(settings_grid, text="⌨️ Клавиша триггера:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        # Фрейм для выбора клавиши
        key_frame = ttk.Frame(settings_grid)
        key_frame.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        self.trigger_key_var = tk.StringVar(value=self.settings.get('trigger_key', 'shift'))
        self.trigger_key_display = ttk.Label(key_frame, text=self.trigger_key_var.get(), width=15, relief='sunken', padding=5)
        self.trigger_key_display.pack(side='left', padx=(0, 10))
        
        ttk.Button(
            key_frame, 
            text="Выбрать клавишу", 
            command=self.select_trigger_key
        ).pack(side='left')
        
        # Клавиша для клика
        ttk.Label(settings_grid, text="🖱️ Клавиша для клика:", font=('Segoe UI', 11, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        # Фрейм для выбора клавиши клика
        click_key_frame = ttk.Frame(settings_grid)
        click_key_frame.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        self.click_key_var = tk.StringVar(value=self.settings.get('click_key', 'left'))
        self.click_key_display = ttk.Label(click_key_frame, text=self.click_key_var.get(), width=15, relief='sunken', padding=5)
        self.click_key_display.pack(side='left', padx=(0, 10))
        
        ttk.Button(
            click_key_frame, 
            text="Выбрать клавишу", 
            command=self.select_click_key
        ).pack(side='left')
        
        # Радиус обнаружения (фиксированный = 1 пиксель)
        ttk.Label(settings_grid, text="📏 Область захвата:", font=('Segoe UI', 11, 'bold')).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        radius_info_frame = ttk.Frame(settings_grid)
        radius_info_frame.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        radius_info_label = ttk.Label(radius_info_frame, text="3x3 пикселя (фиксированно)", font=('Segoe UI', 10), foreground='gray')
        radius_info_label.pack(side='left')
        
        # Погрешность цвета (в процентах)
        ttk.Label(settings_grid, text="🎨 Погрешность цвета (%):", font=('Segoe UI', 11, 'bold')).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
        tolerance_frame = ttk.Frame(settings_grid)
        tolerance_frame.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        
        self.trigger_tolerance_scale = ttk.Scale(tolerance_frame, from_=1, to=100, orient='horizontal', length=200, command=self.update_tolerance_label)
        self.trigger_tolerance_scale.pack(side='left')
        self.trigger_tolerance_scale.set(self.settings.get('color_tolerance', 15))
        
        self.tolerance_value_label = ttk.Label(tolerance_frame, text=f"{self.settings.get('color_tolerance', 15)}%", width=8)
        self.tolerance_value_label.pack(side='left', padx=(10, 0))
        
        # Длительность клика
        ttk.Label(settings_grid, text="⏱️ Длительность клика:", font=('Segoe UI', 11, 'bold')).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.trigger_duration_entry = ttk.Entry(settings_grid, width=15)
        self.trigger_duration_entry.grid(row=4, column=1, padx=10, pady=10, sticky='w')
        self.trigger_duration_entry.insert(0, str(self.settings.get('click_duration', 0.1)))
        
        # Кнопки сохранения настроек
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            buttons_frame,
            text="💾 Сохранить настройки триггера",
            command=self.save_trigger_settings,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 10))
        
        # Основной фрейм для статуса и предварительного просмотра
        main_control_frame = ttk.Frame(parent)
        main_control_frame.pack(fill='x', padx=20, pady=20)
        
        # Левая часть - статус и управление
        left_frame = ttk.Frame(main_control_frame)
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        
        # Статус
        status_frame = ttk.LabelFrame(left_frame, text="📊 Статус триггер-бота", padding=20)
        status_frame.pack(fill='x')
        
        self.trigger_status_label = ttk.Label(
            status_frame, 
            text="⏹️ Статус: Остановлен", 
            font=('Segoe UI', 14, 'bold')
        )
        self.trigger_status_label.pack(pady=20)
        
        # Кнопки управления
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(pady=20)
        
        ttk.Button(
            control_frame, 
            text="▶️ Запустить триггер-бот", 
            command=self.start_trigger_bot,
            style='Accent.TButton'
        ).pack(side='left', padx=10)
        
        ttk.Button(
            control_frame, 
            text="⏹️ Остановить триггер-бот", 
            command=self.stop_trigger_bot,
            style='Danger.TButton'
        ).pack(side='left', padx=10)
        
        # Средняя часть - график цветов во времени
        graph_frame = ttk.LabelFrame(main_control_frame, text="📈 Цвет в центре (R/G/B) во времени", padding=10)
        graph_frame.pack(side='left', fill='both', expand=True, padx=(0, 20))
        try:
            self.create_trigger_color_graph(graph_frame)
            self.start_color_graph_update()
        except Exception:
            pass

        # Правая часть - предварительный просмотр
        right_frame = ttk.Frame(main_control_frame)
        right_frame.pack(side='right', fill='y')
        
        # Предварительный просмотр области
        preview_frame = ttk.LabelFrame(right_frame, text="👁️ Предварительный просмотр области", padding=20)
        preview_frame.pack(fill='both', expand=True)
        
        # Canvas для отображения области (150x150 пикселей)
        self.trigger_preview_canvas = tk.Canvas(
            preview_frame, 
            width=150, 
            height=150, 
            bg='black',
            relief='sunken',
            bd=2
        )
        self.trigger_preview_canvas.pack(pady=10)
        
        # Информация о предварительном просмотре
        preview_info_label = ttk.Label(
            preview_frame,
            text="Автообновление: 150 FPS",
            font=('Segoe UI', 9),
            foreground='gray'
        )
        preview_info_label.pack(pady=5)
        
        # Кнопки управления предпросмотром
        preview_control_frame = ttk.Frame(preview_frame)
        preview_control_frame.pack(pady=5)
        
        ttk.Button(
            preview_control_frame,
            text="🔄 Обновить предпросмотр",
            command=self.update_trigger_preview,
            width=20
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            preview_control_frame,
            text="⏹️ Остановить автообновление",
            command=self.stop_trigger_preview_update,
            width=20
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            preview_control_frame,
            text="▶️ Запустить автообновление",
            command=self.start_trigger_preview_update,
            width=20
        ).pack(side='left')
        
        # Информация о работе
        info_frame = ttk.LabelFrame(parent, text="📝 Информация о работе", padding=20)
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.trigger_info_text = scrolledtext.ScrolledText(
            info_frame, 
            height=10, 
            width=80,
            font=('Consolas', 10)
        )
        self.trigger_info_text.pack(fill='both', expand=True)
        
        # Запускаем предпросмотр триггер-бота сразу после создания вкладки
        self.root.after(1000, self.start_trigger_preview_update)
    
    def create_vision_tab(self, parent):
        """Создание вкладки машинного зрения"""
        # Статус
        status_frame = ttk.LabelFrame(parent, text="📊 Статус машинного зрения", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.vision_status_label = ttk.Label(
            status_frame, 
            text="⏹️ Статус: Остановлено", 
            font=('Segoe UI', 14, 'bold')
        )
        self.vision_status_label.pack(pady=8)
        # Флаги автообновления предпросмотра
        self.vision_preview_active = False
        self.vision_preview_update_id = None
        
        # Кнопки управления
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(pady=8)
        
        ttk.Button(
            control_frame, 
            text="🧠 Обучить YOLOv8", 
            command=self.train_model,
            style='Accent.TButton'
        ).pack(side='left', padx=10)
        
        ttk.Button(
            control_frame, 
            text="📦 Загрузить выбранную модель", 
            command=self.load_yolo_model,
            style='Accent.TButton'
        ).pack(side='left', padx=10)

        ttk.Button(
            control_frame, 
            text="▶️ Запустить обнаружение", 
            command=self.start_detection,
            style='Accent.TButton'
        ).pack(side='left', padx=10)
        
        ttk.Button(
            control_frame, 
            text="⏹️ Остановить обнаружение", 
            command=self.stop_detection,
            style='Danger.TButton'
        ).pack(side='left', padx=10)

        ttk.Button(
            control_frame,
            text="🧪 Отбор данных",
            command=self.open_data_curation_window
        ).pack(side='left', padx=10)

        # Блок выбора модели из папки models
        model_select_frame = ttk.LabelFrame(status_frame, text="🧩 Выбор модели", padding=8)
        model_select_frame.pack(fill='x', padx=0, pady=(6, 0))
        model_row = ttk.Frame(model_select_frame)
        model_row.pack(fill='x')
        ttk.Label(model_row, text="Модель (.pt) из папки models:").pack(side='left', padx=(0, 10))
        self.model_combobox = ttk.Combobox(model_row, state='readonly', width=60)
        self.model_combobox.pack(side='left', fill='x', expand=True)
        self.model_combobox.bind("<<ComboboxSelected>>", self.on_model_selected)
        # Надпись с выбранным файлом модели
        self.selected_model_label = ttk.Label(model_select_frame, text="Файл модели: не выбрана")
        self.selected_model_label.pack(anchor='w', pady=(6, 0))
        # Инициализируем список моделей
        try:
            self.refresh_models_list()
        except Exception:
            pass

        # Параметры обучения (выбор датасета и имени модели)
        training_params_frame = ttk.LabelFrame(status_frame, text="🛠 Параметры обучения", padding=8)
        training_params_frame.pack(fill='x', padx=0, pady=(8, 0))

        # Строка выбора датасета
        dataset_row = ttk.Frame(training_params_frame)
        dataset_row.pack(fill='x', pady=(0, 4))
        ttk.Label(dataset_row, text="Папка датасета:").pack(side='left', padx=(0, 10))
        ttk.Button(dataset_row, text="Выбрать папку", command=self.choose_training_dataset).pack(side='left')
        self.selected_dataset_label = ttk.Label(training_params_frame, text="Датасет: не выбран")
        self.selected_dataset_label.pack(anchor='w')

        # Строка имени модели
        modelname_row = ttk.Frame(training_params_frame)
        modelname_row.pack(fill='x', pady=(6, 0))
        ttk.Label(modelname_row, text="Имя модели:").pack(side='left', padx=(0, 10))
        try:
            self.model_name_var = tk.StringVar()
        except Exception:
            self.model_name_var = None
        self.model_name_entry = ttk.Entry(modelname_row, width=40, textvariable=self.model_name_var)
        self.model_name_entry.pack(side='left', fill='x', expand=True)

        # Ряд с кнопкой сброса данных (подготовка к первому запуску)
        reset_row = ttk.Frame(training_params_frame)
        reset_row.pack(fill='x', pady=(8, 0))
        ttk.Button(reset_row, text="🧹 Сброс данных (первый запуск)", command=self.reset_all_data).pack(side='left')
        
        # Предпросмотр всего экрана для машинного зрения
        preview_frame = ttk.LabelFrame(parent, text="👁️ Предпросмотр экрана", padding=12)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Кнопки управления предпросмотром
        control_frame2 = ttk.Frame(preview_frame)
        control_frame2.pack(fill='x', pady=(0, 8))
        
        ttk.Button(
            control_frame2,
            text="🔄 Обновить",
            command=self.update_vision_preview
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame2,
            text="▶️ Автообновление",
            command=self.start_vision_preview_update
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame2,
            text="⏹️ Стоп",
            command=self.stop_vision_preview_update
        ).pack(side='left')
        
        # Canvas для отображения экрана
        self.vision_canvas = tk.Canvas(
            preview_frame,
            width=800,
            height=600,
            bg='black',
            relief='sunken',
            bd=2
        )
        self.vision_canvas.pack(pady=6)

    def refresh_models_list(self):
        """Обновляет список доступных моделей в комбобоксе из папки models."""
        try:
            import os, glob
            model_dir = self.settings.get('model_path', 'models/')
            os.makedirs(model_dir, exist_ok=True)
            model_paths = sorted(glob.glob(os.path.join(model_dir, '*.pt')))
            self._models_map = {os.path.basename(p): p for p in model_paths}
            values = list(self._models_map.keys())
            if hasattr(self, 'model_combobox'):
                self.model_combobox['values'] = values
                # Выбираем текущую загруженную модель, если она есть
                current_basename = None
                if getattr(self, 'yolo_model_path', None):
                    current_basename = os.path.basename(self.yolo_model_path)
                if current_basename in self._models_map:
                    self.model_combobox.set(current_basename)
                elif values:
                    self.model_combobox.set(values[0])
                else:
                    self.model_combobox.set('')
                # Обновляем надпись
                selected = self.model_combobox.get()
                if hasattr(self, 'selected_model_label'):
                    if selected:
                        self.selected_model_label.config(text=f"Файл модели: {selected}")
                    else:
                        self.selected_model_label.config(text="Файл модели: не выбрана")
        except Exception as e:
            try:
                self.log_message(f'Ошибка обновления списка моделей: {e}')
            except Exception:
                pass

    def on_model_selected(self, event=None):
        """Обработчик выбора модели в комбобоксе."""
        try:
            selected = self.model_combobox.get() if hasattr(self, 'model_combobox') else ''
            if hasattr(self, 'selected_model_label'):
                if selected:
                    self.selected_model_label.config(text=f"Файл модели: {selected}")
                else:
                    self.selected_model_label.config(text="Файл модели: не выбрана")
        except Exception:
            pass

    def choose_training_dataset(self):
        """Открывает диалог выбора папки датасета и сохраняет путь для обучения."""
        try:
            from tkinter import filedialog
            dataset_dir = filedialog.askdirectory(title='Выберите папку с данными (должны быть подпапки "Labels" и "Data_Photo")')
            if dataset_dir:
                self.training_dataset_dir = dataset_dir
                if hasattr(self, 'selected_dataset_label'):
                    self.selected_dataset_label.config(text=f"Датасет: {dataset_dir}")
        except Exception:
            pass

    def reset_all_data(self):
        """Удаляет все датасеты, обученные модели и временные папки, подготавливая первый запуск."""
        try:
            import os
            import shutil
            # Список папок для очистки
            to_remove = [
                os.path.join(os.getcwd(), 'datasets'),
                os.path.join(os.getcwd(), 'yolo_dataset'),
                os.path.join(os.getcwd(), 'Labels'),
                os.path.join(os.getcwd(), 'Data_Photo'),
                os.path.join(os.getcwd(), 'Input_Photo'),
                os.path.join(os.getcwd(), 'models'),
                os.path.join(os.getcwd(), 'runs'),
            ]
            for path in to_remove:
                try:
                    if os.path.exists(path):
                        shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass

            # Сброс состояния приложения
            self.training_dataset_dir = None
            self.yolo_model_path = None
            self.model_trained = False
            self.detection_active = False
            self.aim_active = False
            try:
                self.yolo = None
            except Exception:
                pass

            # Останавливаем активные процессы и обновляем статусные надписи
            try:
                self.stop_detection()
            except Exception:
                pass
            try:
                self.stop_aim()
            except Exception:
                pass
            try:
                if hasattr(self, 'vision_status_label'):
                    self.vision_status_label.config(text="⏹️ Статус: Остановлено")
                if hasattr(self, 'aim_status_label'):
                    self.aim_status_label.config(text="⏹️ Статус: Остановлена")
            except Exception:
                pass

            # Обновляем UI
            try:
                if hasattr(self, 'selected_dataset_label'):
                    self.selected_dataset_label.config(text="Датасет: не выбран")
            except Exception:
                pass
            try:
                if hasattr(self, 'selected_model_label'):
                    self.selected_model_label.config(text="Файл модели: не выбрана")
                if hasattr(self, 'model_combobox'):
                    self.model_combobox['values'] = []
                    self.model_combobox.set('')
                # Пересоздадим пустую папку models и обновим список
                os.makedirs(self.settings.get('model_path', 'models/'), exist_ok=True)
                self.refresh_models_list()
            except Exception:
                pass

            try:
                messagebox.showinfo("Сброс", "Все данные удалены. Программа подготовлена к первому запуску.")
            except Exception:
                pass
        except Exception as e:
            try:
                messagebox.showerror("Сброс", f"Не удалось выполнить сброс: {e}")
            except Exception:
                pass
    
    def create_aim_tab(self, parent):
        """Создание вкладки авто-наводки"""
        # Статус
        status_frame = ttk.LabelFrame(parent, text="📊 Статус авто-наводки", padding=20)
        status_frame.pack(fill='x', padx=20, pady=20)
        
        self.aim_status_label = ttk.Label(
            status_frame, 
            text="⏹️ Статус: Остановлена", 
            font=('Segoe UI', 14, 'bold')
        )
        self.aim_status_label.pack(pady=20)
        
        # Кнопки управления
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(pady=20)
        
        ttk.Button(
            control_frame, 
            text="▶️ Запустить авто-наводку", 
            command=self.start_aim,
            style='Accent.TButton'
        ).pack(side='left', padx=10)
        
        ttk.Button(
            control_frame, 
            text="⏹️ Остановить авто-наводку", 
            command=self.stop_aim,
            style='Danger.TButton'
        ).pack(side='left', padx=10)
        
        # Настройки авто-наводки
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Настройки авто-наводки", padding=20)
        settings_frame.pack(fill='x', padx=20, pady=10)

        grid = ttk.Frame(settings_frame)
        grid.pack(fill='x')

        # Клавиша автонаводки
        ttk.Label(grid, text="⌨️ Клавиша автонаводки:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        aim_key_frame = ttk.Frame(grid)
        aim_key_frame.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.aim_key_var = tk.StringVar(value=self.settings.get('aim_key', 'alt'))
        self.aim_key_display = ttk.Label(aim_key_frame, text=self.aim_key_var.get(), width=15, relief='sunken', padding=5)
        self.aim_key_display.pack(side='left', padx=(0, 10))
        ttk.Button(aim_key_frame, text="Выбрать клавишу", command=self.select_aim_key).pack(side='left')

        # Скорость (пикселей в секунду, дробное)
        ttk.Label(grid, text="🚀 Скорость (px/s):", font=('Segoe UI', 11, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.aim_speed_entry2 = ttk.Entry(grid, width=15)
        self.aim_speed_entry2.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.aim_speed_entry2.insert(0, str(self.settings.get('aim_speed', 100.0)))

        # Точность (радиус пикселей)
        ttk.Label(grid, text="🎯 Точность (радиус px):", font=('Segoe UI', 11, 'bold')).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.aim_accuracy_entry = ttk.Entry(grid, width=15)
        self.aim_accuracy_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.aim_accuracy_entry.insert(0, str(self.settings.get('aim_accuracy_radius', 10)))

        # Цель (выпадающий список)
        ttk.Label(grid, text="🎯 Цель:", font=('Segoe UI', 11, 'bold')).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.aim_target_var = tk.StringVar(value=self.settings.get('aim_target', 'Enemy_Head'))
        ttk.Combobox(grid, textvariable=self.aim_target_var, state='readonly', values=[
            'Enemy_Head', 'Enemy_Body', 'Friendly_Head', 'Friendly_Body'
        ], width=20).grid(row=3, column=1, padx=10, pady=10, sticky='w')

        # Режим вывода и подключение к аппаратной мыши
        ttk.Label(grid, text="🖱️ Режим вывода:", font=('Segoe UI', 11, 'bold')).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.output_mode_var = tk.StringVar(value=self.settings.get('output_mode', 'virtual'))
        ttk.Combobox(grid, textvariable=self.output_mode_var, state='readonly', values=['virtual', 'hardware', 'interception'], width=20).grid(row=4, column=1, padx=10, pady=10, sticky='w')

        hw_row = ttk.Frame(grid)
        hw_row.grid(row=5, column=0, columnspan=2, sticky='w', padx=10, pady=(0,10))
        ttk.Label(hw_row, text="COM:").pack(side='left')
        self.hw_port_entry = ttk.Entry(hw_row, width=12)
        self.hw_port_entry.pack(side='left', padx=(5,10))
        self.hw_port_entry.insert(0, str(self.settings.get('hardware_port', '')))
        ttk.Label(hw_row, text="Baud:").pack(side='left')
        self.hw_baud_entry = ttk.Entry(hw_row, width=8)
        self.hw_baud_entry.pack(side='left', padx=(5,10))
        self.hw_baud_entry.insert(0, str(self.settings.get('hardware_baud', 115200)))
        ttk.Button(hw_row, text="Подключить", command=self.connect_hardware_mouse).pack(side='left')
        ttk.Button(hw_row, text="Установить Interception", command=self.open_interception_install_help).pack(side='left', padx=(10,0))

        # Предпросмотр и визуализация линии наведения
        preview_frame = ttk.LabelFrame(parent, text="👁️ Предпросмотр авто-наводки", padding=12)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.aim_preview_canvas = tk.Canvas(preview_frame, width=800, height=600, bg='black', relief='sunken', bd=2)
        self.aim_preview_canvas.pack(pady=10)
        # Флаг обновления предпросмотра автонаводки
        self.aim_preview_active = False
        self.aim_preview_job = None
        # Кнопки управления предпросмотром
        controls = ttk.Frame(preview_frame)
        controls.pack(fill='x')
        ttk.Button(controls, text="🔄 Обновить", command=self.update_aim_preview).pack(side='left', padx=(0, 10))
        ttk.Button(controls, text="▶️ Автообновление", command=self.start_aim_preview_update).pack(side='left', padx=(0, 10))
        ttk.Button(controls, text="⏹️ Стоп", command=self.stop_aim_preview_update).pack(side='left')
    
    def create_monitor_tab(self, parent):
        """Создание вкладки мониторинга"""
        # Экран мониторинга
        monitor_frame = ttk.LabelFrame(parent, text="📺 Экран мониторинга", padding=20)
        monitor_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Кнопки управления мониторингом
        control_frame = ttk.Frame(monitor_frame)
        control_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(
            control_frame,
            text="🔄 Обновить экран",
            command=self.update_monitor_screen
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="▶️ Запустить автообновление",
            command=self.start_monitor_update
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="⏹️ Остановить автообновление",
            command=self.stop_monitor_update
        ).pack(side='left')
        
        # Canvas для отображения экрана
        self.monitor_canvas = tk.Canvas(
            monitor_frame, 
            width=800, 
            height=600, 
            bg='black',
            relief='sunken',
            bd=2
        )
        self.monitor_canvas.pack(pady=20)
        
        # Информация о текущем состоянии
        info_frame = ttk.LabelFrame(parent, text="📊 Текущее состояние", padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        self.monitor_info_text = scrolledtext.ScrolledText(
            info_frame, 
            height=8, 
            width=80,
            font=('Consolas', 10)
        )
        self.monitor_info_text.pack(fill='x')
        
        # Инициализация мониторинга
        self.monitor_active = False
        self.monitor_update_id = None
        
        # Инициализация автообновления предварительного просмотра триггера
        self.trigger_preview_active = False
        self.trigger_preview_update_id = None
    
    def create_logs_tab(self, parent):
        """Создание вкладки логов"""
        # Управление логами
        control_frame = ttk.LabelFrame(parent, text="🔧 Управление логами", padding=20)
        control_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(
            control_frame, 
            text="🗑️ Очистить логи", 
            command=self.clear_logs
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame, 
            text="💾 Сохранить логи", 
            command=self.save_logs
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame, 
            text="🔄 Обновить", 
            command=self.refresh_logs
        ).pack(side='left')
        
        # Область логов
        logs_frame = ttk.LabelFrame(parent, text="📝 Системные логи", padding=20)
        logs_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame, 
            height=20, 
            width=100,
            font=('Consolas', 9)
        )
        self.logs_text.pack(fill='both', expand=True)
        
        # Заполнение логов (будет вызвано после создания статус бара)
    
    def create_status_bar(self, parent):
        """Создание статус бара"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill='x', pady=(10, 0))
        
        # Статус программы
        self.status_label = ttk.Label(self.status_bar, text="Готов к работе")
        self.status_label.pack(side='left')
        
        # Время работы
        self.uptime_label = ttk.Label(self.status_bar, text="Время работы: 00:00:00")
        self.uptime_label.pack(side='right')
        
        # Обновление времени
        self.update_uptime()
        
        # Инициализация логов после создания всех элементов
        if hasattr(self, 'logs_text'):
            self.refresh_logs()
    
    def apply_theme(self):
        """Применение темы интерфейса"""
        theme = self.settings.get('theme', 'dark')
        
        if theme == 'dark':
            style = ttk.Style()
            style.theme_use('clam')
            
            # Настройка цветов для темной темы
            style.configure('TFrame', background='#2b2b2b')
            style.configure('TLabel', background='#2b2b2b', foreground='white')
            style.configure('TButton', background='#404040', foreground='white')
            style.configure('Accent.TButton', background='#007acc', foreground='white')
            style.configure('Danger.TButton', background='#d13438', foreground='white')
            
            self.root.configure(bg='#2b2b2b')
        else:
            # Светлая тема (по умолчанию)
            style = ttk.Style()
            style.theme_use('clam')
    
    def on_theme_change(self, event=None):
        """Обработчик изменения темы"""
        self.settings['theme'] = self.theme_var.get()
        self.apply_theme()
        self.save_settings()
    
    def populate_settings_fields(self):
        """Заполнение полей настроек"""
        try:
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.settings['screen_width']))
            
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.settings['screen_height']))
            
            # Проверяем существование элементов триггер-бота
            if hasattr(self, 'trigger_key_var'):
                self.trigger_key_var.set(self.settings['trigger_key'])
                if hasattr(self, 'trigger_key_display'):
                    self.trigger_key_display.config(text=self.settings['trigger_key'])
            
            if hasattr(self, 'click_key_var'):
                self.click_key_var.set(self.settings.get('click_key', 'left'))
                if hasattr(self, 'click_key_display'):
                    self.click_key_display.config(text=self.settings.get('click_key', 'left'))
            

            # Инициализация значения погрешности на ползунке триггера
            if hasattr(self, 'trigger_tolerance_scale'):
                try:
                    self.trigger_tolerance_scale.set(self.settings['color_tolerance'])
                    if hasattr(self, 'tolerance_value_label'):
                        self.tolerance_value_label.config(text=f"{int(self.settings['color_tolerance'])}%")
                except Exception:
                    pass
            elif hasattr(self, 'tolerance_scale'):
                self.tolerance_scale.set(self.settings['color_tolerance'])
            
            if hasattr(self, 'duration_entry'):
                self.duration_entry.delete(0, tk.END)
                self.duration_entry.insert(0, str(self.settings['click_duration']))
            
            if hasattr(self, 'aim_speed_entry'):
                self.aim_speed_entry.delete(0, tk.END)
                self.aim_speed_entry.insert(0, str(self.settings['aim_speed']))
            
            if hasattr(self, 'body_part_var'):
                self.body_part_var.set(self.settings['target_body_part'])
            if hasattr(self, 'team_var'):
                self.team_var.set(self.settings['team_to_detect'])
            if hasattr(self, 'theme_var'):
                self.theme_var.set(self.settings['theme'])
        except Exception as e:
            self.log_message(f"Ошибка заполнения полей настроек: {e}")
    
    def update_dashboard_stats(self):
        """Обновление статистики дашборда"""
        try:
            # Системная информация
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            system_info = f"CPU: {cpu_percent}% | RAM: {memory_percent}%"
            self.system_info_label.config(text=system_info)
            
            # Статистика программы
            stats_info = f"Триггер: {'Активен' if self.trigger_bot_running else 'Неактивен'}\n"
            stats_info += f"Зрение: {'Активно' if self.detection_active else 'Неактивно'}\n"
            stats_info += f"Наводка: {'Активна' if self.aim_active else 'Неактивна'}"
            self.stats_info_label.config(text=stats_info)
            
            # Производительность
            perf_info = f"Модель: {'Обучена' if self.model_trained else 'Не обучена'}\n"
            perf_info += f"Статус: {'Работает' if self.is_running else 'Остановлено'}"
            self.perf_info_label.config(text=perf_info)
            
        except Exception as e:
            self.log_message(f"Ошибка обновления статистики: {e}")
    
    def update_uptime(self):
        """Обновление времени работы"""
        if hasattr(self, 'start_time'):
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            self.uptime_label.config(text=f"Время работы: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        self.root.after(1000, self.update_uptime)
    
    def start_all_features(self):
        """Запуск всех функций"""
        try:
            self.start_trigger_bot()
            self.start_detection()
            self.start_aim()
            self.log_message("Все функции запущены")
            self.update_dashboard_stats()
        except Exception as e:
            self.log_message(f"Ошибка запуска всех функций: {e}")
    
    def stop_all_features(self):
        """Остановка всех функций"""
        try:
            self.stop_trigger_bot()
            self.stop_detection()
            self.stop_aim()
            self.log_message("Все функции остановлены")
            self.update_dashboard_stats()
        except Exception as e:
            self.log_message(f"Ошибка остановки всех функций: {e}")
    
    def log_message(self, message):
        """Логирование сообщений"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Добавление в соответствующие текстовые поля
        if hasattr(self, 'trigger_info_text'):
            self.trigger_info_text.insert(tk.END, log_entry)
            self.trigger_info_text.see(tk.END)
        
        if hasattr(self, 'vision_info_text'):
            self.vision_info_text.insert(tk.END, log_entry)
            self.vision_info_text.see(tk.END)
        
        if hasattr(self, 'aim_info_text'):
            self.aim_info_text.insert(tk.END, log_entry)
            self.aim_info_text.see(tk.END)
        
        if hasattr(self, 'logs_text'):
            self.logs_text.insert(tk.END, log_entry)
            self.logs_text.see(tk.END)
        
        # Обновление статуса (если статус бар уже создан)
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def clear_logs(self):
        """Очистка логов"""
        if hasattr(self, 'logs_text'):
            self.logs_text.delete(1.0, tk.END)
            self.log_message("Логи очищены")
    
    def save_logs(self):
        """Сохранение логов"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                self.log_message(f"Логи сохранены в {filename}")
        except Exception as e:
            self.log_message(f"Ошибка сохранения логов: {e}")
    
    def refresh_logs(self):
        """Обновление логов"""
        if hasattr(self, 'logs_text'):
            self.logs_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Логи обновлены\n")
            self.logs_text.see(tk.END)
    
    def reset_settings(self):
        """Сброс настроек к умолчаниям"""
        if messagebox.askyesno("Сброс настроек", "Сбросить все настройки к значениям по умолчанию?"):
            self.settings = {
                'screen_width': 1920,
                'screen_height': 1080,
                'trigger_key': 'shift',
                'click_key': 'left',  # left, right, middle для мыши
                'detection_radius': 1,  # Фиксированный радиус = 1 пиксель
                'color_tolerance': 15,
                'click_duration': 0.1,
                'aim_speed': 100.0,
                'target_body_part': 'head',
                'team_to_detect': 'both',
                'model_path': 'models/',
                'theme': 'dark'
            }
            self.populate_settings_fields()
            self.save_settings()
            self.log_message("Настройки сброшены к значениям по умолчанию")
    
    def import_settings(self):
        """Импорт настроек"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_settings = json.load(f)
                    self.settings.update(imported_settings)
                    self.populate_settings_fields()
                    self.save_settings()
                    self.log_message(f"Настройки импортированы из {filename}")
        except Exception as e:
            self.log_message(f"Ошибка импорта настроек: {e}")
    
    def export_settings(self):
        """Экспорт настроек"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=4, ensure_ascii=False)
                self.log_message(f"Настройки экспортированы в {filename}")
        except Exception as e:
            self.log_message(f"Ошибка экспорта настроек: {e}")
    
    # Методы для работы с функциями
    def select_trigger_key(self):
        """Выбор клавиши для триггер-бота"""
        try:
            # Создаем окно для выбора клавиши
            key_window = tk.Toplevel(self.root)
            key_window.title("Выбор клавиши триггера")
            key_window.geometry("400x250")
            key_window.resizable(False, False)
            key_window.transient(self.root)
            key_window.grab_set()
            
            # Центрируем окно
            key_window.update_idletasks()
            x = (key_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (key_window.winfo_screenheight() // 2) - (250 // 2)
            key_window.geometry(f'400x250+{x}+{y}')
            
            # Инструкция
            instruction = ttk.Label(
                key_window, 
                text="Нажмите клавишу для активации триггера\n(поддерживается кириллица)",
                font=('Segoe UI', 11),
                justify='center'
            )
            instruction.pack(pady=20)
            
            # Поле для отображения выбранной клавиши
            selected_key_label = ttk.Label(
                key_window, 
                text="Ожидание нажатия...",
                font=('Segoe UI', 14, 'bold'),
                foreground='blue'
            )
            selected_key_label.pack(pady=10)
            
            # Информация о поддержке
            info_label = ttk.Label(
                key_window,
                text="💡 Поддерживаются: shift, ctrl, alt, space, буквы (латиница/кириллица)",
                font=('Segoe UI', 9),
                foreground='gray'
            )
            info_label.pack(pady=5)
            
            # Кнопка отмены
            cancel_button = ttk.Button(
                key_window,
                text="Отмена",
                command=key_window.destroy
            )
            cancel_button.pack(pady=10)
            
            def on_key_press(event):
                """Обработчик нажатия клавиши"""
                # Преобразуем в стандартные названия клавиш
                key_name = self.convert_key_name(event.keysym)
                display_name = self.get_display_key_name(event.keysym)
                selected_key_label.config(text=f"Выбрано: {display_name}")
                
                # Обновляем переменную и отображение
                self.trigger_key_var.set(key_name)
                self.trigger_key_display.config(text=display_name)
                
                # Закрываем окно через небольшую задержку
                key_window.after(1000, key_window.destroy)
            
            # Привязываем обработчик к окну
            key_window.bind('<Key>', on_key_press)
            key_window.focus_set()
            
        except Exception as e:
            self.log_message(f"Ошибка выбора клавиши: {e}")
            messagebox.showerror("Ошибка", f"Ошибка выбора клавиши: {e}")
    
    def select_click_key(self):
        """Выбор клавиши для клика триггер-бота"""
        try:
            # Создаем окно для выбора клавиши
            key_window = tk.Toplevel(self.root)
            key_window.title("Выбор клавиши для клика")
            key_window.geometry("400x300")
            key_window.resizable(False, False)
            key_window.transient(self.root)
            key_window.grab_set()
            
            # Центрируем окно
            key_window.update_idletasks()
            x = (key_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (key_window.winfo_screenheight() // 2) - (300 // 2)
            key_window.geometry(f'400x300+{x}+{y}')
            
            # Инструкция
            instruction = ttk.Label(
                key_window, 
                text="Выберите тип клика:",
                font=('Segoe UI', 12, 'bold'),
                justify='center'
            )
            instruction.pack(pady=20)
            
            # Фрейм для кнопок мыши
            mouse_frame = ttk.LabelFrame(key_window, text="🖱️ Кнопки мыши", padding=10)
            mouse_frame.pack(fill='x', padx=20, pady=10)
            
            # Кнопки мыши
            ttk.Button(
                mouse_frame, 
                text="Левая кнопка (left)", 
                command=lambda: self.set_click_key("left", key_window)
            ).pack(fill='x', pady=2)
            
            ttk.Button(
                mouse_frame, 
                text="Правая кнопка (right)", 
                command=lambda: self.set_click_key("right", key_window)
            ).pack(fill='x', pady=2)
            
            ttk.Button(
                mouse_frame, 
                text="Средняя кнопка (middle)", 
                command=lambda: self.set_click_key("middle", key_window)
            ).pack(fill='x', pady=2)
            
            # Фрейм для клавиш клавиатуры
            keyboard_frame = ttk.LabelFrame(key_window, text="⌨️ Клавиши клавиатуры", padding=10)
            keyboard_frame.pack(fill='x', padx=20, pady=10)
            
            # Инструкция для клавиатуры
            ttk.Label(
                keyboard_frame, 
                text="Нажмите любую клавишу на клавиатуре\n(поддерживается кириллица)",
                font=('Segoe UI', 9),
                justify='center'
            ).pack(pady=5)
            
            # Поле для отображения выбранной клавиши
            selected_key_label = ttk.Label(
                keyboard_frame, 
                text="Ожидание нажатия...",
                font=('Segoe UI', 12, 'bold'),
                foreground='blue'
            )
            selected_key_label.pack(pady=5)
            
            # Кнопка отмены
            cancel_button = ttk.Button(
                key_window,
                text="Отмена",
                command=key_window.destroy
            )
            cancel_button.pack(pady=10)
            
            def on_key_press(event):
                """Обработчик нажатия клавиши"""
                # Преобразуем в стандартные названия клавиш
                key_name = self.convert_key_name(event.keysym)
                display_name = self.get_display_key_name(event.keysym)
                selected_key_label.config(text=f"Выбрано: {display_name}")
                
                # Обновляем переменную и отображение
                self.click_key_var.set(key_name)
                self.click_key_display.config(text=display_name)
                
                # Закрываем окно через небольшую задержку
                key_window.after(1000, key_window.destroy)
            
            # Привязываем обработчик к окну
            key_window.bind('<Key>', on_key_press)
            key_window.focus_set()
            
        except Exception as e:
            self.log_message(f"Ошибка выбора клавиши для клика: {e}")
            messagebox.showerror("Ошибка", f"Ошибка выбора клавиши для клика: {e}")
    
    def set_click_key(self, key_name, window):
        """Установка клавиши для клика"""
        try:
            self.click_key_var.set(key_name)
            self.click_key_display.config(text=key_name)
            self.log_message(f"Выбрана клавиша для клика: {key_name}")
            window.destroy()
        except Exception as e:
            self.log_message(f"Ошибка установки клавиши клика: {e}")
    
    def convert_key_name(self, keysym):
        """Преобразование названий клавиш в стандартные"""
        key_mapping = {
            'Shift_L': 'shift',
            'Shift_R': 'shift',
            'Control_L': 'ctrl',
            'Control_R': 'ctrl',
            'Alt_L': 'alt',
            'Alt_R': 'alt',
            'space': 'space',
            'Return': 'enter',
            'Tab': 'tab',
            'Escape': 'esc',
            'BackSpace': 'backspace',
            'Delete': 'delete',
            'Insert': 'insert',
            'Home': 'home',
            'End': 'end',
            'Page_Up': 'page up',
            'Page_Down': 'page down',
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'F1': 'f1',
            'F2': 'f2',
            'F3': 'f3',
            'F4': 'f4',
            'F5': 'f5',
            'F6': 'f6',
            'F7': 'f7',
            'F8': 'f8',
            'F9': 'f9',
            'F10': 'f10',
            'F11': 'f11',
            'F12': 'f12'
        }
        
        # Если есть специальное название, используем его
        if keysym in key_mapping:
            return key_mapping[keysym]
        
        # Поддержка кириллицы - преобразуем в латиницу для библиотеки keyboard
        cyrillic_mapping = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        # Проверяем кириллицу
        if keysym in cyrillic_mapping:
            return cyrillic_mapping[keysym]
        
        # Иначе возвращаем в нижнем регистре
        return keysym.lower()
    
    def get_display_key_name(self, keysym):
        """Получение отображаемого названия клавиши (с поддержкой кириллицы)"""
        # Сначала пробуем преобразовать для библиотеки keyboard
        internal_key = self.convert_key_name(keysym)
        
        # Для отображения используем оригинальное название, если это кириллица
        if keysym in ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 
                      'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 
                      'ъ', 'ы', 'ь', 'э', 'ю', 'я']:
            return f"{keysym} ({internal_key})"
        
        return internal_key
    

    
    def update_tolerance_label(self, value):
        """Обновление метки погрешности"""
        try:
            tolerance = int(float(value))
            self.tolerance_value_label.config(text=f"{tolerance}%")
        except:
            pass
    
    def update_monitor_screen(self):
        """Обновление экрана мониторинга"""
        try:
            import pyautogui
            import cv2
            import numpy as np
            
            # Захват экрана
            screenshot = pyautogui.screenshot()
            
            # Конвертация в формат OpenCV
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Изменение размера для отображения
            display_width = 800
            display_height = 600
            
            # Сохраняем пропорции
            h, w = img.shape[:2]
            aspect = w / h
            if aspect > display_width / display_height:
                new_w = display_width
                new_h = int(display_width / aspect)
            else:
                new_h = display_height
                new_w = int(display_height * aspect)
            
            img_resized = cv2.resize(img, (new_w, new_h))
            
            # Создаем черный фон нужного размера
            background = np.zeros((display_height, display_width, 3), dtype=np.uint8)
            
            # Размещаем изображение по центру
            y_offset = (display_height - new_h) // 2
            x_offset = (display_width - new_w) // 2
            background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
            
            # Конвертация в формат Tkinter
            img_rgb = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            
            # Очистка canvas и отображение изображения
            self.monitor_canvas.delete("all")
            self.monitor_canvas.create_image(0, 0, anchor='nw', image=img_tk)
            
            # Сохранение ссылки на изображение
            self.monitor_image = img_tk
            
            # Обновление информации
            self.monitor_info_text.delete(1.0, tk.END)
            info = f"Экран обновлен: {time.strftime('%H:%M:%S')}\n"
            info += f"Размер экрана: {w}x{h}\n"
            info += f"Размер отображения: {new_w}x{new_h}\n"
            info += f"Статус мониторинга: {'Активен' if self.monitor_active else 'Неактивен'}"
            self.monitor_info_text.insert(tk.END, info)
            
            self.log_message("Экран мониторинга обновлен")
            
        except Exception as e:
            self.log_message(f"Ошибка обновления экрана мониторинга: {e}")
            self.monitor_info_text.delete(1.0, tk.END)
            self.monitor_info_text.insert(tk.END, f"Ошибка: {e}")
    
    def start_monitor_update(self):
        """Запуск автообновления мониторинга"""
        if not self.monitor_active:
            self.monitor_active = True
            self.log_message("Автообновление мониторинга запущено")
            self.update_monitor_loop()
    
    def stop_monitor_update(self):
        """Остановка автообновления мониторинга"""
        if self.monitor_active:
            self.monitor_active = False
            if self.monitor_update_id:
                self.root.after_cancel(self.monitor_update_id)
                self.monitor_update_id = None
            self.log_message("Автообновление мониторинга остановлено")
    
    def update_monitor_loop(self):
        """Цикл обновления мониторинга"""
        if self.monitor_active:
            self.update_monitor_screen()
            # Обновляем каждые 2 секунды
            self.monitor_update_id = self.root.after(2000, self.update_monitor_loop)
    
    def update_vision_preview(self):
        """Обновление предпросмотра экрана во вкладке машинного зрения"""
        try:
            import pyautogui
            import cv2
            import numpy as np
            from PIL import Image
            try:
                from joblib import load
            except Exception:
                load = None
            
            screenshot = pyautogui.screenshot()
            img_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            display_width, display_height = 800, 600
            h, w = img_bgr.shape[:2]
            aspect = w / h
            if aspect > display_width / display_height:
                new_w = display_width
                new_h = int(display_width / aspect)
            else:
                new_h = display_height
                new_w = int(display_height * aspect)
            img_resized = cv2.resize(img_bgr, (new_w, new_h))
            background = np.zeros((display_height, display_width, 3), dtype=np.uint8)
            y_offset = (display_height - new_h) // 2
            x_offset = (display_width - new_w) // 2
            background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
            # Наложение результатов детекции через YOLOv8, если загружена модель
            try:
                if hasattr(self, 'yolo') and self.yolo is not None:
                    # Прогоняем уменьшенное изображение через YOLO (ожидает RGB)
                    img_small_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                    results = self.yolo.predict(img_small_rgb, imgsz=img_small_rgb.shape[0], verbose=False)
                    for r in results:
                        if not hasattr(r, 'boxes') or r.boxes is None:
                            continue
                        for b in r.boxes:
                            try:
                                x1, y1, x2, y2 = b.xyxy[0].tolist()
                                cls_id = int(b.cls[0].item()) if hasattr(b, 'cls') else -1
                                conf = float(b.conf[0].item()) if hasattr(b, 'conf') else 0.0
                                label = str(self.yolo.names.get(cls_id, cls_id))
                                color = (0, 255, 0) if 'Enemy' in label else (0, 0, 255)
                                cv2.rectangle(background, (x_offset + int(x1), y_offset + int(y1)), (x_offset + int(x2), y_offset + int(y2)), color, 2)
                                cv2.putText(background, f"{label} {conf:.2f}", (x_offset + int(x1), y_offset + int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
                            except Exception:
                                continue
            except Exception:
                pass

            img_rgb = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.vision_canvas.delete("all")
            self.vision_canvas.create_image(0, 0, anchor='nw', image=img_tk)
            self.vision_image = img_tk
        except Exception as e:
            self.log_message(f"Ошибка предпросмотра (Vision): {e}")

    def _vision_extract_features(self, pil_img):
        """Вспомогательная функция извлечения признаков, согласованная с train_model."""
        import numpy as np
        img = np.array(pil_img.convert('RGB'))
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        hist_r, _ = np.histogram(r, bins=8, range=(0, 255), density=True)
        hist_g, _ = np.histogram(g, bins=8, range=(0, 255), density=True)
        hist_b, _ = np.histogram(b, bins=8, range=(0, 255), density=True)
        mean = img.mean(axis=(0, 1)) / 255.0
        std = img.std(axis=(0, 1)) / 255.0
        feat = np.concatenate([hist_r, hist_g, hist_b, mean, std]).astype('float32')
        return feat

    def update_vision_preview_loop(self):
        """Цикл автообновления предпросмотра (Vision)"""
        if self.vision_preview_active:
            self.update_vision_preview()
            self.vision_preview_update_id = self.root.after(100, self.update_vision_preview_loop)

    # ======== Предпросмотр автонаводки: линия от центра экрана до цели ========
    def start_aim_preview_update(self):
        if not getattr(self, 'aim_preview_active', False):
            self.aim_preview_active = True
            self.update_aim_preview_loop()

    def stop_aim_preview_update(self):
        if getattr(self, 'aim_preview_active', False):
            self.aim_preview_active = False
            if getattr(self, 'aim_preview_job', None):
                try:
                    self.root.after_cancel(self.aim_preview_job)
                except Exception:
                    pass
                self.aim_preview_job = None

    def update_aim_preview_loop(self):
        if getattr(self, 'aim_preview_active', False):
            try:
                self.update_aim_preview()
            except Exception:
                pass
            self.aim_preview_job = self.root.after(100, self.update_aim_preview_loop)

    def update_aim_preview(self):
        """Рисует на canvas предпросмотра линию от центра экрана до центра выбранной цели (если найдена)."""
        try:
            if not hasattr(self, 'aim_preview_canvas'):
                return
            import pyautogui
            import cv2
            import numpy as np
            from PIL import Image, ImageTk
            # Скрин и масштабирование под canvas 800x600
            try:
                screenshot = pyautogui.screenshot()
            except Exception:
                return
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            display_w, display_h = 800, 600
            h, w = frame.shape[:2]
            aspect = w / h
            if aspect > display_w / display_h:
                new_w = display_w
                new_h = int(display_w / aspect)
            else:
                new_h = display_h
                new_w = int(display_h * aspect)
            img_resized = cv2.resize(frame, (new_w, new_h))
            background = np.zeros((display_h, display_w, 3), dtype=np.uint8)
            y_offset = (display_h - new_h) // 2
            x_offset = (display_w - new_w) // 2
            background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized

            # Ищем цель выбранного класса
            target_label = self.settings.get('aim_target', 'Enemy_Head')
            target_center = None
            if hasattr(self, 'yolo') and self.yolo is not None:
                try:
                    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                    results = self.yolo.predict(img_rgb, imgsz=img_rgb.shape[0], verbose=False)
                    for r in results:
                        if not hasattr(r, 'boxes') or r.boxes is None:
                            continue
                        for b in r.boxes:
                            try:
                                cls_id = int(b.cls[0].item()) if hasattr(b, 'cls') else -1
                                label = str(self.yolo.names.get(cls_id, cls_id))
                                if label != target_label:
                                    continue
                                x1, y1, x2, y2 = b.xyxy[0].tolist()
                                cx = int(x_offset + (x1 + x2) / 2)
                                cy = int(y_offset + (y1 + y2) / 2)
                                target_center = (cx, cy)
                                # Отрисуем бокс для наглядности
                                cv2.rectangle(background, (x_offset + int(x1), y_offset + int(y1)), (x_offset + int(x2), y_offset + int(y2)), (0, 255, 0), 2)
                                break
                            except Exception:
                                continue
                        if target_center is not None:
                            break
                except Exception:
                    pass

            # Рисуем линию от центра canvas к цели (если найдена)
            center_canvas = (display_w // 2, display_h // 2)
            if target_center is not None:
                cv2.line(background, center_canvas, target_center, (144, 238, 144), 2)  # light green

            # Выводим на canvas
            img_rgb = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.aim_preview_canvas.delete("all")
            self.aim_preview_canvas.create_image(0, 0, anchor='nw', image=img_tk)
            # удерживаем ссылку, чтобы изображение не сборщилось GC
            self.aim_preview_canvas.image = img_tk
        except Exception as e:
            try:
                self.log_message(f"Ошибка предпросмотра автонаводки: {e}")
            except Exception:
                pass

    def start_vision_preview_update(self):
        if not self.vision_preview_active:
            self.vision_preview_active = True
            self.update_vision_preview_loop()
            self.log_message("Автообновление предпросмотра (Vision) запущено")
        else:
            self.log_message("Предпросмотр (Vision) уже активен")

    def stop_vision_preview_update(self):
        if self.vision_preview_active:
            self.vision_preview_active = False
            if self.vision_preview_update_id:
                self.root.after_cancel(self.vision_preview_update_id)
                self.vision_preview_update_id = None
            self.log_message("Автообновление предпросмотра (Vision) остановлено")

    # ======== Окно отбора данных для машинного зрения ========
    def open_data_curation_window(self):
        try:
            import os
            import glob
            import json
            import shutil
            from PIL import Image
        except Exception as e:
            self.log_message(f"Ошибка импорта модулей для отбора данных: {e}")
            return

        window = tk.Toplevel(self.root)
        window.title("Отбор данных для машинного зрения")
        window.geometry("1200x800")
        window.minsize(1000, 700)

        container = ttk.Frame(window)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # ===== Управление датасетом (база папки, в ней подпапки: Input_Photo, Data_Photo, Labels) =====
        current_dataset_base = os.getcwd()
        dataset_path_var = tk.StringVar(value=f"Датасет: {current_dataset_base}")
        just_switched = False

        def switch_dataset(base_dir: str):
            """Переключает текущий датасет на указанную базовую папку."""
            nonlocal current_dataset_base, input_dir, processed_dir, labels_dir, image_paths, just_switched
            try:
                current_dataset_base = base_dir
                os.makedirs(current_dataset_base, exist_ok=True)
                input_dir = os.path.join(current_dataset_base, 'Input_Photo')
                processed_dir = os.path.join(current_dataset_base, 'Data_Photo')
                labels_dir = os.path.join(current_dataset_base, 'Labels')
                os.makedirs(input_dir, exist_ok=True)
                os.makedirs(processed_dir, exist_ok=True)
                os.makedirs(labels_dir, exist_ok=True)
                image_paths = sorted(glob.glob(os.path.join(input_dir, '*.*')))
                self.curation_index = 0
                dataset_path_var.set(f"Датасет: {current_dataset_base}")
                # Флаг чтобы не закрывать окно, если изображений нет
                just_switched = True
                load_current_image()
            except Exception as e:
                try:
                    messagebox.showerror("Датасет", f"Не удалось переключить датасет: {e}")
                except Exception:
                    pass

        def create_new_dataset():
            """Создаёт новый датасет внутри ./datasets/<name> и переключается на него."""
            try:
                from tkinter import simpledialog
                # Запрашиваем имя
                name = simpledialog.askstring("Новый датасет", "Введите имя датасета:")
                if not name:
                    return
                # Небольшая санитация имени
                safe_name = ''.join(c for c in name if c.isalnum() or c in ('_', '-', ' ')).strip()
                safe_name = safe_name.replace(' ', '_')
                if not safe_name:
                    messagebox.showwarning("Датасет", "Некорректное имя датасета")
                    return
                datasets_root = os.path.join(os.getcwd(), 'datasets')
                os.makedirs(datasets_root, exist_ok=True)
                base_dir = os.path.join(datasets_root, safe_name)
                # Переключаемся и создаём структуру
                switch_dataset(base_dir)
                # Откроем папку Input_Photo для удобства
                try:
                    os.startfile(os.path.join(base_dir, 'Input_Photo'))
                except Exception:
                    pass
            except Exception as e:
                try:
                    messagebox.showerror("Датасет", f"Ошибка создания датасета: {e}")
                except Exception:
                    pass

        dataset_frame = ttk.Frame(container)
        dataset_frame.pack(fill='x', pady=(0, 8))
        ttk.Label(dataset_frame, textvariable=dataset_path_var).pack(side='left')
        # Кнопка выбора существующей папки с датасетом
        def choose_existing_dataset():
            try:
                from tkinter import filedialog
                base_dir = filedialog.askdirectory(title='Выберите папку датасета (содержит Input_Photo, Data_Photo, Labels)')
                if base_dir:
                    switch_dataset(base_dir)
            except Exception:
                pass
        ttk.Button(dataset_frame, text="Выбрать папку", command=choose_existing_dataset).pack(side='right', padx=(6, 0))
        ttk.Button(dataset_frame, text="Новый датасет", command=create_new_dataset).pack(side='right')

        # Статусная панель (прогресс и выбранный класс)
        status_frame = ttk.Frame(container)
        status_frame.pack(fill='x', pady=(0, 8))
        progress_var = tk.StringVar(value="0/0")
        current_label_var = tk.StringVar(value="Класс: —")
        ttk.Label(status_frame, textvariable=progress_var).pack(side='left')
        ttk.Label(status_frame, textvariable=current_label_var).pack(side='right')

        # Холст для отображения текущего изображения
        self.curation_canvas = tk.Canvas(container, width=1100, height=700, bg='black')
        self.curation_canvas.pack(side='top', fill='both', expand=True)

        # Панель кнопок классов
        buttons_frame = ttk.Frame(container)
        buttons_frame.pack(side='bottom', fill='x', pady=(10, 0))

        classes = [
            ("Противник: голова", "Enemy_Head"),
            ("Противник: тело", "Enemy_Body"),
            ("Союзник: голова", "Friendly_Head"),
            ("Союзник: тело", "Friendly_Body")
        ]

        # Папки (по умолчанию текущая директория проекта)
        input_dir = os.path.join(current_dataset_base, 'Input_Photo')
        processed_dir = os.path.join(current_dataset_base, 'Data_Photo')
        labels_dir = os.path.join(current_dataset_base, 'Labels')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)

        # Список файлов
        image_paths = sorted(glob.glob(os.path.join(input_dir, '*.*')))
        self.curation_index = 0
        self.curation_boxes = []  # [(x1,y1,x2,y2,label)]
        self.curation_current_label = None

        # Загрузка текущего изображения
        def load_current_image():
            nonlocal just_switched
            self.curation_boxes.clear()
            self.curation_canvas.delete('all')
            if self.curation_index >= len(image_paths):
                # Если только что переключились на новый датасет, не закрываем окно
                try:
                    total = len(image_paths)
                    progress_var.set(f"Фото: {min(self.curation_index, total)}/{total}")
                except Exception:
                    pass
                if just_switched:
                    just_switched = False
                    return
                else:
                    messagebox.showinfo("Готово", "Все данные отобраны")
                    window.destroy()
                    return
            path = image_paths[self.curation_index]
            try:
                img = Image.open(path).convert('RGB')
                self.curation_image_pil = img
                # Масштаб под canvas
                w, h = img.size
                canvas_w = self.curation_canvas.winfo_width() or 1100
                canvas_h = self.curation_canvas.winfo_height() or 700
                scale = min(canvas_w / w, canvas_h / h)
                new_w = max(1, int(w * scale))
                new_h = max(1, int(h * scale))
                img_resized = img.resize((new_w, new_h))
                self.curation_scale = scale
                self.curation_offset_x = (canvas_w - new_w) // 2
                self.curation_offset_y = (canvas_h - new_h) // 2
                self.curation_image_tk = ImageTk.PhotoImage(img_resized)
                self.curation_canvas.create_image(self.curation_offset_x, self.curation_offset_y, anchor='nw', image=self.curation_image_tk)
                # Обновляем прогресс
                total = len(image_paths)
                progress_var.set(f"Фото: {self.curation_index + 1}/{total}")
            except Exception as e:
                self.log_message(f"Ошибка загрузки изображения: {e}")
                self.curation_index += 1
                load_current_image()

        # Выделение областей мышью
        start = {'x': 0, 'y': 0}
        current_rect = {'id': None}

        def on_mouse_down(event):
            start['x'] = event.x
            start['y'] = event.y
            if current_rect['id'] is not None:
                self.curation_canvas.delete(current_rect['id'])
                current_rect['id'] = None

        def on_mouse_move(event):
            if start['x'] or start['y']:
                if current_rect['id'] is not None:
                    self.curation_canvas.delete(current_rect['id'])
                current_rect['id'] = self.curation_canvas.create_rectangle(start['x'], start['y'], event.x, event.y, outline='lime', width=2)

        def on_mouse_up(event):
            if current_rect['id'] is not None:
                x1, y1 = start['x'], start['y']
                x2, y2 = event.x, event.y
                # Нормализуем координаты
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])
                # Преобразуем в координаты исходного изображения
                inv_scale = 1.0 / (self.curation_scale or 1.0)
                ix1 = int((x1 - self.curation_offset_x) * inv_scale)
                iy1 = int((y1 - self.curation_offset_y) * inv_scale)
                ix2 = int((x2 - self.curation_offset_x) * inv_scale)
                iy2 = int((y2 - self.curation_offset_y) * inv_scale)
                # Требуем выбранный класс
                if not self.curation_current_label:
                    messagebox.showwarning("Разметка", "Сначала выберите класс, затем выделяйте область")
                else:
                    self.curation_boxes.append([ix1, iy1, ix2, iy2, self.curation_current_label])
                # Оставляем зеленый прямоугольник
                current_rect['id'] = None

        self.curation_canvas.bind('<ButtonPress-1>', on_mouse_down)
        self.curation_canvas.bind('<B1-Motion>', on_mouse_move)
        self.curation_canvas.bind('<ButtonRelease-1>', on_mouse_up)

        def save_and_next():
            nonlocal image_paths
            if self.curation_index >= len(image_paths):
                return
            path = image_paths[self.curation_index]
            base = os.path.basename(path)
            name, _ = os.path.splitext(base)
            label_path = os.path.join(labels_dir, f"{name}.json")
            # Сохраняем JSON (даже если боксов нет)
            data = {
                'image': base,
                'boxes': [
                    {'x1': b[0], 'y1': b[1], 'x2': b[2], 'y2': b[3], 'label': b[4]}
                    for b in self.curation_boxes
                ]
            }
            try:
                with open(label_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.log_message(f"Ошибка сохранения разметки: {e}")
            # Переносим обработанную фотографию
            try:
                shutil.move(path, os.path.join(processed_dir, os.path.basename(path)))
            except Exception:
                # Если уже существует, удаляем исходник
                try:
                    os.remove(path)
                except Exception:
                    pass
            # Следующее изображение
            self.curation_index += 1
            load_current_image()

        def mark_no_targets_and_next():
            nonlocal image_paths
            if self.curation_index >= len(image_paths):
                return
            path = image_paths[self.curation_index]
            base = os.path.basename(path)
            name, _ = os.path.splitext(base)
            label_path = os.path.join(labels_dir, f"{name}.json")
            data = { 'image': base, 'boxes': [], 'no_targets': True }
            try:
                with open(label_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.log_message(f"Ошибка сохранения no-targets: {e}")
            try:
                shutil.move(path, os.path.join(processed_dir, os.path.basename(path)))
            except Exception:
                try:
                    os.remove(path)
                except Exception:
                    pass
            self.curation_index += 1
            load_current_image()

        # Кнопки выбора класса (нажимаем класс, затем рисуем рамки)
        def set_current_class(k: str, title: str):
            self.curation_current_label = k
            current_label_var.set(f"Класс: {title}")

        for title, key in classes:
            ttk.Button(buttons_frame, text=title, command=lambda k=key, t=title: set_current_class(k, t)).pack(side='left', padx=5)

        # Нет целей — сохраняем пустую разметку и далее
        ttk.Button(buttons_frame, text="Нет целей", command=mark_no_targets_and_next).pack(side='left', padx=12)

        # Кнопки управления
        ttk.Button(buttons_frame, text="Сохранить и далее", command=save_and_next).pack(side='right', padx=5)
        ttk.Button(buttons_frame, text="Остановиться", command=window.destroy).pack(side='right', padx=5)

        # Старт загрузки первого изображения
        window.after(100, load_current_image)

    def start_trigger_preview_update(self):
        """Запуск автообновления предварительного просмотра триггера"""
        if not self.trigger_preview_active:
            self.trigger_preview_active = True
            self.log_message("Автообновление предварительного просмотра триггера запущено (150 FPS)")
            self.update_trigger_preview_loop()
        else:
            self.log_message("Предпросмотр триггер-бота уже активен")
    
    def stop_trigger_preview_update(self):
        """Остановка автообновления предварительного просмотра триггера"""
        if self.trigger_preview_active:
            self.trigger_preview_active = False
            if self.trigger_preview_update_id:
                self.root.after_cancel(self.trigger_preview_update_id)
                self.trigger_preview_update_id = None
            self.log_message("Автообновление предварительного просмотра триггера остановлено")
    
    def update_trigger_preview_loop(self):
        """Цикл автообновления предварительного просмотра триггера (150 FPS)"""
        if self.trigger_preview_active:
            self.update_trigger_preview()
            # Обновляем каждые ~6-7 мс для ~150 FPS
            self.trigger_preview_update_id = self.root.after(7, self.update_trigger_preview_loop)

    # ======== График цвета 3x3 центра экрана ========
    def create_trigger_color_graph(self, parent):
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import collections
        except Exception as e:
            try:
                self.log_message(f"Ошибка инициализации графика: {e}")
            except Exception:
                pass
            return

        self.color_history_len = 120  # ~30 секунд при 4 Гц
        self.color_r = collections.deque(maxlen=self.color_history_len)
        self.color_g = collections.deque(maxlen=self.color_history_len)
        self.color_b = collections.deque(maxlen=self.color_history_len)
        self.color_t = collections.deque(maxlen=self.color_history_len)

        self.color_fig, self.color_ax = plt.subplots(figsize=(4, 2.2), dpi=100)
        self.color_ax.set_title('Цвет центра 3x3', fontsize=9)
        self.color_ax.set_xlabel('t (секунды)')
        self.color_ax.set_ylabel('Интенсивность (0-255)')
        self.color_ax.set_ylim(0, 255)
        self.color_ax.set_xlim(0, 30)
        self.color_ax.set_xticks([0, 10, 20, 30])
        self.color_ax.grid(True, alpha=0.3)
        (self.line_r,) = self.color_ax.plot([], [], color='red', label='R', linewidth=1)
        (self.line_g,) = self.color_ax.plot([], [], color='green', label='G', linewidth=1)
        (self.line_b,) = self.color_ax.plot([], [], color='blue', label='B', linewidth=1)
        self.color_ax.legend(loc='upper right', fontsize=8)

        self.color_canvas = FigureCanvasTkAgg(self.color_fig, master=parent)
        self.color_canvas_widget = self.color_canvas.get_tk_widget()
        self.color_canvas_widget.pack(fill='both', expand=True)

        self.color_update_job = None
        # частота выборки 4 Гц
        self.color_sample_hz = 4.0
        self.color_sample_period = 1.0 / self.color_sample_hz

    def start_color_graph_update(self):
        # 4 Гц -> каждые 250 мс
        try:
            self.stop_color_graph_update()
        except Exception:
            pass
        self.schedule_color_graph_update()

    def stop_color_graph_update(self):
        try:
            if self.color_update_job is not None:
                self.root.after_cancel(self.color_update_job)
                self.color_update_job = None
        except Exception:
            pass

    def schedule_color_graph_update(self):
        try:
            self.update_color_graph()
        except Exception:
            pass
        # поддерживаем точную частоту 4 Гц
        self.color_update_job = self.root.after(int(self.color_sample_period * 1000), self.schedule_color_graph_update)

    def update_color_graph(self):
        try:
            import numpy as np
            # Центр экрана
            screen_width = self.settings.get('screen_width', 1920)
            screen_height = self.settings.get('screen_height', 1080)
            center_x = screen_width // 2
            center_y = screen_height // 2
            # Регион 3x3
            region = (center_x - 1, center_y - 1, 3, 3)
            try:
                from mss import mss
                with mss() as sct:
                    monitor = {'left': region[0], 'top': region[1], 'width': region[2], 'height': region[3]}
                    shot = sct.grab(monitor)
                    arr = np.array(shot)
                    rgb = arr[:, :, :3][:, :, ::-1]
            except Exception:
                import pyautogui
                img = pyautogui.screenshot(region=region)
                import cv2
                rgb = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)[:, :, ::-1]

            avg = rgb.mean(axis=(0, 1))
            r, g, b = [int(v) for v in avg]
            t = (self.color_t[-1] + 1) if self.color_t else 0
            self.color_r.append(r)
            self.color_g.append(g)
            self.color_b.append(b)
            self.color_t.append(t)

            # Формируем ось X в секундах, статично 0..30
            n = len(self.color_r)
            x_vals = np.arange(n) * self.color_sample_period
            self.line_r.set_data(x_vals, list(self.color_r))
            self.line_g.set_data(x_vals, list(self.color_g))
            self.line_b.set_data(x_vals, list(self.color_b))
            self.color_canvas.draw_idle()
        except Exception as e:
            try:
                self.log_message(f"Ошибка обновления графика цвета: {e}")
            except Exception:
                pass
    
    def save_trigger_settings(self):
        """Сохранение настроек триггер-бота"""
        try:
            # Получаем значения
            trigger_key = self.trigger_key_var.get()
            click_key = self.click_key_var.get()
            color_tolerance = int(self.trigger_tolerance_scale.get())
            click_duration = float(self.trigger_duration_entry.get())
            
            # Проверяем корректность значений
            if not trigger_key:
                raise ValueError("Не выбрана клавиша триггера")
            
            if not click_key:
                raise ValueError("Не выбрана клавиша для клика")
            
            if color_tolerance < 1 or color_tolerance > 100:
                raise ValueError("Погрешность цвета должна быть от 1% до 100%")
            
            if click_duration < 0.01 or click_duration > 1.0:
                raise ValueError("Длительность клика должна быть от 0.01 до 1.0 секунды")
            
            # Сохраняем настройки (область захвата фиксированно 3x3)
            self.settings['trigger_key'] = trigger_key
            self.settings['click_key'] = click_key
            self.settings['detection_radius'] = 1  # историческое поле, фактически используется 3x3 регион
            self.settings['color_tolerance'] = int(color_tolerance)
            self.settings['click_duration'] = float(click_duration)
            
            # Сохраняем в файл
            self.save_settings()
            
            self.log_message("Настройки триггер-бота сохранены")
            self.log_message(f"Клавиша триггера: {trigger_key}, Клавиша клика: {click_key}, Область: 3x3 (фиксированно), Погрешность: {color_tolerance}%, Длительность: {click_duration}s")
            messagebox.showinfo("Успех", "Настройки триггер-бота сохранены!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверное значение: {e}")
            self.log_message(f"Ошибка валидации настроек: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
            self.log_message(f"Ошибка сохранения настроек: {e}")
    
    def update_trigger_preview(self):
        """Обновление предварительного просмотра области триггера"""
        try:
            # Захват экрана
            import pyautogui
            import cv2
            import numpy as np
            
            # Получение центра экрана из настроек пользователя
            screen_width = self.settings.get('screen_width', 1920)
            screen_height = self.settings.get('screen_height', 1080)
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # Фиксированный размер области для предварительного просмотра (150x150 пикселей)
            preview_size = 150
            half_size = preview_size // 2
            
            # Захват области 150x150 пикселей вокруг центра для предварительного просмотра
            left = int(center_x - half_size)
            top = int(center_y - half_size)
            region = (left, top, preview_size, preview_size)
            
            try:
                screenshot = pyautogui.screenshot(region=region)
            except Exception as e:
                self.log_message(f"Ошибка захвата экрана: {e}")
                return
            
            # Конвертация в формат OpenCV
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Изменение размера для отображения на canvas (150x150)
            img_resized = cv2.resize(img, (150, 150))
            
            # Конвертация в формат Tkinter
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            
            # Очистка canvas и отображение изображения
            self.trigger_preview_canvas.delete("all")
            self.trigger_preview_canvas.create_image(0, 0, anchor='nw', image=img_tk)
            
            # Сохранение ссылки на изображение
            self.trigger_preview_image = img_tk
            
            # Рисование красной рамки вокруг области
            self.trigger_preview_canvas.create_rectangle(
                0, 0, 150, 150,
                outline='red', width=2
            )
            
            # Рисование красной области 3x3 вокруг центра
            # квадрат 3x3 в координатах canvas (центр 75,75)
            self.trigger_preview_canvas.create_rectangle(
                74, 74, 76, 76,
                outline='red', width=2
            )
            center_dot_size = 1
            self.trigger_preview_canvas.create_oval(
                75 - center_dot_size, 75 - center_dot_size,
                75 + center_dot_size, 75 + center_dot_size,
                fill='red', outline='red'
            )
            
            # Добавление информации о центре и области захвата
            info_text = f"Центр: ({center_x}, {center_y}) | Захват: 3x3 пикселя @150 FPS"
            self.trigger_preview_canvas.create_text(
                75, 130,
                text=info_text, fill='white', font=('Arial', 8, 'bold')
            )
            
            
        except Exception as e:
            self.log_message(f"Ошибка обновления предварительного просмотра: {e}")
            import traceback
            error_details = traceback.format_exc()
            self.log_message(f"Детали ошибки: {error_details}")
    
    def start_trigger_bot(self):
        """Запуск триггер-бота"""
        if self.trigger_bot_running:
            self.log_message("Триггер-бот уже запущен")
            return
            
        try:
            # Обновление настроек
            self.save_trigger_settings()
            
            # Проверяем, что все необходимые настройки загружены
            if not self.settings.get('trigger_key'):
                raise ValueError("Не выбрана клавиша триггера")
            
            # Дополнительная проверка корректности настроек
            tolerance = int(self.settings.get('color_tolerance', 15))
            click_duration = float(self.settings.get('click_duration', 0.1))
            
            if tolerance < 1 or tolerance > 100:
                raise ValueError(f"Некорректная погрешность: {tolerance}%")
            if click_duration < 0.01 or click_duration > 1.0:
                raise ValueError(f"Некорректная длительность: {click_duration}")
            
            self.log_message(f"Проверка настроек: область=3x3 (фиксированно), погрешность={tolerance}%, длительность={click_duration}s")
            
            # Запуск в отдельном потоке
            self.trigger_bot_running = True
            self.trigger_status_label.config(text="▶️ Статус: Работает")
            
            # Запуск потока триггер-бота
            self.trigger_thread = threading.Thread(target=self.trigger_bot_loop, daemon=True)
            self.trigger_thread.start()
            
            # Запуск автообновления предварительного просмотра
            self.start_trigger_preview_update()
            
            self.log_message("Триггер-бот запущен")
            
        except Exception as e:
            self.trigger_bot_running = False
            self.trigger_status_label.config(text="⏹️ Статус: Ошибка")
            self.log_message(f"Ошибка запуска триггер-бота: {e}")
            # Показываем детальную ошибку пользователю
            import traceback
            error_details = traceback.format_exc()
            self.log_message(f"Детали ошибки: {error_details}")
    
    def stop_trigger_bot(self):
        """Остановка триггер-бота"""
        if not self.trigger_bot_running:
            self.log_message("Триггер-бот уже остановлен")
            return
            
        try:
            self.trigger_bot_running = False
            self.trigger_status_label.config(text="⏹️ Статус: Остановлен")
            
            # Предпросмотр оставляем активным для постоянной работы
            
            self.log_message("Триггер-бот остановлен")
            
        except Exception as e:
            self.log_message(f"Ошибка остановки триггер-бота: {e}")
    
    def trigger_bot_loop(self):
        """Основной цикл триггер-бота"""
        try:
            import pyautogui
            import keyboard
            import time
            # Убираем внутреннюю паузу PyAutoGUI и отключаем failsafe для минимальной задержки
            try:
                pyautogui.PAUSE = 0
                pyautogui.FAILSAFE = False
            except Exception:
                pass
            # Пытаемся использовать сверхбыстрый захват экрана через mss
            try:
                from mss import mss
                use_mss = True
            except Exception:
                use_mss = False
            
            # Получение настроек
            trigger_key = self.settings.get('trigger_key', 'shift')
            click_key = self.settings.get('click_key', 'left')
            radius = 1  # Фиксированный радиус = 1 пиксель
            tolerance = int(self.settings.get('color_tolerance', 15))
            click_duration = self.settings.get('click_duration', 0.1)
            
            # Проверяем настройки
            if not trigger_key:
                raise ValueError("Клавиша триггера не настроена")
            
            # Получение центра экрана из настроек пользователя
            screen_width = self.settings.get('screen_width', 1920)
            screen_height = self.settings.get('screen_height', 1080)
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # Проверяем, что радиус не превышает размер экрана
            if radius > min(screen_width, screen_height) // 2:
                radius = min(screen_width, screen_height) // 2
                self.log_message(f"Радиус уменьшен до {radius}px для соответствия размеру экрана")
            
            # Для захвата используем формат (left, top, width, height)
            # Квадрат 3x3 пикселя вокруг центра экрана
            region = (center_x - 1, center_y - 1, 3, 3)
            monitor = {
                'left': region[0],
                'top': region[1],
                'width': region[2],
                'height': region[3]
            }
            
            self.log_message(f"Триггер-бот активен. Клавиша триггера: {trigger_key}, Клавиша клика: {click_key}, Область: 3x3 (фиксированно), Погрешность: {int(tolerance)}%, Центр: ({center_x}, {center_y})")
            self.log_message(f"Захват цвета: 3x3 пикселя вокруг центра экрана")
            
            # Переменные для отслеживания состояния
            saved_color = None
            trigger_was_pressed = False
            clicked = False
            
            # Целевая частота ~150 FPS
            target_frame_time = 1.0 / 150.0
            # Инициализируем mss один раз (если доступен)
            sct = mss() if use_mss else None

            while self.trigger_bot_running:
                try:
                    loop_start = time.perf_counter()
                    if keyboard.is_pressed(trigger_key):
                        if not trigger_was_pressed:
                            # Первое нажатие - запоминаем цвет (захват региона 3x3)
                            if use_mss and sct is not None:
                                shot = sct.grab(monitor)
                                arr = np.array(shot)  # BGRA
                                rgb = arr[:, :, :3][:, :, ::-1]  # to RGB
                                avg = rgb.mean(axis=(0, 1))
                                saved_color = tuple(int(v) for v in avg)
                            else:
                                img = pyautogui.screenshot(region=region)
                                saved_color = self.get_average_color(img, 1, 1, radius)
                            trigger_was_pressed = True
                            clicked = False
                            self.log_message(f"Цвет запомнен: {saved_color}")
                        else:
                            # Клавиша зажата - проверяем изменение цвета (захват региона 3x3)
                            if use_mss and sct is not None:
                                shot = sct.grab(monitor)
                                arr = np.array(shot)  # BGRA
                                rgb = arr[:, :, :3][:, :, ::-1]
                                avg = rgb.mean(axis=(0, 1))
                                current_color = tuple(int(v) for v in avg)
                            else:
                                img = pyautogui.screenshot(region=region)
                                current_color = self.get_average_color(img, 1, 1, radius)
                            
                            if self.colors_are_different(current_color, saved_color, tolerance) and not clicked:
                                # Цвет изменился - выполняем действие (без перемещения мыши, с заданной длительностью)
                                self.perform_trigger_action(click_key, click_duration)
                                self.log_message(f"Триггер сработал! Действие: {click_key}")
                                clicked = True
                            elif not self.colors_are_different(current_color, saved_color, tolerance):
                                clicked = False
                    else:
                        # Клавиша отпущена - сбрасываем состояние
                        saved_color = None
                        trigger_was_pressed = False
                        clicked = False
                    
                    # Регулируем задержку под 150 FPS
                    elapsed = time.perf_counter() - loop_start
                    sleep_time = target_frame_time - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                except Exception as e:
                    self.log_message(f"Ошибка в цикле триггер-бота: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            self.log_message(f"Критическая ошибка триггер-бота: {e}")
            import traceback
            error_details = traceback.format_exc()
            self.log_message(f"Детали ошибки: {error_details}")
            self.trigger_bot_running = False
            # Обновляем статус в главном потоке
            self.root.after(0, lambda: self.trigger_status_label.config(text="⏹️ Статус: Ошибка"))
    
    def get_average_color(self, img, x, y, radius):
        """Получение среднего цвета в квадрате 3x3 по центру"""
        try:
            # Квадрат 3x3 вокруг точки (x, y)
            left = max(0, x - 1)
            top = max(0, y - 1)
            right = min(img.width, x + 2)  # +2, потому что правая граница исключительная
            bottom = min(img.height, y + 2)
            region = img.crop((left, top, right, bottom))
            arr = np.array(region)
            avg = arr.mean(axis=(0, 1))
            return tuple(int(v) for v in avg)
        except Exception as e:
            self.log_message(f"Ошибка получения цвета: {e}")
            return (0, 0, 0)
    
    def colors_are_different(self, color1, color2, tolerance_percent):
        """Проверка, отличаются ли цвета на заданный процент (рабочий метод из test)"""
        try:
            if tolerance_percent <= 0:
                return color1 != color2
            # Быстрая векторная проверка порога на основе L1-нормы
            c1r, c1g, c1b = color1
            c2r, c2g, c2b = color2
            diff = abs(c1r - c2r) + abs(c1g - c2g) + abs(c1b - c2b)
            # Порог: 3 канала по 255 каждый, масштабируем по проценту
            threshold = int(3 * 255 * (tolerance_percent / 100.0))
            return diff > threshold
        except Exception:
            # Фоллбек на старую поканальную проверку
            if tolerance_percent == 0:
                return color1 != color2
            for i in range(3):
                max_value = 255
                tolerance = max_value * tolerance_percent / 100
                if abs(color1[i] - color2[i]) > tolerance:
                    return True
            return False
    
    def color_difference(self, color1, color2):
        """Вычисление разности между цветами"""
        try:
            import numpy as np
        except Exception:
            # Без numpy используем простой L1 как фоллбек
            try:
                dr = abs(color1[0] - color2[0])
                dg = abs(color1[1] - color2[1])
                db = abs(color1[2] - color2[2])
                return float(dr + dg + db)
            except Exception:
                return 0.0
        
        # Проверяем входные данные
        if not color1 or not color2:
            return 0.0
        
        # Преобразуем в numpy массивы
        c1 = np.array(color1, dtype=float)
        c2 = np.array(color2, dtype=float)
        
        # Проверяем, что массивы имеют правильную форму
        if c1.shape != (3,) or c2.shape != (3,):
            self.log_message(f"Неверная форма цвета: c1={c1.shape}, c2={c2.shape}")
            return 0.0
        
        # Проверяем на NaN и Inf
        if np.any(np.isnan(c1)) or np.any(np.isnan(c2)) or np.any(np.isinf(c1)) or np.any(np.isinf(c2)):
            self.log_message("Обнаружены недопустимые значения цвета")
            return 0.0
        
        # Вычисляем разность (L2-норма)
        diff = np.linalg.norm(c1 - c2)
        
        # Проверяем результат
        if np.isnan(diff) or np.isinf(diff):
            self.log_message("Результат вычисления разности недопустим")
            return 0.0
        
        return float(diff)
            
    def perform_trigger_action(self, click_key: str, click_duration: float) -> None:
        """Быстрое выполнение действия триггера без перемещения курсора.
        Для мыши — удержание/клик с длительностью, для клавиатуры — press.
        """
        try:
            import pyautogui
            import time
            mode = self.settings.get('output_mode', 'virtual')
            if mode == 'hardware' and self.hardware_serial:
                # Протокол: CLICK <btn> <ms>\n  где btn=L|R|M
                btn = 'L' if click_key == 'left' else 'R' if click_key == 'right' else 'M'
                ms = max(0, int(click_duration * 1000))
                try:
                    self.hardware_serial.write(f"CLICK {btn} {ms}\n".encode('ascii', 'ignore'))
                    self.hardware_serial.flush()
                except Exception:
                    pass
            elif mode == 'interception':
                try:
                    import subprocess, sys, os
                    map_btn = 'L' if click_key == 'left' else ('R' if click_key == 'right' else 'M')
                    cli_py = os.path.join(os.getcwd(), 'interception_cli.py')
                    if os.path.exists(cli_py):
                        subprocess.run([sys.executable, cli_py, 'click', map_btn, str(ms)], timeout=0.4)
                    else:
                        subprocess.run(['interception-cli.exe', 'click', map_btn, str(ms)], timeout=0.4)
                except Exception:
                    if click_key in ['left', 'right', 'middle']:
                        if click_key == 'left':
                            pyautogui.mouseDown(button='left')
                            if click_duration > 0:
                                time.sleep(click_duration)
                            pyautogui.mouseUp(button='left')
                        elif click_key == 'right':
                            pyautogui.mouseDown(button='right')
                            if click_duration > 0:
                                time.sleep(click_duration)
                            pyautogui.mouseUp(button='right')
                        elif click_key == 'middle':
                            pyautogui.mouseDown(button='middle')
                            if click_duration > 0:
                                time.sleep(click_duration)
                            pyautogui.mouseUp(button='middle')
                    else:
                        pyautogui.press(click_key)
            else:
                if click_key in ['left', 'right', 'middle']:
                    if click_key == 'left':
                        pyautogui.mouseDown(button='left')
                        if click_duration > 0:
                            time.sleep(click_duration)
                        pyautogui.mouseUp(button='left')
                    elif click_key == 'right':
                        pyautogui.mouseDown(button='right')
                        if click_duration > 0:
                            time.sleep(click_duration)
                        pyautogui.mouseUp(button='right')
                    elif click_key == 'middle':
                        pyautogui.mouseDown(button='middle')
                        if click_duration > 0:
                            time.sleep(click_duration)
                        pyautogui.mouseUp(button='middle')
                else:
                    pyautogui.press(click_key)
        except Exception as e:
            self.log_message(f"Ошибка выполнения действия триггера: {e}")
        
            self.log_message(f"Ошибка вычисления разности цветов: {e}")
            return 0
    
    def get_color_percentage_threshold(self, initial_color, tolerance_percent):
        """Вычисление порога погрешности в процентах от начального цвета"""
        try:
            import numpy as np
            
            # Проверяем входные данные
            if not initial_color or tolerance_percent <= 0:
                return 0
            
            # Преобразуем в numpy массив
            color = np.array(initial_color, dtype=float)
            
            # Вычисляем среднюю яркость цвета
            brightness = np.mean(color)
            
            # Если яркость слишком низкая, используем минимальный порог
            if brightness < 10:
                brightness = 10
            
            # Вычисляем порог как процент от яркости
            threshold = (brightness * tolerance_percent) / 100.0
            
            return float(threshold)
            
        except Exception as e:
            self.log_message(f"Ошибка вычисления порога погрешности: {e}")
            return 0
    

    
    def train_model(self):
        """Обучение YOLOv8 на размеченных данных (Labels + Data_Photo)."""
        try:
            import os, json, glob, yaml, shutil
            from ultralytics import YOLO
            # Подготовка безопасной загрузки весов для PyTorch 2.6+
            try:
                import torch
                from ultralytics.nn.tasks import DetectionModel
                if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'add_safe_globals'):
                    torch.serialization.add_safe_globals([DetectionModel])
            except Exception:
                torch = None
            from PIL import Image

            # Определяем папки исходя из выбранного пользователем датасета
            base_ds = getattr(self, 'training_dataset_dir', os.getcwd())
            labels_dir = os.path.join(base_ds, 'Labels')
            images_dir = os.path.join(base_ds, 'Data_Photo')
            yolo_ds = os.path.join(os.getcwd(), 'yolo_dataset')
            images_out = os.path.join(yolo_ds, 'images')
            labels_out = os.path.join(yolo_ds, 'labels')
            for split in ['train', 'val']:
                os.makedirs(os.path.join(images_out, split), exist_ok=True)
                os.makedirs(os.path.join(labels_out, split), exist_ok=True)

            label_files = sorted(glob.glob(os.path.join(labels_dir, '*.json')))
            if not label_files:
                messagebox.showwarning("YOLO", "Нет размеченных данных в папке Labels выбранного датасета")
                return

            # Классы
            names = ['Enemy_Head', 'Enemy_Body', 'Friendly_Head', 'Friendly_Body']
            name_to_id = {n: i for i, n in enumerate(names)}

            # Формируем датасет (простое разделение 90/10)
            split_idx = max(1, int(len(label_files) * 0.9))
            train_files = label_files[:split_idx]
            val_files = label_files[split_idx:]

            def process_split(files, split):
                for lf in files:
                    with open(lf, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    img_name = data['image']
                    src_img = os.path.join(images_dir, img_name)
                    if not os.path.exists(src_img):
                        continue
                    # Копируем изображение
                    dst_img = os.path.join(images_out, split, img_name)
                    shutil.copyfile(src_img, dst_img)
                    # Создаём yolo label
                    im = Image.open(src_img).convert('RGB')
                    w, h = im.size
                    yolo_lines = []
                    for b in data.get('boxes', []):
                        cls = b.get('label', 'None')
                        if cls not in name_to_id:
                            continue
                        x1, y1, x2, y2 = b['x1'], b['y1'], b['x2'], b['y2']
                        cx = (x1 + x2) / 2.0 / w
                        cy = (y1 + y2) / 2.0 / h
                        bw = (x2 - x1) / w
                        bh = (y2 - y1) / h
                        cls_id = name_to_id[cls]
                        yolo_lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
                    lbl_name = os.path.splitext(img_name)[0] + '.txt'
                    with open(os.path.join(labels_out, split, lbl_name), 'w', encoding='utf-8') as f:
                        f.write('\n'.join(yolo_lines))

            process_split(train_files, 'train')
            process_split(val_files, 'val')

            # Создаём data.yaml
            data_yaml = {
                'path': yolo_ds,
                'train': 'images/train',
                'val': 'images/val',
                'names': {i: n for i, n in enumerate(names)}
            }
            with open(os.path.join(yolo_ds, 'data.yaml'), 'w', encoding='utf-8') as f:
                yaml.safe_dump(data_yaml, f, allow_unicode=True)

            # Обучаем YOLOv8n (можно сменить на s/m/l при необходимости)
            # Поддержка PyTorch 2.6: держим патч weights_only=False на всём цикле создания модели и training
            model = None
            if torch is not None:
                # Добавляем часто используемые классы в allowlist
                try:
                    import torch.nn as nn
                    allow = []
                    if hasattr(nn.modules.container, 'Sequential'):
                        allow.append(nn.modules.container.Sequential)
                    if allow and hasattr(torch, 'serialization') and hasattr(torch.serialization, 'add_safe_globals'):
                        torch.serialization.add_safe_globals(allow)
                except Exception:
                    pass
                orig_torch_load = torch.load
                def _patched_load(*a, **k):
                    try:
                        k.setdefault('weights_only', False)
                    except Exception:
                        pass
                    return orig_torch_load(*a, **k)
                torch.load = _patched_load
                try:
                    try:
                        model = YOLO('yolov8n.pt')
                    except Exception:
                        model = YOLO('yolov8n.yaml')
                    results = model.train(data=os.path.join(yolo_ds, 'data.yaml'), epochs=50, imgsz=640)
                finally:
                    torch.load = orig_torch_load
            else:
                try:
                    model = YOLO('yolov8n.pt')
                except Exception:
                    model = YOLO('yolov8n.yaml')
                results = model.train(data=os.path.join(yolo_ds, 'data.yaml'), epochs=50, imgsz=640)

            # Сохраняем лучшую модель под выбранным именем
            model_root = self.settings.get('model_path', 'models/')
            os.makedirs(model_root, exist_ok=True)
            best_path = os.path.join(results.save_dir, 'weights', 'best.pt')
            # Имя модели берём из поля ввода; если пусто — используем yolov8_best
            name = None
            try:
                name = self.model_name_var.get().strip() if self.model_name_var else ''
            except Exception:
                name = ''
            if not name:
                name = 'yolov8_best'
            # Сохраняем PT по пути models/<name>.pt и дублируем в models/<name>/best.pt
            final_file = f"{name}.pt"
            final_path = os.path.join(model_root, final_file)
            shutil.copyfile(best_path, final_path)
            # Дополнительно создаём папку под именем модели
            model_named_dir = os.path.join(model_root, name)
            os.makedirs(model_named_dir, exist_ok=True)
            shutil.copyfile(best_path, os.path.join(model_named_dir, 'best.pt'))
            self.yolo_model_path = final_path
            # Автозагрузка обученной модели для предпросмотра
            try:
                if torch is not None:
                    orig_torch_load = torch.load
                    def _patched_load2(*a, **k):
                        try:
                            k.setdefault('weights_only', False)
                        except Exception:
                            pass
                        return orig_torch_load(*a, **k)
                    torch.load = _patched_load2
                    # Разрешаем и Sequential на всякий случай
                    try:
                        import torch.nn as nn
                        if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'add_safe_globals'):
                            torch.serialization.add_safe_globals([nn.modules.container.Sequential])
                    except Exception:
                        pass
                    self.yolo = YOLO(final_path)
                else:
                    self.yolo = YOLO(final_path)
            except Exception:
                self.yolo = None
            finally:
                if torch is not None:
                    torch.load = orig_torch_load
            # Обновляем список моделей и выбираем новую в интерфейсе
            try:
                self.refresh_models_list()
                if hasattr(self, 'model_combobox'):
                    base = os.path.basename(final_path)
                    if base in getattr(self, '_models_map', {}):
                        self.model_combobox.set(base)
                        self.on_model_selected()
            except Exception:
                pass
            self.log_message(f"YOLOv8 обучена. Модель: {final_path}")
            messagebox.showinfo("YOLO", f"Обучение завершено. Модель: {final_path}")
        except Exception as e:
            self.log_message(f"Ошибка обучения YOLO: {e}")
            messagebox.showerror("YOLO", f"Ошибка обучения: {e}")

    def load_yolo_model(self):
        """Загрузка уже обученной модели YOLOv8 (.pt) из выбранного элемента комбобокса."""
        try:
            from ultralytics import YOLO
            # PyTorch 2.6+: разрешаем глобалы Ultralytics для безопасной загрузки весов
            try:
                import torch
                from ultralytics.nn.tasks import DetectionModel
                # Глобально добавляем allowlist
                if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'add_safe_globals'):
                    torch.serialization.add_safe_globals([DetectionModel])
            except Exception:
                DetectionModel = None  # fallback

            # Получаем выбранную модель из комбобокса
            selected_name = ''
            if hasattr(self, 'model_combobox'):
                selected_name = self.model_combobox.get()
            if not selected_name:
                messagebox.showwarning("YOLO", "Выберите модель в списке перед загрузкой")
                return
            path = None
            if hasattr(self, '_models_map') and selected_name in self._models_map:
                path = self._models_map[selected_name]
            else:
                # Фоллбек на папку models
                import os
                model_dir = self.settings.get('model_path', 'models/')
                candidate = os.path.join(model_dir, selected_name)
                if os.path.isfile(candidate):
                    path = candidate
            if not path:
                messagebox.showerror("YOLO", "Выбранный файл модели не найден")
                return

            try:
                # Предпочитаем контекстный менеджер safe_globals на время загрузки
                import torch
                # Временный патч torch.load, чтобы всегда использовать weights_only=False (PyTorch 2.6+)
                orig_torch_load = torch.load
                def _patched_load(*a, **k):
                    try:
                        k.setdefault('weights_only', False)
                    except Exception:
                        pass
                    return orig_torch_load(*a, **k)
                torch.load = _patched_load
                try:
                    if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'safe_globals') and DetectionModel is not None:
                        with torch.serialization.safe_globals([DetectionModel]):
                            self.yolo = YOLO(path)
                    else:
                        self.yolo = YOLO(path)
                finally:
                    # Возвращаем оригинальную функцию загрузки
                    torch.load = orig_torch_load
            except Exception:
                # Последняя попытка: вновь добавить allowlist и повторить
                try:
                    import torch
                    from ultralytics.nn.tasks import DetectionModel as _DM
                    if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'add_safe_globals'):
                        torch.serialization.add_safe_globals([_DM])
                    if hasattr(torch, 'serialization') and hasattr(torch.serialization, 'safe_globals'):
                        with torch.serialization.safe_globals([_DM]):
                            self.yolo = YOLO(path)
                    else:
                        self.yolo = YOLO(path)
                except Exception as e2:
                    raise e2
            self.yolo_model_path = path
            self.model_trained = True
            # Обновляем надпись о выбранной модели
            try:
                base = os.path.basename(path)
                if hasattr(self, 'selected_model_label'):
                    self.selected_model_label.config(text=f"Файл модели: {base}")
            except Exception:
                pass
            self.log_message(f"YOLOv8 модель загружена: {path}")
            messagebox.showinfo("YOLO", "Модель загружена")
        except Exception as e:
            self.log_message(f"Ошибка загрузки YOLO модели: {e}")
            messagebox.showerror("YOLO", f"Ошибка загрузки: {e}")
    
    def start_detection(self):
        self.detection_active = True
        self.vision_status_label.config(text="▶️ Статус: Работает")
        self.log_message("Обнаружение запущено")
        # При запуске обнаружения включаем автообновление предпросмотра
        try:
            self.start_vision_preview_update()
        except Exception:
            pass
    
    def stop_detection(self):
        self.detection_active = False
        self.vision_status_label.config(text="⏹️ Статус: Остановлено")
        self.log_message("Обнаружение остановлено")
        try:
            self.stop_vision_preview_update()
        except Exception:
            pass
    
    def start_aim(self):
        self.aim_active = True
        self.aim_status_label.config(text="▶️ Статус: Работает")
        # Сохраняем параметры автонаводки
        try:
            self.settings['aim_speed'] = float(self.aim_speed_entry2.get())
            self.settings['aim_accuracy_radius'] = int(float(self.aim_accuracy_entry.get()))
            self.settings['aim_target'] = self.aim_target_var.get()
            self.settings['aim_key'] = self.aim_key_var.get()
        except Exception:
            pass
        # Запуск цикла автонаводки
        try:
            if not hasattr(self, 'aim_thread') or not self.aim_thread or not self.aim_thread.is_alive():
                self.aim_thread = threading.Thread(target=self.aim_loop, daemon=True)
                self.aim_thread.start()
        except Exception:
            pass
        try:
            self.start_aim_preview_update()
        except Exception:
            pass
        try:
            self.log_message("Авто-наводка запущена")
        except Exception:
            pass
    
    def stop_aim(self):
        self.aim_active = False
        self.aim_status_label.config(text="⏹️ Статус: Остановлена")
        try:
            self.stop_aim_preview_update()
        except Exception:
            pass
        try:
            self.log_message("Авто-наводка остановлена")
        except Exception:
            pass
    
    def select_aim_key(self):
        """Выбор клавиши для автонаводки"""
        try:
            key_window = tk.Toplevel(self.root)
            key_window.title("Выбор клавиши автонаводки")
            key_window.geometry("400x250")
            key_window.resizable(False, False)
            key_window.transient(self.root)
            key_window.grab_set()

            key_window.update_idletasks()
            x = (key_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (key_window.winfo_screenheight() // 2) - (250 // 2)
            key_window.geometry(f'400x250+{x}+{y}')

            instruction = ttk.Label(key_window, text="Нажмите клавишу для автонаводки", font=('Segoe UI', 11), justify='center')
            instruction.pack(pady=20)

            selected_key_label = ttk.Label(key_window, text="Ожидание нажатия...", font=('Segoe UI', 14, 'bold'), foreground='blue')
            selected_key_label.pack(pady=10)

            cancel_button = ttk.Button(key_window, text="Отмена", command=key_window.destroy)
            cancel_button.pack(pady=10)

            def on_key_press(event):
                key_name = self.convert_key_name(event.keysym)
                display_name = self.get_display_key_name(event.keysym)
                selected_key_label.config(text=f"Выбрано: {display_name}")
                self.aim_key_var.set(key_name)
                self.aim_key_display.config(text=display_name)
                key_window.after(500, key_window.destroy)

            key_window.bind('<Key>', on_key_press)
            key_window.focus_set()
        except Exception as e:
            self.log_message(f"Ошибка выбора клавиши автонаводки: {e}")

    def connect_hardware_mouse(self):
        """Подключение к аппаратной мыши через COM-порт (HID-бридж на микроконтроллере)."""
        try:
            import serial
        except Exception as e:
            self.log_message(f"pyserial не установлен: {e}")
            messagebox.showerror("Hardware", "Установите pyserial: pip install pyserial")
            return
        try:
            port = self.hw_port_entry.get().strip() if hasattr(self, 'hw_port_entry') else self.settings.get('hardware_port', '')
            baud = int(self.hw_baud_entry.get()) if hasattr(self, 'hw_baud_entry') else int(self.settings.get('hardware_baud', 115200))
            if not port:
                messagebox.showwarning("Hardware", "Укажите COM-порт устройства (например, COM4)")
                return
            if self.hardware_serial:
                try:
                    self.hardware_serial.close()
                except Exception:
                    pass
            self.hardware_serial = serial.Serial(port=port, baudrate=baud, timeout=0)
            self.settings['hardware_port'] = port
            self.settings['hardware_baud'] = baud
            self.settings['output_mode'] = self.output_mode_var.get() if hasattr(self, 'output_mode_var') else 'hardware'
            self.save_settings()
            self.log_message(f"Подключено к аппаратной мыши: {port} @ {baud}")
            try:
                self.hardware_serial.write(b"HELLO\n")
                self.hardware_serial.flush()
            except Exception:
                pass
        except Exception as e:
            self.log_message(f"Ошибка подключения к аппаратной мыши: {e}")
            messagebox.showerror("Hardware", f"Ошибка подключения: {e}")

    def open_interception_install_help(self):
        """Показывает инструкцию по быстрой установке драйвера Interception (низкоуровневый ввод)."""
        try:
            msg = (
                "Interception — легкий драйвер фильтра клавиатуры/мыши.\n\n"
                "Шаги установки (≈1–2 минуты):\n"
                "1) Скачайте архив releases: https://github.com/oblitum/Interception/releases\n"
                "2) Распакуйте, откройте cmd от администратора в папке /command_line\n"
                "3) Выполните: install-interception.exe /install\n"
                "4) Перезагрузите ПК.\n\n"
                "В программе выберите режим 'interception' — будет использоваться low-level ввод без pyautogui."
            )
            messagebox.showinfo("Interception", msg)
        except Exception:
            pass

    def aim_loop(self):
        """Главный цикл авто-наводки: двигает мышь к центру выбранной цели при зажатой клавише."""
        try:
            import pyautogui
            import time
            import keyboard
            import numpy as np
            import cv2
        except Exception as e:
            self.log_message(f"Ошибка импорта для автонаводки: {e}")
            return

        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        last_time = time.perf_counter()
        while self.aim_active:
            now = time.perf_counter()
            dt = max(1e-3, now - last_time)
            last_time = now

            aim_key = self.settings.get('aim_key', 'alt')
            if not keyboard.is_pressed(aim_key):
                time.sleep(0.01)
                continue

            # Параметры
            speed_px_s = float(self.settings.get('aim_speed', 100.0))
            accuracy_radius = int(self.settings.get('aim_accuracy_radius', 10))
            target_label = self.settings.get('aim_target', 'Enemy_Head')

            # Центр экрана (куда хотим свести прицел)
            screen_w = int(self.settings.get('screen_width', 1920))
            screen_h = int(self.settings.get('screen_height', 1080))
            center_x = screen_w // 2
            center_y = screen_h // 2

            # Получаем текущие детекции через YOLO
            target_center = None
            try:
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                if hasattr(self, 'yolo') and self.yolo is not None:
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.yolo.predict(img_rgb, imgsz=img_rgb.shape[0], verbose=False)
                    for r in results:
                        if not hasattr(r, 'boxes') or r.boxes is None:
                            continue
                        for b in r.boxes:
                            try:
                                cls_id = int(b.cls[0].item()) if hasattr(b, 'cls') else -1
                                label = str(self.yolo.names.get(cls_id, cls_id))
                                if label != target_label:
                                    continue
                                x1, y1, x2, y2 = b.xyxy[0].tolist()
                                cx = int((x1 + x2) / 2)
                                cy = int((y1 + y2) / 2)
                                target_center = (cx, cy)
                                break
                            except Exception:
                                continue
                        if target_center is not None:
                            break
            except Exception:
                pass

            if target_center is None:
                time.sleep(0.01)
                continue

            dx = target_center[0] - center_x
            dy = target_center[1] - center_y
            dist = (dx**2 + dy**2) ** 0.5
            if dist <= max(1, accuracy_radius):
                time.sleep(0.005)
                continue

            max_step = speed_px_s * dt
            if dist <= max_step:
                step_x, step_y = dx, dy
            else:
                k = max_step / dist
                step_x = dx * k
                step_y = dy * k

            try:
                mode = self.settings.get('output_mode', 'virtual')
                if mode == 'hardware' and self.hardware_serial:
                    # Протокол: MOVE dx dy\n
                    self.hardware_serial.write(f"MOVE {int(step_x)} {int(step_y)}\n".encode('ascii', 'ignore'))
                    self.hardware_serial.flush()
                elif mode == 'interception':
                    # Попытка через встроенный Python-обертку или внешнюю CLI
                    try:
                        import subprocess, sys, os
                        cli_py = os.path.join(os.getcwd(), 'interception_cli.py')
                        if os.path.exists(cli_py):
                            subprocess.run([sys.executable, cli_py, 'move', str(int(step_x)), str(int(step_y))], timeout=0.3)
                        else:
                            subprocess.run(['interception-cli.exe', 'move', str(int(step_x)), str(int(step_y))], timeout=0.3)
                    except Exception:
                        # Фоллбек на pyautogui
                        pyautogui.moveRel(int(step_x), int(step_y), duration=0)
                else:
                    pyautogui.moveRel(int(step_x), int(step_y), duration=0)
            except Exception:
                pass

            time.sleep(0.001)
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            # Обновление настроек из полей
            self.settings['screen_width'] = int(self.width_entry.get())
            self.settings['screen_height'] = int(self.height_entry.get())
            
            # Проверяем существование элементов триггер-бота
            if hasattr(self, 'trigger_key_var'):
                self.settings['trigger_key'] = self.trigger_key_var.get()

            # Точкой истинны для триггер-бота является ползунок на вкладке триггера
            if hasattr(self, 'trigger_tolerance_scale'):
                self.settings['color_tolerance'] = int(self.trigger_tolerance_scale.get())
            elif hasattr(self, 'tolerance_scale'):
                # Фоллбек на общий ползунок
                self.settings['color_tolerance'] = int(self.tolerance_scale.get())
            if hasattr(self, 'duration_entry'):
                self.settings['click_duration'] = float(self.duration_entry.get())
            
            # Настройки автонаводки
            if hasattr(self, 'aim_speed_entry2'):
                self.settings['aim_speed'] = float(self.aim_speed_entry2.get())
            if hasattr(self, 'aim_accuracy_entry'):
                self.settings['aim_accuracy_radius'] = int(float(self.aim_accuracy_entry.get()))
            if hasattr(self, 'aim_target_var'):
                self.settings['aim_target'] = self.aim_target_var.get()
            if hasattr(self, 'aim_key_var'):
                self.settings['aim_key'] = self.aim_key_var.get()
            if hasattr(self, 'output_mode_var'):
                self.settings['output_mode'] = self.output_mode_var.get()
            if hasattr(self, 'hw_port_entry'):
                self.settings['hardware_port'] = self.hw_port_entry.get()
            if hasattr(self, 'hw_baud_entry'):
                try:
                    self.settings['hardware_baud'] = int(self.hw_baud_entry.get())
                except Exception:
                    pass
            if hasattr(self, 'body_part_var'):
                self.settings['target_body_part'] = self.body_part_var.get()
            if hasattr(self, 'team_var'):
                self.settings['team_to_detect'] = self.team_var.get()
            if hasattr(self, 'theme_var'):
                self.settings['theme'] = self.theme_var.get()
            
            # Сохранение в файл
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            self.log_message("Настройки сохранены")
            messagebox.showinfo("Успех", "Настройки сохранены!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверное значение: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def load_settings(self):
        """Загрузка настроек"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                    self.populate_settings_fields()
                    self.log_message("Настройки загружены")
        except Exception as e:
            self.log_message(f"Ошибка загрузки настроек: {e}")
    
    def run(self):
        """Запуск приложения"""
        self.start_time = time.time()
        self.log_message("Приложение запущено")
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernGameAssistant()
    app.run() 