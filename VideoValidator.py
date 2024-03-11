import os
from tkinter import *
from ffprobe import FFProbe
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

def browse_file():
    file_path = askopenfilename()
    if file_path:
        properties, notes = check_video(file_path)
    else:
        messagebox.showwarning("No File Selected", "Please select a video file.")

    if notes != "":
        messagebox.showerror("Errors Found", notes)
    else:
        messagebox.showinfo("Video Check", "Video matches targets.")

    outputText.configure(state='normal')
    outputText.delete('1.0', END)
    outputText.insert(END, properties)
    outputText.configure(state='disabled')

def check_video(file_path):
    try:
        videoProperties = ""
        validationNotes = ""

        metadata = FFProbe(file_path).streams[0]

        # frame count
        frameCount = int(metadata.frames())
        videoProperties += "Frame Count: " + str(frameCount) + "\n"

        if int(targetFrameCount.get()) != frameCount:
            validationNotes += "Frame count doesn't match.\n"

        # frame rate
        fps = frameCount / metadata.duration_seconds()
        videoProperties += "Frame Rate: " + str(fps) + "\n"

        if int(targetFrameRate.get()) != fps:
            validationNotes += "Frame rate doesn't match.\n"

        # resolution
        resolution = str(metadata.width) + "x" + str(metadata.height)
        videoProperties += "Resolution: " + resolution + "\n"

        if targetResolution.get() != resolution:
            validationNotes += "Resolution doesn't match.\n"

        # codec
        codec = str(metadata.codec()).lower()
        videoProperties += "Codec: " + metadata.codec() + "\n"

        if (targetCodec.get().lower().replace(".","") != codec):
            validationNotes += "Codec doesn't match.\n"

        # file size
        size = round(os.stat(file_path).st_size / (1024 * 1024), 2)
        videoProperties += "File Size: " + str(size) + "MB" + "\n"

        if int(targetFileSize.get()) < size:
            validationNotes += "File size is too big.\n"

        # file extension
        extension = str(os.path.splitext(file_path)[1]).lower().replace(".","")
        videoProperties += "File Extension: " + extension

        if targetFileExtension.get().lower().replace(".","") != extension:
            validationNotes += "File extension doesn't match doesn't match."
    
        return videoProperties, validationNotes
    
    except Exception as e:
        return f"Error processing video: {str(e)}", ""

# window
root = Tk()
root.title("Video Validator")
root.geometry('400x320')
root.resizable(False, False)

paddingY = 8

# frame count input
targetFrameCount = StringVar()

frameCountLabel = Label(root, text = "Target Frame Count")
frameCountLabel.grid(column=1, row=1, sticky="e", padx=(10, 5), pady=(paddingY, paddingY))
frameCountInput = Entry(root, width=10, textvariable=targetFrameCount)
frameCountInput.grid(column=2, row=1)

targetFrameCount.set("120")

# frame rate input
targetFrameRate = StringVar()

frameRateLabel = Label(root, anchor="w", text = "Target Frame Rate")
frameRateLabel.grid(column=1, row=2, sticky="e", padx=(10, 5), pady=(paddingY, paddingY))
frameRateInput = Entry(root, width=10, textvariable=targetFrameRate)
frameRateInput.grid(column=2, row=2)

targetFrameRate.set("24")

# resolution input
targetResolution = StringVar()

resolutionXLabel = Label(root, text = "Target Resolution HxV")
resolutionXLabel.grid(column=1, row=3, sticky="e", padx=(10, 5), pady=(paddingY, paddingY))
resolutionXInput = Entry(root, width=10, textvariable=targetResolution)
resolutionXInput.grid(column=2, row=3)

targetResolution.set("1080x1920")

# codec input
targetCodec = StringVar()

codecLabel = Label(root, text = "Target Codec")
codecLabel.grid(column=1, row=4, sticky="e", padx=(10, 5), pady=(paddingY, paddingY))
codecInput = Entry(root, width=10, textvariable=targetCodec)
codecInput.grid(column=2, row=4)

targetCodec.set("h264")

# file size input
targetFileSize = StringVar()

fileSizeLabel = Label(root, text = "Maximum File Size (in MB)")
fileSizeLabel.grid(column=1, row=5, sticky="e", padx=(10, 5), pady=(paddingY, paddingY))
fileSizeInput = Entry(root, width=10, textvariable=targetFileSize)
fileSizeInput.grid(column=2, row=5)

targetFileSize.set("100")

# file extension input
targetFileExtension = StringVar()

fileExtensionLabel = Label(root, text = "Target File Extension")
fileExtensionLabel.grid(column=1, row=6, sticky="e", padx=(10, 5), pady=(paddingY, paddingY))
fileExtensionInput = Entry(root, width=10, textvariable=targetFileExtension)
fileExtensionInput.grid(column=2, row=6)

targetFileExtension.set("mp4")

# browse button
browseButton = Button(root, width=10, text = "Browse...", command=browse_file)
browseButton.grid(column=1, columnspan=3, row=7, pady=(45,0))

# output
outputText = Text(root, spacing3=23, width=20, height=6)
outputText.insert(END, "File info...")
outputText.configure(font =("TkDefaultFont", 9))
outputText.configure(state='disabled')
outputText.grid(column=3, row=1, rowspan=7, sticky="nw", padx=(10, 10), pady=(paddingY, paddingY))

root.mainloop()