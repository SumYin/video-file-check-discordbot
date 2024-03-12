import os
import subprocess
from typing import NamedTuple
import json
import aiohttp

# file download
async def download_video(attached_file):
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
    "-show_format",
    "-show_streams",
    "-count_frames",
    file_path]

    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    return FFProbeResult(return_code=result.returncode,
                        json=result.stdout,
                        error=result.stderr)

#check/return video data
async def check_video(file_path, debug=False):
    videoProperties = {}
    
    videoProperties["file_path"] = file_path
    
    data = json.loads(ffprobe(file_path).json)
    streams = data.get("streams", [])

    for stream in streams:
        if stream.get("codec_type") == "video":

            # file size (float)
            videoProperties["file_size"] = round(os.stat(file_path).st_size / (1024 * 1024), 2)

            # file type (string)
            videoProperties["file_type"] = str(os.path.splitext(file_path)[1])

            # resolution (int, int)
            videoProperties["file_resolution"] = (int(stream.get("width", 0)), int(stream.get("height", 0)))

            # frame count (int)
            frameCount = int(stream.get("nb_read_frames", 0))
            videoProperties["file_framecount"] = frameCount

            # frame rate (float)
            if 'duration' in stream: #duration not always present
                if frameCount == 0 or float(stream.get("duration")) == 0:
                    fps = 0
                else:
                    fps = round(float(frameCount / float(stream.get("duration", 0))), 2)
            elif stream.get("avg_frame_rate"):
                fps = stream.get("avg_frame_rate").split("/")[0]
            else:
                fps = "undefined"

            videoProperties["file_framerate"] = fps

            # codec (string)
            codec = str(stream.get("codec_name", "unknown"))
            videoProperties["file_codec"] = codec

    # debug
    if debug == True:
        videoProperties["raw"] = streams
    
    # error
    if len(videoProperties) == 0: # dictionary is empty
        videoProperties["error"] = "Couldn't analyze file."

    return videoProperties