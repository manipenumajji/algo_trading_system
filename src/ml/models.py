from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


class ModelFactory:

    @staticmethod
    def get_xgboost():

        model = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42
        )

        return model

    @staticmethod
    def get_random_forest():

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )

        return model

    @staticmethod
    def get_logistic_regression():

        model = LogisticRegression(
            max_iter=1000,
            random_state=42
        )

        return model

    @staticmethod
    def get_all_models():

        return {
            "xgboost":
                ModelFactory.get_xgboost(),

            "random_forest":
                ModelFactory.get_random_forest(),

            "logistic_regression":
                ModelFactory.get_logistic_regression()
        }