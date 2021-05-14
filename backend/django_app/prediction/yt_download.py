# importing the module
from pytube import YouTube

def progress_func(stream, data_chunks, bytes_remaining):
	print("Progress: {:.2f}%".format((FILE_SIZE - bytes_remaining) / FILE_SIZE * 100))

def complete_func(stream, file_path):
	print("Completed, path: %s" % file_path)

YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()
yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo', on_progress_callback=progress_func, on_complete_callback=complete_func,)
video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
FILE_SIZE = video.filesize
video.download()
