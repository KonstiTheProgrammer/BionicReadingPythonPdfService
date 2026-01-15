from flask import Flask, render_template, request, send_file
import os
import tempfile
from processor import process_pdf_file

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Prüfen ob Datei vorhanden
        if 'file' not in request.files:
            return 'Keine Datei hochgeladen', 400

        file = request.files['file']
        if file.filename == '':
            return 'Keine Datei ausgewählt', 400

        if file:
            # Temporäre Verzeichnisse nutzen (sicherer)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as input_tmp:
                file.save(input_tmp.name)
                input_path = input_tmp.name

            output_path = input_path.replace(".pdf", "_bionic.pdf")

            # PDF Verarbeiten
            success = process_pdf_file(input_path, output_path, x_offset=-10, font_scale=0.92)

            if success:
                # Datei an User zurücksenden
                try:
                    return send_file(output_path, as_attachment=True, download_name=f"bionic_{file.filename}")
                finally:
                    # Aufräumen (Dateien löschen nach dem Senden ist tricky in Flask,
                    # hier lassen wir es simpel. In Prod nutzt man Background Tasks)
                    pass
            else:
                return "Fehler bei der Verarbeitung", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)