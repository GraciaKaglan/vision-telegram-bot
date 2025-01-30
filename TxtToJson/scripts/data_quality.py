import json
import os

def check_data_quality(json_folder):
    """Check if extracted text meets the data quality contract for each JSON file."""
    quality_issues = {}

    for json_file in os.listdir(json_folder):
        if json_file.endswith(".json"):
            file_path = os.path.join(json_folder, json_file)
            with open(file_path, 'r') as file:
                results = json.load(file)

            issues = []
            for field, match in results.items():
                if match == "No match":
                    issues.append(f"Missing expected field: {field}")
                elif isinstance(match, list) and len(match) > 1:
                    issues.append(f"Multiple values found for field {field}, expected only one: {match}")

            if issues:
                quality_issues[json_file] = issues

    if quality_issues:
        print("⚠️ Data Quality Issues Found:")
        for file, issues in quality_issues.items():
            print(f"File: {file}")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("✅ All files meet the data quality contract.")

if __name__ == "__main__":
    json_folder = "TxtToJson/json_output"
    check_data_quality(json_folder)
