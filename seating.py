import csv
import random
from collections import defaultdict

students = []
halls = []

# Read students.csv
with open("students.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        students.append({
            "name": row["Name"],
            "subject": row["Subject"]
        })

# 🔥 Smart shuffle (avoid same subject consecutively)
subject_groups = defaultdict(list)

# Group by subject
for student in students:
    subject_groups[student["subject"]].append(student)

# Shuffle each subject group
for group in subject_groups.values():
    random.shuffle(group)

# Interleave students
mixed_students = []
while any(subject_groups.values()):
    for subject in list(subject_groups.keys()):
        if subject_groups[subject]:
            mixed_students.append(subject_groups[subject].pop())

students = mixed_students

# Read hall.csv
with open("hall.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        halls.append((row["Hall"], int(row["Capacity"])))

# Seat allocation
student_index = 0

for hall, capacity in halls:
    for seat in range(1, capacity + 1):
        if student_index < len(students):
            student = students[student_index]
            print(f"{hall} Seat {seat} -> {student['name']} ({student['subject']})")
            student_index += 1

# ✅ Final check
if student_index < len(students):
    print("\n⚠️ Not enough seats for all students!")
else:
    print("\n✅ All students successfully allocated seats!")
