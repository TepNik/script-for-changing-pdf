import fitz  # PyMuPDF library
import os

# --- Configuration ---
INPUT_FOLDER = "input_pdfs"         # Folder containing original PDFs
OUTPUT_FOLDER = "output_pdfs"        # Folder to save redacted PDFs
RIGHT_MARGIN_OFFSET = 30           # Points from the right edge to leave as margin
AGENT_BLOCK_BOTTOM_PADDING = 5    # Extra space below the identified agent block bottom
# Increased padding to avoid covering the line below fare rules
FARE_RULES_BOTTOM_PADDING = 7     # PREVIOUSLY: 2

# Text markers for block identification
AGENT_START_TEXT = "Agent:"
AGENT_END_TEXT = "Address:"          # Used to find the bottom of the agent block

FARE_RULES_START_TEXT = "Fare rules:"
FARE_RULES_END_MARKERS = ["ENDORSEMENT/RESTRICTIONS", "Fare:"] # Text indicating content *after* the fare rules

def find_text_coords(page, text):
    """Helper function to search for text and return its coordinates."""
    return page.search_for(text, quads=False)

def redact_pdf_sections(input_pdf_path, output_pdf_path):
    """Opens a PDF, applies redactions to specified sections, and saves the result."""
    try:
        doc = fitz.open(input_pdf_path)
        print(f"--- Processing {os.path.basename(input_pdf_path)} ({len(doc)} pages) ---")
        redactions_applied_overall = False # Flag to check if any changes were made

        for page_num, page in enumerate(doc):
            print(f"  Page {page_num + 1}...")
            page_rect = page.rect # Get page dimensions
            redactions_on_page = [] # Store redaction areas for this page

            # --- 1. Find and Redact Agent Block ---
            agent_start_coords = find_text_coords(page, AGENT_START_TEXT)
            if agent_start_coords:
                agent_y0 = agent_start_coords[0].y0
                agent_x0 = agent_start_coords[0].x0
                agent_y1 = 0 # Initialize bottom coordinate

                address_coords = find_text_coords(page, AGENT_END_TEXT)
                if address_coords:
                    agent_y1 = max(rect.y1 for rect in address_coords) + AGENT_BLOCK_BOTTOM_PADDING
                else:
                    print(f"    ! Agent block: '{AGENT_END_TEXT}' not found. Using estimated height.")
                    agent_y1 = agent_start_coords[0].y1 + AGENT_BLOCK_BOTTOM_PADDING * 15

                if agent_y1 > agent_y0:
                    agent_x1 = page_rect.width - RIGHT_MARGIN_OFFSET
                    redact_rect = fitz.Rect(agent_x0, agent_y0, agent_x1, agent_y1)
                    redactions_on_page.append(redact_rect)
                    print(f"    > Adding redaction for Agent block: {redact_rect}")

            # --- 2. Find and Redact Fare Rules Block ---
            fare_rules_start_coords = find_text_coords(page, FARE_RULES_START_TEXT)
            if fare_rules_start_coords:
                rules_y0 = fare_rules_start_coords[0].y0
                rules_x0 = fare_rules_start_coords[0].x0
                end_marker_y = page_rect.height

                possible_end_coords = []
                for marker in FARE_RULES_END_MARKERS:
                    coords = find_text_coords(page, marker)
                    valid_coords = [rect for rect in coords if rect.y0 > rules_y0]
                    if valid_coords:
                        possible_end_coords.extend(valid_coords)

                if possible_end_coords:
                    end_marker_y = min(rect.y0 for rect in possible_end_coords)
                    print(f"    > Fare Rules: Found end marker.")
                else:
                    print(f"    ! Fare Rules: No end marker found below. Redacting towards bottom margin.")
                    end_marker_y = page_rect.height - RIGHT_MARGIN_OFFSET

                # Calculate bottom coordinate for redaction using the increased padding
                rules_y1 = end_marker_y - FARE_RULES_BOTTOM_PADDING
                if rules_y1 > rules_y0:
                    rules_x1 = page_rect.width - RIGHT_MARGIN_OFFSET
                    redact_rect = fitz.Rect(rules_x0, rules_y0, rules_x1, rules_y1)
                    redactions_on_page.append(redact_rect)
                    print(f"    > Adding redaction for Fare Rules block: {redact_rect}")

            # --- Apply redactions found on this page ---
            if redactions_on_page:
                redactions_applied_overall = True
                for rect in redactions_on_page:
                    # Add the redaction annotation with WHITE fill color
                    page.add_redact_annot(rect, fill=(1, 1, 1)) # White color
                # Apply redactions permanently
                page.apply_redactions()
                print(f"    Applied {len(redactions_on_page)} redaction(s) with white color.")
            else:
                print("    No sections identified for redaction on this page.")

        # --- Save the document ---
        if redactions_applied_overall:
            doc.save(output_pdf_path, garbage=4, deflate=True)
            print(f"--- Saved modified file to: {output_pdf_path} ---")
        else:
            print(f"--- No redactions applied to {os.path.basename(input_pdf_path)}. Original file not overwritten in output. ---")

        doc.close()

    except Exception as e:
        print(f"[ERROR] Failed to process {input_pdf_path}: {e}")

# --- Main script execution ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}")

    if not os.path.exists(INPUT_FOLDER):
         print(f"[ERROR] Input folder '{INPUT_FOLDER}' not found!")
    else:
        for filename in os.listdir(INPUT_FOLDER):
            if filename.lower().endswith(".pdf"):
                input_path = os.path.join(INPUT_FOLDER, filename)
                output_filename = f"{os.path.splitext(filename)[0]}_redacted.pdf"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                redact_pdf_sections(input_path, output_path)

    print("=========================================")
    print("Script finished.")