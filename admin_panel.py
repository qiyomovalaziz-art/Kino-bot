# admin_panel.py
import os
from flask import Flask, request, jsonify, render_template_string
from database import init_db, saqla_kino

app = Flask(__name__)
init_db()

# Oddiy HTML forma
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head><title>🎬 Admin Panel</title></head>
<body>
  <h2>Kino Qo'shish</h2>
  <p>📌 Faqat Telegram bot orqali kino yuklangan file_id ni kiriting!</p>
  <form method="POST">
    <label>File ID: <input name="file_id" required></label><br><br>
    <label>Tur:
      <select name="file_type" required>
        <option value="video">Video</option>
        <option value="photo">Rasm</option>
        <option value="document">Hujjat</option>
      </select>
    </label><br><br>
    <button type="submit">✅ Saqlash</button>
  </form>
  {% if kino_id %}
    <h3 style="color:green;">✅ Kino saqlandi! Raqami: {{ kino_id }}</h3>
  {% endif %}
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        file_id = request.form.get("file_id")
        file_type = request.form.get("file_type")
        if file_id and file_type in ["video", "photo", "document"]:
            kino_id = saqla_kino(file_id, file_type)
            return render_template_string(HTML_FORM, kino_id=kino_id)
    return render_template_string(HTML_FORM)

# Railway uchun portni sozlash
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
