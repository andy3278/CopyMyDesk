import pandas as pd
from datetime import datetime
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

# load secret from env
load_dotenv(find_dotenv())

youtube_key = os.environ.get('YOUTUBE_KEY')
api_key = youtube_key

youtube = build('youtube', 'v3', developerKey=api_key)

# Replace 'your_keyword' with the keyword you want to search

max_results = 1
serach_keyword = 'Desk setup 2023'

request = youtube.search().list(
    part='snippet',
    maxResults=max_results,  
    q=serach_keyword,
    publishedAfter='2023-01-01T00:00:00Z', # get only result after 2023
    relevanceLanguage = 'en',
    type = 'video'
)

response = request.execute()

# for item in response['items']:
#     print('Video ID: ', item['id']['videoId'])
#     print('Title: ', item['snippet']['title'])
#     print('Channel: ', item['snippet']['channelTitle'])
#     print('---------------------------')

# storage results in a dataframe

video_id = []
title = []
channel = []
release_date = []

for item in response['items']:
    video_id.append(item['id']['videoId'])
    title.append(item['snippet']['title'])
    channel.append(item['snippet']['channelTitle'])
    release_date.append(item['snippet']['publishedAt'])

df = pd.DataFrame({'video_id': video_id, 'title':title, 'channel':channel, 'release_date':release_date})

# fotmat the release date
date_formatter = lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
df['release_date'] = df['release_date'].apply(date_formatter)


# get video transcript

def get_transcripts(video_ids:str) -> list:
    transcripts = []
    for video_id in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcripts.append(transcript)
        except:
            transcripts.append(None)

    return transcripts

# get transcript for each video_id in df
df['transcript'] = get_transcripts(df['video_id'])

# get transcript text
df['transcript_text'] = df['transcript'].apply(lambda x: ' '.join([item['text'] for item in x]))
print(df.sample())