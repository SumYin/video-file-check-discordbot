from tkinter import *
from tkinter.filedialog import askopenfilename
import asyncio

from video_check import *

# get all test files
directory = './test-data'
file_paths = []

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    file_paths.append(file_path)

# local file browsing
async def browse_file():
    file_path = askopenfilename()
    data = await check_video(file_path)
    print_data(data)

# check all files in sample folder
async def batch_check():
    for file_path in file_paths:
        data = await check_video(file_path)
        print_data(data)

def print_data(data):
    print("\n")
    print(data.get("file_path"))
    print(data.get("file_size"))
    print(data.get("file_type"))
    print(data.get("file_resolution"))
    print(data.get("file_framecount"))
    print(data.get("file_framerate"))
    print(data.get("file_codec"))
    print(data.get("error"))
    print(data.get("raw"))

# window
root = Tk()
root.title("Video Validator")
root.geometry('140x140')
root.resizable(False, False)

browseButton = Button(root, width=10, text = "Browse", command=lambda: asyncio.run(browse_file()))
browseButton.grid(column=1, row=1, padx=(30,30), pady=(30,0))

batchButton = Button(root, width=10, text = "Batch Test", command=lambda: asyncio.run(batch_check()))
batchButton.grid(column=1, row=2, padx=(30,30), pady=(30,0))

root.mainloop()