@echo off
setlocal
REM ============================================================================
REM Recompile observer\StsObserverAgent.java into observer\sts_observer.jar
REM ============================================================================

if not defined STS_DIR set "STS_DIR=C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire"

if not exist "%STS_DIR%\desktop-1.0.jar" (
    echo [ERROR] Could not find desktop-1.0.jar in "%STS_DIR%"
    echo Set STS_DIR to your Slay the Spire installation folder first.
    exit /b 1
)

cd /d "%~dp0observer"
echo Compiling StsObserverAgent.java against "%STS_DIR%\desktop-1.0.jar" ...
javac -source 8 -target 8 -cp "%STS_DIR%\desktop-1.0.jar" StsObserverAgent.java
if errorlevel 1 (
    echo [ERROR] Compilation failed. Make sure JDK 8+ (javac) is on your PATH.
    exit /b 1
)

echo Packaging sts_observer.jar ...
jar cfm sts_observer.jar MANIFEST.MF StsObserverAgent*.class
echo Done! Built "%~dp0observer\sts_observer.jar"
