#!/usr/bin/env python3
"""
Simple parser for CoStar text files - extract all spaces and create CSV output.
"""

import re
import json
import csv

def find_records_in_file(filename):
    """Find all property records in a text file."""
    print(f"Processing {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all record starts
    record_pattern = r'^(\d+\s+\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl|Court|Ct))'
    records = []
    current_page = 1  # Default to page 1
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for page markers
        page_match = re.match(r'^=== PAGE (\d+) ===', line)
        if page_match:
            current_page = int(page_match.group(1))
            continue
        
        if re.match(record_pattern, line):
            # Found a record start
            address_match = re.search(record_pattern, line)
            if address_match:
                address = address_match.group(1).strip()
                
                # Get city/state from next line
                city_state = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if re.match(r'^[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}', next_line):
                        city_state = next_line
                
                # Find spaces in this record
                spaces = find_spaces_in_record(lines, i, current_page)
                
                records.append({
                    'address': address,
                    'city_state': city_state,
                    'page_number': current_page,
                    'spaces': spaces
                })
                
                print(f"  Found: {address} - {len(spaces)} spaces (Page {current_page})")
    
    print(f"Total records found: {len(records)}")
    return records

def find_spaces_in_record(lines, start_line, page_number):
    """Find all spaces in a record starting from start_line."""
    spaces = []
    
    # Look for Available Spaces sections
    for i in range(start_line, min(start_line + 100, len(lines))):
        line = lines[i].strip()
        
        if line == 'Available Spaces':
            # Found spaces section, parse the table
            # Skip the header lines
            j = i + 1
            while j < min(i + 30, len(lines)):
                space_line = lines[j].strip()
                
                # Stop if we hit end markers
                if (not space_line or 
                    space_line.startswith('2025 CoStar') or 
                    space_line.startswith('Page') or
                    space_line.startswith('=') or
                    space_line.startswith('Unit Mix') or
                    space_line.startswith('Property Summary')):
                    break
                
                # Skip header lines
                if (space_line.startswith('Floor') or 
                    space_line.startswith('Building') or
                    'Use Type' in space_line or
                    'SF Available' in space_line):
                    j += 1
                    continue
                
                # Parse space line - handle the correct table format
                # Format: P Retail Retail Direct 1,500 1,500 1,500 Withheld Vacant Negotiable
                # Then next line: GRND (floor info)
                parts = space_line.split()
                if len(parts) >= 6:
                    try:
                        # Skip lines that are clearly not space data
                        if any(skip_word in space_line for skip_word in ['2025', 'CoStar', 'Group', 'Licensed', 'Page']):
                            j += 1
                            continue
                        
                        # First part is floor indicator (P, E, etc.)
                        floor_indicator = parts[0]
                        
                        # Get the floor - for office spaces it's in the same line, for retail it's on the next line
                        floor = ''
                        
                        # Check if this is office format: E 12 - Office Direct...
                        if len(parts) > 2 and parts[1].isdigit() and parts[2] == '-':
                            # Office format: E 12 - Office Direct 500 - 10,000...
                            floor = parts[1]
                        else:
                            # Check next line for floor info (retail format)
                            if j + 1 < len(lines):
                                next_line = lines[j + 1].strip()
                                if next_line in ['GRND', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']:
                                    floor = next_line
                                    j += 1  # Skip the floor line
                        
                        # Parse the space data
                        if len(parts) >= 6:
                            # Check if this is office format: E 12 - Office Direct 500 - 10,000...
                            if len(parts) > 2 and parts[1].isdigit() and parts[2] == '-':
                                # Office format: E 12 - Office Direct 500 - 10,000 10,000 10,000 $3.00 +UTIL
                                suite = '-'  # No suite number
                                use_type = parts[3] if len(parts) > 3 else ''
                                lease_type = parts[4] if len(parts) > 4 else ''
                                sf_available = parts[5] if len(parts) > 5 else ''
                                
                                # Find rent (look for $)
                                rent = ''
                                for k in range(6, len(parts)):
                                    if parts[k].startswith('$'):
                                        rent = parts[k]
                                        break
                            else:
                                # Retail format: P Retail Retail Direct 1,500 1,500 1,500 Withheld
                                suite = parts[1] if len(parts) > 1 else ''
                                use_type = parts[2] if len(parts) > 2 else ''
                                lease_type = parts[3] if len(parts) > 3 else ''
                                sf_available = parts[4] if len(parts) > 4 else ''
                                
                                # Find rent (look for $ or "Withheld")
                                rent = ''
                                for k in range(5, len(parts)):
                                    if parts[k].startswith('$'):
                                        rent = parts[k]
                                        break
                                    elif parts[k] == 'Withheld':
                                        rent = 'Withheld'
                                        break
                        
                        # Clean up the data and validate
                        sf_available = sf_available.replace(',', '') if sf_available else ''
                        
                        # Only add if we have meaningful data
                        if sf_available and sf_available.isdigit() and int(sf_available) > 0:
                            spaces.append({
                                'floor': floor,
                                'suite': suite,
                                'use_type': use_type,
                                'size_sf': sf_available,
                                'rent_per_sf': rent,
                                'page_number': page_number
                            })
                    except Exception as e:
                        # Skip problematic lines
                        pass
                
                j += 1
    
    return spaces

def calculate_distance(addr1, addr2):
    """Simple distance calculation."""
    try:
        num1 = int(addr1.split()[0])
        num2 = int(addr2.split()[0])
        
        if abs(num1 - num2) < 100:
            return 0.1
        elif abs(num1 - num2) < 500:
            return 0.3
        else:
            return 0.5
    except:
        return 1.0

def create_csv_output(retail_records, office_records):
    """Create CSV file with all spaces from both retail and office records."""
    print("Creating CSV output...")
    
    with open('all_spaces.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['property_type', 'address', 'city_state', 'floor', 'suite', 'use_type', 'size_sf', 'rent_per_sf', 'page_number']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Add retail spaces
        for record in retail_records:
            for space in record['spaces']:
                writer.writerow({
                    'property_type': 'Retail',
                    'address': record['address'],
                    'city_state': record['city_state'],
                    'floor': space['floor'],
                    'suite': space['suite'],
                    'use_type': space['use_type'],
                    'size_sf': space['size_sf'],
                    'rent_per_sf': space['rent_per_sf'],
                    'page_number': space['page_number']
                })
        
        # Add office spaces
        for record in office_records:
            for space in record['spaces']:
                writer.writerow({
                    'property_type': 'Office',
                    'address': record['address'],
                    'city_state': record['city_state'],
                    'floor': space['floor'],
                    'suite': space['suite'],
                    'use_type': space['use_type'],
                    'size_sf': space['size_sf'],
                    'rent_per_sf': space['rent_per_sf'],
                    'page_number': space['page_number']
                })
    
    print("CSV file created: all_spaces.csv")

def main():
    print("=== CoStar Parser - CSV Output ===")
    
    # Parse both files
    retail_records = find_records_in_file("retail_full_text.txt")
    office_records = find_records_in_file("office_full_text.txt")
    
    print(f"\nRetail records: {len(retail_records)}")
    print(f"Office records: {len(office_records)}")
    
    # Count total spaces
    total_retail_spaces = sum(len(record['spaces']) for record in retail_records)
    total_office_spaces = sum(len(record['spaces']) for record in office_records)
    
    print(f"Total retail spaces: {total_retail_spaces}")
    print(f"Total office spaces: {total_office_spaces}")
    print(f"Total spaces: {total_retail_spaces + total_office_spaces}")
    
    # Create CSV output
    create_csv_output(retail_records, office_records)
    
    # Also save JSON for reference
    results = {
        'retail_records': retail_records,
        'office_records': office_records,
        'summary': {
            'total_retail_records': len(retail_records),
            'total_office_records': len(office_records),
            'total_retail_spaces': total_retail_spaces,
            'total_office_spaces': total_office_spaces
        }
    }
    
    with open('simple_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults also saved to simple_results.json")

if __name__ == "__main__":
    main()
