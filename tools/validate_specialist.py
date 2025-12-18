#!/usr/bin/env python3
import os
import yaml
import sys
import glob

def validate_specialist(filepath):
    """
    Validates a single specialist YAML file against the required schema using PyYAML.
    """
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            
        if not data:
             print(f"❌ {filepath}: Empty file")
             return False

        # Required top-level keys based on actual schema
        required_keys = ['specialist', 'core_identity', 'activation_patterns']
        missing = [key for key in required_keys if key not in data]
        
        if missing:
            print(f"❌ {filepath}: Missing keys {missing}")
            return False
            
        # Check that core_identity has 'role' (optional deeper check)
        if 'core_identity' in data and isinstance(data['core_identity'], dict):
            if 'role' not in data['core_identity']:
                 print(f"❌ {filepath}: 'core_identity' missing 'role'")
                 return False

        print(f"✅ {filepath}: Valid")
        return True

    except Exception as e:
        print(f"❌ {filepath}: Invalid YAML - {str(e)}")
        return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    staff_dir = os.path.join(base_dir, 'staff')
    
    # Find all .yaml files in staff/ (recursive)
    yaml_files = glob.glob(os.path.join(staff_dir, '**', '*.yaml'), recursive=True)
    
    print(f"🔍 Validating {len(yaml_files)} specialists in {staff_dir}...\n")
    
    passed = 0
    failed = 0
    
    for file in yaml_files:
        if validate_specialist(file):
            passed += 1
        else:
            failed += 1
            
    print(f"\n📊 Result: {passed} Passed, {failed} Failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
