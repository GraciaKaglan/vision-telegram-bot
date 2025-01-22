import yaml
import re

def validate_regex(pattern):
    """Validate if the entered regex pattern is valid."""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

def get_user_input(prompt, validation_func=None):
    """Get validated user input from the terminal."""
    while True:
        value = input(f"{prompt}: ")
        if validation_func and not validation_func(value):
            print("Invalid input. Please try again.")
        else:
            return value

def generate_config():
    print("Welcome to the YAML config generator for text parsing!\n")
    
    # Basic info
    supplier_name = get_user_input("Enter the supplier name")
    logo_path = get_user_input("Enter the path to the supplier's logo")
    
    regexes = {}
    print("\nEnter the regex patterns for parsing fields in the text file.")
    
    while True:
        field_name = input("\nEnter the field name (e.g., 'invoice_number', 'date', etc.) or type 'done' to finish: ").strip()
        if field_name.lower() == "done":
            break
        
        regex_pattern = get_user_input(f"Enter the regex pattern for {field_name}", validate_regex)
        regexes[field_name] = regex_pattern

    config_data = {
        'supplier': {
            'name': supplier_name,
            'logo_path': logo_path
        },
        'parsing': {
            'regex_patterns': regexes
        }
    }

    # Save to YAML
    yaml_file_name = f"{supplier_name.lower().replace(' ', '_')}_config.yaml"
    with open(yaml_file_name, 'w') as yaml_file:
        yaml.dump(config_data, yaml_file, default_flow_style=False)
    
    print(f"\nConfiguration saved to {yaml_file_name}")

if __name__ == "__main__":
    generate_config()
