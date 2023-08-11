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

UPLOAD_FOLDER = 'static/files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4', 'avi', 'mov'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_watermark(input_image, watermark_text):
    img = Image.open(input_image)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("Arial.ttf", 36)

    text_width, text_height = draw.textsize(watermark_text, font=font)
    margin = 10
    x = img.width - text_width - margin
    y = img.height - text_height - margin

    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return output

#convert video in gif
def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def convert_to_gif(video_path):
    video = VideoFileClip(video_path)
    gif_path = os.path.splitext(video_path)[0] + '.gif'
    video.write_gif(gif_path)
    return gif_path

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
        
@app.route("/add-video-watermark", methods=["POST"])
def add_text_watermark():
    try:
        video = request.files["file"]
        watermark_text = request.form.get("watermark_text", "onlypu.com")

        if video:
            video_path = "input_video.mp4"
            video.save(video_path)

            video_clip = VideoFileClip(video_path)
            
            # Create a TextClip for the watermark
            txt_clip = TextClip(watermark_text, fontsize=24, color="white").set_position(("center", "bottom")).set_duration(video_clip.duration)

            # Overlay the watermark text on the video
            video_with_watermark = CompositeVideoClip([video_clip, txt_clip])

            output_path = "output_video.mp4"
            video_with_watermark.write_videofile(output_path, codec="libx264")
            
            return send_file(output_path, as_attachment=True)
        else:
            return {"error": "Debe proporcionar un video."}, 400
	
    except Exception as e:
        return {"error": str(e)}, 500
    
# def add_video_watermark():
#     try:
#         watermark_video = "static/files/watermark.mp4"
#         watermark_audio = "watermark.wav"

#         video = request.files["file"]
        
#         if video:
#             video_path = "input_video.mp4"
#             video.save(video_path)
            
#             video_clip = VideoFileClip(video_path)
#             watermark_clip = VideoFileClip(watermark_video)
            
#             video_with_watermark = video_clip.set_audio(watermark_clip.audio)
#             output_path = "output_video.mp4"
#             video_with_watermark.write_videofile(output_path, codec="libx264")
            
#             return send_file(output_path, as_attachment=True)
#         else:
#             return {"error": "Debe proporcionar un video."}, 400
	
#     except Exception as e:
#         return {"error": str(e)}, 500
    
@app.route("/convert-to-gif", methods=["POST"])
def convert_to_gif_endpoint():
    try:
        video = request.files["file"]

        if video and allowed_video_file(video.filename):
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(video.filename))
            video.save(video_path)

            gif_path = convert_to_gif(video_path)

            return jsonify({"message": "Video converted to GIF successfully.", "gif_path": gif_path})
        else:
            return jsonify({"error": "Invalid video format. Allowed formats: mp4, avi, mov."}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/add-watermark", methods=["POST"])
def add_watermark_endpoint():
    try:
        watermark_text = request.form.get("watermark_text", "onlypu.com")
        image = request.files["file"]

        if image and watermark_text:
            output = add_watermark(image, watermark_text)
            return jsonify({"message": "Marca de agua agregada exitosamente.", "image": output.getvalue().decode("latin1")})
        else:
            return jsonify({"error": "Debe proporcionar una imagen y un texto de marca de agua."}), 400
	
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/file-upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        resp = jsonify({'message' : 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
