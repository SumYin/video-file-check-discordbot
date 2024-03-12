import os
from media_check import *
import asyncio

directory = './media-refs_heads_main-test-data'
file_locations = []

# Iterate through the files in the directory
for filename in os.listdir(directory):
    # Get the full file path
    file_path = os.path.join(directory, filename)
    
    # Add the file location to the list
    file_locations.append(file_path)

# Define an async function to run the check_video function on each file location
async def run_check_video():
    for file_location in file_locations:
        data = await check_video(file_location)
        print(data.get("file_path"))
        print(data.get("file_size"))
        print(data.get("file_type"))
        print(data.get("file_resolution"))
        print(data.get("file_framecount"))
        print(data.get("file_framerate"))
        print(data.get("file_codec"))
        print(data.get("error"))
        print("\n")

# Run the async function
asyncio.run(run_check_video())