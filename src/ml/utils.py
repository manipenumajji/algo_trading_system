import os
import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


class MLUtils:

    @staticmethod
    def evaluate_model(
        y_true,
        y_pred
    ):

        metrics = {
            "accuracy": accuracy_score(
                y_true,
                y_pred
            ),

            "precision": precision_score(
                y_true,
                y_pred,
                zero_division=0
            ),

            "recall": recall_score(
                y_true,
                y_pred,
                zero_division=0
            ),

            "f1_score": f1_score(
                y_true,
                y_pred,
                zero_division=0
            )
        }

        return metrics

    @staticmethod
    def print_metrics(
        y_true,
        y_pred
    ):

        metrics = (
            MLUtils.evaluate_model(
                y_true,
                y_pred
            )
        )

        print("\n========== Metrics ==========")

        print(
            f"Accuracy  : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Precision : "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"Recall    : "
            f"{metrics['recall']:.4f}"
        )

        print(
            f"F1 Score  : "
            f"{metrics['f1_score']:.4f}"
        )

        print(
            "\nConfusion Matrix:"
        )

        print(
            confusion_matrix(
                y_true,
                y_pred
            )
        )

        print(
            "\nClassification Report:"
        )

        print(
            classification_report(
                y_true,
                y_pred,
                zero_division=0
            )
        )

    @staticmethod
    def save_model(
        model,
        filepath
    ):

        folder = os.path.dirname(
            filepath
        )

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        joblib.dump(
            model,
            filepath
        )

        print(
            f"Model saved to "
            f"{filepath}"
        )

    @staticmethod
    def load_model(
        filepath
    ):

        if not os.path.exists(
            filepath
        ):
            raise FileNotFoundError(
                f"Model not found: "
                f"{filepath}"
            )

        model = joblib.load(
            filepath
        )

        return model

    @staticmethod
    def feature_importance(
        model,
        feature_names
    ):

        if not hasattr(
            model,
            "feature_importances_"
        ):
            return None

        importance = pd.DataFrame(
            {
                "feature":
                feature_names,

                "importance":
                model.feature_importances_
            }
        )

        importance = (
            importance
            .sort_values(
                by="importance",
                ascending=False
            )
            .reset_index(
                drop=True
            )
        )

        return importance