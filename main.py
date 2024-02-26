from flask import Flask, request, jsonify, send_file
import os
from flask_cors import CORS  # Import CORS
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import io
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pydub import AudioSegment
import moviepy.editor as mp
import numpy as np
import requests

UPLOAD_FOLDER = 'static/files'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_VIDEO_EXTENSIONS = set(['mp4', 'avi', 'mov'])

# resize image
def resize_image(image, fixed_height):
    try:
        width, height = image.size
        new_width = int((width / height) * fixed_height)
        new_height = fixed_height
        resized_image = image.resize((new_width, new_height))
        return resized_image
    except Exception as e:
        print("Error:", e)
        return None
    
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

@app.route('/api/get-snapshot', methods=['POST'])
def get_snapshot():
    try:
        video = request.files['file']

        if video and video.filename.endswith(('.mp4', '.avi', '.mov')):

            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_video.mp4')
            snapshot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'snapshot.png')
        
            video.save(video_path)

            video_clip = VideoFileClip(video_path)
            snapshot = video_clip.get_frame(5)  # Obtiene el cuadro en el segundo 5

            snapshot_np = np.array(snapshot)
            snapshot_image = Image.fromarray(snapshot_np)

            snapshot_image.save(snapshot_path)

            # Cierra el archivo de video
            video_clip.reader.close()

            # Elimina el archivo local de video
            #os.remove(video_path)

            return send_file(snapshot_path, as_attachment=True)

            # Envía el archivo de snapshot a NestJS
            #nestjs_url = 'http://tu-servidor-nestjs.com/upload-snapshot'
            #files = {'file': open(snapshot_path, 'rb')}
            #response = requests.post(nestjs_url, files=files)

            #if response.status_code == 200:
            #    return send_file(snapshot_path, as_attachment=True)
            #else:
            #    return {'error': 'Error al enviar snapshot a NestJS'}, 500
            

        else:
            return {'error': 'Debe proporcionar un video válido (formato: mp4, avi, mov).'}, 400

    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/resize-image', methods=['POST'])
def resize_image_api():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        image = request.files['file']
        fixed_height = 60

        if image and image.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif')):
            image_stream = io.BytesIO(image.read())
            pil_image = Image.open(image_stream)
            
            resized_image = resize_image(pil_image, fixed_height)
            if resized_image:
                # Convertir la imagen a modo RGB antes de guardar como JPEG
                resized_image = resized_image.convert("RGB")
                
                output_stream = io.BytesIO()
                resized_image.save(output_stream, format='JPEG')
                output_stream.seek(0)
                
                return send_file(output_stream, mimetype='image/jpeg')
            else:
                return jsonify({'error': 'Error resizing image'}), 500
        else:
            return jsonify({'error': 'Invalid image format. Allowed formats: jpg, jpeg, png.'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/api/convert-to-gif", methods=["POST"])
def convert_to_gif_endpoint():
    try:
        video = request.files["file"]

        if video:
            #video_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(video.filename))
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_video.mp4')
            gif_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_video.gif')

            video.save(video_path)

            gif_path = convert_to_gif(video_path)

            # Eliminar el archivo de video después de convertirlo
            #os.remove(video_path)

            #return jsonify({"message": "Video converted to GIF successfully.", "gif_path": gif_path})
            return send_file(gif_path, as_attachment=True)
        else:
            return jsonify({"error": "Invalid video format. Allowed formats: mp4, avi, mov."}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/telegram_message", methods=["POST"])
def telegram_message():
    try:

        data = request.json
        chat_id = data.get("chat_id")
        message = data.get("message")

        # Token de acceso del bot de Telegram
        TOKEN = '5818670079:AAH5-IpP2SQIRC6qqF4SD9BcX5KAUuN9HeI'

        # ID del chat del bot
        #chat_id = '-1002115848401'

        # URL de la API de Telegram para enviar messages
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

        # Parámetros del message
        params = {
            'chat_id': chat_id,
            'text': message
        }

        # Envío del message
        response = requests.post(url, json=params)

        # Verificación de la respuesta
        if response.status_code == 200:
            return jsonify({"ok": "true", "message": "Message sent successfully."}), 200
        else:
            return jsonify({"error": f"Error al enviar el message: {response.status_code} {response.text}"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/telegram_message_media", methods=["POST"])
def telegram_message_media():
    try:
        data = request.json
        chat_id = data.get("chat_id")
        message = data.get("message")
        media = data.get("media")
        file_url = data.get("file_url")

        if not chat_id or not message or not media or not file_url:
            return jsonify({"error": "chat_id, message, media, and file_url are required fields"}), 400

        # Token de acceso del bot de Telegram
        TOKEN = '5818670079:AAH5-IpP2SQIRC6qqF4SD9BcX5KAUuN9HeI'

        # URL de la API de Telegram para enviar imágenes o videos
        url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto' if media == 'photo' else f'https://api.telegram.org/bot{TOKEN}/sendVideo'

        # Parámetros del mensaje
        params = {
            'chat_id': chat_id,
            'caption': message,
            'photo' if media == 'photo' else 'video': file_url
        }

        # Envío del mensaje, imagen o video
        response = requests.post(url, json=params)

        # Verificación de la respuesta
        if response.status_code == 200:
            return jsonify({"ok": "true", "message": "Message sent successfully."}), 200
        else:
            return jsonify({"error": "Error sending the file: {response.status_code} {response.text}"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5001))
