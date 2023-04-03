import pytz
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime as dt
import urllib.request
import config
import pymongo
import json

# Firebase


def intialize_app():
    json_cred = config.firebase['cred']
    cred = credentials.Certificate(json_cred)
    firebase_admin.initialize_app(cred)
    return True


def firestore_client():
    firestore_client = firestore.client()
    return firestore_client


def insert_ids_firestore(ref, id):
    ref.add({"id": id})
    return True


def retrieve_ids_firestore(ref):
    stream = ref.stream()
    li_ids = []
    for i in stream:
        li_ids.append(i.to_dict()['id'])
    return li_ids


def delete_ids_firestore(ref):
    doc_li = ref.list_documents()
    for doc in doc_li:
        doc.delete()
    return True


def create_mongo_client():
    mongo_user = config.mongo['user']
    mongo_pass = config.mongo['password']
    mongo_uri = config.mongo['uri']
    mongo_db = config.mongo['db_name']
    srv = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_uri}/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(srv)
    return client[mongo_db]


def insert_mongo_collection(id, collection):
    collection.insert_one({'id': id})
    return None


def check_post_id_mongo(id, collection):
    id_count = collection.count_documents({'id': id})
    if (id_count):
        return True
    else:
        return False


def delete_old_ids(collection):
    cols_count = collection.count_documents({})
    if cols_count > 100:
        collection.delete_many({})
    return None


def get_start_end_timestamp():
    now_time = dt.today()
    end_time = now_time.timestamp()
    start_time = end_time - 300
    return int(start_time), int(end_time)


def time_passed_since_utc_str(utc_str):
    # parse the string as a datetime object
    utc_dt = dt.strptime(utc_str, '%Y-%m-%d %H:%M:%S')

    # convert to IST timezone
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_dt = pytz.utc.localize(utc_dt).astimezone(ist_tz)

    # calculate minutes passed since that time
    now_dt = dt.now(ist_tz)
    total_seconds_passed = (now_dt - ist_dt).total_seconds()
    minutes_passed = total_seconds_passed / 60

    # convert to hours if more than 60 minutes have passed
    if minutes_passed >= 60:
        hours_passed = minutes_passed / 60
        return f'{hours_passed:.2f} hours have passed since {ist_dt} UTC'
    else:
        return f'{minutes_passed:.2f} minutes have passed since {ist_dt} UTC'


def get_filtered_posts_with_firebase(url, sub_name):
    response = urllib.request.urlopen(url)
    text = response.read()
    req_data = json.loads(text.decode("utf-8"))
    posts = req_data["data"]
    client = firestore_client()
    ref = client.collection(sub_name)
    pre_ids = retrieve_ids_firestore(ref)
    filtered_posts = []
    for post in posts:
        if post['id'] in pre_ids:
            continue
        else:
            if post['utc_datetime_str']:
                posted_ago = time_passed_since_utc_str(
                    post['utc_datetime_str'])
                post['posted_ago'] = posted_ago
            insert_ids_firestore(ref, post['id'])
            filtered_posts.append(post)
    return filtered_posts


def get_filtered_posts_with_mongo(url, sub_name, client):
    response = urllib.request.urlopen(url)
    text = response.read()
    req_data = json.loads(text.decode("utf-8"))
    posts = req_data["data"]
    col = client[sub_name]
    delete_old_ids(col)
    filtered_posts = []
    for post in posts:
        # id = post['id']
        id_exist = check_post_id_mongo(post['id'], col)
        # id_exist = False
        if id_exist:
            continue
        else:
            if post.get('utc_datetime_str', ''):
                posted_ago = get_posted_ago_in_local_time(
                    post['utc_datetime_str'])
                post['posted_ago'] = posted_ago
            insert_mongo_collection(post['id'], col)
            filtered_posts.append(post)
    return filtered_posts


def get_all_posts():
    client = create_mongo_client()
    st_time, end_tim = get_start_end_timestamp()

    india = f"https://api.pushshift.io/reddit/search/submission?subreddit=india&since={st_time}&until={end_tim}&sort=created_utc&order=desc&agg_size=25&shard_size=1.5&track_total_hits=false&limit=100&filter=subreddit%2Cselftext%2Ctitle%2Cid%2Curl%2Cutc_datetime_str"

    askreddit = f"https://api.pushshift.io/reddit/search/submission?subreddit=askreddit&since={st_time}&until={end_tim}&sort=created_utc&order=desc&agg_size=100&shard_size=1.5&track_total_hits=false&limit=100&filter=subreddit%2Cselftext%2Ctitle%2Cid%2Curl%2Cutc_datetime_str"

    filtered_posts = []
    filtered_posts.append(get_filtered_posts_with_mongo(
        india, 'india', client))
    filtered_posts.append(
        get_filtered_posts_with_mongo(askreddit, 'askreddit', client))
    return filtered_posts


if __name__ == '__main__':
    s = get_all_posts()
    # quic delete
    pass
