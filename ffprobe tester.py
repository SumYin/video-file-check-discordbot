import os
import subprocess
from typing import NamedTuple
import json

from tkinter import *
from tkinter.filedialog import askopenfilename

def browse_file():
    file_path = askopenfilename()
    print(check_video(file_path))

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
def check_video(file_path):
    try:
        videoProperties = {}
        
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
                try:
                    fps = round(float(int(stream.get("nb_read_frames", 0)) / float(stream.get("duration", 0))), 2)
                    videoProperties["file_framerate"] = fps
                except:
                    videoProperties["file_framerate"] = "null"
    
                # codec (string)
                codec = str(stream.get("codec_name", "unknown"))
                videoProperties["file_codec"] = codec
    
        # debug
        videoProperties["raw"] = streams

        return videoProperties
    
    except Exception as e:
        print(e)
        raise e

root = Tk()
root.title("Video Validator")
root.geometry('150x100')
root.resizable(False, False)

browseButton = Button(root, width=10, text = "Browse...", command=browse_file)
browseButton.grid(column=1, row=1, padx=(30,30), pady=(30,30))

root.mainloop()