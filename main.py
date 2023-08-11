from flask import Flask, request, jsonify, send_file
import os

from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import io
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip,TextClip, CompositeVideoClip
from pydub import AudioSegment
import moviepy.editor as mp
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})

@app.route('/get-snapshot', methods=['POST'])
def get_snapshot():
    try:
        video = request.files['file']

        if video and video.filename.endswith(('.mp4', '.avi', '.mov')):
            video_path = 'input_video.mp4'
            video.save(video_path)

            video_clip = VideoFileClip(video_path)
            snapshot = video_clip.get_frame(5)  # Obtiene el cuadro en el segundo 5

            snapshot_np = np.array(snapshot)
            snapshot_image = Image.fromarray(snapshot_np)

            snapshot_path = 'snapshot.png'
            snapshot_image.save(snapshot_path)

            # Cierra el archivo de video
            #video_clip.reader.close()

            # Elimina el archivo local de video
            #os.remove(video_path)

            return send_file(snapshot_path, as_attachment=True)

        else:
            return {'error': 'Debe proporcionar un video válido (formato: mp4, avi, mov).'}, 400

    except Exception as e:
        return {'error': str(e)}, 500
    
if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
