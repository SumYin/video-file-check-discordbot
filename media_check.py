import os
from tkinter import *
from ffprobe import FFProbe
import requests

# data_format={
#         "file_name": str,
#         "file_size": float,
#         "file_type": str,
#         "file_resolution": (int,int),
#         "file_framecount": int,
#         "file_framerate": float,
#         "file_codec": str,
#     }

async def download_video(url, id):
    try:
        response = requests.get(url)
        #remove things after the ? in the name
        file_name = f"{id}_{os.path.basename(url).split('?')[0]}"
        file_path = os.path.join("./videos", file_name)

        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path
    except Exception as e:
        return f"Error downloading video: {str(e)}"


async def check_video(file_path):
    try:
        videoProperties = {}
        
        metadata = FFProbe(file_path).streams[0]

        
        videoProperties["file_name"] = os.path.basename(file_path)

        # frame count
        videoProperties["file_framecount"] = int(metadata.frames())

        # frame rate
        videoProperties["file_framerate"] = videoProperties["file_framecount"] / metadata.duration_seconds()

        # resolution
        videoProperties["file_resolution"] = (int(metadata.width), int(metadata.height))

        # codec
        videoProperties["file_codec"] = str(metadata.codec()).lower()

        # file size
        videoProperties["file_size"] = round(os.stat(file_path).st_size / (1024 * 1024), 2)

        # file extension
        videoProperties["file_type"] = str(os.path.splitext(file_path)[1]).lower().replace(".","")
    
        return videoProperties
    
    except Exception as e:
        return f"Error processing video: {str(e)}", ""