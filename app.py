from flask import Flask, render_template, request
import csv
import random

app = Flask(__name__)

def generate_seating():
    students = []
    halls = []

    with open("students.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append({
                "name": row["Name"],
                "subject": row["Subject"]
            })

    random.shuffle(students)

    with open("hall.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            halls.append((row["Hall"], int(row["Capacity"])))

    data = []
    student_index = 0

    for hall, capacity in halls:
        for seat in range(1, capacity + 1):
            if student_index < len(students):
                student = students[student_index]
                data.append({
                    "hall": hall,
                    "seat": seat,
                    "name": student["name"],
                    "subject": student["subject"]
                })
                student_index += 1

    return data


@app.route("/")
def index():
    search = request.args.get("search", "").lower()
    hall_filter = request.args.get("hall", "")

    data = generate_seating()

    if search:
        data = [d for d in data if search in d["name"].lower()]

    if hall_filter:
        data = [d for d in data if d["hall"] == hall_filter]

    halls = sorted(list(set(d["hall"] for d in data)))

    return render_template("index.html", data=data, halls=halls)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
