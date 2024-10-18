from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, render_template_string, flash
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tajne-heslo'  # Bezpečnostný kľúč pre relácie (sessions)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Vytvorte priečinok 'uploads' ak neexistuje
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# Dekorátor na kontrolu prihlásenia
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:  # Kontrola, či je používateľ prihlásený
            flash('Prosím, prihláste sa najprv.')
            return redirect(url_for('home'))  # Presmerovanie na login stránku, ak nie je prihlásený
        return f(*args, **kwargs)
    return decorated_function

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

# Pridanie dekorátora na ochranu stránky
@app.route('/upload', methods=['GET', 'POST'])
@login_required  # Ochrana pomocou login_required dekorátora
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
@login_required  # Ochrana pomocou login_required dekorátora
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
@login_required  # Ochrana pomocou login_required dekorátora
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('upload_file'))

if __name__ == "__main__":
    app.run(host='192.168.1.4', port=5000, debug=True)