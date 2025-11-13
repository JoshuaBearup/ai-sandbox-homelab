@echo off
REM AI Sandbox - Local Development Helper Script
REM Usage: dev.bat [command]

SET COMPOSE_FILE=docker-compose.local.yml

IF "%1"=="" (
    echo AI Sandbox - Local Development Helper
    echo.
    echo Usage: dev.bat [command]
    echo.
    echo Commands:
    echo   start       - Start PostgreSQL
    echo   stop        - Stop PostgreSQL
    echo   restart     - Restart PostgreSQL
    echo   status      - Check status
    echo   logs        - View PostgreSQL logs
    echo   clean       - Stop and remove all data ^(WARNING: Deletes database^)
    echo   app1        - Run app1 ^(localhost only^)
    echo.
    echo Examples:
    echo   dev.bat start
    echo   dev.bat app1
    exit /b 0
)

IF "%1"=="start" (
    echo Starting PostgreSQL...
    docker-compose -f %COMPOSE_FILE% up -d
    echo.
    echo PostgreSQL is starting. Wait ~10 seconds for it to be ready.
    echo Check status with: dev.bat status
    exit /b 0
)

IF "%1"=="stop" (
    echo Stopping PostgreSQL...
    docker-compose -f %COMPOSE_FILE% down
    echo Done.
    exit /b 0
)

IF "%1"=="restart" (
    echo Restarting PostgreSQL...
    docker-compose -f %COMPOSE_FILE% restart
    echo Done.
    exit /b 0
)

IF "%1"=="status" (
    echo Checking status...
    docker ps --filter "name=ai-sandbox"
    exit /b 0
)

IF "%1"=="logs" (
    echo Showing PostgreSQL logs ^(Ctrl+C to exit^)...
    docker-compose -f %COMPOSE_FILE% logs -f postgres
    exit /b 0
)

IF "%1"=="clean" (
    echo WARNING: This will delete all data in the database!
    set /p CONFIRM="Are you sure? (yes/no): "
    if /i "%CONFIRM%"=="yes" (
        echo Stopping and removing all data...
        docker-compose -f %COMPOSE_FILE% down -v
        echo Done. All data removed.
    ) else (
        echo Cancelled.
    )
    exit /b 0
)

IF "%1"=="app1" (
    echo Starting app1...
    echo URL: http://localhost:8501
    echo Press Ctrl+C to stop
    echo.
    python -m streamlit run streamlit_apps/app1/streamlit_main.py --server.address=localhost --server.headless=true
    exit /b 0
)

echo Unknown command: %1
echo Run 'dev.bat' without arguments to see available commands.
exit /b 1
