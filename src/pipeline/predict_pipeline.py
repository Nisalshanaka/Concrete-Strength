
import os
import sys
import pandas as pd

from src.exception import CustomException
from src.utils import load_object


class PredictPipeline:
    def __init__(self):
        pass

    def predict(self, features: pd.DataFrame):
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join(
                "artifacts", "proprocessor.pkl"
            )

            print("Loading model and preprocessor...")

            model = load_object(file_path=model_path)
            preprocessor = load_object(
                file_path=preprocessor_path
            )

            print("Model and preprocessor loaded.")
            print("Input columns:", features.columns.tolist())

            # Transform using the fitted preprocessor
            data_transformed = preprocessor.transform(features)

            print("Input preprocessing completed.")
            print("Transformed shape:", data_transformed.shape)

            # Predict concrete compressive strength
            predictions = model.predict(data_transformed)

            print("Prediction completed:", predictions)

            return predictions

        except Exception as e:
            raise CustomException(e, sys) from e


class CustomData:
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
            # These column names match the original dataset.
            custom_data_input_dict = {
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

            return pd.DataFrame(custom_data_input_dict)

        except Exception as e:
            raise CustomException(e, sys) from e
