cd "$(dirname "$0")/.."
source .venv/bin/activate

# Add the project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

streamlit run FilePilot/src/welcome.py