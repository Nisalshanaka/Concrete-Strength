
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.exception import CustomException
from src.utils import load_object


def get_project_root():
    """
    Locate the project root during development or when
    running a PyInstaller-packaged Windows application.
    """
    if getattr(sys, "frozen", False):
        # Directory containing bundled application resources
        return Path(sys._MEIPASS)

    # File is: project_root/src/pipeline/predict_pipeline.py
    return Path(__file__).resolve().parents[2]


class PredictPipeline:
    def __init__(self):
        self.base_dir = get_project_root()

    def predict(self, features: pd.DataFrame):
        try:
            model_path = self.base_dir / "artifacts" / "model.pkl"
            preprocessor_path = (
                self.base_dir / "artifacts" / "preprocessor.pkl"
            )

            # Check that required artifacts exist
            if not model_path.is_file():
                raise FileNotFoundError(
                    f"Model file not found: {model_path}"
                )

            if not preprocessor_path.is_file():
                raise FileNotFoundError(
                    f"Preprocessor file not found: "
                    f"{preprocessor_path}"
                )

            # Validate input type
            if not isinstance(features, pd.DataFrame):
                raise TypeError(
                    "Input features must be a pandas DataFrame."
                )

            # These names must match the columns used when
            # fitting the original preprocessor.
            expected_columns = [
                "Cement",
                "Blast Furnace Slag",
                "Fly Ash",
                "Water",
                "Superplasticizer",
                "Coarse Aggregate",
                "Fine Aggregate",
                "Age",
            ]

            missing_columns = [
                column for column in expected_columns
                if column not in features.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"Missing input columns: {missing_columns}"
                )

            # Keep the original training feature order
            features = features[expected_columns].copy()

            # Check that all inputs are numeric and finite
            for column in expected_columns:
                features[column] = pd.to_numeric(
                    features[column], errors="raise"
                )

            if not np.isfinite(
                features.to_numpy(dtype=float)
            ).all():
                raise ValueError(
                    "Input data contains NaN or infinite values."
                )

            print(f"Loading model from: {model_path}")
            model = load_object(file_path=str(model_path))

            print(
                f"Loading preprocessor from: "
                f"{preprocessor_path}"
            )
            preprocessor = load_object(
                file_path=str(preprocessor_path)
            )

            print("Model and preprocessor loaded successfully.")
            print("Input DataFrame:")
            print(features)

            # Apply the fitted training preprocessor
            transformed_features = preprocessor.transform(features)

            print(
                "Transformed input shape:",
                transformed_features.shape
            )

            # Generate predictions
            predictions = model.predict(transformed_features)

            predictions = np.asarray(predictions).reshape(-1)

            if predictions.size != len(features):
                raise ValueError(
                    "The number of predictions does not match "
                    "the number of input rows."
                )

            if not np.isfinite(predictions.astype(float)).all():
                raise ValueError(
                    "The model returned a non-finite prediction."
                )

            print("Predicted Strength:", predictions)

            return predictions

        except Exception as e:
            # Preserve your project's existing exception handling
            raise CustomException(e, sys) from e


class CustomData:
    """
    Converts user-entered concrete mix values into the
    DataFrame expected by the fitted preprocessor.
    """

    def __init__(
        self,
        Cement: float,
        Blast_Furnace_Slag: float,
        Fly_Ash: float,
        Water: float,
        Superplasticizer: float,
        Coarse_Aggregate: float,
        Fine_Aggregate: float,
        Age: float,
    ):
        self.Cement = Cement
        self.Blast_Furnace_Slag = Blast_Furnace_Slag
        self.Fly_Ash = Fly_Ash
        self.Water = Water
        self.Superplasticizer = Superplasticizer
        self.Coarse_Aggregate = Coarse_Aggregate
        self.Fine_Aggregate = Fine_Aggregate
        self.Age = Age

    def get_data_as_data_frame(self):
        try:
            input_data = {
                "Cement": [self.Cement],
                "Blast Furnace Slag": [
                    self.Blast_Furnace_Slag
                ],
                "Fly Ash": [self.Fly_Ash],
                "Water": [self.Water],
                "Superplasticizer": [
                    self.Superplasticizer
                ],
                "Coarse Aggregate": [
                    self.Coarse_Aggregate
                ],
                "Fine Aggregate": [
                    self.Fine_Aggregate
                ],
                "Age": [self.Age],
            }

            features = pd.DataFrame(input_data)

            # Ensure numeric input values
            features = features.astype(float)

            if not np.isfinite(features.to_numpy()).all():
                raise ValueError(
                    "Input features must be finite numbers."
                )

            return features

        except Exception as e:
            raise CustomException(e, sys) from e
