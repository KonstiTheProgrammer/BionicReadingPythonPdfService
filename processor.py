import fitz  # PyMuPDF
import math
import os

def calculate_bold_length(word):
    length = len(word)
    clean_word = word.rstrip(".,:;!?\"')]} ")
    clean_len = len(clean_word)
    if clean_len <= 1: return 1
    elif clean_len == 2: return 1
    elif clean_len == 3: return 2
    elif clean_len == 4: return 2
    else: return math.ceil(clean_len * 0.4)

def process_pdf_file(input_path, output_path, x_offset=-10, font_scale=0.95):
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"Fehler: {e}")
        return False

    font_regular = fitz.Font("helv")
    font_bold = fitz.Font("hebo")

    for page in doc:
        text_instances = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block: continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    if not text.strip(): continue
                    text_instances.append({
                        "text": text,
                        "origin": span["origin"],
                        "size": span["size"],
                        "bbox": span["bbox"]
                    })

        # Redaction (Text entfernen)
        for item in text_instances:
            page.add_redact_annot(item["bbox"], fill=(1, 1, 1))
        page.apply_redactions()

        # Neuen Text schreiben
        writer = fitz.TextWriter(page.rect)
        for item in text_instances:
            original_text = item["text"]
            origin = item["origin"]
            original_size = item["size"]
            words = original_text.split(" ")

            cursor_x = origin[0] + x_offset
            cursor_y = origin[1]
            current_font_size = original_size * font_scale

            for i, word in enumerate(words):
                if not word: continue
                split_index = calculate_bold_length(word)
                if split_index > len(word): split_index = len(word)

                part_bold = word[:split_index]
                part_regular = word[split_index:]

                writer.append((cursor_x, cursor_y), part_bold, font=font_bold, fontsize=current_font_size)
                cursor_x += font_bold.text_length(part_bold, fontsize=current_font_size)

                if part_regular:
                    writer.append((cursor_x, cursor_y), part_regular, font=font_regular, fontsize=current_font_size)
                    cursor_x += font_regular.text_length(part_regular, fontsize=current_font_size)

                if i < len(words) - 1:
                    cursor_x += font_regular.text_length(" ", fontsize=current_font_size)

        writer.write_text(page)

    doc.save(output_path)
    return True