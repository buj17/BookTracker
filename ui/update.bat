@echo off

for %%a in (*.ui) do (
  pyuic6 "%%a" -o "%%~na_ui.py"
  echo "Файл %%a преобразован в %%~na_ui.py"
)

pause