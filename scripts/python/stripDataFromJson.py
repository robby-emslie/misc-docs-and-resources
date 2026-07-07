"""
stripDataFromJson.py
A simple tool to sanitize JSON for schema examples

USAGE: py stripDataFromJson.py <source.json>

Keep in mind that this will *overwrite* your source.json with the sanitized JSON
object (that's a security feature so you don't accidentally send something with
PII to someone who doesn't need to see it - you're welcome!)

"""

import json
import argparse
import sys
from pathlib import Path

def get_data_type(value):
    if value is None:
        return "<null>"
    elif isinstance(value, bool):
        return "<boolean>"
    elif isinstance(value, int):
        return "<integer>"
    elif isinstance(value, float):
        return "<float>"
    elif isinstance(value, str):
        return "<string>"
    elif isinstance(value, list):
        return "<array>"
    elif isinstance(value, dict):
        return "<object>"
    else:
        return "<unknown>"

def is_array_of_objects(value):
    if not isinstance(value, list):
        return False
    if len(value) == 0:
        return False
    return all(isinstance(item, dict) for item in value)

def transform_json(obj):
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                # Preserve objects (nested structures)
                result[key] = transform_json(value)
            elif is_array_of_objects(value):
                # Preserve arrays of objects
                result[key] = [transform_json(item) for item in value]
            elif isinstance(value, list):
                # For regular arrays, replace with data type
                result[key] = get_data_type(value)
            else:
                # Replace scalar values with their data type
                result[key] = get_data_type(value)
        return result
    elif isinstance(obj, list):
        return [transform_json(item) for item in obj]
    else:
        return get_data_type(obj)

def main():
    parser = argparse.ArgumentParser(
        description='Transform JSON file into a schema with data type placeholders'
    )
    parser.add_argument(
        'input_file',
        help='Path to the JSON file to transform'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    
    # Validate file exists
    if not input_path.exists():
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Validate it's a JSON file
    if input_path.suffix.lower() != '.json':
        print(f"Warning: File does not have .json extension", file=sys.stderr)
    
    try:
        # Read the JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Transform the JSON
    transformed_data = transform_json(data)
    
    # Write back to the same file
    try:
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, indent=2)
        print(f"Successfully transformed and saved to {args.input_file}")
    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
