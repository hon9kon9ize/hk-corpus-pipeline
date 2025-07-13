import os
from datetime import datetime
import duckdb
import boto3
from io import BytesIO
from dotenv import load_dotenv
import pandas as pd
import argparse


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


def get_r2_client():
    r2_key_id = os.getenv("R2_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_KEY")
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    s3 = boto3.resource(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_key_id,
        aws_secret_access_key=r2_secret_key,
        region_name="weur",
    )

    return s3


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
    ACCOUNT_ID '{r2_account_id}'
);"""
    )


def main():
    args = argparse.ArgumentParser(description="Archive R2 data to Parquet")
    args.add_argument(
        "--day-ago",
        type=int,
        default=3,
        help="Number of days ago to archive data from (default: 3)",
    )
    args = args.parse_args()

    load_env_vars()
    setup_duckdb_connection()
    s3 = get_r2_client()
    bucket_name = os.getenv("R2_BUCKET_NAME")
    today = datetime.now()
    yesterday = today.replace(hour=0, minute=0, second=0, microsecond=0) - pd.Timedelta(
        days=args.day_ago
    )
    date_string = yesterday.strftime("%Y-%m-%d")

    print(f"Archiving data for date: {date_string}")

    query = f"SELECT * FROM read_json('r2://{bucket_name}/event_date={date_string}/**/*.json.gz')"

    try:
        df = conn.execute(query).df()

        if df.empty:
            print(f"No data found for date: {date_string}")
            return

        df = df[df["event"] == "scraping"]  # filter for scraping events
        df = pd.DataFrame(df["payload"].tolist())  # extract payload column
        df = df.drop_duplicates(
            subset=["url"]
        )  # remove duplicates based on title and date
        df = df[df["extracted"] != ""]  # filter out empty extracted content

        # save to R2 and remove old data
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)

        parquet_buffer.seek(0)  # rewind to beginning before upload

        s3.Object(bucket_name, f"event_date={date_string}/hr=01/archive.parquet").put(
            Body=parquet_buffer.getvalue()
        )

        # remove old data
        old_files = s3.Bucket(bucket_name).objects.filter(
            Prefix=f"event_date={date_string}"
        )

        for f in old_files:
            if f.key.endswith(".json.gz"):
                print(f"Deleting old file: {f.key}")
                s3.Object(bucket_name, f.key).delete()
    except Exception as e:
        print(f"Error processing data for date {date_string}: {e}")
        return


if __name__ == "__main__":
    main()
    print("DuckDB connection established, data fetched, and clustering complete.")
