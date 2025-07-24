from flask import Flask, request, render_template, redirect, url_for, session, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
app.secret_key = "a-very-secret-key"
PASSWORD = "anatole"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Suivi enfants lait").worksheet("Heure de lait_A")

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
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
            previous_formula = sheet.cell(last_row, 4).value
            insert_row_index = last_row + 1
            new_row = ["", date, time, previous_formula, quantite, change, pipi, caca, remarques]
            sheet.insert_row(new_row, insert_row_index)
            flash("✅ Donnée enregistrée avec succès !", "success")
        except Exception as err:
            flash(f"❌ Erreur lors de l'enregistrement : {str(err)}", "danger")

    return render_template("dashboard.html", **get_dashboard_data())

def get_dashboard_data():
    data = sheet.get_all_values()[2:]
    latest_entries = data[-3:][::-1] if len(data) >= 3 else data[::-1]
    intake_data = []

    for row in data[-30:]:
        date_str, time_str, qty = row[1], row[2], row[4]
        if date_str and time_str and qty:
            try:
                dt = datetime.strptime(date_str + " " + time_str, "%d/%m/%Y %H:%M")
                intake_data.append({"x": dt.isoformat(), "y": int(qty)})
            except:
                continue

    days_old = (datetime.now().date() - datetime(2025, 7, 23).date()).days
    if days_old == 0:
        intake_min, intake_max = 5, 10
    elif days_old == 1:
        intake_min, intake_max = 10, 20
    elif days_old == 2:
        intake_min, intake_max = 20, 30
    elif 3 <= days_old <= 4:
        intake_min, intake_max = 30, 60
    elif 5 <= days_old <= 6:
        intake_min, intake_max = 60, 90
    else:
        intake_min, intake_max = 90, 150

    return {
        "recent": latest_entries,
        "chart_data": intake_data,
        "intake_min": intake_min,
        "intake_max": intake_max
    }

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return "❌ Mot de passe incorrect", 401
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
