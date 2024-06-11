import os, sys
import jsonlines

cur_path = os.path.dirname(os.path.abspath(sys.argv[0]))
datasets_name = "elyza_tasks_100"
input_file_dir = f"{os.path.dirname(cur_path)}/assets/{datasets_name}"
output_file_path = f"{os.path.dirname(cur_path)}/assets/{datasets_name}/score.txt"

os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

def process_file(file_path):
    grades = []
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            grades.append(obj["grade"])

    # Calculate statistics
    total_grades = len(grades)
    average_grade = sum(grades) / total_grades if total_grades > 0 else 0
    grade_counts = {grade: grades.count(grade) for grade in set(grades)}

    # Prepare the result string
    result_str = []
    result_str.append(f"File: {os.path.basename(file_path)}")
    result_str.append(f"Total number of grades: {total_grades}")
    result_str.append(f"Average grade: {average_grade:.2f}")
    result_str.append("Grade counts:")
    for grade, count in grade_counts.items():
        result_str.append(f"  Grade {grade}: {count} occurrences")
    result_str.append("\n")
    return "\n".join(result_str)

all_results = []

for file_name in os.listdir(input_file_dir):
    if "result" in file_name and file_name.endswith(".jsonl"):
        file_path = os.path.join(input_file_dir, file_name)
        all_results.append(process_file(file_path))

# Write all results to the output text file
with open(output_file_path, 'w') as f:
    f.write("\n".join(all_results))

print("Completed writing scoring to:", output_file_path)
