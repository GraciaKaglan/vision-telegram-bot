import yaml
import json
import re

def load_yaml_config(yaml_file):
    """Load YAML configuration file."""
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def load_text_file(txt_file):
    """Load text from a .txt file."""
    with open(txt_file, 'r') as file:
        return file.read()

def test_regexes(yaml_config, text):
    """Test regexes from the YAML file against the text."""
    regex_patterns = yaml_config.get('parsing', {}).get('regex_patterns', {})
    results = {}

    for field, pattern in regex_patterns.items():
        try:
            matches = re.findall(pattern, text)
            results[field] = matches
        except re.error as e:
            results[field] = f"Invalid regex: {e}"

    return results

def save_results_to_json(results, output_file):
    """Save results to a JSON file."""
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)


if __name__ == "__main__":
    # File paths
    yaml_file = "config/relay_config.yaml" 
    txt_file = "texte/output.txt"
    output_json = "results.json"

    # Load YAML config and text
    yaml_config = load_yaml_config(yaml_file)
    text = load_text_file(txt_file)

    # Test regexes
    results = test_regexes(yaml_config, text)

    save_results_to_json(results, output_json)

    print(f"Results saved to {output_json}")