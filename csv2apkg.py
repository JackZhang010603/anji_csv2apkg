#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project: anji_csv2apkg
File: csv2apkg.py
Created: 2025-09-27
Updated: 2025-09-27

Description:
    Converts CSV vocabulary files into Anki flashcard decks (.apkg files).
    Takes words and meanings from CSV and creates ready-to-import Anki decks.

Usage:
    # Simple way - process all CSV files in input folder:
    python csv2apkg.py
    
    # Convert specific files:
    python csv2apkg.py vocabulary.csv
    python csv2apkg.py vocab1.csv vocab2.csv
    python csv2apkg.py *.csv
    
    # With custom options:
    python csv2apkg.py vocab.csv -o "My Deck.apkg"
    python csv2apkg.py vocab.csv -d "Spanish Words"
    python csv2apkg.py vocab.csv --output-dir custom_output/
    
    # Get help:
    python csv2apkg.py -h

CSV Format:
    Your CSV file should have two columns (word, meaning):
    apple,red fruit that grows on trees
    book,collection of pages with text
    computer,electronic device for processing data

Notes:
    - CSV files should be UTF-8 encoded for best results
    - Empty rows and malformed entries are automatically skipped
    - Output files are saved as [filename].apkg in the output directory
    - Requires genanki library: pip install genanki
    - Compatible with Anki 2.1 and newer versions
"""

import csv
import os
import sys
import argparse
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

def csv_to_apkg(csv_file_path, output_dir, custom_output=None, custom_deck_name=None):
    """Convert a single CSV file to APKG format"""
    print(f"Processing: {csv_file_path}")
    
    # Create deck name from filename or use custom name
    deck_name = custom_deck_name or csv_file_path.stem
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
                if custom_output:
                    output_file = custom_output
                    if not output_file.suffix:
                        output_file = output_file.with_suffix('.apkg')
                else:
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert CSV files to Anki package (.apkg) files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Process all CSV files in input/ folder
  %(prog)s vocab.csv                    # Convert single file
  %(prog)s vocab.csv -o my_deck.apkg    # Convert with custom output name
  %(prog)s vocab.csv -d "My Vocabulary" # Convert with custom deck name
  %(prog)s *.csv                        # Convert multiple files
        """
    )
    
    parser.add_argument(
        'input_files', 
        nargs='*', 
        help='CSV file(s) to convert. If not specified, processes all CSV files in input/ folder'
    )
    
    parser.add_argument(
        '-o', '--output', 
        help='Output file name (for single file conversion only)'
    )
    
    parser.add_argument(
        '-d', '--deck-name', 
        help='Custom deck name (for single file conversion only)'
    )
    
    parser.add_argument(
        '--output-dir', 
        default='output',
        help='Output directory (default: output/)'
    )
    
    return parser.parse_args()

def main():
    """Main function with argument parsing support"""
    args = parse_arguments()
    
    # Set up directories
    script_dir = Path(__file__).parent
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = script_dir / output_dir
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Determine input files
    if args.input_files:
        # Process specified files
        csv_files = []
        for file_pattern in args.input_files:
            file_path = Path(file_pattern)
            if not file_path.is_absolute():
                file_path = script_dir / file_path
            
            if file_path.exists() and file_path.suffix.lower() == '.csv':
                csv_files.append(file_path)
            elif '*' in str(file_path):
                # Handle glob patterns
                csv_files.extend(script_dir.glob(file_pattern))
            else:
                print(f"⚠️  File not found or not a CSV: {file_pattern}")
        
        if not csv_files:
            print("❌ No valid CSV files found")
            sys.exit(1)
    else:
        # Process all files in input directory (default behavior)
        input_dir = script_dir / "input"
        
        if not input_dir.exists():
            print(f"❌ Input directory not found: {input_dir}")
            print("Please create an input/ folder or specify CSV files as arguments")
            sys.exit(1)
        
        csv_files = list(input_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"⚠️  No CSV files found in {input_dir}")
            print("Please add CSV files to the input folder or specify files as arguments")
            sys.exit(1)
    
    # Handle single file with custom options
    if len(csv_files) == 1 and (args.output or args.deck_name):
        csv_file = csv_files[0]
        custom_output = None
        custom_deck_name = args.deck_name or csv_file.stem
        
        if args.output:
            custom_output = Path(args.output)
            if not custom_output.is_absolute():
                custom_output = output_dir / custom_output
        
        print(f"Converting single file: {csv_file.name}")
        success = csv_to_apkg(csv_file, output_dir, custom_output, custom_deck_name)
        
        if success:
            print("🎉 Conversion complete!")
        else:
            print("❌ Conversion failed!")
            sys.exit(1)
    else:
        # Batch processing
        if args.output or args.deck_name:
            print("⚠️  Custom output name and deck name are only supported for single file conversion")
        
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
