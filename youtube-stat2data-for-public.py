import googleapiclient.discovery
import pandas as pd

####################################################
########INSERT API KEYS AND THE CHANNEL ID##########
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = [YOUR_API_KEY1, YOUR_API_KEY2, YOUR_API_KEY3] # Include at least 3 if you are pulling more than 5,000 videos
channel_id = "UCupvZG-5ko_eiXAupbDfxWw" 
# Refer to the README.md to see how to get the channel ID 
# The channel_ID above is the channel ID for CNN's Youtube channel


results_summary = {}
all_videos = []
res_dump = []
pageToken = ""
query_count = 0


#############################################################
##INSERT THE YEAR OR YEARS YOU WANT TO PULL DATA FROM########

for year in [YEAR1, YEAR2, YEAR3]:
    for month in range(1, 13, 1):
        start_time = f"{year}-{month:02d}-{20}T00:00:00Z"
        
        if month == 12:
            end_time = f"{year+1}-{1:02d}-{20}T00:00:00Z"
        else:
            end_time = f"{year}-{month+1:02d}-{20}T00:00:00Z"
            
        monthly_videos = []
        
        
        while True:

            youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY[query_count % 3])

            res = youtube.search().list(
                part="id,snippet",
                channelId=channel_id,
                type="video",
                order="date",
                publishedAfter=start_time,
                publishedBefore=end_time,
                maxResults=50,
                pageToken = pageToken if pageToken != "" else "").execute()
            
            query_count += 1

            v = res.get('items', [])
            if v:
                monthly_videos.extend(v)
            pageToken = res.get('nextPageToken')
            if not pageToken:
                break
            
        all_videos.extend(monthly_videos)
        
        time_text = f"Year{year}-{month:02d}"
        
        results_summary[time_text] = len(monthly_videos)
        
        desc = f"{time_text} | #Videos {len(monthly_videos)} | # All Videos: {len(all_videos)}"
        print(desc)
            

## stat part
data = all_videos
video_ids = list(map(lambda x:x['id']['videoId'], data))
stats = []

for i in range(0, len(video_ids), 40):
    res = (youtube).videos().list(id=','.join(video_ids[i:i+40]), part='statistics').execute()
    stats += res['items']


## table step
youtube_result = all_videos
video_ids = list(map(lambda x:x['id']['videoId'], youtube_result))
youtube_stats = stats
len_videos = len(video_ids)

title = []
like = []
favorite = []
views = []
url = []
comment = []
video_id = []
published_date = []
video_description = []

for i in range(0,len_videos):
    title.append((youtube_result[i])['snippet']['title'])
    published_date.append((youtube_result[i])['snippet']['publishedAt'])
    video_description.append((youtube_result[i])['snippet']['description'])

    if "likeCount" in youtube_stats[i]['statistics']:
        like.append(int((youtube_stats[i])['statistics']['likeCount']))
    else:
        like.append("no info") 

    if "favoriteCount" in youtube_stats[i]['statistics']:
        favorite.append(int((youtube_stats[i])['statistics']['favoriteCount']))
    else:
        favorite.append("no info")

    if "viewCount" in youtube_stats[i]['statistics']:
        views.append(int((youtube_stats[i])['statistics']['viewCount']))
    else:
        views.append("no info")

    if "commentCount" in youtube_stats[i]['statistics']:
        comment.append(int((youtube_stats[i])['statistics']['commentCount']))
    else:
        comment.append("no info") 

    video_id.append((youtube_result[i])['id']['videoId'])
    i += 1

data = {'title': title, 'video_id': video_id, 'video_description': video_description, 'published_date': published_date, 'like': like, 'favorite': favorite, 'views': views, 'comment': comment}
df = pd.DataFrame(data)

df.to_csv("youtube-data.csv", index=False)