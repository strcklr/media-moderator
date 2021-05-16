from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
import prediction.verify as verify
from prediction.state_enum import State
import threading
import uuid

def save_to_disk(file):
    """
    Saves a given file to disk
    :param file: UploadedFile to save to disk
    :return: the path to the file
    """
    import os
    if not os.path.isdir(settings.MEDIA_ROOT + 'tmp/'):
        os.mkdir(settings.MEDIA_ROOT + 'tmp/')

    with default_storage.open('tmp/' + file.name, 'wb+') as destination:
        print("Destination: %s" % repr(destination))
        for chunk in file.chunks():
            destination.write(chunk)

    return os.path.join(settings.MEDIA_ROOT, 'tmp/' + file.name)


class FileHandler(APIView):
    token = None
    state = {
        "progress": "not_started"
    }
    status = 200
    urls = None

    def progress_func(self, stream, data_chunks, bytes_remaining):
        bar_len = 100
        percent = (self.yt.file_size - bytes_remaining) / self.yt.file_size * 100
        self.state['progress'] = percent
        self.state['state'] = "in progress"
        self.state['token'] = self.token
        self.status = 202

    def complete_func(self, stream, file_path):
        print("\nComplete! Wrote file to: %s" % file_path)
        self.state['progress'] = 100
        self.state['state'] = "complete"
        self.state['path'] = file_path
        self.state['token'] = self.token
        self.status = 200
        # self.classify_video(file_path)

    def _process(self, data):
        """
        Processes the HTTP request data
        :param data: the HTTPRequest.data to be processed
        :return: an HTTPResponse
        """
        if 'file' in data:
            file = data['file']
            try:
                itype = verify.get_input_type(file)
            except IOError as e:
                print(e)
                self.state = {
                    "error": "Failed to verify file, likely due to the file being corrupt."
                }
                self.status=400
            try:
                if itype == verify.InputType.JPEG:
                    return self.classifier.classify_image(file)
                elif itype == verify.InputType.MP4:
                    path = save_to_disk(file)
                    self.classifier.classify_video(path)
                else:
                    self.state = {
                        "error": "File type is not supported!",
                        "file": file.name
                    }
                    self.status=400
            except Exception as e:
                print(e)
                self.state = {
                    "message": "An unexpected error has ocurred!",
                    "error": repr(e),
                }
                self.status = 500

        elif self.urls is not None:
            from prediction.yt_download import YouTubeDownloader
            import asyncio
            try:
                self.yt = YouTubeDownloader(on_complete=self.complete_func, on_progress=self.progress_func)
                self.yt.download(self.urls, self.token)
            except Exception as e:
                self.state = {
                    "error": str(e)
                }
                self.status = 500
    
    def post(self, request, format=None):
        import sys
        if self.status == 202: # In Progress, TODO use HTTP status definitions
            return Response({
                "message": "Download already in progress!",
            }, status=self.status)

        self.token = str(uuid.uuid4())
        if "youtube-url" in request.data:
            self.state = {
                "progress": 0,
                "state": "in_progress",
                "token": self.token
            }
            self.status = 202
            self.urls = [request.data["youtube-url"]]
        thread = threading.Thread(target=self._process, args=(request.data))
        thread.daemon = True
        thread.start()
        return Response(self.state, status=self.status)

    def get(self, request):
        """
        Returns the progress and state of the YouTube download.
        :param request: the GET request, ignored
        :return: a dictionary with the state of the download of the YouTube video
        """
        return Response(self.state, status=self.status)