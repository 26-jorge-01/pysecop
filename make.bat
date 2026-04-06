@echo off

rem --- Check if parameter is provided ---
if "%~1"=="" goto help
if "%~1"=="help" goto help

rem --- Route to labels based on %1 ---
if "%~1"=="install" goto :install
if "%~1"=="install-dev" goto :install_dev
if "%~1"=="build" goto :build
if "%~1"=="rebuild" goto :rebuild
if "%~1"=="test" goto :test
if "%~1"=="coverage" goto :coverage
if "%~1"=="example" goto :example
if "%~1"=="clean" goto :clean

echo Comando no reconocido: %1
echo Usa "make.bat" para ver las opciones validas.
goto :eof

:install
echo Installing the package locally...
pip install .
goto :eof

:install_dev
echo Installing the package in editable mode with development dependencies...
pip install -e ".[dev]"
goto :eof

:build
echo Building Docker image (pysecop-dev)...
docker build -t pysecop-dev .
goto :eof

:rebuild
echo Rebuilding Docker image from scratch (no-cache)...
docker build --no-cache -t pysecop-dev .
goto :eof

:test
echo Running tests with pytest...
pytest
goto :eof

:coverage
echo Generating coverage report...
pytest --cov=pysecop --cov-report=html --cov-report=xml
if exist "htmlcov\index.html" echo Coverage report generated in htmlcov\index.html
goto :eof

:example
echo Running example usage script...
python experiments\example_usage.py
goto :eof

:clean
echo Cleaning up temporary files...
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist ".coverage" del /f /q ".coverage"
if exist "htmlcov" rmdir /s /q "htmlcov"
if exist "coverage.xml" del /f /q "coverage.xml"
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo Cleaning up __pycache__ and other temp files...
del /s /q *.pyc *.pyo *.pyd >nul 2>&1
goto :eof

:help
echo Available commands:
echo   install        : Install the package locally
echo   install-dev    : Install the package in editable mode with development dependencies
echo   build          : Build the source and wheel distributions
echo   dist           : Alias for build (prepare for release)
echo   docker-build   : Build the Docker image
echo   docker-rebuild : Rebuild the Docker image without cache
echo   test           : Run tests using pytest
echo   coverage       : Run tests and generate coverage report
echo   example        : Run the example usage script from experiments
echo   clean          : Remove temporary files and build artifacts
goto :eof