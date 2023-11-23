# CopyMyDesk
In this visualization, I collected 400+ youtube videos about desk setup and i tried to visualize the result. 

## How I collect the data

All video data is from Youtube Data API https://developers.google.com/youtube/v3/docs/search/list

search word is “Desk setup 2023”

videos publish date must be on or after 2023-01-01

the language of the video and transcript should be in english

video transcript collected using https://pypi.org/project/youtube-transcript-api/ if no transcript is found, that video will be dropped

since Youtube data API only return 50 results each request, a loop is needed to get more data

## data cleaning

remove duplicate videos by drop duplicate video ids

remove rows if youtube-transcript-api can’t get transcript

remove timestamp from transcript and keep text only

remove if publish date is before 2023-01-01 (the youtube data api should already done this but just in case)

remove rows that transcript length < 100 because it means the transcript api failed to get transcript

after the cleaning we got about 900 video transcripts left
