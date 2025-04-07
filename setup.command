#!/bin/bash

# --- Change to the script's directory ---
# Ensures relative paths work correctly when double-clicked
cd "$(dirname "$0")" || exit 1

# We will check exit codes manually to provide pauses on errors
# set -e # Deactivated to allow custom error handling pauses

echo "--- Starting Project Setup ---"
echo "Setup script running from: $(pwd)" # Show current directory

# --- Define Folder Names ---
INPUT_FOLDER="input_pdfs"
OUTPUT_FOLDER="output_pdfs"

# --- Ensure Input/Output Folders Exist ---
echo "Checking/Creating required folders..."
mkdir -p "$INPUT_FOLDER"
if [ $? -ne 0 ]; then # Check exit status of mkdir
    echo "-----------------------------------------------------" >&2
    echo "Error: Failed to create input folder '$INPUT_FOLDER'." >&2
    echo "Check permissions." >&2
    echo "-----------------------------------------------------" >&2
    read -p "Press Enter to close this window..."
    exit 1
fi
mkdir -p "$OUTPUT_FOLDER"
if [ $? -ne 0 ]; then # Check exit status of mkdir
    echo "-----------------------------------------------------" >&2
    echo "Error: Failed to create output folder '$OUTPUT_FOLDER'." >&2
    echo "Check permissions." >&2
    echo "-----------------------------------------------------" >&2
    read -p "Press Enter to close this window..."
    exit 1
fi
echo "Required folders '$INPUT_FOLDER' and '$OUTPUT_FOLDER' are ready."

# --- Check for Python 3 ---
echo "Checking for Python 3..."
if command -v python3 >/dev/null 2>&1; then
    echo "Python 3 found: $(python3 --version)"
else
    echo "-----------------------------------------------------" >&2
    echo "Error: Python 3 is required but not found." >&2
    echo "Please install Python 3 (e.g., from python.org or using Homebrew: 'brew install python')." >&2
    echo "-----------------------------------------------------" >&2
    read -p "Press Enter to close this window..."
    exit 1
fi

# --- Define Virtual Environment Name ---
VENV_NAME=".venv"
echo "Using virtual environment directory: $VENV_NAME"

# --- Create Virtual Environment (if it doesn't exist) ---
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_NAME"
    if [ $? -ne 0 ]; then
        echo "-----------------------------------------------------" >&2
        echo "Error: Failed to create virtual environment." >&2
        echo "Check permissions and available disk space." >&2
        echo "-----------------------------------------------------" >&2
        read -p "Press Enter to close this window..."
        exit 1
    fi
    echo "Virtual environment created successfully."
else
    echo "Virtual environment '$VENV_NAME' already exists. Skipping creation."
fi

# --- Activate Virtual Environment (for this script's execution) ---
echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"
if [ -z "$VIRTUAL_ENV" ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Failed to activate virtual environment." >&2
    echo "Ensure '$VENV_NAME/bin/activate' exists and has correct permissions." >&2
    echo "-----------------------------------------------------" >&2
    read -p "Press Enter to close this window..."
    exit 1
fi
echo "Virtual environment activated."

# --- Check for requirements.txt ---
if [ ! -f "requirements.txt" ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: requirements.txt not found in this directory." >&2
    echo "Make sure 'requirements.txt' exists alongside this script." >&2
    echo "-----------------------------------------------------" >&2
    deactivate
    read -p "Press Enter to close this window..."
    exit 1
fi

# --- Install Dependencies ---
echo "Installing dependencies from requirements.txt (this might take a moment)..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "-----------------------------------------------------" >&2
    echo "Error: Failed to install dependencies using pip." >&2
    echo "Check your internet connection and the contents of requirements.txt." >&2
    echo "-----------------------------------------------------" >&2
    deactivate
    read -p "Press Enter to close this window..."
    exit 1
fi
echo "Dependencies installed successfully."

# --- Deactivate Environment (optional cleanup) ---
deactivate

# --- Success Message ---
echo "-----------------------------------------------------"
echo "--- Setup Complete ---"
echo "Folders '$INPUT_FOLDER' and '$OUTPUT_FOLDER' created/verified."
echo "The project environment is ready."
echo "You can now put PDF files into the 'input_pdfs' folder"
echo "and double-click 'run.command' to process them."
echo "-----------------------------------------------------"

# Keep window open briefly for success message
echo ""
echo "(This window will close automatically in 10 seconds)"
sleep 10

exit 0