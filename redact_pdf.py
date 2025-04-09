import fitz  # PyMuPDF library
import os

# --- Configuration ---
INPUT_FOLDER = "input_pdfs"
OUTPUT_FOLDER = "output_pdfs"
RIGHT_MARGIN_OFFSET = 30
# Константы для Fare Rules (подобранные вами)
ESTIMATED_LINE_HEIGHT = 16 # Оставляем 16, как вы подобрали
FARE_RULES_LINES_TO_REDACT = 3
# --- ИЗМЕНЕНО --- Отдельная константа высоты для Links to comments
LINKS_REDACTION_HEIGHT_ADDITION = 12 # Кол-во пунктов для добавления ПОСЛЕ строки "Links..." (Подберите, если нужно)

AGENT_START_TEXT = "Agent:"
AGENT_END_TEXT = "Address:"
AGENT_BLOCK_BOTTOM_PADDING = 5

FARE_RULES_START_TEXT = "Fare rules:"
LINKS_START_TEXT = "Links to comments:"


def find_text_coords(page, text):
    """Helper function to search for text and return its coordinates using search_for."""
    return page.search_for(text, quads=False)

# --- Основная функция редактирования ---
def redact_pdf_sections(input_pdf_path, output_pdf_path):
    """Opens a PDF, applies redactions to specified sections, and saves the result."""
    try:
        doc = fitz.open(input_pdf_path)
        print(f"--- Processing {os.path.basename(input_pdf_path)} ({len(doc)} pages) ---")
        redactions_applied_overall = False

        for page_num, page in enumerate(doc):
            print(f"  Page {page_num + 1}...")
            page_rect = page.rect
            redactions_on_page = []

            # --- 1. Find and Redact Agent Block ---
            # (Без изменений)
            agent_start_coords = find_text_coords(page, AGENT_START_TEXT)
            if agent_start_coords:
                agent_y0 = agent_start_coords[0].y0
                agent_x0 = agent_start_coords[0].x0
                agent_y1 = 0
                address_coords = find_text_coords(page, AGENT_END_TEXT)
                valid_address_coords = [rect for rect in address_coords if rect.y0 > agent_y0]
                if valid_address_coords:
                    agent_y1 = max(rect.y1 for rect in valid_address_coords) + AGENT_BLOCK_BOTTOM_PADDING
                else:
                    print(f"    ! Agent block: '{AGENT_END_TEXT}' not found below start. Using estimated height.")
                    # Используем общую высоту строки для агента
                    agent_y1 = agent_start_coords[0].y1 + ESTIMATED_LINE_HEIGHT * 5
                if agent_y1 > agent_y0:
                    agent_x1 = page_rect.width - RIGHT_MARGIN_OFFSET
                    redact_rect = fitz.Rect(agent_x0, agent_y0, agent_x1, agent_y1)
                    redactions_on_page.append(redact_rect)
                    print(f"    > Adding redaction for Agent block: {redact_rect}")


            # --- 2. Find and Redact Fare Rules Block ---
            # (Использует ESTIMATED_LINE_HEIGHT = 16, FARE_RULES_LINES_TO_REDACT = 3)
            fare_rules_start_coords = find_text_coords(page, FARE_RULES_START_TEXT)
            if fare_rules_start_coords:
                for start_coord in fare_rules_start_coords:
                    rules_x0 = start_coord.x0
                    rules_y0 = start_coord.y0
                    # Вычисляем нижнюю границу как низ строки "Fare rules:" + N строк
                    rules_y1 = start_coord.y1 + FARE_RULES_LINES_TO_REDACT * ESTIMATED_LINE_HEIGHT
                    rules_y1 = min(rules_y1, page_rect.height - 1) # Ограничение по высоте страницы

                    if rules_y1 > rules_y0:
                        rules_x1 = page_rect.width - RIGHT_MARGIN_OFFSET
                        redact_rect = fitz.Rect(rules_x0, rules_y0, rules_x1, rules_y1)
                        if redact_rect.height > 0.1:
                           redactions_on_page.append(redact_rect)
                           print(f"    > Adding redaction for Fare Rules block (fixed height): {redact_rect}")
                        else:
                           print(f"    > Skipping tiny Fare Rules redaction: {redact_rect}")


            # --- 3. Find and Redact Links to comments Block ---
            # --- ИЗМЕНЕНО: Используем LINKS_REDACTION_HEIGHT_ADDITION ---
            links_start_coords = find_text_coords(page, LINKS_START_TEXT)
            if links_start_coords:
                for start_coord in links_start_coords:
                    link_x0 = start_coord.x0
                    link_y0 = start_coord.y0
                    # Вычисляем нижнюю границу как низ строки "Links..." + фиксированное кол-во пунктов
                    link_y1 = start_coord.y1 + LINKS_REDACTION_HEIGHT_ADDITION
                    link_y1 = min(link_y1, page_rect.height - 1) # Ограничение по высоте страницы

                    if link_y1 > link_y0:
                        link_x1 = page_rect.width - RIGHT_MARGIN_OFFSET
                        redact_rect = fitz.Rect(link_x0, link_y0, link_x1, link_y1)
                        if redact_rect.height > 0.1:
                           redactions_on_page.append(redact_rect)
                           print(f"    > Adding redaction for Links block (fixed height addition): {redact_rect}")
                        else:
                            print(f"    > Skipping tiny Links redaction: {redact_rect}")


            # --- Apply redactions found on this page ---
            if redactions_on_page:
                redactions_applied_overall = True
                for rect in redactions_on_page:
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
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
    # (Без изменений)
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}")

    if not os.path.exists(INPUT_FOLDER):
         print(f"[ERROR] Input folder '{INPUT_FOLDER}' not found!")
    else:
        print(f"Starting PDF processing from '{INPUT_FOLDER}' to '{OUTPUT_FOLDER}'...")
        for filename in os.listdir(INPUT_FOLDER):
            if filename.lower().endswith(".pdf"):
                input_path = os.path.join(INPUT_FOLDER, filename)
                base_name = os.path.splitext(filename)[0]
                if base_name.lower().endswith('_redacted'):
                    base_name = base_name[:-9]
                output_filename = f"{base_name}_redacted.pdf"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                redact_pdf_sections(input_path, output_path)
            else:
                print(f"Skipping non-PDF file: {filename}")

    print("=========================================")
    print("Script finished.")