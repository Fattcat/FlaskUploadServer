from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Vytvorte priečinok 'uploads' ak neexistuje
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')  # Získanie všetkých nahraných súborov
        for file in files:
            if file.filename == '':
                continue  # Ak žiadny súbor nebol vybraný
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)  # Uloženie každého súboru

        return redirect(url_for('upload_file'))

    # Získanie zoznamu nahratých súborov
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('upload_file'))

if __name__ == "__main__":
    app.run(host='192.168.1.4', port=5000, debug=True)
