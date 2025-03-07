import io
import os
import csv
import glob
import tkinter as tk
from zipfile import ZipFile
from tkinter.filedialog import askopenfilename


def acquire_file(manual_select, pattern, path=""):
    """select a .csv.zip file from Google Forms either manually, or by creation date."""
    if manual_select is False:
        files = glob.glob(os.path.join(path, f"{pattern}*.csv*.zip"))
        if not files:
            raise FileNotFoundError(f"No files found in {path}")
        return max(files, key=os.path.getctime)
    else:
        root = tk.Tk()
        root.withdraw()
        return askopenfilename()


def parse_file(filepath):
    """produce a nested list from a csv.zip export from Google Forms."""
    with ZipFile(filepath, "r") as zipfile:
        with zipfile.open(zipfile.namelist()[0], "r") as csvfile:
            reader = csv.reader(io.TextIOWrapper(csvfile, "utf-8"))
            return list(reader)
