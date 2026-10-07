#!/usr/bin/env bash
# ==============================================================================
# AI-Based Waste Segregation & Regional Decision Intelligence System
# Runner Script (Bash / Git Bash / Linux / macOS / WSL)
# ==============================================================================

set -e

# Change directory to project root
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

export PYTHONPATH="."

echo "======================================================================"
echo "♻️  Smart Waste AI & Regional Decision Intelligence System"
echo "======================================================================"

# Determine Python executable
if [ -f "/c/Program Files/Python312/python.exe" ]; then
    PYTHON_CMD="/c/Program Files/Python312/python.exe"
elif [ -f "C:/Program Files/Python312/python.exe" ]; then
    PYTHON_CMD="C:/Program Files/Python312/python.exe"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v py &>/dev/null; then
    PYTHON_CMD="py"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python is not installed or not in PATH."
    exit 1
fi

echo "Using Python: $("$PYTHON_CMD" --version)"

# Check arguments
MODE="${1:-serve}"

case "$MODE" in
    serve|start|"")
        echo ""
        echo "🚀 Starting AI Waste Intelligence Server on http://127.0.0.1:8000 ..."
        echo "👉 Opening Dashboard in Browser..."
        
        # Auto-open browser across Windows / Git Bash / Mac / Linux
        (sleep 1 && (cmd.exe /c start http://127.0.0.1:8000/ 2>/dev/null || open http://127.0.0.1:8000/ 2>/dev/null || xdg-open http://127.0.0.1:8000/ 2>/dev/null || true)) &
        
        echo "Press CTRL+C to stop the server."
        echo "======================================================================"
        exec "$PYTHON_CMD" app.py
        ;;

    test)
        echo ""
        echo "🧪 Running full automated test suite..."
        "$PYTHON_CMD" -m pytest tests/ -v
        ;;

    forecast)
        echo ""
        echo "📈 Re-running Regional Waste Forecasting Pipeline (2024–2027)..."
        "$PYTHON_CMD" scripts/forecasting/build_regional_forecast.py
        ;;

    train)
        echo ""
        echo "🧠 Training RealWaste Vision Classifier..."
        "$PYTHON_CMD" scripts/training/train_classifier.py
        ;;

    help|--help|-h)
        echo ""
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  ./run.sh           Start the FastAPI server & Dashboard (Default)"
        echo "  ./run.sh test      Run the 14-test verification suite"
        echo "  ./run.sh forecast  Run the 2024-2027 forecasting pipeline"
        echo "  ./run.sh train     Train the MobileNetV3 image classifier"
        ;;

    *)
        echo "❌ Unknown command: $MODE"
        echo "Run './run.sh help' for usage instructions."
        exit 1
        ;;
esac
