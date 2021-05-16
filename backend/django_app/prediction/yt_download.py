# importing the module
from pytube import YouTube
import argparse
import uuid

class YouTubeDownloader():
	file_size = -1
	video = None
	yt = None
	percent = 0
	complete_callback = None
	progress_callback = None

	def __init__(self, on_complete=None, on_progress=None):
		if on_complete is None:
			on_complete = self.complete_func
		self.complete_callback = on_complete

		if on_progress is None:
			on_progress = self.progress_func
		self.progress_callback = on_progress
		

	def progress_func(self, stream, data_chunks, bytes_remaining):
		import sys
		bar_len = 100
		self.percent = (self.file_size - bytes_remaining) / self.file_size * 100
		bar = '*' * int(round(self.percent)) + '.' * (bar_len - int(round(self.percent)))
		sys.stdout.write("\rProgress [{}] {:.2f}%".format(bar, self.percent))
		sys.stdout.flush()

	def complete_func(self, stream, file_path):
		self.percent = 100
		print("\nComplete in YT DOWNLOADER! Wrote file to: %s" % file_path)

	def download(self, urls, token):
		for url in urls:
			self.yt = YouTube(url, on_progress_callback=self.progress_callback, on_complete_callback=self.complete_callback,)
			self.video = self.yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
			self._print_metadata(self.yt, url)
			self.file_size = self.video.filesize
			self.video.download(output_path="tmp/", filename=token)

	def _print_metadata(self, yt, url):
		print("\nDownloading video from URL: %s" % url)
		print("---- Title: %s" % yt.title)
		print("---- Author: %s" % yt.author)
		print("---- Views: %d" % yt.views)
		print("---- Channel URL: %s" % yt.channel_url)
		print("---- Length: %d seconds" % yt.length)
		print("---- Thumbnail URL: %s" % yt.thumbnail_url)
		print("---- Description: %s" % yt.description)
		print("\n")


def main():
	parser = argparse.ArgumentParser(description='Download a video from YouTube given a URL')
	parser.add_argument('urls', metavar='URLS', type=str, nargs='+', help='the url of the video to download')
	args = parser.parse_args()
	downloader = YouTubeDownloader()
	downloader.download(args.urls)


if __name__=="__main__":
	main()
