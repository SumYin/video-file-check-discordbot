import os
import subprocess
from typing import NamedTuple
import json
import os
import aiohttp

# data_format={
#         "file_size": float,
#         "file_type": str,
#         "file_resolution": (int,int),
#         "file_framecount": int,
#         "file_framerate": float,
#         "file_codec": str,
#     }

#download the video/file
async def download_video(attached_file):
    try:
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
    except Exception as e:
        print(e)
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

#check/return video data
async def check_video(file_path):
    try:
        videoProperties = {}
        
        data = json.loads(ffprobe(file_path).json)
        streams = data.get("streams", [])


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
                try:
                    fps = float(int(stream.get("nb_frames", 0)) / float(stream.get("duration", 0)))
                    videoProperties["file_framerate"] = fps
                except:
                    videoProperties["file_framerate"] = "Null"
    
                # codec
                codec = str(stream.get("codec_name", "unknown"))
                videoProperties["file_codec"] = codec
    
        return videoProperties
    
    except Exception as e:
        print(e)
        raise e