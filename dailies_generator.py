#!/usr/bin/env python3

"""
Script Name: Generate Dailies
Description: Automates the generation of dailies for VFX/animation workflows.
Author: Hayden Guy
Date: 2024-12-14
Version: 1.0
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import date

# Location of the dailies template
template = Image.open("/home/hayden/Downloads/dailies/dailies_template.png")

# Initializing font to use with path and size
font_path = "/usr/share/fonts/open-sans/OpenSans-Bold.ttf"
font = ImageFont.truetype(font_path, size=120)

# Initialize drawing on the template
draw = ImageDraw.Draw(template)

# Get current date and convert to YYYY-MM-DD
current_date = date.today()
date_text = current_date.strftime("%Y-%m-%d")

# Position of where to draw date on the template
date_pos = (225, 75)

# Draws the date on the template with given position, text, colour, and font 
draw.text(date_pos, date_text, fill="black", font=font)

template.show() # Placeholder to show the image once drawing has happened