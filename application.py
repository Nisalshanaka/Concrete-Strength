
from flask import Flask, request, jsonify
import numpy as np

from src.pipeline.predict_pipeline import (
    CustomData,
    PredictPipeline
)

application = Flask(__name__)
app = application


# -----------------------------
# Health check
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "success",
        "message": "Concrete Strength Prediction API is running",
        "endpoint": "/predictdata"
    })


# -----------------------------
# Prediction endpoint
# -----------------------------
@app.route("/predictdata", methods=["POST"])
def predict_datapoint():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "error": "A valid JSON object is required."
            }), 400

        required_fields = [
            "Cement",
            "Blast_Furnace_Slag",
            "Fly_Ash",
            "Water",
            "Superplasticizer",
            "Coarse_Aggregate",
            "Fine_Aggregate",
            "Age"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return jsonify({
                "status": "error",
                "error": "Missing required fields.",
                "missing_fields": missing_fields
            }), 400

        # Convert JSON values into numerical values
        values = {}

        for field in required_fields:
            value = float(data[field])

            if not np.isfinite(value):
                return jsonify({
                    "status": "error",
                    "error": f"{field} must be a finite number."
                }), 400

            values[field] = value

        # Basic input validation
        if any(values[field] < 0 for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Input quantities cannot be negative."
            }), 400

        if values["Age"] < 1:
            return jsonify({
                "status": "error",
                "error": "Age must be at least one day."
            }), 400

        if (
            values["Cement"]
            + values["Blast_Furnace_Slag"]
            + values["Fly_Ash"] <= 0
        ):
            return jsonify({
                "status": "error",
                "error": (
                    "At least one cementitious material "
                    "must have a positive quantity."
                )
            }), 400

        # Create the input DataFrame using CustomData
        custom_data = CustomData(
            Cement=values["Cement"],
            Blast_Furnace_Slag=values["Blast_Furnace_Slag"],
            Fly_Ash=values["Fly_Ash"],
            Water=values["Water"],
            Superplasticizer=values["Superplasticizer"],
            Coarse_Aggregate=values["Coarse_Aggregate"],
            Fine_Aggregate=values["Fine_Aggregate"],
            Age=values["Age"]
        )

        input_df = custom_data.get_data_as_data_frame()

        print("Input DataFrame:")
        print(input_df)

        # Run the existing prediction pipeline
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(input_df)

        prediction = float(
            np.asarray(results).reshape(-1)[0]
        )

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "unit": "MPa"
        }), 200

    except (TypeError, ValueError) as e:
        return jsonify({
            "status": "error",
            "error": f"Invalid input: {str(e)}"
        }), 400

    except Exception:
        # Full traceback is printed in the Flask terminal.
        app.logger.exception("Concrete strength prediction failed")

        return jsonify({
            "status": "error",
            "error": (
                "Prediction failed. Check the Flask "
                "terminal for the traceback."
            )
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        
    )
