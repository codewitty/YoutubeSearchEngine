import pandas as pd
from flask import abort, Flask, render_template, request, redirect, url_for, Response, send_file 
import requests
import tempfile
import os, re
from isodate import parse_duration
from forms import Queryform
from dotenv import load_dotenv


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thecodex'

load_dotenv()




@app.route("/", methods=['GET', 'POST'])
def index():
    form = Queryform()
    if request.method == 'POST':
        form = Queryform()
        if form.validate_on_submit():
            return redirect(url_for("result", query=form.searchTerm.data, maxResults=form.maxResults.data))

    return render_template("base.html", form=form)

@app.route("/results/<string:query>/<int:maxResults>", methods=['GET', 'POST'])
def result(query, maxResults):
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    excel_list = []

    videos = []
    max_num = maxResults
    query = query
    api_key = os.getenv('API_KEY')

    print("Key:", api_key)

    search_params = {
        'key' : api_key,
        'q' : query,
        'part' : 'snippet',
        'maxResults' : max_num,
        'relevanceLanguage' : 'en',
        'type' : 'video'
    }

    r = requests.get(search_url, params=search_params)

    results = r.json()['items']

    video_ids = []
    for result in results:
        video_ids.append(result['id']['videoId'])

    video_params = {
        'key' : api_key,
        'id' : ','.join(video_ids),
        'part' : 'snippet,contentDetails, statistics',
        'maxResults' : max_num
    }

    r = requests.get(video_url, params=video_params)
    results = r.json()['items']
    str1 = ","
    for result in results:
        video_data = {
            'id' : result['id'],
            'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail' : result['snippet']['thumbnails']['high']['url'],
            'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
            'title' : result['snippet']['title'] if 'title' in result['snippet'] else 'NONE',
            'Views' : result['statistics']['viewCount'] if 'viewCount' in result['statistics'] else 'NONE',
            'Tags' : str1.join(result['snippet']['tags']) if 'tags' in result['snippet'] else 'NONE',
            'Description' : result['snippet']['description'] if 'description' in result['snippet'] else 'NONE',
            'Uploader Name' : result['snippet']['channelTitle'] if 'channelTitle' in result['snippet'] else 'NONE',
            'Likes' : result['statistics']['likeCount'] if 'likeCount' in result['statistics'] else 'NONE',
            'Dislikes' : result['statistics']['dislikeCount'] if 'dislikeCount' in result['statistics'] else 'NONE',
            'Year' : result['snippet']['publishedAt'].split('-')[0] if 'publishedAt' in result['snippet'] else 'NONE',
        }
        videos.append(video_data)

    for result in results:
        video_data = {
            'Title' : result['snippet']['title'] if 'title' in result['snippet'] else 'NONE',
            'Link' : f'https://www.youtube.com/watch?v={ result["id"] }',
            'Views' : result['statistics']['viewCount'] if 'viewCount' in result['statistics'] else 'NONE',
            'Year' : result['snippet']['publishedAt'].split('-')[0] if 'publishedAt' in result['snippet'] else 'NONE',
            'Tags' : str1.join(result['snippet']['tags']) if 'tags' in result['snippet'] else 'NONE',
            'Description' : result['snippet']['description'] if 'description' in result['snippet'] else 'NONE',
            'Uploader Name' : result['snippet']['channelTitle'] if 'channelTitle' in result['snippet'] else 'NONE',
            'Likes' : result['statistics']['likeCount'] if 'likeCount' in result['statistics'] else 'NONE',
            'Dislikes' : result['statistics']['dislikeCount'] if 'dislikeCount' in result['statistics'] else 'NONE',
        }
        excel_list.append(video_data)


    return render_template('results.html', videos=videos)

@app.route("/download", methods=['GET'])
def download():
    try:
        df = pd.DataFrame(excel_list)

        print("\n\n\nDataframe: ", df)

        # Remove special characters
        for col in df.columns:
            df[col] = df[col].map(lambda x: re.sub(r'[^\x00-\x7F]+', '', str(x)))

        # Save the DataFrame to a text file
        df.to_csv("search_results.txt", sep="\t", index=False)

        return send_file("search_results.txt", as_attachment=True)
    except Exception as e:
        print("Error in download function: ", e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
