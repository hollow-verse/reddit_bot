import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime as dt
import urllib.request
import config
import json


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


def get_day_timestamp():
    today = dt.today().strftime('%Y-%m-%d')
    today_date = dt.strptime(today, '%Y-%m-%d')
    return int(today_date.timestamp())


def get_filtered_posts(url, sub_name):
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
            insert_ids_firestore(ref, post['id'])
            filtered_posts.append(post)
    return filtered_posts


def get_all_posts():
    t_stamp = get_day_timestamp()
    
    ask_reddit_url = f"https://api.pushshift.io/reddit/search/submission?subreddit=askreddit&since={t_stamp}&sort=created_utc&order=desc&agg_size=25&shard_size=1.5&track_total_hits=false&limit=100&filter=subreddit%2Cselftext%2Ctitle%2Cid%2Curl%2Cutc_datetime_str"
    
    india_url = f"https://api.pushshift.io/reddit/search/submission?subreddit=india&since={t_stamp}&sort=created_utc&order=desc&agg_size=100&shard_size=1.5&track_total_hits=false&limit=100&filter=subreddit%2Cselftext%2Ctitle%2Cid%2Curl%2Cutc_datetime_st"
    filtered_posts = []
    filtered_posts.append(get_filtered_posts(ask_reddit_url, 'askreddit'))
    filtered_posts.append(get_filtered_posts(india_url,'india'))
    return filtered_posts

