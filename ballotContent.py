import io
import csv
import tkinter as tk
from zipfile import ZipFile
from tkinter.filedialog import askopenfilename

def runtimeToReadable(runtime):
    [h,m,s] = map(int, runtime.split(':'))
    return '{}h{}m'.format(h,m)

def main():
    root = tk.Tk()
    root.withdraw()
    filepath = askopenfilename()

    zipcsv = ZipFile(filepath)
    zipname = zipcsv.namelist()[0]
    suggestions = []
    with io.StringIO(zipcsv.read(zipname).decode('utf-8')) as csvfile:
        reader = csv.DictReader(csvfile)

        for entry in list(reader):
            suggestions.append({
                'title': entry['Name of Movie'],
                'synopsis': entry['Spoiler Free Synopsis'].replace('\n',' ').strip(),
                'runtime': entry['Runtime'],
                'release': entry['Release Year'],
                'notes': entry['General Notes']
            })

    output = []
    output.append(', '.join([suggestion['title'] for suggestion in suggestions]))
    output.append('\n\n'.join(['{} - {}{}'.format(suggestion['title'], suggestion['synopsis'], ' (notes: {})'.format(suggestion['notes']) if suggestion['notes'] else "") for suggestion in suggestions]))
    output.append('\n'.join(['{} ({}, {})'.format(suggestion['title'], suggestion['release'], runtimeToReadable(suggestion['runtime'])) for suggestion in suggestions]))
    output = '\n\n\n'.join(output)
    with open('latestBallot.txt', 'w', encoding='utf-8') as outfile:
        outfile.write(output)

if __name__ == "__main__":
    main()