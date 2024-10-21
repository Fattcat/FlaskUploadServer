from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, render_template_string
import os
import logging

app = Flask(__name__)
app.secret_key = 'tajne-heslo'  # Bezpečnostný kľúč pre relácie (sessions)

# Priečinok pre nahrané súbory
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Vytvorte priečinok 'uploads' ak neexistuje
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Maximálna veľkosť súboru 50 MB

# Nastavenie logovania chýb
logging.basicConfig(level=logging.ERROR)

# HTML kód pre login stránku
html_content_index = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prihlásenie</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f4f8; padding: 20px; }
        .container { max-width: 800px; margin: auto; padding: 20px; background: white; border-radius: 8px; }
        h1 { color: #007bff; }
        .error { color: red; font-weight: bold; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { padding: 10px; background-color: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Prihlásenie</h1>
        {% if error_message %}
            <p class="error">{{ error_message }}</p>
        {% endif %}
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Používateľské meno" required>
            <input type="password" name="password" placeholder="Heslo" required>
            <button type="submit">Prihlásiť sa</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('upload_file'))
    error_message = request.args.get('error_message')
    return render_template_string(html_content_index, error_message=error_message)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin_1' and password == 'AdminPass':
        session['logged_in'] = True
        return redirect(url_for('upload_file'))
    else:
        return redirect(url_for('home', error_message='Zlé meno alebo heslo!'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        files = request.files.getlist('file')  # Získanie všetkých nahraných súborov
        if not files or files == ['']:
            return render_template('index.html', error="Žiadny súbor nebol vybraný!")

        for file in files:
            if file.filename == '':
                continue  # Ak žiadny súbor nebol vybraný
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)  # Uloženie každého súboru
            except Exception as e:
                app.logger.error(f"Chyba pri ukladaní súboru: {str(e)}")
                return render_template('index.html', error=f"Nastala chyba pri ukladaní súboru: {str(e)}")

        return redirect(url_for('upload_file'))

    # Získanie zoznamu nahratých súborov
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files, error=None)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Súbor neexistuje", 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('upload_file'))

# Pridanie spracovania výnimiek a logovanie chýb
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Nastala chyba: {str(e)}")
    return "An error occurred!", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
