# Borrow from https://github.com/alphrc/lilm

import os
from typing import Literal, List, Dict
from dataclasses import dataclass
import requests


@dataclass
class Category:
    cat_id: str
    name: str
    postable: bool

    def __init__(self, data: Dict):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)


class Remark:
    last_reply_count: int
    no_of_uni_not_push_post: int

    def __init__(self, data: Dict):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)


class User:
    gender: str
    is_blocked: bool
    is_disappear: bool
    is_following: bool
    is_newbie: bool
    level: int
    level_name: str
    nickname: str
    status: int
    user_id: str

    def __init__(self, data: Dict):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)


class Thread:
    allow_create_child_thread: bool
    cat_id: int
    category: Category
    create_time: int
    dislike_count: int
    display_vote: bool
    first_post_id: str
    is_adu: bool
    is_bookmarked: bool
    is_hot: bool
    is_replied: bool
    item_data: List["Post"]
    last_reply_time: int
    last_reply_user_id: int
    like_count: int
    max_reply: int
    max_reply_dislike_count: int
    max_reply_like_count: int
    no_of_reply: int
    no_of_uni_user_reply: int
    page: str
    parent_thread_id: str
    remark: Remark
    reply_dislike_count: int
    reply_like_count: int
    status: int
    sub_cat_id: int
    thread_id: str
    title: str
    total_page: int
    user: User
    user_gender: str
    user_id: str
    user_nickname: str
    vote_status: str

    def __init__(self, data: Dict):
        if data is not None:
            for key, value in data.items():
                if key == "category":
                    setattr(self, key, Category(value))
                elif key == "item_data":
                    setattr(self, key, [Post(item) for item in value])
                elif key == "remark":
                    setattr(self, key, Remark(value))
                elif key == "user":
                    setattr(self, key, User(value))
                else:
                    setattr(self, key, value)

    def rank_by(self, order: Literal["reply_time", "score"]) -> None:
        if order == "reply_time":
            self.item_data.sort(key=lambda x: x.reply_time)
        elif order == "score":
            self.item_data.sort(key=lambda x: x.vote_score)

    def get_valid_entries(self) -> List[Dict]:
        thread_entry = {
            "cat_id": self.cat_id,
            "category": self.category.name,
            "thread_id": self.thread_id,
            "title": self.title,
            "author": self.user_nickname,
            "content": self.item_data[0].msg,
            "thread_vote_score": self.item_data[0].vote_score,
            "thread_reaction_count": self.item_data[0].like_count
            + self.item_data[0].dislike_count,
        }
        entries = []
        for post in self.item_data:
            if post.is_valid():
                entries.append(thread_entry | post.as_entry())
        return entries

    def is_valid(self) -> bool:
        return (
            len(self.item_data) > 1
            and not self.item_data[0].user_nickname == self.item_data[1].user_nickname
        )

    def to_dict(self) -> Dict:
        if not self.is_valid():
            return

        entries = self.get_valid_entries()

        return entries

    @staticmethod
    def from_id(thread_id: int) -> dict:
        url = f"https://lihkg.com/api_v2/thread/{thread_id}/page/1?order=reply_time"
        headers = get_headers(referer=f"https://lihkg.com/thread/{thread_id}/page/1")
        response = get(url=url, headers=headers)
        thread = Thread(response["response"])
        return {
            "category": thread.category.name,
            "title": thread.title,
            "content": thread.item_data[0].msg,
        }


@dataclass
class Post:
    dislike_count: int
    display_vote: bool
    is_minimized_keywords: bool
    like_count: bool
    low_quality: bool
    msg: str
    msg_num: int
    no_of_quote: int
    page: int
    post_id: str
    quote: "Post"
    quote_post_id: str
    remark: str
    reply_time: int
    status: int
    thread_id: str
    user: User
    user_gender: str
    user_nickname: str
    vote_score: int

    def __init__(self, data: Dict):
        if data is not None:
            for key, value in data.items():
                if key == "user":
                    setattr(self, key, User(value))
                if key == "msg":
                    setattr(self, key, value.replace("<br />", ""))
                else:
                    setattr(self, key, value)

    def is_hot(self) -> bool:
        return self.like_count + self.dislike_count >= 10

    def contains_external_link(self) -> bool:
        return "http://" in self.msg or "https://" in self.msg

    def is_valid(self) -> bool:
        return self.is_hot() and not self.contains_external_link()

    def as_entry(self) -> dict:
        return {
            "post_id": self.post_id,
            "msg_num": self.msg_num,
            "replier": self.user_nickname,
            "msg": self.msg,
            "like_count": self.like_count,
            "dislike_count": self.dislike_count,
            "vote_score": self.vote_score,
            "reaction_count": self.like_count + self.dislike_count,
            "quote_post_id": self.quote_post_id if hasattr(self, "quote") else None,
        }


def get(url: str, headers: dict) -> dict:
    try:
        response = requests.get(url=url, headers=headers, verify=True).json()
        return response
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}


def get_headers(referer: str) -> dict[str, str]:
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "lihkg.com",
        "Referer": referer,
        "User-Agent": os.getenv(
            "HEADERS_USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        ),
    }
    return headers


def get_lihkg_new_threads(page=1, count=100):
    """
    Fetches the latest threads from LIHKG's API and returns a list of Thread objects.
    """
    api_url = "https://lihkg.com/api_v2/thread/latest"
    params = {"page": page, "count": count}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Referer": "https://lihkg.com/category/1",
        "X-Lihkg-Device-Type": "web",
    }

    print(f"Fetching latest {count} threads from API...")
    threads = []
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("success") == 1 and "items" in data.get("response", {}):
            thread_items = data["response"]["items"]
            for item in thread_items:
                thread_id = item.get("thread_id")
                # Use the static method to fetch full thread details
                try:
                    thread_data = Thread.from_id(thread_id)
                    threads.append(thread_data)
                except Exception as e:
                    print(f"Error fetching thread {thread_id}: {e}")
        else:
            print("Error: API response format not as expected.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    return threads
