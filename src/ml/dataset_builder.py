import pandas as pd


class DatasetBuilder:

    def __init__(
        self,
        db_manager
    ):
        self.db_manager = db_manager

    def load_features(self):

        query = """
        SELECT *
        FROM features_v1
        """

        return pd.read_sql(
            query,
            self.db_manager.connection
        )

    def load_labels(self):

        query = """
        SELECT *
        FROM labels_v1
        """

        return pd.read_sql(
            query,
            self.db_manager.connection
        )

    def build_dataset(self):

        features = (
            self.load_features()
        )

        labels = (
            self.load_labels()
        )

        dataset = features.merge(
            labels,
            on=[
                "symbol",
                "timestamp"
            ],
            how="inner"
        )

        # --------------------------------
        # Remove unresolved labels
        # --------------------------------

        dataset = dataset[
            (
                dataset[
                    "long_label"
                ] != -1
            )
            &
            (
                dataset[
                    "short_label"
                ] != -1
            )
        ]

        # --------------------------------
        # Remove duplicate columns
        # --------------------------------

        drop_columns = [
            "entry_price",
            "long_sl",
            "long_tp",
            "short_sl",
            "short_tp"
        ]

        existing = [
            c
            for c in drop_columns
            if c in dataset.columns
        ]

        dataset = dataset.drop(
            columns=existing
        )

        dataset = dataset.reset_index(
            drop=True
        )
        dataset = dataset.fillna(0)

        print(
            f"Final dataset size: "
            f"{len(dataset)} rows"
        )

        print(
            f"Columns: "
            f"{len(dataset.columns)}"
        )

        return dataset

    def get_long_dataset(
        self,
        dataset
    ):

        y = dataset[
            "long_label"
        ]

        X = dataset.drop(
            columns=[
                "long_label",
                "short_label",
                "symbol",
                "timestamp"
            ]
        )

        return X, y

    def get_short_dataset(
        self,
        dataset
    ):

        y = dataset[
            "short_label"
        ]

        X = dataset.drop(
            columns=[
                "long_label",
                "short_label",
                "symbol",
                "timestamp"
            ]
        )

        return X, y

    def run(self):

        dataset = (
            self.build_dataset()
        )

        long_X, long_y = (
            self.get_long_dataset(
                dataset
            )
        )

        short_X, short_y = (
            self.get_short_dataset(
                dataset
            )
        )

        print(
            f"Long samples: "
            f"{len(long_y)}"
        )

        print(
            f"Short samples: "
            f"{len(short_y)}"
        )

        return (
            long_X,
            long_y,
            short_X,
            short_y
        )