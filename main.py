import json
import requests
from flask import Flask, jsonify, request, send_file, Response, stream_with_context, render_template
from urllib.parse import urlparse
from uuid import *
from utils import Utils
import os

app = Flask(__name__)


@app.route('/')
def home():
    return "Hello, Flask!2"


@app.route('/search-youtube', methods=['GET','POST'])
def search_youtube():
    return render_template('search_youtube.html')


@app.route('/download-file', methods=['GET'])
def download_file():
    params = request.args
    file_name = params.get('file_name', '')
    try:
        return send_file(file_name, as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/clean-all')
def clean_all():
    for directory in ['videos', 'mp3']:
        # Loop through all files in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                # Check if it's a file and remove it
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f'Removed file: {file_path}')
            except Exception as e:
                print(f'Error deleting file {file_path}: {e}')

    return "clean"


@app.route('/download-youtube', methods=['POST'])
def youtube_download():
    try:
        params = json.loads(request.data)
        url = params.get('url', '')
        output_path = params.get('output_path', './videos')
        output_path_mp3 = params.get('output_path_mp3', './mp3')
        file_name = params.get('file_name', uuid4())
        is_audio = params.get('is_audio', 0)
        parsed_url = urlparse(url)
        isPlayList = parsed_url.query.__contains__('list')
        Utils.check_and_make_directory(output_path)
        Utils.check_and_make_directory(output_path_mp3)

        if not isPlayList:
            result = Utils.get_webm_youtube(
                url=url,
                output_path=output_path,
                file_name=file_name,
                is_audio=is_audio
            )
            if result:
                output_file = '{}/{}.{}'.format(output_path, file_name, result['ext'])
                file = ""
                if is_audio == 1:
                    file = Utils.convert_webm_to_mp3(output_file, '{}/{}.mp3'.format(output_path_mp3, file_name))
                return jsonify({'data': [{"file": output_file, "mp3": file}]}), 200

        # make directory for list
        Utils.check_and_make_directory("{}/{}".format(output_path, file_name))
        Utils.check_and_make_directory("{}/{}".format(output_path_mp3, file_name))

        results = Utils.get_playlist_webm_youtube(
            url=url,
            output_path=output_path,
            file_name=file_name,
            is_audio=is_audio
        )

        if results:
            data = []
            for i in range(len(results)):
                # Create a dictionary with the 'file' key
                entry = {'file': results[i], 'mp3': ''}
                # Check if mp3_files is not empty
                if is_audio == 1:
                    entry['mp3'] = Utils.convert_webm_to_mp3(results[i], '{}/{}/{}'.format(
                        output_path_mp3, file_name, os.path.basename(results[i]).replace('webm', 'mp3')))
                data.append(entry)
            return jsonify({'data': data}), 200

        return jsonify({'message': 'create failed'}), 400
    except Exception as e:
        print(f"Error: {str(e)}")  # Print the error message to the console
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False)
