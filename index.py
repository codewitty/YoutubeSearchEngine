import pandas as pd
from flask import abort, Flask, render_template, request, redirect, url_for, Response
import requests
import os
from isodate import parse_duration
from forms import Queryform


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thecodex'

@app.route("/", methods=['GET', 'POST'])
def index():
    form = Queryform()
    if request.method == 'POST':
        form = Queryform()
        if form.validate_on_submit():
            return redirect(url_for("result", query=form.searchTerm.data, maxResults=form.maxResults.data, api_key=form.api_key.data ))

    return render_template("base.html", form=form)

@app.route("/results/<string:query>/<int:maxResults>/<string:api_key>", methods=['GET', 'POST'])
#@app.route("/results", methods=['GET', 'POST'])
def result(query, maxResults, api_key):
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    videos = []
    max_num = maxResults
    query = query
    key = api_key

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

    print("Key: ", api_key)

    video_params = {
        'key' : key,
        'id' : ','.join(video_ids),
        'part' : 'snippet,contentDetails, statistics',
        'maxResults' : max_num
    }

    r = requests.get(video_url, params=video_params)
    results = r.json()['items']
    str1 = ","
    excel_list = []
    for result in results:
        video_data = {
            'id' : result['id'],
            'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail' : result['snippet']['thumbnails']['high']['url'],
            'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
            'title' : result['snippet']['title'] if 'title' in result['snippet'] else 'NONE',
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


    print(excel_list)
    df = pd.DataFrame(excel_list)
    print(df)
    print("Current working directory: ", os.getcwd())
    try: 
        df.to_csv('./static/search_results.csv', sep='\t', encoding='utf-8', index=False)
    except Exception as e:
        print("Error writing to CSV file: ", e)

    #df.to_excel('./static/search_results.xlsx', encoding='utf-8', index=False)

    return render_template('results.html', videos=videos)

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
    app.run(debug=True)
