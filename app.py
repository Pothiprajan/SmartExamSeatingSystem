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
def add_student(name, subject):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, subject])

# -----------------------------
# SMART SEATING LOGIC
# -----------------------------
def generate_seating(students):

    # Group by subject
    subject_groups = defaultdict(list)
    for s in students:
        subject_groups[s['subject']].append(s)

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
                if neighbor and neighbor['subject'] == student['subject']:
                    return False
        return True

    # Fill seating
    seating = [[None for _ in range(COLS)] for _ in range(ROWS)]
    index = 0
    attempts = 0

    for i in range(ROWS):
        for j in range(COLS):

            placed = False
            loop_count = 0

            while index < len(mixed_students) and loop_count < len(mixed_students):
                student = mixed_students[index]

                if is_safe(seating, i, j, student):
                    seating[i][j] = student
                    mixed_students.pop(index)
                    placed = True
                    break
                else:
                    # rotate list
                    mixed_students.append(mixed_students.pop(index))
                    loop_count += 1

            # fallback (if no safe placement)
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
        students = [s for s in students if search in s['name'].lower()]

    if subject_filter:
        students = [s for s in students if s['subject'] == subject_filter]

    seating = generate_seating(students)

    subjects = list(set([s['subject'] for s in read_students()]))

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
    name = request.form.get("name")
    subject = request.form.get("subject")

    if name and subject:
        add_student(name, subject)

    return redirect("/")

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
