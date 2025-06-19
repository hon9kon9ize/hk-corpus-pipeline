# Borrow from https://github.com/alphrc/lilm

from __future__ import annotations

import os
from typing import Literal
import requests


class Category:
    cat_id: str
    name: str
    postable: bool

    def __init__(self, data: dict):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)


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
    quote: Post
    quote_post_id: str
    remark: str
    reply_time: int
    status: int
    thread_id: str
    user: User
    user_gender: str
    user_nickname: str
    vote_score: int

    def __init__(self, data: dict):
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


class Remark:
    last_reply_count: int
    no_of_uni_not_push_post: int

    def __init__(self, data: dict):
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

    def __init__(self, data: dict):
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
    item_data: list[Post]
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

    def __init__(self, data: dict):
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

    def get_valid_entries(self) -> list[dict]:
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

    def to_dict(self) -> dict:
        if not self.is_valid():
            return

        entries = self.get_valid_entries()

        return entries


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


def get_thread_from_id(thread_id: int) -> dict:
    print(f"Getting thread {thread_id}", "blue")

    url = f"https://lihkg.com/api_v2/thread/{thread_id}/page/1?order=reply_time"
    headers = get_headers(referer=f"https://lihkg.com/thread/{thread_id}/page/1")

    response = get(url=url, headers=headers)

    print(response)

    thread = Thread(response["response"])

    return {
        "category": thread.category.name,
        "title": thread.title,
        "content": thread.item_data[0].msg,
    }
