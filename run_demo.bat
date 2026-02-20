@echo off
REM Lanceur pour GoldArmyArgent Demo
REM Utilise directement Python 3.14 sans passer par les alias corrompus

SET PYTHON_EXE=C:\Users\yayzo\AppData\Local\Python\pythoncore-3.14-64\python.exe

echo ======================================================================
echo  GoldArmyArgent - Mode Demo (Sans dependances)
echo ======================================================================
echo.

REM Vérifier si Python existe
if not exist "%PYTHON_EXE%" (
    echo ERREUR: Python 3.14 non trouve a: %PYTHON_EXE%
    echo.
    echo Cherchons Python...
    where python
    pause
    exit /b 1
)

echo Python trouve: %PYTHON_EXE%
echo.

REM Lancer le mode interactif par défaut
"%PYTHON_EXE%" demo.py interactive

pause
