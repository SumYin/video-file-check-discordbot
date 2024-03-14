import os
import subprocess
from typing import NamedTuple
import json
import aiohttp
import requests
import time

# get host data
f = open('host.json')
host = json.load(f)
max_size = host.get("max_upload_size", 100)
max_time = host.get("max_upload_time", 60)

# attachment download
async def download_attachment(attached_file):
    error = ""

    async with aiohttp.ClientSession() as session:
        async with session.get(attached_file.url) as response:
            file_path = os.path.join("./videos", f"{attached_file.id}_{os.path.basename(attached_file.filename).split('?')[0]}")

            size = 0
            start = time.time()

            with open(file_path, "wb") as file:
                while True:
                    chunk = await response.content.read(1024)

                    # timeout
                    if time.time() - start > max_time:
                        error = "Download took too long."
                        break

                    # size limit
                    size += len(chunk)
                    if size > max_size:
                        error = "File is too large."
                        break

                    if not chunk:
                        break
                    file.write(chunk)
    
    # raise error outside of file write so that it's not used by system
    if error != "":
        os.remove(file_path)
        raise ValueError(error)

    return file_path

# link download
async def download_link(linked_file, id):
    r = requests.get(linked_file, stream=True)

    file_name = f"{id}_{os.path.basename(linked_file).split('?')[0]}"
    file_path = os.path.join("./videos", file_name)

    size = 0
    start = time.time()

    for chunk in r.iter_content(1024):
        # timeout
        if time.time() - start > max_time:
            raise ValueError("Download took too long.")
            return
        
        # size limit
        size += len(chunk)
        if size > max_size:
            raise ValueError("File is too large.")
            return

    with open(file_path, "wb") as file:
        file.write(r.content)
    return file_path

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

    # path
    videoProperties["file_path"] = file_path

    # raw data
    rawData = ffprobe(file_path).json
    videoProperties["raw"] = rawData

    # size
    videoProperties["file_size"] = round(os.stat(file_path).st_size / (1024 * 1024), 2)

    # type
    videoProperties["file_type"] = str(os.path.splitext(file_path)[1])

    data = json.loads(rawData)
    stream = data.get("streams")[0]

    # resolution
    videoProperties["file_resolution"] = str((stream.get("width", "unknown width"))) + "x" + str(stream.get("height", "unknown height"))

    # frame count
    frameCount = str(stream.get("nb_read_frames", "unknown"))
    videoProperties["file_framecount"] = frameCount

    # frame rate
    fps = round(float(stream.get("avg_frame_rate", 0).split("/")[0]) / float(stream.get("avg_frame_rate", 0).split("/")[1]), 2)
    if fps == 0:
        fps = "unknown"
    videoProperties["file_framerate"] = fps

    # codec
    codec = str(stream.get("codec_name", "unknown"))
    videoProperties["file_codec"] = codec

    return videoProperties