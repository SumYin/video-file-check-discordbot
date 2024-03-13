import os
import subprocess
from typing import NamedTuple
import json
import aiohttp
import requests

# attachment download
async def download_attachment(attached_file):
    async with aiohttp.ClientSession() as session:
        async with session.get(attached_file.url) as response:
            file_path = os.path.join("./videos", f"{attached_file.id}_{os.path.basename(attached_file.filename).split('?')[0]}")
            with open(file_path, "wb") as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)
    return file_path

# link download
async def download_link(linked_file, id):
    try:
        response = requests.get(linked_file)
        file_name = f"{id}_{os.path.basename(linked_file).split('?')[0]}"
        file_path = os.path.join("./videos", file_name)

        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path

    except Exception as e: # can occur due to network or server connectivity issues
        print(f"Error downloading video: {str(e)}")
        return f"Error downloading video: {str(e)}"

# data class for ffprobe output
class FFProbeResult(NamedTuple):
    return_code: int
    json: str
    error: str

# ffprobe command
def ffprobe(file_path) -> FFProbeResult:
    command_array = ["ffprobe",
    "-v", "quiet",
    "-print_format", "json",
    "-show_streams",
    "-select_streams", "v:0",
    "-count_frames",
    file_path]

    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return FFProbeResult(return_code=result.returncode, json=result.stdout, error=result.stderr)

# analyze video data
async def check_video(file_path):
    videoProperties = {}

    # path (string)
    videoProperties["file_path"] = file_path

    # raw data (string)
    rawData = ffprobe(file_path).json
    videoProperties["raw"] = rawData

    # size (float)
    videoProperties["file_size"] = round(os.stat(file_path).st_size / (1024 * 1024), 2)

    # type (string)
    videoProperties["file_type"] = str(os.path.splitext(file_path)[1])

    try:
        data = json.loads(rawData)
        stream = data.get("streams")[0]

        # resolution (int, int)
        videoProperties["file_resolution"] = (int(stream.get("width", 0)), int(stream.get("height", 0)))

        # frame count (int)
        frameCount = int(stream.get("nb_read_frames", 0))
        videoProperties["file_framecount"] = frameCount

        # frame rate (float)
        fps = round(float(stream.get("avg_frame_rate", 0).split("/")[0]) / float(stream.get("avg_frame_rate", 0).split("/")[1]), 2)
        videoProperties["file_framerate"] = fps

        # codec (string)
        codec = str(stream.get("codec_name", "unknown"))
        videoProperties["file_codec"] = codec
        
    except Exception as e: #can occur for a large variety of reasons related to ffprobe's inability to parse all files, especially corrupt ones
        videoProperties["error"] = "Couldn't analyze video."
        print(f"Couldn't analyze video: {str(e)} ")

    return videoProperties