import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os
import random_words
import random
import requests
import shutil
import cv2
import numpy as np
import pickle
import time
from os import listdir
from os.path import isfile, join

# indicates we failed to download a file
BAD_DL = -1

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "oath_client.json"
thumb_prefix = './img/to_parse/'
dict_prefix = './dicts/'


img_count = 0

used_words = {}
parsed_vids = {}

def save_dict(dictionary,File):
    with open(dict_prefix + File, "wb") as myFile:
        pickle.dump(dictionary, myFile)
        myFile.close()

def load_dict(File):
    with open(dict_prefix + File, "rb") as myFile:
        dict = pickle.load(myFile)
        myFile.close()
        return dict

def get_search_words():
    r = random_words.RandomWords()

    random_letter = r.available_letters[random.randint(0, len(r.available_letters) - 1)]
    count = 10
    if random_letter == 'z':
        count = 7
    print(random_letter)
    return r.random_words(random_letter, count)

def get_thumb_links(youtube, words):
    thumb_links = []
    for word in words:
        # skip it if we've already parsed
        if word in used_words.keys():
            continue
        else:
            #mark it as found
            used_words[word] = 1

        #query youtube url for our random search term
        request = youtube.search().list(
            part="snippet",
            q = word,
            maxResults=50,
            order="searchSortUnspecified",
            publishedBefore="2009-12-14T00:00:00Z",
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

def save_thumb(url):
    global img_count
    filename = url.split("/")[-2] + ".jpg"

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open( thumb_prefix + filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        img_count += 1
    else:
        return BAD_DL
    return filename

def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_canny = cv2.Canny(img_blur, 25, 200)
    #25 200 = 48
    kernel = np.ones((3, 3))
    img_dilate = cv2.dilate(img_canny, kernel, iterations=3)
    img_erode = cv2.erode(img_dilate, kernel, iterations=3)
    return img_erode
def find_tip(points, convex_hull):
    length = len(points)
    indices = np.setdiff1d(range(length), convex_hull)
    for i in range(2):
        j = indices[i] + 2
        if j > length - 1:
            j = length - j
        if np.all(points[j] == points[indices[i - 1] - 2]):
            return tuple(points[j])
def parse_image(filename):
    print("parsing " +  str(filename))

    foundarrow = False

    try:
        img = cv2.imread(thumb_prefix + filename)

        # remove everything other than red from iamge
        img_red = np.copy(img)
        img_red[(img_red[:, :, 0] > 50) | (img_red[:, :, 1] > 50) | (img_red[:, :, 2] < 90)] = 0
        # ihstack((cv2.resize(img, (650, 500)), cv2.resize(img_copy, (650, 500))))
        img = img_red


        contours, hierarchy = cv2.findContours(preprocess(img), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            area = cv2.contourArea(cnt)
            approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
            hull = cv2.convexHull(approx, returnPoints=False)
            sides = len(hull)
            if 6 > sides > 3 and sides + 2 == len(approx):
                arrow_tip = find_tip(approx[:,0,:], hull.squeeze())
                if arrow_tip:
                    foundarrow = True
                    cv2.drawContours(img, [cnt], -1, (0, 255, 0), 3)
                    cv2.circle(img, arrow_tip, 3, (0, 0, 255), cv2.FILLED)
    except:
        print(filename + "was bad")
        save_dict(used_words, 'used_words.dict')
        save_dict(parsed_vids, 'parsed_vids.dict')

    parsed_vids[filename] = 1
    if foundarrow:
        return True
    return False




def main():
    global img_count
    global used_words

    #reload the list of used words
    if 'used_words.dict' in os.listdir('./dicts'):
        used_words = load_dict('used_words.dict')
    if 'parsed_vids.dict' in os.listdir('./dicts'):
        parsed_vids = load_dict('parsed_vids.dict')

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    #get words to search with
    words = get_search_words()
    #get and save our new thumbnails to ./img/to_parse
    thumb_links = get_thumb_links(youtube, words)
    thumbnails = []

    # save all the images locally
    for url in thumb_links:
        filename = save_thumb(url)
        if filename != BAD_DL:
            thumbnails.append(filename)

    arrows = []
    idx = 0
    for filename in thumbnails:
        # save this video_id as parsed
        if parse_image(str(filename)):
            # save the filename and the idx so we can get the url it game with
            arrows.append(filename)
        else:
            try:
                #remove the image if we didn't find an arrow
                os.remove(thumb_prefix + filename)
                img_count -= 1
            except:
                #donothing
                print('missingfile')
        idx += 1

    f = open('arrows.txt', 'w')
    for filename in arrows:
        f.write(filename + "\n")
    f.close()

    #update our dictionaries
    save_dict(used_words, 'used_words.dict')
    save_dict(parsed_vids, 'parsed_vids.dict')


main()






