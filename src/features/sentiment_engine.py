import psycopg2
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentEngine:

    def __init__(self, db_config):
        self.db_config = db_config
        self.analyzer = SentimentIntensityAnalyzer()

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def fetch_news(self, asset):

        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        SELECT title
        FROM news_raw
        WHERE asset = %s
        """

        cursor.execute(query, (asset,))
        rows = cursor.fetchall()

        conn.close()

        return [row[0] for row in rows]

    def analyze_asset(self, asset):

        titles = self.fetch_news(asset)

        if not titles:
            return None

        total_score = 0

        bullish = 0
        bearish = 0
        neutral = 0

        for title in titles:

            score = self.analyzer.polarity_scores(
                title
            )["compound"]

            total_score += score

            if score > 0.05:
                bullish += 1
            elif score < -0.05:
                bearish += 1
            else:
                neutral += 1

        average_score = total_score / len(titles)

        return {
            "asset": asset,
            "sentiment_score": average_score,
            "article_count": len(titles),
            "bullish_count": bullish,
            "bearish_count": bearish,
            "neutral_count": neutral
        }

    def save_sentiment(self, result):

        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO news_sentiment
        (
            asset,
            sentiment_score,
            article_count,
            bullish_count,
            bearish_count,
            neutral_count
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )
        """

        cursor.execute(
            query,
            (
                result["asset"],
                result["sentiment_score"],
                result["article_count"],
                result["bullish_count"],
                result["bearish_count"],
                result["neutral_count"]
            )
        )

        conn.commit()
        conn.close()

    def run(self):

        assets = [
            "BTC",
            "XRP",
            "ADA"
        ]

        for asset in assets:

            result = self.analyze_asset(asset)

            if result:

                self.save_sentiment(result)

                print(
                    f"{asset} sentiment: "
                    f"{result['sentiment_score']:.3f}"
                )