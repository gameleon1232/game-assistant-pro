# Game Assistant Pro - CS2 Helper
# PowerShell скрипт для запуска

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Game Assistant Pro - CS2 Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Запуск программы..." -ForegroundColor Green
Write-Host ""

try {
    python main_modern.py
}
catch {
    Write-Host "Ошибка запуска: $_" -ForegroundColor Red
    Write-Host "Попробуйте запустить: py main_modern.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Программа завершена. Нажмите любую клавишу для выхода..." -ForegroundColor Yellow
Read-Host 