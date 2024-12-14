#!/usr/bin/env python3

"""
Script Name: Generate Dailies
Description: Automates the generation of dailies for VFX/animation workflows.
Author: Hayden Guy
Date: 2024-12-14
Version: 1.0
"""

import sys
import os

from PIL import Image, ImageDraw, ImageFont
from datetime import date

# Print error message and exit unless a single argument is given
if len(sys.argv) != 2:
    print("Usage: ./script.py <version directory>")
    sys.exit(1)

# Full path of the passed dir
version_dir_path = sys.argv[1]

# Split the path into a list eg. ["home", "user", "Documents"]
path_split = version_dir_path.strip(os.sep).split(os.sep)

# Last item in list is version, -3 -2 is the Seq and Shot
version_text = path_split[-1]
name_text = f"{path_split[-3]} : {path_split[-2]}"

# Location of the dailies template
template = Image.open("/home/hayden/Downloads/dailies/dailies_template.jpg")

# Initializing font to use with path and size
font_path = "/usr/share/fonts/open-sans/OpenSans-Bold.ttf"
large_font = ImageFont.truetype(font_path, size=120)
small_font = ImageFont.truetype(font_path, size=60)

# Initialize drawing on the template
draw = ImageDraw.Draw(template)

# Get current date and convert to YYYY-MM-DD
current_date = date.today()
date_text = current_date.strftime("%Y-%m-%d")

# Positions of where to draw on the template
date_pos = (240, 75)
version_pos = (1400, 75)
name_pos = (240, 310)
notes_pos = (240, 600)

# Notes text, char limit and count for max notes (<= 5)
notes_text = ""
char_limit = 40
count = 0

print(f"\nEnter your notes; max 5, char limit {char_limit}")
print("Press Enter on an empty line to finish\n")

# Add note to the notes_text if count less than 5
while count < 5:
   note = str(input(f"Enter note (max {char_limit} characters): "))

   if len(note) > char_limit: # Error message if exceeding char limit
       print(f"Input exceeds {char_limit} characters")
   elif note == "": # Exit loop if enter is pressed on empty note
       break
   else: # Add "- Note text" <newline> and increment count
    notes_text += " - " + note + "\n"
    count += 1

# Draws on the template with given position, text, colour, and font size
draw.text(date_pos, date_text, fill="black", font=large_font)
draw.text(version_pos, version_text, fill="black", font=large_font)
draw.text(name_pos, name_text, fill="black", font=large_font)
draw.text(notes_pos, notes_text, fill="black", font=small_font)

template.show() # Placeholder to show the image once drawing has happened