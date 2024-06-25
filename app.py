from flask import Flask, request, jsonify,send_file
from lord.main import call_current_node, process_user_input, delete_memory
from tts.text_to_speach import text_to_speech
from stt.speeach_recog import transcribe_audio_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/Audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/call_node', methods=['GET'])
def call_node():
    response = call_current_node()
    return jsonify(response)

@app.route('/process_input', methods=['POST'])
def process_input():
    data = request.json
    user_input = data.get('user_input')
    response = process_user_input(user_input)
    return jsonify(response)

@app.route('/delete_memory', methods=['POST'])
def delete_memory_route():
    response = delete_memory()
    return jsonify({'status': 'memory deleted', 'response': response})

@app.route('/upload_wav', methods=['POST'])
def upload_wav():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.wav'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        # Process the WAV file here if needed
        transcription = transcribe_audio_file(filepath)
        process_user_input(transcription)
        return jsonify({'status': 'file uploaded', 'filename': file.filename, 'transcription': transcription}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/call_node_tts', methods=['POST'])
def call_node_tts():
    text = call_current_node()['text']
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    audio_path = text_to_speech(text)
    if not audio_path:
        return jsonify({'error': 'Text to speech conversion failed'}), 500

    return send_file(audio_path, mimetype='audio/wav', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
