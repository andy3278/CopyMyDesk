from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

youtube_key = os.environ.get('YOUTUBE_KEY')
api_key = youtube_key

youtube = build('youtube', 'v3', developerKey=api_key)

# Replace 'your_keyword' with the keyword you want to search
request = youtube.search().list(
    part='snippet',
    maxResults=20,  # You can adjust the max results
    q='Desk setup 2023',
    publishedAfter='2023-01-01T00:00:00Z',
    relevanceLanguage = 'en',
    type = 'video'
)

response = request.execute()

for item in response['items']:
    print('Video ID: ', item['id']['videoId'])
    print('Title: ', item['snippet']['title'])
    print('Channel: ', item['snippet']['channelTitle'])
    print('---------------------------')
