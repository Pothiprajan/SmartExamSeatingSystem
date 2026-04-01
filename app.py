from flask import Flask, render_template, request, redirect
import csv
from collections import defaultdict

app = Flask(__name__)

CSV_FILE = "students.csv"
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
                students.append(row)
    except FileNotFoundError:
        pass
    return students

# -----------------------------
# ADD STUDENT
# -----------------------------
def add_student(regno, name, dept, subject):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([regno, name, dept, subject])

# -----------------------------
# SMART SEATING LOGIC
# -----------------------------
def generate_seating(students):

    subject_groups = defaultdict(list)

    # ✅ FIXED HERE (Subject instead of subject)
    for s in students:
        if 'Subject' in s and s['Subject']:
            subject_groups[s['Subject']].append(s)

    # Mix students (round robin)
    mixed_students = []
    while any(subject_groups.values()):
        for subject in list(subject_groups.keys()):
            if subject_groups[subject]:
                mixed_students.append(subject_groups[subject].pop(0))

    # Safety check
    def is_safe(seating, i, j, student):
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < ROWS and 0 <= nj < COLS:
                neighbor = seating[ni][nj]
                if neighbor and neighbor['Subject'] == student['Subject']:
                    return False
        return True

    # Fill seating
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

            # fallback
            if not placed and mixed_students:
                seating[i][j] = mixed_students.pop(0)

    return seating

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    students = read_students()

    search = request.args.get("search", "").lower()
    subject_filter = request.args.get("subject", "")

    # Filter logic
    if search:
        students = [s for s in students if search in s['Name'].lower()]

    if subject_filter:
        students = [s for s in students if s['Subject'] == subject_filter]

    seating = generate_seating(students)

    subjects = list(set([s['Subject'] for s in read_students() if 'Subject' in s]))

    return render_template("index.html",
                           seating=seating,
                           subjects=subjects,
                           search=search,
                           selected_subject=subject_filter)

# -----------------------------
# ADD STUDENT ROUTE
# -----------------------------
@app.route("/add", methods=["POST"])
def add():
    regno = request.form.get("regno")
    name = request.form.get("name")
    dept = request.form.get("dept")
    subject = request.form.get("subject")

    if regno and name and dept and subject:
        add_student(regno, name, dept, subject)

    return redirect("/")

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
