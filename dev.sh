#!/bin/bash
# AI Sandbox - Local Development Helper Script
# Usage: ./dev.sh [command]

COMPOSE_FILE="docker-compose.local.yml"

function show_help() {
    echo "AI Sandbox - Local Development Helper"
    echo
    echo "Usage: ./dev.sh [command]"
    echo
    echo "Commands:"
    echo "  start       - Start PostgreSQL"
    echo "  stop        - Stop PostgreSQL"
    echo "  restart     - Restart PostgreSQL"
    echo "  status      - Check status"
    echo "  logs        - View PostgreSQL logs"
    echo "  clean       - Stop and remove all data (WARNING: Deletes database)"
    echo "  app1        - Run app1 (localhost only)"
    echo
    echo "Examples:"
    echo "  ./dev.sh start"
    echo "  ./dev.sh app1"
}

case "$1" in
    "")
        show_help
        ;;

    "start")
        echo "Starting PostgreSQL..."
        docker-compose -f "$COMPOSE_FILE" up -d
        echo
        echo "PostgreSQL is starting. Wait ~10 seconds for it to be ready."
        echo "Check status with: ./dev.sh status"
        ;;

    "stop")
        echo "Stopping PostgreSQL..."
        docker-compose -f "$COMPOSE_FILE" down
        echo "Done."
        ;;

    "restart")
        echo "Restarting PostgreSQL..."
        docker-compose -f "$COMPOSE_FILE" restart
        echo "Done."
        ;;

    "status")
        echo "Checking status..."
        docker ps --filter "name=ai-sandbox"
        ;;

    "logs")
        echo "Showing PostgreSQL logs (Ctrl+C to exit)..."
        docker-compose -f "$COMPOSE_FILE" logs -f postgres
        ;;

    "clean")
        echo "WARNING: This will delete all data in the database!"
        read -p "Are you sure? (yes/no): " CONFIRM
        if [ "$CONFIRM" = "yes" ]; then
            echo "Stopping and removing all data..."
            docker-compose -f "$COMPOSE_FILE" down -v
            echo "Done. All data removed."
        else
            echo "Cancelled."
        fi
        ;;

    "app1")
        echo "Starting app1..."
        echo "URL: http://localhost:8501"
        echo "Press Ctrl+C to stop"
        echo
        cd streamlit_apps/app1
        python -m streamlit run streamlit_main.py --server.address=localhost --server.headless=true
        ;;

    *)
        echo "Unknown command: $1"
        echo "Run './dev.sh' without arguments to see available commands."
        exit 1
        ;;
esac
