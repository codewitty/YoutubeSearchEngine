import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, Response
import os
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv
import requests
from isodate import parse_duration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thecodex'

# API key setup
path = '/Users/joshuagomes/YouTube/.env/key.py'
load_dotenv(dotenv_path=path,verbose=True)

class Config:
    print("Inside the Config file")
    API_KEY = os.environ.get("KEY")

c = Config()
key = c.API_KEY
print(key)

@app.route("/", methods=['GET', 'POST'])
def index():
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    videos = []
    max_num = request.form.get('maxResults')
    query = request.form.get('searchTerm')
    if max_num == '':
        max_num = 1
    if request.form.get('searchTerm') == '':
        query = "Hello World"


    if request.method == 'POST':
        search_params = {
            'key' : key,
            'q' : query,
            'part' : 'snippet',
            'maxResults' : max_num,
            'relevanceLanguage' : 'en',
            'type' : 'video'
        }
        print(search_params)

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])

        video_params = {
            'key' : key,
            'id' : ','.join(video_ids),
            'part' : 'snippet,contentDetails, statistics',
            'maxResults' : max_num
        }

        r = requests.get(video_url, params=video_params)
        results = r.json()['items']
        str1 = ","
        for result in results:
            print("VIDEO RESULTS:")
            video_data = {
                'id' : result['id'],
                'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'title' : result['snippet']['title'],
                'views' : result['statistics']['viewCount'],
                'likes' : result['statistics']['likeCount'] if 'likeCount' in result['statistics'] else 'NONE',
                'dislikes' : result['statistics']['dislikeCount'] if 'dislikeCount' in result['statistics'] else 'NONE',
                'tags' : str1.join(result['snippet']['tags']) if 'tags' in result['snippet'] else 'NONE',
            }
            videos.append(video_data)


        print("DF")
        df = pd.DataFrame(videos)
        print(df)
        df.to_csv('./static/search_results.csv', sep='\t', encoding='utf-8', index=False)

    return render_template('base.html', videos=videos)

@app.route("/downloadCSV", methods=['GET'])
def download():
    with open("static/search_results.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=search_results.csv"})

if __name__ == '__main__':
    app.run()
