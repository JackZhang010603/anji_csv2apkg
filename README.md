# anji_csv2apkg

Convert CSV files to Anki flashcards (.apkg)

## Usage

### Batch Processing (Default)
```bash
python csv2apkg.py                    # Process all CSV files in input/ folder
```

### Single File Conversion
```bash
python csv2apkg.py vocab.csv          # Convert single file
python csv2apkg.py vocab.csv -o my_deck.apkg    # Custom output name
python csv2apkg.py vocab.csv -d "My Vocabulary" # Custom deck name
```

### Multiple Files
```bash
python csv2apkg.py file1.csv file2.csv  # Convert specific files
python csv2apkg.py *.csv                # Convert all CSV files in current directory
```

## CSV Format
```
word,meaning
apple,red fruit
book,reading material
```

## Requirements
```
pip install genanki
```