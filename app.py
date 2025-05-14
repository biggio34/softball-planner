from flask import Flask, request, render_template, redirect, url_for, Response
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

# Load drills from JSON file
def load_drills():
    try:
        with open("drills.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save drills to JSON file
def save_drills(drills):
    with open("drills.json", "w") as f:
        json.dump(drills, f)

# Home page: Drill management
@app.route("/", methods=["GET", "POST"])
def index():
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
    return render_template("index.html", drills=drills, error=error)

# Delete drill
@app.route("/delete/<int:index>")
def delete_drill(index):
    drills = load_drills()
    if 0 <= index < len(drills):
        drills.pop(index)
        save_drills(drills)
    return redirect(url_for("index"))

# Practice plan page
@app.route("/plan", methods=["GET", "POST"])
def plan():
    drills = load_drills()
    schedule = None
    error = None
    warning = None
    plan_date = None
    if request.method == "POST":
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        selected_indices = request.form.getlist("drills")
        
        try:
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            practice_duration = int((end_dt - start_dt).total_seconds() / 60)
            
            selected_drills = [drills[int(i)] for i in selected_indices]
            total_drill_time = sum(drill["duration"] for drill in selected_drills)
            
            if total_drill_time > practice_duration:
                error = f"Drills exceed practice time by {total_drill_time - practice_duration} minutes"
            elif total_drill_time < practice_duration:
                warning = f"Drills are {practice_duration - total_drill_time} minutes short of practice time"
            
            if not error:
                schedule = []
                current_time = start_dt
                for drill in selected_drills:
                    drill_start = current_time.strftime("%H:%M")
                    current_time += timedelta(minutes=drill["duration"])
                    drill_end = current_time.strftime("%H:%M")
                    schedule.append(f"{drill_start}–{drill_end}: {drill['name']}")
                plan_date = date
        
        except ValueError:
            error = "Invalid date or time format"
    
    return render_template("plan.html", drills=drills, schedule=schedule, error=error, warning=warning, plan_date=plan_date)

# PDF export
@app.route("/export_pdf/<date>")
def export_pdf(date):
    drills = load_drills()
    # Recompute schedule for the given date (simplified; assumes recent plan)
    schedule = []
    # Load the plan details from the last POST (for simplicity, this is a placeholder)
    # In a full app, you'd store plans and retrieve by date
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Practice Plan for {date}")
    y = 730
    for item in request.args.getlist("schedule"):
        c.drawString(100, y, item)
        y -= 20
    c.showPage()
    c.save()
    buffer.seek(0)
    return Response(buffer, mimetype="application/pdf", headers={"Content-Disposition": f"attachment;filename=plan_{date}.pdf"})

if __name__ == "__main__":
    app.run(debug=True)
