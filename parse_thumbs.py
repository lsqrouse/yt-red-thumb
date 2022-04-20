import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import random_words
import random
import os

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "oath_client.json"

def get_search_words():
    r = random_words.RandomWords()

    random_letter = r.available_letters[random.randint(0, len(r.available_letters) - 1)]
    count = 10
    if random_letter == 'z':
        count = 7
    print(random_letter)
    return r.random_words(random_letter, count)

def get_thumb_links(youtube):
    words = get_search_words()
    thumb_links = []
    for word in words:

        #query youtube url for our random search term
        request = youtube.search().list(
            part="snippet",
            q = word,
            maxResults=50,
            order="searchSortUnspecified",
            publishedAfter="2012-01-01T00:00:00Z",
            publishedBefore="2012-01-02T00:00:00Z",
            regionCode="US",
            relevanceLanguage="en",
            type="video"
        )
        response = request.execute()
        videos = response["items"]
        for video in videos:
            thumbnail_url = video["snippet"]["thumbnails"]["high"]["url"]
            # add the thumbnail
            thumb_links.append(str(thumbnail_url))
            print(thumbnail_url)
    return thumb_links

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    thumb_links = get_thumb_links(youtube)
    print("got: ")
    print(str(thumb_links))
    print(str(len(thumb_links)))

main()






