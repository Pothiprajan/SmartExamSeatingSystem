import csv

students = []
halls = []

with open("students.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        students.append(row["Name"])


with open("hall.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        halls.append((row["Hall"],int(row["Capacity"])))

student_index = 0

for hall,capacity in halls:
    for seat in range(1,capacity+1):
        if student_index < len(students):
             print(f"{hall} Seat {seat} -> {students[student_index]}")
             student_index += 1
