from pathlib import Path
import joblib
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"


def train_and_save_model() -> None:
    """
    Train a very simple binary classifier and save it to disk.
    This is enough for the final project structure and future CI retrain step.
    """
    X, y = make_classification(
        n_samples=500,
        n_features=3,
        n_informative=3,
        n_redundant=0,
        n_classes=2,
        random_state=42
    )

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()
