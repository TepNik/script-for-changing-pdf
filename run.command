#!/bin/bash

# --- Change to the script's directory ---
# This is crucial for finding relative paths (.venv, python script) when double-clicked
cd "$(dirname "$0")" || exit 1

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting PDF Redaction Script ---"
echo "Script location: $(pwd)" # Show current directory for debugging

# --- Define Virtual Environment Name ---
VENV_NAME=".venv"

# --- Check if Virtual Environment Exists ---
if [ ! -d "$VENV_NAME" ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Virtual environment '$VENV_NAME' not found." >&2
    echo "Please run the setup script first." >&2
    echo "Open Terminal in this folder and run: bash setup.sh" >&2
    echo "-----------------------------------------------------" >&2
    # Keep window open for user to read error
    echo ""
    read -p "Press Enter to close this window..."
    exit 1
fi

# --- Activate Virtual Environment ---
echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"
if [ $? -ne 0 ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Failed to activate virtual environment." >&2
    echo "-----------------------------------------------------" >&2
    read -p "Press Enter to close this window..."
    exit 1
fi
echo "Virtual environment activated."

# --- Check for Python Script ---
PYTHON_SCRIPT="redact_pdf.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Python script '$PYTHON_SCRIPT' not found." >&2
    echo "-----------------------------------------------------" >&2
    deactivate # Deactivate before exiting
    read -p "Press Enter to close this window..."
    exit 1
fi

# --- Check for Input Folder ---
INPUT_FOLDER="input_pdfs"
if [ ! -d "$INPUT_FOLDER" ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Input folder '$INPUT_FOLDER' not found." >&2
    echo "Please create '$INPUT_FOLDER' and place your PDF files inside it." >&2
    echo "-----------------------------------------------------" >&2
    deactivate # Deactivate before exiting
    read -p "Press Enter to close this window..."
    exit 1
fi

# --- Run the Python Script ---
echo "Running $PYTHON_SCRIPT..."
# Use python3 explicitly
python3 "$PYTHON_SCRIPT"
SCRIPT_EXIT_CODE=$? # Capture exit code of the python script

# --- Deactivate Environment ---
deactivate
echo "Virtual environment deactivated."


if [ $SCRIPT_EXIT_CODE -ne 0 ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Python script execution failed (Exit Code: $SCRIPT_EXIT_CODE)." >&2
    echo "Please check the messages above for details." >&2
    echo "-----------------------------------------------------" >&2
    read -p "Press Enter to close this window..."
    exit 1
else
    echo "-----------------------------------------------------"
    echo "--- PDF Redaction Script Finished Successfully ---"
    echo "Check the '$OUTPUT_FOLDER' folder for results."
    echo "-----------------------------------------------------"
    # Keep window open briefly so user can see the success message
    echo ""
    echo "(This window will close automatically in 10 seconds)"
    sleep 10
fi

exit 0