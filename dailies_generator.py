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
import subprocess

from PIL import Image, ImageDraw, ImageFont
from datetime import date

FONT_PATH = "/usr/share/fonts/open-sans/OpenSans-Bold.ttf"

# Fills in the dailies template
def template_fill(version_dir_path, root_path, path_split):
    # Full path of the dailies template
    template = Image.open(f"/{root_path}/dailies_template.png")

    # Last item in list is version, -3 -2 is the Seq and Shot
    version_text = path_split[-1]
    name_text = f"{path_split[-3]} : {path_split[-2]}"

    # Initializing font to use with path and size
    large_font = ImageFont.truetype(FONT_PATH, size=120)
    small_font = ImageFont.truetype(FONT_PATH, size=60)

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

    # Set the name of the output file
    template_output = f"{version_dir_path}/0000.png"

    # Save the output file as png
    template.save(template_output, format="PNG")

# Create a 5 second video of the dailies template
def create_dailies_template_intro_card(version_dir_path):
    command = [
        "ffmpeg", 
        "-loop", "1",                               # Loop the input image
        "-i", f"{version_dir_path}/0000.png",       # Input image file
        "-c:v", "libx264",                          # Specify the video codec
        "-t", "5",                                  # Duration of the video
        "-pix_fmt", "yuv420p",                      # Ensure compatibility with most players
        f"{version_dir_path}/template_intro_card.mp4"   # Output video file
    ]

    # Tries to run the ffmpeg command with subprocess
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e: # Raised when exit with a non-zero status
        print(f"Error: {e}")

# Creates an mp4 from a sequence of PNG images
def create_video_from_img_sequence(version_dir_path, path_split):
    input_pattern = f"{version_dir_path}/%04d.png" # 0000.png
    video_name = f"{path_split[-3]}_{path_split[-2]}_{path_split[-1]}.mp4" # Seq#_Shot#_v#.mp4

    # ffmpeg command 
    command = [
        "ffmpeg",
        "-framerate", "24",                 # Frame rate 24 fps
        "-i", input_pattern,                # Input pattern is the files 0001... in verrsion dir
        "-vf",                              # Video filter draw: video name, timestamp, frame number
        f"""
            drawtext=fontfile={FONT_PATH}:text='{video_name}':x=10:y=10:fontsize=30:fontcolor=white,
            drawtext=fontfile={FONT_PATH}:text='%{{pts\\:hms}}':x=0:y=65:fontsize=30:fontcolor=white,
            drawtext=fontfile={FONT_PATH}:text='Frame\\: %{{n}}':x=7:y=100:fontsize=26:fontcolor=white
        """,
        "-c:v", "libx264",                  # Video codec
        "-pix_fmt", "yuv420p",              # Ensure compatibility with most players
        f"{version_dir_path}/{video_name}"  # Output video file
    ]

    # Tries to run the ffmpeg command with subprocess
    try:
        subprocess.run(command, check=True) # check=True : checks exit with a non-zero status
    except subprocess.CalledProcessError as e: # Raised when exit with a non-zero status
        print(f"Error: {e}")

    return video_name

# Concatenates two videos into one using ffmpeg
def combine_intro_card_and_version_video(version_dir_path, video_name, output_path):
    command = [
        "ffmpeg",
        "-i", f"{version_dir_path}/template_intro_card.mp4", # First input video
        "-i", f"{version_dir_path}/{video_name}",            # Second input video
        "-filter_complex",                                  # Advanced export options
        "[0:v:0][1:v:0]concat=n=2:v=1:a=0[outv]",           # Concatenate first and second video
        "-map", "[outv]",                                   # Map the concatenated video stream to the output file
        "-c:v", "libx264",                                  # Set the video codec to H.264
        "-crf", "23",                                       # Specify CRF (lower is higher quality)
        "-preset", "slow",                                  # Use slower preset for better quality
        "-pix_fmt", "yuv420p",                              # Pixel format
        f"{output_path}/{video_name}"                       # Output full path
    ]

    # Tries to run the ffmpeg command with subprocess
    try:
        subprocess.run(command, check=True)  # check=True : checks exit with a non-zero status
        print(f"Video saved: {output_path}/{video_name}")
    except subprocess.CalledProcessError as e: # Raised when exit with a non-zero status
        print(f"Error: {e}")

