from enum import Enum
import integv


class InputType(Enum):
    JPEG = 'jpeg',
    PNG = 'png',
    MP4 = 'mp4',


def get_input_type(file):
    """
    Verifies a given file isn't corrupt and gets the MIME type,
    returns an InputType
    """
    if not integv.verify(file, file_type=file.content_type):
        raise IOError("Unable to verify file, it may be corrupt.")
    mime = str(file.content_type)
    if "image" in mime:
        if "jpeg" in mime:
            return _validate_jpeg(file)
        elif "png" in mime:
            return _validate_png(file)
    elif "video" in mime:
        if "mp4" in mime:
            return _validate_mp4(file)


def _validate_jpeg(file):
    return InputType.JPEG


def _validate_png(file):
    # return InputType.PNG
    return None


def _validate_mp4(file):
    return InputType.MP4
