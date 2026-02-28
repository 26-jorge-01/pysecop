@echo off
SETLOCAL

REM ——————————————————————————————
REM Asegura que exista la carpeta local data\
REM ——————————————————————————————
if not exist "%cd%\data" (
    mkdir "%cd%\data"
)

REM ——————————————————————————————
REM BUILD
REM ——————————————————————————————
IF "%1"=="build" (
    docker build --network=host --progress=plain -t pysecop-starter .
    GOTO :EOF
)

REM ——————————————————————————————
REM BUILD SIN CACHÉ
REM ——————————————————————————————
IF "%1"=="rebuild" (
    docker build --no-cache -t pysecop-starter .
    GOTO :EOF
)

REM ——————————————————————————————
REM COVERAGE (HTML + XML + ZIP EN RAÍZ)
REM ——————————————————————————————
@echo off
setlocal EnableExtensions

IF "%1"=="coverage" (
    IF NOT EXIST "htmlcov" (
        echo No se encontro la carpeta htmlcov\. Revisa tu configuracion de pytest/coverage.
        GOTO :EOF
    )

    rem Opción 1: usando echo( (recomendado)
    echo Eliminando zip anterior
    IF EXIST "coverage-html.zip" del /f /q "coverage-html.zip"

    echo Comprimiendo reporte HTML en la raiz...
    powershell -NoProfile -Command ^
        "Compress-Archive -Path 'htmlcov\*' -DestinationPath 'coverage-html.zip' -Force" ^
    || (
        echo Error al comprimir con PowerShell. Intentando con tar...
        tar -a -c -f "coverage-html.zip" -C "htmlcov" .
    )

    echo Listo. Archivo generado en: %cd%\coverage-html.zip
    echo Puedes abrir htmlcov\index.html localmente o compartir el ZIP.
    GOTO :EOF
)

echo Comando no reconocido: %1
echo Opciones válidas: build, rebuild, coverage