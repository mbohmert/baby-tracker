from flask import Flask, request, render_template, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = "a-very-secret-key"  # Replace with your own secret key
PASSWORD = "anatole"

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Suivi enfants lait").worksheet("Heure de lait_A")

@app.route("/", methods=["GET", "POST"])
def index():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        date = request.form["date"]
        time = request.form["time"]
        quantite = request.form["milk"]
        change = request.form["changed"]
        pipi = request.form["pee"]
        caca = request.form["poo"]
        remarques = request.form["comment"]

        try:
            col_b = sheet.col_values(2)
            last_row = len(col_b)
            previous_formula = sheet.cell(last_row, 4).value  # Column D
            insert_row_index = last_row + 1
            new_row = ["", date, time, previous_formula, quantite, change, pipi, caca, remarques]
            sheet.insert_row(new_row, insert_row_index)
            return "✅ Données enregistrées avec succès !"
        except Exception as e:
            return f"❌ Erreur lors de l'enregistrement: {str(e)}"

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "❌ Mot de passe incorrect", 401
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
