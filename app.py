from flask import Flask, render_template, request, redirect
import csv
import random
from collections import defaultdict

app = Flask(__name__)

CSV_FILE = "students.csv"
SEATING_FILE = "seating.csv"

ROWS = 5
COLS = 6

# -----------------------------
# READ STUDENTS
# -----------------------------
def read_students():
    students = []
    try:
        with open(CSV_FILE, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row:
                    students.append(row)
    except FileNotFoundError:
        pass
    return students

# -----------------------------
# SAVE STUDENTS
# -----------------------------
def save_students(students):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["RegNo","Name","Dept","Subject"])
        for s in students:
            writer.writerow([s["RegNo"], s["Name"], s["Dept"], s["Subject"]])

# -----------------------------
# SAVE SEATING
# -----------------------------
def save_seating(seating):
    with open(SEATING_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["hall", "seat", "Name", "Subject", "RegNo"])

        for s in seating:
            writer.writerow([
                s.get("hall", ""),
                s.get("seat", ""),
                s.get("Name", ""),
                s.get("Subject", ""),
                s.get("RegNo", "")
            ])

# -----------------------------
# ADD STUDENT (NO DUPLICATE)
# -----------------------------
def add_student(regno, name, dept, subject):
    students = read_students()

    for s in students:
        if s["RegNo"] == regno:
            return False

    students.append({
        "RegNo": regno,
        "Name": name,
        "Dept": dept,
        "Subject": subject
    })

    save_students(students)
    return True

# -----------------------------
# SMART SEATING
# -----------------------------
def generate_seating(students):

    if not students:
        return []

    subject_groups = defaultdict(list)

    for s in students:
        subject = s.get('Subject')
        if subject:
            subject_groups[subject].append(s)

    # 🔥 RANDOMIZE GROUPS
    for subject in subject_groups:
        random.shuffle(subject_groups[subject])

    mixed_students = []
    while any(subject_groups.values()):
        for subject in list(subject_groups.keys()):
            if subject_groups[subject]:
                mixed_students.append(subject_groups[subject].pop(0))

    # 🔥 FINAL SHUFFLE
    random.shuffle(mixed_students)

    def is_safe(seating, i, j, student):
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < ROWS and 0 <= nj < COLS:
                neighbor = seating[ni][nj]
                if neighbor and neighbor.get('Subject') == student.get('Subject'):
                    return False
        return True

    seating = [[None for _ in range(COLS)] for _ in range(ROWS)]

    for i in range(ROWS):
        for j in range(COLS):

            placed = False
            loop_count = 0

            while mixed_students and loop_count < len(mixed_students):
                student = mixed_students[0]

                if is_safe(seating, i, j, student):
                    seating[i][j] = student
                    mixed_students.pop(0)
                    placed = True
                    break
                else:
                    mixed_students.append(mixed_students.pop(0))
                    loop_count += 1

            if not placed and mixed_students:
                seating[i][j] = mixed_students.pop(0)

    final_seating = []

    for i in range(ROWS):
        for j in range(COLS):
            student = seating[i][j]
            if student:

                if i < 2:
                    hall = "Hall - A"
                elif i < 4:
                    hall = "Hall - B"
                else:
                    hall = "Hall - C"

                final_seating.append({
                    "hall": hall,
                    "seat": f"{i+1}-{j+1}",
                    "Name": student.get("Name"),
                    "Subject": student.get("Subject"),
                    "RegNo": student.get("RegNo")
                })

    return final_seating

# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def index():
    students = read_students()
    seating = generate_seating(students)
    save_seating(seating)
    return render_template("index.html", seating=seating)

# -----------------------------
# GENERATE BUTTON
# -----------------------------
@app.route("/generate")
def generate():
    students = read_students()
    seating = generate_seating(students)
    save_seating(seating)
    return redirect("/")

# -----------------------------
# DELETE STUDENT
# -----------------------------
@app.route("/delete/<regno>")
def delete(regno):
    students = read_students()
    students = [s for s in students if s["RegNo"] != regno]

    save_students(students)

    seating = generate_seating(students)
    save_seating(seating)

    return redirect("/")

# -----------------------------
# ADD STUDENT
# -----------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        regno = request.form.get("regno")
        name = request.form.get("name")
        dept = request.form.get("dept")
        subject = request.form.get("subject")

        if regno and name and dept and subject:
            add_student(regno, name, dept, subject)

        return redirect("/")

    return render_template("add.html")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
