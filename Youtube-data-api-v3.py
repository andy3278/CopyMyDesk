import pandas as pd
from datetime import datetime
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import openai

# load secret from env
load_dotenv(find_dotenv())

openai.api_key = os.environ.get("OPENAI_API_KEY")
youtube_key = os.environ.get('YOUTUBE_KEY')
api_key = youtube_key

youtube = build('youtube', 'v3', developerKey=api_key)

# Replace 'your_keyword' with the keyword you want to search

max_results = 3
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
# drop transcript column
df = df.drop('transcript', axis=1)
# pass transcript text to openai api and get desk items from transcript

def openai_api(text:str) -> str:
    # openai api
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": """You will be provided with Desk setup youtube video transcripts, and your task is to extract what items are mentioned in video: 
                1. you must only extract items mentioned in the video 
                2. you must find 3 main items in the video, computer, mouse and keyboard, if its not found in video, say \"NA\" 
                3. if other desk items is mentioned also put them in the output, monitor, lights, desk, charger, computer dock etc.
                4. if same category have multiple items put them in a string with comma separated.
                5. your output format should be in json\n\n
                here is one example of respond:
                ```
                {"computer": "14 inch MacBook Pro", "mouse": "Logitech MX Master 3s", "keyboard": "Logitech MX mechanical mini", "monitor": "Apple Studio display, BenQ PD 3220u", "lights": "Elgato key light air", "desk": "Ikea countertop, Alex drawers, Carly kitchen countertop", "charger": "CalDigit TS4 Thunderbolt Hub", "computer dock": "Book Arc by 12 South", "neon sign": "custom neon sign by Illusion Neon", "acoustic panels": "gig Acoustics panels", "desk chair": "Autonomous Ergo chair plus", "scanner": "Fujitsu scanner", "charging stand": "Pataka charging stand", "pen": "Grovemade pen", "sticky notes": "sticky notes", "webcam": "Opal C1", "microphone": "Shure MV7", "audio interface": "Apollo twin X", "speakers": "Yamaha HS5", "headphones": "Rode NTH100s", "mic arm": "Rode PSA1 Plus", "controller": "Tour Box Elite", "light control": "Elgato Stream Deck Plus", "tablet": "iPad Pro", "tablet arm": "Cooks you desk arm", "monitor mount": "BenQ monitor mount", "travel charger": "ESR travel charger", "desk mat": "Grovemade felt mat", "smart home device": "Amazon Alexa Show", "security cameras": "UV security cameras", "Mac Mini": "Mac Mini Pro"}
                ```
            """
            },
            {
                "role":"user",
                "content": text
            }
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0]['message']['content']

df['items'] = df['transcript_text'].apply(openai_api)

# save results to csv
df.to_csv('youtube-desk-setup.csv', index=False)