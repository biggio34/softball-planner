from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Load drills from JSON
def load_drills():
    try:
        with open("drills.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save drills to JSON
def save_drills(drills):
    with open("drills.json", "w") as f:
        json.dump(drills, f)

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/drills", methods=["GET", "POST"])
def drills():
    drills = load_drills()
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        try:
            duration = int(request.form.get("duration"))
            if name and duration > 0:
                drills.append({"name": name, "duration": duration})
                save_drills(drills)
            else:
                error = "Enter valid name and duration"
        except ValueError:
            error = "Duration must be a number"
    return render_template("drills.html", drills=drills, error=error)

if __name__ == "__main__":
    app.run(debug=True)
