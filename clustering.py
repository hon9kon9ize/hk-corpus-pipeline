import os
import re
from datetime import datetime
import duckdb
from dotenv import load_dotenv
import pandas as pd
from pydips import BertModel
from collections import defaultdict
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

bret_model = BertModel()
stopwords = []

with open("stopwords.txt", "r", encoding="utf-8") as f:
    for line in f:
        stopwords.append(line.strip())

REQUIRED_VARS = [
    "R2_KEY_ID",
    "R2_SECRET_KEY",
    "R2_ACCOUNT_ID",
    "R2_BUCKET_NAME",
]

conn = duckdb.connect()


def load_env_vars(required_vars: list[str] = REQUIRED_VARS):
    # Load .env file
    load_dotenv()
    for var in required_vars:
        if not os.getenv(var):
            raise Exception(f"Required environment variable not set: {var}")


def setup_duckdb_connection():
    # Set up DuckDB connection with R2 storage
    r2_key_id = os.getenv("R2_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_KEY")
    r2_account_id = os.getenv("R2_ACCOUNT_ID")

    conn.execute(
        f"""CREATE SECRET (
    TYPE r2,
    KEY_ID '{r2_key_id}',
    SECRET '{r2_secret_key}',
    ACCOUNT_ID '{r2_account_id}',
);"""
    )


def tokenization(text: str) -> list[str]:
    tokens = []
    lines = []

    # remove brackets
    text = re.sub(r"[\[\]（）(){}《》「」『』【】]", "\n", text)

    for line in text.splitlines():
        if line.strip():
            line = line.strip().lower()

        if len(line) >= 510:
            if all(len(part) < 510 for part in line.split("。")):
                lines.extend([part + "。" for part in line.split("。") if part.strip()])
        else:
            lines.append(line)

    for line in lines:
        tokens.extend(bret_model.cut(line, mode="coarse"))

    # 去重
    tokens = list(set(tokens))

    # 去掉空白 token
    tokens = [token for token in tokens if token.strip()]

    # 去單字 token
    tokens = [token for token in tokens if len(token) > 1]

    # 去數字 token
    tokens = [token for token in tokens if not re.match(r"^[0-9,\.:]+$", token)]

    # 去日期 token
    tokens = [
        token
        for token in tokens
        if not re.match(r"^[0-9一二三四五六七八九十百千]+[日月年]$", token)
    ]

    # 去停用詞
    tokens = [token for token in tokens if token not in stopwords]

    return list(set(tokens))


def cluster_documents(df: pd.DataFrame, sim_threshold: float = 0.8):
    # Tokenize
    df["tokens"] = df["extracted"].apply(lambda x: tokenization(x))

    # Build document-term matrix
    doc_dicts = []
    for row in df.itertuples():
        tokens = row.tokens
        text = row.extracted
        word_freq = defaultdict(int)
        for token in tokens:
            word_freq[token] += text.count(token)
        doc_dicts.append(word_freq)
    dict_vectorizer = DictVectorizer()
    X_counts = dict_vectorizer.fit_transform(doc_dicts)
    tfidf_transformer = TfidfTransformer()
    X_tfidf = tfidf_transformer.fit_transform(X_counts)
    similarity = cosine_similarity(X_tfidf)
    G = nx.Graph()
    N = len(df)
    for i in range(N):
        for j in range(i + 1, N):
            if similarity[i, j] > sim_threshold:
                G.add_edge(i, j)
    clusters = list(nx.connected_components(G))

    return clusters, df


def main():
    load_env_vars()
    setup_duckdb_connection()

    bucket_name = os.getenv("R2_BUCKET_NAME")
    today = datetime.now().strftime("%Y-%m-%d")
    query = f"SELECT * FROM read_json('r2://{bucket_name}/event_date={today}/**/*')"
    df = conn.execute(query).df()
    df = df[df["event"] == "scraping"]  # filter for scraping events
    df = pd.DataFrame(df["payload"].tolist())  # extract payload column
    df = df.drop_duplicates(subset=["url"])  # remove duplicates based on title and date
    df = df[df["extracted"] != ""]  # filter out empty extracted content
    clusters, df = cluster_documents(df)

    print(f"Number of clusters: {len(clusters)}")
    for idx, cluster in enumerate(clusters):
        print(f"\nCluster {idx+1} (size: {len(cluster)}):")
        for i in cluster:
            print(f"- {df.iloc[i].get('title', '')}")


if __name__ == "__main__":
    main()
    print("DuckDB connection established, data fetched, and clustering complete.")
