import os
from PIL import Image
import io
from moviepy.editor import VideoFileClip
import numpy as np

UPLOAD_FOLDER = 'static/files'

def resize_image_service(image, fixed_height):
    try:
        width, height = image.size
        new_width = int((width / height) * fixed_height)
        new_height = fixed_height
        resized_image = image.resize((new_width, new_height))
        return resized_image
    except Exception as e:
        print("Error:", e)
        return None

def convert_to_gif_service(video_path):
    video = VideoFileClip(video_path)
    gif_path = os.path.splitext(video_path)[0] + '.gif'
    video.write_gif(gif_path)
    return gif_path
