import os
import subprocess
from typing import NamedTuple
import json
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
    file_path]

    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    return FFProbeResult(return_code=result.returncode,
                        json=result.stdout,
                        error=result.stderr)

async def check_video(file_path):
    try:
        videoProperties = {}
        
        data = json.loads(ffprobe(file_path).json)
        streams = data.get("streams", [])
        
        # file name
        videoProperties["file_name"] = os.path.basename(file_path)

        for stream in streams:
            if stream.get("codec_type") == "video":

                # file size
                videoProperties["file_size"] = round(os.stat(file_path).st_size / (1024 * 1024), 2)

                # file type
                videoProperties["file_type"] = str(os.path.splitext(file_path)[1])

                # resolution
                videoProperties["file_resolution"] = (int(stream.get("width", 0)), int(stream.get("height", 0)))

                # frame count
                frameCount = int(stream.get("nb_frames", 0))
                videoProperties["file_framecount"] = frameCount

                # frame rate
                fps = float(int(stream.get("nb_frames", 0)) / float(stream.get("duration", 0)))
                videoProperties["file_framerate"] = fps
    
                # codec
                codec = str(stream.get("codec_name", "unknown"))
                videoProperties["file_codec"] = codec
    
        return videoProperties
    
    except Exception as e:
        return f"Error processing video: {str(e)}", ""