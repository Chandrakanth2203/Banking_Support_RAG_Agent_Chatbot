#!/bin/bash
# Docker Entrypoint Script
# Handles starting Streamlit and FastAPI services

set -e

# Configuration
FASTAPI_HOST=${FASTAPI_HOST:-0.0.0.0}
FASTAPI_PORT=${FASTAPI_PORT:-8000}
STREAMLIT_HOST=${STREAMLIT_HOST:-0.0.0.0}
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

echo "=========================================="
echo "Banking Support AI Agent Chatbot"
echo "Docker Startup Script"
echo "=========================================="

# Create log directory
mkdir -p /app/logs

# Function to start FastAPI
start_fastapi() {
    echo "Starting FastAPI server on ${FASTAPI_HOST}:${FASTAPI_PORT}..."
    cd /app/FastAPI
    python -m uvicorn main:app \
        --host ${FASTAPI_HOST} \
        --port ${FASTAPI_PORT} \
        --reload \
        --log-level info \
        &
    FASTAPI_PID=$!
    echo "FastAPI started with PID: $FASTAPI_PID"
}

# Function to start Streamlit
start_streamlit() {
    echo "Starting Streamlit application on ${STREAMLIT_HOST}:${STREAMLIT_PORT}..."
    cd /app/Streamlit
    streamlit run app.py \
        --server.address ${STREAMLIT_HOST} \
        --server.port ${STREAMLIT_PORT} \
        --server.enableCORS=true \
        --server.enableXsrfProtection=false \
        --logger.level=info \
        &
    STREAMLIT_PID=$!
    echo "Streamlit started with PID: $STREAMLIT_PID"
}

# Function to start only FastAPI
start_fastapi_only() {
    echo "Starting FastAPI server only..."
    cd /app/FastAPI
    exec python -m uvicorn main:app \
        --host ${FASTAPI_HOST} \
        --port ${FASTAPI_PORT} \
        --log-level info
}

# Function to start only Streamlit
start_streamlit_only() {
    echo "Starting Streamlit application only..."
    cd /app/Streamlit
    exec streamlit run app.py \
        --server.address ${STREAMLIT_HOST} \
        --server.port ${STREAMLIT_PORT} \
        --server.enableCORS=true \
        --server.enableXsrfProtection=false
}

# Main entrypoint logic
case "${1:-all}" in
    all)
        echo "Starting all services (FastAPI + Streamlit)..."
        start_fastapi
        sleep 3  # Wait for FastAPI to start
        start_streamlit
        
        # Keep both services running
        wait
        ;;
    fastapi)
        echo "Starting FastAPI service only..."
        start_fastapi_only
        ;;
    streamlit)
        echo "Starting Streamlit service only..."
        start_streamlit_only
        ;;
    shell)
        echo "Starting interactive shell..."
        exec /bin/bash
        ;;
    *)
        echo "Unknown command: $1"
        echo "Available commands: all, fastapi, streamlit, shell"
        exit 1
        ;;
esac
