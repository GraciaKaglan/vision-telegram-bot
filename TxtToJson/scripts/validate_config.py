import os
import yaml
import json
import re

def load_yaml_config(yaml_file):
    """Load YAML configuration file."""
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def validate_text_files(text_folder, config_file, output_folder):
    """Validate multiple regex patterns from YAML config on extracted text files."""
    config = load_yaml_config(config_file)
    regex_patterns = config.get("parsing", {}).get("regex_patterns", {})

    os.makedirs(output_folder, exist_ok=True)

    for txt_file in os.listdir(text_folder):
        if txt_file.endswith(".txt"):
            file_path = os.path.join(text_folder, txt_file)
            with open(file_path, 'r') as file:
                text = file.read()

            results = {}
            for field, patterns in regex_patterns.items():
                if not isinstance(patterns, list):  # Ensure patterns are a list
                    patterns = [patterns]

                match_found = None
                for pattern in patterns:
                    try:
                        match = re.search(pattern, text)
                        if match:
                            match_found = match.group(0)
                            break  # Stop at the first valid match
                    except re.error as e:
                        match_found = f"Invalid regex: {e}"
                        break

                results[field] = match_found if match_found else "No match"

            output_json = os.path.join(output_folder, txt_file.replace(".txt", ".json"))
            with open(output_json, 'w') as json_file:
                json.dump(results, json_file, indent=4)

            print(f"Validation results saved to {output_json}")

if __name__ == "__main__":
    validate_text_files(
        "TxtToJson/Txt",
        "TxtToJson/config/relay_config.yaml",
        "TxtToJson/json_output"
    )
