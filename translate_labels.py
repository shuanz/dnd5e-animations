import json
from deep_translator import GoogleTranslator

def translate_labels(input_file, output_file):
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Counter for progress
    total_labels = sum(1 for _ in json.dumps(data).split('"label":')) - 1
    current = 0
    
    # Function to recursively find and add Portuguese translations
    def add_portuguese_translations(d):
        nonlocal current
        if isinstance(d, dict):
            # Create a list of items to avoid modifying dict during iteration
            items = list(d.items())
            for key, value in items:
                if key == 'label' and isinstance(value, str):
                    current += 1
                    print(f"[{current}/{total_labels}] Translating: {value}")
                    # Add Portuguese translation as a new field
                    try:
                        translated = GoogleTranslator(source='auto', target='pt').translate(value)
                        d['label_pt_br'] = translated
                        print(f"   → {translated}")
                    except Exception as e:
                        print(f"   Error translating '{value}': {e}")
                        d['label_pt_br'] = value  # Keep original if translation fails
                elif isinstance(value, (dict, list)):
                    add_portuguese_translations(value)
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, (dict, list)):
                    add_portuguese_translations(item)
    
    print(f"Starting translation of {total_labels} labels...")
    # Process the data
    add_portuguese_translations(data)
    
    # Save the modified data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)

if __name__ == "__main__":
    input_file = "module/autorec.json"
    output_file = "module/autorec_with_translations.json"
    translate_labels(input_file, output_file)
    print(f"\nTranslation complete! Output saved to {output_file}")
    print("Original labels are kept as 'label' and Portuguese translations are added as 'label_pt_br'")