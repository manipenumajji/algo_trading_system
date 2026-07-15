import joblib

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from sklearn.model_selection import (
    train_test_split
)

from src.ml.models import (
    ModelFactory
)

from src.ml.dataset_builder import (
    DatasetBuilder
)

from src.utils.logger import logger


class Trainer:

    def __init__(
        self,
        db_manager
    ):

        self.db_manager = db_manager

        self.dataset_builder = (
            DatasetBuilder(
                db_manager
            )
        )

    def evaluate(
        self,
        model,
        X_test,
        y_test,
        model_name
    ):

        predictions = model.predict(
            X_test
        )

        accuracy = accuracy_score(
            y_test,
            predictions
        )

        precision = precision_score(
            y_test,
            predictions
        )

        recall = recall_score(
            y_test,
            predictions
        )

        f1 = f1_score(
            y_test,
            predictions
        )

        logger.info(
            f"{model_name}"
        )

        logger.info(
            f"Accuracy: "
            f"{accuracy:.4f}"
        )

        logger.info(
            f"Precision: "
            f"{precision:.4f}"
        )

        logger.info(
            f"Recall: "
            f"{recall:.4f}"
        )

        logger.info(
            f"F1 Score: "
            f"{f1:.4f}"
        )

        logger.info(
            classification_report(
                y_test,
                predictions
            )
        )

        logger.info(
            confusion_matrix(
                y_test,
                predictions
            )
        )

    def train_single_model(
        self,
        X,
        y,
        model_name,
        model_file
    ):

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42,
                shuffle=True
            )
        )

        models = (
            ModelFactory
            .get_all_models()
        )

        best_model = None
        best_score = -1

        for name, model in (
            models.items()
        ):

            logger.info(
                f"Training "
                f"{name}"
            )

            model.fit(
                X_train,
                y_train
            )

            predictions = (
                model.predict(
                    X_test
                )
            )

            score = f1_score(
                y_test,
                predictions
            )

            self.evaluate(
                model,
                X_test,
                y_test,
                name
            )

            if score > best_score:

                best_score = score
                best_model = model

        logger.info(
            f"Best model for "
            f"{model_name}: "
            f"{best_model.__class__.__name__}"
        )

        logger.info(
            f"Best F1 score: "
            f"{best_score:.4f}"
        )

        joblib.dump(
            best_model,
            model_file
        )

        logger.info(
            f"Model saved: "
            f"{model_file}"
        )

    def run(self):

        (
            long_X,
            long_y,
            short_X,
            short_y
        ) = (
            self.dataset_builder
            .run()
        )

        logger.info(
            "Training long model"
        )

        self.train_single_model(
            long_X,
            long_y,
            "LONG",
            "models/long_model.pkl"
        )

        logger.info(
            "Training short model"
        )

        self.train_single_model(
            short_X,
            short_y,
            "SHORT",
            "models/short_model.pkl"
        )

        logger.info(
            "Training completed."
        )