# Adds audio to a video using ffmpeg
def add_audio(version_dir_path, video_name, output_path, path_split):
    # Gets the shot directory path
    shot_dir_path = os.path.dirname(version_dir_path.rstrip('/')) + "/"
    
    # Gets the audio file path from the shot directory
    audio_path = f"{shot_dir_path}{path_split[-3]}_{path_split[-2]}_audio.wav"

    # Gets the video name from output with no extension
    video_no_ext = os.path.splitext(os.path.basename(video_name))[0]

    command = [
        "ffmpeg",
        "-i", f"{output_path}/{video_name}",                # Input video file
        "-i", audio_path,                                   # Input audio file
        "-filter_complex", "adelay=5000|5000[aud]",         # Add 5s delay to audio
        "-map", "0:v",                                      # Map video stream from the first input
        "-map", "[aud]",                                    # Map audio stream from the second input
        "-c:v", "copy",                                     # Copy the video stream without re-encoding
        "-shortest",                                        # End output when the shortest stream finishes
        f"{output_path}/{video_no_ext}_audio.mp4"           # Output file path
    ]

    # Tries to run the ffmpeg command with subprocess
    try:
        subprocess.run(command, check=True) # check=True : checks exit with a non-zero status
    except subprocess.CalledProcessError as e:
        if e.returncode == 254: # Exit 254 if the audio file is not found 
            print(f"No audio file found: {audio_path}")
        else:
            print(f"Error: {e}")

# Removes the temporary png and videos used to create the dailies video
def file_cleanup(version_dir_path, video_name, output_path, audio_choice):
    template_png = f"{version_dir_path}/0000.png"
    template_video = f"{version_dir_path}/template_intro_card.mp4"
    img_seq_video = f"{version_dir_path}/{video_name}"

    delete_files = [template_png, template_video, img_seq_video]
    
    # If there is audio delete the output folder img seq video with audio
    if audio_choice == "y":
        vid_no_audio = f"{output_path}/{video_name}"
        delete_files.append(vid_no_audio)
    else:
        pass
    
    # rm on a list of file paths
    try:
        subprocess.run(["rm"] + delete_files, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def main():
    # Print error message and exit unless a single argument is given
    if len(sys.argv) != 2:
        print("Usage: ./script.py <version directory>")
        sys.exit(1)

    # Full path of the passed dir
    version_dir_path = sys.argv[1]

    # Check to see if there is audio to add
    while True:
        audio_choice = input("Do you wish to add an audio file? (y/n): ")

        if audio_choice.lower() == "y":
            audio_choice = "y"
            break
        elif audio_choice.lower() == "n":
            audio_choice = "n"
            break
        else:
            continue
        
    # Split the path into a list eg. ["home", "user", "Documents"]
    path_split = version_dir_path.strip(os.sep).split(os.sep)

    # Gets the root folder path
    root_path = "/".join(path_split[:-3])

    # Path for the dailies outputs
    output_path = f"/{root_path}/output"

    template_fill(version_dir_path, root_path, path_split)
    create_dailies_template_intro_card(version_dir_path)
    video_name = create_video_from_img_sequence(version_dir_path, path_split)
    combine_intro_card_and_version_video(version_dir_path, video_name, output_path)
    
    # If there is audio to add run the add audio function
    if audio_choice == "y":
        add_audio(version_dir_path, video_name, output_path, path_split)

    file_cleanup(version_dir_path, video_name, output_path, audio_choice)

if __name__ == "__main__":
   main()