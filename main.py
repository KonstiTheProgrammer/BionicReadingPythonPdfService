import fitz  # PyMuPDF
import os
import math

def calculate_bold_length(word):
    """
    Berechnet, wie viele Buchstaben am Anfang fett sein sollen.
    """
    length = len(word)
    clean_word = word.rstrip(".,:;!?\"')]} ")
    clean_len = len(clean_word)

    if clean_len <= 1:
        return 1
    elif clean_len == 2:
        return 1
    elif clean_len == 3:
        return 2
    elif clean_len == 4:
        return 2
    else:
        return math.ceil(clean_len * 0.4)

def apply_true_bionic_reading_clean(input_pdf_path, output_pdf_path, x_offset=-10, font_scale=0.95):
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"Fehler beim Öffnen: {e}")
        return

    # Fonts definieren
    font_regular = fitz.Font("helv")
    font_bold = fitz.Font("hebo")

    print(f"Bearbeite {len(doc)} Seiten mit Clean-Mode...")

    for page in doc:
        # Liste um alle Textelemente der Seite zwischenzuspeichern
        text_instances = []

        # 1. SCHRITT: Daten sammeln
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block: continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    if not text.strip(): continue

                    # Wir speichern alles, was wir brauchen, in einer Liste
                    text_instances.append({
                        "text": text,
                        "origin": span["origin"],
                        "size": span["size"],
                        "bbox": span["bbox"]
                    })

        # 2. SCHRITT: Originaltext entfernen (Redaction)
        # Das verhindert das "schwarze Rauschen" von überlappenden Boxen
        for item in text_instances:
            # Wir markieren den Bereich zur Entfernung und füllen ihn weiß (fill=(1,1,1))
            page.add_redact_annot(item["bbox"], fill=(1, 1, 1))

        # Führt die Löschung durch (Text und Grafiken in den Bereichen werden entfernt)
        page.apply_redactions()

        # 3. SCHRITT: Neuen Text schreiben
        writer = fitz.TextWriter(page.rect)

        for item in text_instances:
            original_text = item["text"]
            origin = item["origin"]
            original_size = item["size"]

            words = original_text.split(" ")

            # Position anpassen (Offset)
            cursor_x = origin[0] + x_offset
            cursor_y = origin[1]

            # Größe anpassen (Scale)
            current_font_size = original_size * font_scale

            for i, word in enumerate(words):
                if not word: continue

                split_index = calculate_bold_length(word)
                if split_index > len(word): split_index = len(word)

                part_bold = word[:split_index]
                part_regular = word[split_index:]

                # 1. Fetter Teil
                writer.append(
                    (cursor_x, cursor_y),
                    part_bold,
                    font=font_bold,
                    fontsize=current_font_size
                )
                cursor_x += font_bold.text_length(part_bold, fontsize=current_font_size)

                # 2. Normaler Teil
                if part_regular:
                    writer.append(
                        (cursor_x, cursor_y),
                        part_regular,
                        font=font_regular,
                        fontsize=current_font_size
                    )
                    cursor_x += font_regular.text_length(part_regular, fontsize=current_font_size)

                # 3. Leerzeichen
                if i < len(words) - 1:
                    space_width = font_regular.text_length(" ", fontsize=current_font_size)
                    cursor_x += space_width

        # Text final auf die Seite schreiben
        writer.write_text(page)

    doc.save(output_pdf_path)
    print(f"Fertig! Saubere Datei: {output_pdf_path}")

# --- Ausführen ---
input_file = "test.pdf"
output_file = "bionic_clean.pdf"

if os.path.exists(input_file):
    # Ich habe die Anpassungen (x_offset, font_scale) beibehalten
    apply_true_bionic_reading_clean(input_file, output_file, x_offset=-10, font_scale=0.92)
else:
    print(f"Datei '{input_file}' nicht gefunden.")