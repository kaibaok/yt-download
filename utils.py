from __future__ import unicode_literals
import hashlib
from os import environ, path
import yt_dlp as youtube_dl
from moviepy.editor import VideoFileClip, AudioFileClip
import os,glob
from urllib.parse import urlparse, parse_qs, urlunparse


class Utils:
    @staticmethod
    def hash_password(password: str = None):
        return hashlib.sha3_256(password.encode()).hexdigest()

    @staticmethod
    def check_password(hashed_password: str = None, password: str = None):
        return Utils.hash_password(password) == hashed_password

    @staticmethod
    def serialize(model):
        """Serialize SQLAlchemy model to a dictionary."""
        result = {}
        for key, value in vars(model).items():
            if not key.startswith('_') and not isinstance(value, DeclarativeMeta):
                result[key] = value
        return result

    @staticmethod
    def get_webm_youtube(
            url: str = None,
            output_path: str ='downloads/videos',
            file_name: str = None,
            is_audio: bool = True
    ):
        if not url:
            return None

        if url.__contains__('list'):
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            # Remove specific parameters related to the playlist
            query_params.pop('list', None)
            query_params.pop('index', None)

            # Update the URL without the removed parameters
            modified_url = parsed_url._replace(query='')
            if query_params:
                modified_url = modified_url._replace(
                    query='&'.join([f'{key}={value[0]}' for key, value in query_params.items()]))
            url = urlunparse(modified_url)

        ydl_opts = {
            'outtmpl': '{}/{}.{}'.format(output_path, file_name, '%(ext)s'),
            # 'progress_hooks': [download_callback],
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if not is_audio else 'bestaudio/best',
            "ignoreerrors": True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                result = ydl.extract_info(url, download=True)
            except youtube_dl.DownloadError as e:
                print(f"Error: {e}")
        return result

    @staticmethod
    def get_playlist_webm_youtube(
            url: str = None,
            output_path: str = 'downloads/videos',
            file_name: str = None,
            is_audio: bool = True
    ):
        def get_list_url():
            ydl_opts = {
                'outtmpl': '{}/{}/{}'.format(output_path, file_name, '%(title)s.%(ext)s'),
                # 'progress_hooks': [download_callback],
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if not is_audio else 'bestaudio/best',
                'extract_flat': 'in_playlist',
                'verbose': True,
                "ignoreerrors": True,
                "quiet": True
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                playlist_dict = ydl.extract_info(url, download=False)
                if 'entries' in playlist_dict:
                    entries = playlist_dict.get('entries')
                    return [item['url'] for item in entries]
            return []

        ydl_opts = {
            'outtmpl': '{}/{}/{}'.format(output_path, file_name, '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if not is_audio else 'bestaudio/best',
            'verbose': True,
            "ignoreerrors": True,

        }

        lists = get_list_url()

        with youtube_dl.YoutubeDL(ydl_opts) as ydl2:
            try:
                ydl2.download(url_list=lists)
            except youtube_dl.DownloadError as e:
                print(f"Error: {e}")

        return glob.glob("{}/{}/*.webm".format(output_path, file_name))

    @staticmethod
    def convert_mp4_to_mp3(input_file, output_file):
        try:
            video_clip = VideoFileClip(input_file)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(output_file, codec='mp3')
            print(f"Conversion successful! MP3 file saved as {output_file}")
            return output_file
        except Exception as e:
            print(f"Error: {e}")
        return None

    @staticmethod
    def convert_webm_to_mp3(input_file, output_file):
        try:
            audio_clip = AudioFileClip(input_file)
            # audio_clip = video_clip.audio
            audio_clip.write_audiofile(output_file, codec='mp3')
            print(f"Conversion successful! MP3 file saved as {output_file}")
            return output_file
        except Exception as e:
            print(f"Error: {e}")
        return None

    @staticmethod
    def convert_webm_to_mp4(input_file, output_file):
        try:
            video_clip = VideoFileClip(input_file)
            video_clip.write_videofile(output_file)
            print(f"Conversion successful! mp4 file saved as {output_file}")
            return output_file
        except Exception as e:
            print(f"Error: {e}")
        return None

    @staticmethod
    def ensure_directory_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def check_and_make_directory(directory:str= None):
        if directory and not path.exists(directory):
            os.mkdir(directory)
