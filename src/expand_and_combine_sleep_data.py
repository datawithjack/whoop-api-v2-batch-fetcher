import json
import csv
import os
import glob
from datetime import datetime

def load_json_file(filepath):
    """Load a JSON file and return the data"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def expand_nested_fields(record):
    """Expand nested fields in a sleep record"""
    expanded_record = {}
    
    for key, value in record.items():
        if isinstance(value, dict):
            # Special handling for the 'score' field which contains nested data
            if key == 'score':
                # Expand the score dictionary into individual columns
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, dict):
                        # Further expand nested dictionaries like stage_summary and sleep_needed
                        for sub_key, sub_value in nested_value.items():
                            expanded_record[f"score.{nested_key}.{sub_key}"] = sub_value
                    else:
                        # Direct values like respiratory_rate, sleep_performance_percentage
                        expanded_record[f"score.{nested_key}"] = nested_value
            else:
                # For other nested dictionaries, use underscore separator
                for nested_key, nested_value in value.items():
                    expanded_record[f"{key}_{nested_key}"] = nested_value
        elif isinstance(value, str):
            # Try to parse as JSON if it's a string (for score fields)
            if key in ['score_sleep_needed', 'score_stage_summary']:
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, dict):
                        # Expand the parsed JSON dictionary
                        for nested_key, nested_value in parsed.items():
                            expanded_record[f"{key}.{nested_key}"] = nested_value
                    else:
                        # Keep original value if not a dict
                        expanded_record[key] = value
                except json.JSONDecodeError:
                    # Keep original value if not valid JSON
                    expanded_record[key] = value
            else:
                # For other strings, keep as is
                expanded_record[key] = value
        elif isinstance(value, list):
            # Convert lists to JSON strings
            expanded_record[key] = json.dumps(value)
        else:
            expanded_record[key] = value
    
    return expanded_record

def debug_score_fields(records):
    """Debug function to examine score fields"""
    if not records:
        return
    
    print(f"\n🔍 Debugging score fields in first record...")
    first_record = records[0]
    
    # Look for score-related fields
    score_fields = [key for key in first_record.keys() if 'score' in key.lower()]
    print(f"📊 Score-related fields found: {score_fields}")
    
    for field in score_fields:
        value = first_record.get(field)
        print(f"\n📋 Field: {field}")
        print(f"   Type: {type(value)}")
        print(f"   Value: {value}")
        
        if isinstance(value, dict):
            print(f"   Dictionary keys: {list(value.keys())}")
        elif isinstance(value, str):
            print(f"   String length: {len(value)}")
            # Try to parse as JSON
            try:
                parsed = json.loads(value)
                print(f"   Parsed JSON type: {type(parsed)}")
                if isinstance(parsed, dict):
                    print(f"   Parsed JSON keys: {list(parsed.keys())}")
            except json.JSONDecodeError:
                print(f"   Not valid JSON")

def process_sleep_json_file(filepath):
    """Process a single sleep JSON file and return expanded records"""
    print(f"📁 Processing: {os.path.basename(filepath)}")
    
    data = load_json_file(filepath)
    if not data:
        return []
    
    # Extract user info and sleep records
    user_info = data.get('user_info', {})
    sleep_records = data.get('sleep_records', [])
    
    if not sleep_records:
        print(f"  ⚠️  No sleep records found")
        return []
    
    print(f"  📊 Found {len(sleep_records)} sleep records")
    
    # Debug score fields for the first file
    if "jackfrankandrew" in filepath:  # Only debug for one user to avoid spam
        debug_score_fields(sleep_records)
    
    # Expand each record
    expanded_records = []
    for record in sleep_records:
        expanded_record = expand_nested_fields(record)
        
        # Add user info to each record
        expanded_record.update({
            'user_email': user_info.get('email', ''),
            'user_name': user_info.get('name', ''),
            'whoop_user_id': user_info.get('whoop_user_id', ''),
            'source_file': os.path.basename(filepath)
        })
        
        expanded_records.append(expanded_record)
    
    print(f"  ✅ Expanded to {len(expanded_records)} records")
    return expanded_records

def find_sleep_json_files():
    """Find all sleep data JSON files"""
    # Look for batch sleep data files in exports/json/
    pattern = os.path.join("exports", "json", "sleep_data_batch_*.json")
    files = glob.glob(pattern)
    
    if not files:
        # Also look for custom sleep data files in exports/json/
        pattern = os.path.join("exports", "json", "sleep_data_custom_*.json")
        files = glob.glob(pattern)
    
    if not files:
        # Fallback: look in current directory
        pattern = "sleep_data_batch_*.json"
        files = glob.glob(pattern)
        
        if not files:
            pattern = "sleep_data_custom_*.json"
            files = glob.glob(pattern)
    
    return sorted(files)

def ensure_output_directory():
    """Ensure the combined_csv output directory exists"""
    output_dir = os.path.join("exports", "combined_csv")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created combined_csv directory: {output_dir}")
    return output_dir

def get_all_fieldnames(records):
    """Get all unique field names from all records"""
    fieldnames = set()
    for record in records:
        fieldnames.update(record.keys())
    return sorted(list(fieldnames))

def main():
    """Main function to expand and combine sleep data"""
    print("🔄 Sleep Data Expander and Combiner")
    print("="*60)
    
    # Ensure output directory exists
    output_dir = ensure_output_directory()
    
    # Find all sleep JSON files
    json_files = find_sleep_json_files()
    
    if not json_files:
        print("❌ No sleep data JSON files found")
        print("💡 Make sure to run the batch sleep fetcher first")
        return
    
    print(f"📋 Found {len(json_files)} JSON files to process")
    
    # Process all files and collect expanded records
    all_records = []
    for filepath in json_files:
        records = process_sleep_json_file(filepath)
        all_records.extend(records)
    
    if not all_records:
        print("❌ No records to export")
        return
    
    print(f"\n📊 Total expanded records: {len(all_records)}")
    
    # Get all field names
    fieldnames = get_all_fieldnames(all_records)
    print(f"📋 Total columns: {len(fieldnames)}")
    
    # Create output filename in the combined_csv directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"combined_sleep_data_expanded_{timestamp}.csv")
    
    # Write to CSV
    print(f"\n💾 Writing to: {output_file}")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
    
    print(f"✅ Successfully exported {len(all_records)} records to {output_file}")
    
    # Show some statistics
    print(f"\n📈 Summary:")
    print(f"   Total records: {len(all_records)}")
    print(f"   Total columns: {len(fieldnames)}")
    print(f"   Users: {len(set(record['user_email'] for record in all_records))}")
    
    # Show expanded columns
    expanded_columns = [col for col in fieldnames if '.' in col]
    if expanded_columns:
        print(f"\n🔍 Expanded columns:")
        for col in expanded_columns:
            print(f"   - {col}")
    
    print(f"\n📁 Output file: {output_file}")

if __name__ == "__main__":
    main() 