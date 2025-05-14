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

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_drill(index):
    drills = load_drills()
    if index < 0 or index >= len(drills):
        return redirect(url_for("drills"))
    drill = drills[index]
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        try:
            duration = int(request.form.get("duration"))
            if name and duration > 0:
                drills[index] = {"name": name, "duration": duration}
                save_drills(drills)
                return redirect(url_for("drills"))
            else:
                error = "Enter valid name and duration"
        except ValueError:
            error = "Duration must be a number"
    return render_template("edit_drill.html", drill=drill, index=index, error=error)

@app.route("/delete/<int:index>")
def delete_drill(index):
    drills = load_drills()
    if 0 <= index < len(drills):
        drills.pop(index)
        save_drills(drills)
    return redirect(url_for("drills"))

if __name__ == "__main__":
    app.run(debug=True)
