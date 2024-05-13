from flask import Flask, render_template, request
from pytube import YouTube

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_mp4_mp3', methods=['POST'])
def get_mp4_mp3():
    youtube_link = request.form['youtube_link']
    try:
        yt = YouTube(youtube_link)
        mp4_url = yt.streams.filter(file_extension='mp4').first().url
        mp3_url = yt.streams.filter(only_audio=True).first().url
        return render_template('result.html', mp4_url=mp4_url, mp3_url=mp3_url)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
