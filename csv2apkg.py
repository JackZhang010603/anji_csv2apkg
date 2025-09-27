#!/usr/bin/env python3
"""
Simple CSV to APKG converter for Anki flashcards
Processes all CSV files in the input folder and converts them to APKG files in the output folder
"""

import csv
import os
import sys
from pathlib import Path
import genanki
import random

def create_anki_model():
    """Create a basic Anki card model for vocabulary"""
    return genanki.Model(
        random.randrange(1 << 30, 1 << 31),  # Random model ID
        'Vocabulary Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Meaning'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '<div style="font-size: 24px; text-align: center;">{{Word}}</div>',
                'afmt': '{{FrontSide}}<hr id="answer"><div style="font-size: 18px; text-align: center;">{{Meaning}}</div>',
            },
        ],
        css="""
        .card {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            padding: 20px;
        }
        """
    )

def csv_to_apkg(csv_file_path, output_dir):
    """Convert a single CSV file to APKG format"""
    print(f"Processing: {csv_file_path}")
    
    # Create deck name from filename
    deck_name = csv_file_path.stem
    deck_id = random.randrange(1 << 30, 1 << 31)
    
    # Create deck and model
    deck = genanki.Deck(deck_id, deck_name)
    model = create_anki_model()
    
    # Read CSV and create notes
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            note_count = 0
            
            for row in reader:
                if len(row) >= 2:  # Ensure we have at least 2 columns
                    word = row[0].strip()
                    meaning = row[1].strip()
                    
                    if word and meaning:  # Skip empty rows
                        note = genanki.Note(
                            model=model,
                            fields=[word, meaning]
                        )
                        deck.add_note(note)
                        note_count += 1
            
            if note_count > 0:
                # Generate output filename
                output_file = output_dir / f"{deck_name}.apkg"
                
                # Create package and write to file
                package = genanki.Package(deck)
                package.write_to_file(str(output_file))
                
                print(f"✅ Created: {output_file} ({note_count} cards)")
                return True
            else:
                print(f"⚠️  No valid cards found in {csv_file_path}")
                return False
                
    except Exception as e:
        print(f"❌ Error processing {csv_file_path}: {str(e)}")
        return False

def main():
    """Main function to process all CSV files in input folder"""
    # Set up directories
    script_dir = Path(__file__).parent
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Find all CSV files in input directory
    csv_files = list(input_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"⚠️  No CSV files found in {input_dir}")
        print("Please add CSV files to the input folder and try again.")
        sys.exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s) to process:")
    for csv_file in csv_files:
        print(f"  - {csv_file.name}")
    
    print("\nStarting conversion...")
    
    # Process each CSV file
    success_count = 0
    for csv_file in csv_files:
        if csv_to_apkg(csv_file, output_dir):
            success_count += 1
    
    print(f"\n🎉 Conversion complete!")
    print(f"Successfully processed: {success_count}/{len(csv_files)} files")
    print(f"Output files saved to: {output_dir}")

if __name__ == "__main__":
    main()
