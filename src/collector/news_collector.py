import requests
import time
from datetime import datetime, timedelta, timezone
import psycopg2


class NewsCollector:

    def __init__(
        self,
        api_key,
        assets,
        db_config,
        hours_back=168
    ):
        self.api_key = api_key
        self.assets = assets
        self.db_config = db_config
        self.hours_back = hours_back

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def fetch_news(self, asset):

        query_map = {
            "BTC": "Bitcoin",
            "XRP": "XRP",
            "ADA": "Cardano"
        }

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": query_map.get(asset, asset),
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
            "apiKey": self.api_key
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                print(
                    f"Failed to fetch {asset} news: "
                    f"{response.status_code} - {response.text}"
                )
                return []

            data = response.json()

            total_articles = len(data.get("articles", []))
            

            articles = []

            cutoff_time = (
                datetime.now(timezone.utc)
                - timedelta(hours=self.hours_back)
            )

            

            for post in data.get("articles", []):

                if not post.get("publishedAt"):
                    continue

                published_at = datetime.fromisoformat(
                    post["publishedAt"].replace(
                        "Z",
                        "+00:00"
                    )
                )


                if published_at < cutoff_time:
                    continue

                article = {
                    "asset": asset,
                    "title": post.get("title", ""),
                    "content": post.get("description", ""),
                    "url": post.get("url", ""),
                    "source": post.get(
                        "source",
                        {}
                    ).get(
                        "name",
                        "Unknown"
                    ),
                    "published_at": published_at
                }

                articles.append(article)

            print(
                f"Fetched {len(articles)} articles for {asset}"
            )

            return articles

        except Exception as e:
            print(
                f"Error fetching news for {asset}: {e}"
            )
            return []

    def save_to_db(self, articles):

        if not articles:
            return

        conn = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO news_raw
            (
                asset,
                title,
                content,
                url,
                source,
                published_at
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s
            )
            ON CONFLICT (url)
            DO NOTHING;
            """

            inserted = 0

            for article in articles:

                cursor.execute(
                    query,
                    (
                        article["asset"],
                        article["title"],
                        article["content"],
                        article["url"],
                        article["source"],
                        article["published_at"]
                    )
                )

                inserted += cursor.rowcount

            conn.commit()

            print(
                f"Inserted {inserted} new articles"
            )

        except Exception as e:
            print(
                f"Database insert failed: {e}"
            )

        finally:
            if conn:
                conn.close()

    def fetch_all(self):

        for asset in self.assets:

            print(f"\nFetching {asset} news...")

            articles = self.fetch_news(asset)

            self.save_to_db(articles)

            time.sleep(1)