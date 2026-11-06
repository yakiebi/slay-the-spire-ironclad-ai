@echo off
setlocal
REM ============================================================================
REM Launch Slay the Spire with the in-process StsObserverAgent attached on :17575
REM ============================================================================

set "AGENT_JAR=%~dp0observer\sts_observer.jar"
if not defined STS_DIR set "STS_DIR=C:\Program Files (x86)\Steam\steamapps\common\SlayTheSpire"

if not exist "%STS_DIR%\desktop-1.0.jar" (
    echo [ERROR] Could not find desktop-1.0.jar in "%STS_DIR%"
    echo Please set STS_DIR to your Slay the Spire installation directory:
    echo   set "STS_DIR=D:\SteamLibrary\steamapps\common\SlayTheSpire"
    exit /b 1
)

echo Launching Slay the Spire with StsObserverAgent on http://127.0.0.1:17575 ...
cd /d "%STS_DIR%"
"%STS_DIR%\jre\bin\java.exe" -Xmx1G "-javaagent:%AGENT_JAR%" -jar desktop-1.0.jar
