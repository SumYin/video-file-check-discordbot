from media_check import *
from tkinter import *
from tkinter.filedialog import askopenfilename
import asyncio

async def browse_file():
    file_path = askopenfilename()
    print(await check_video(file_path,True))

root = Tk()
root.title("Video Validator")
root.geometry('150x100')
root.resizable(False, False)

browseButton = Button(root, width=10, text = "Browse...", command=lambda: asyncio.run(browse_file()))
browseButton.grid(column=1, row=1, padx=(30,30), pady=(30,30))

root.mainloop()