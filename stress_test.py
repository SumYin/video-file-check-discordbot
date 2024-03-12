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
        print(data)

# Run the async function
asyncio.run(run_check_video())