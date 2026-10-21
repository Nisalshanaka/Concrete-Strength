
import streamlit as st
import requests

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Concrete Strength Predictor",
    page_icon="🏗️",
    layout="wide"
)

API_URL = "http://127.0.0.1:5000/predictdata"


# -----------------------------
# Header
# -----------------------------
st.title("🏗️ Concrete Compressive Strength Predictor")

st.write(
    "Predict concrete compressive strength using "
    "a machine learning model."
)

st.caption(
    "Material quantities: kg/m³ | Age: days | "
    "Predicted strength: MPa"
)

st.divider()


# -----------------------------
# Input form
# -----------------------------
st.subheader("Concrete Mix Parameters")

with st.form("concrete_prediction_form"):

    col1, col2 = st.columns(2)

    with col1:
        Cement = st.number_input(
            "Cement (kg/m³)",
            min_value=0.0,
            value=350.0,
            step=10.0
        )

        Blast_Furnace_Slag = st.number_input(
            "Blast Furnace Slag (kg/m³)",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        Fly_Ash = st.number_input(
            "Fly Ash (kg/m³)",
            min_value=0.0,
            value=50.0,
            step=10.0
        )

        Water = st.number_input(
            "Water (kg/m³)",
            min_value=0.0,
            value=180.0,
            step=5.0
        )

    with col2:
        Superplasticizer = st.number_input(
            "Superplasticizer (kg/m³)",
            min_value=0.0,
            value=8.0,
            step=1.0
        )

        Coarse_Aggregate = st.number_input(
            "Coarse Aggregate (kg/m³)",
            min_value=0.0,
            value=1000.0,
            step=10.0
        )

        Fine_Aggregate = st.number_input(
            "Fine Aggregate (kg/m³)",
            min_value=0.0,
            value=750.0,
            step=10.0
        )

        Age = st.number_input(
            "Age (days)",
            min_value=1,
            max_value=365,
            value=28,
            step=1
        )

    submitted = st.form_submit_button(
        "Predict Compressive Strength",
        type="primary",
        use_container_width=True
    )


# -----------------------------
# Send input to Flask
# -----------------------------
if submitted:

    payload = {
        "Cement": Cement,
        "Blast_Furnace_Slag": Blast_Furnace_Slag,
        "Fly_Ash": Fly_Ash,
        "Water": Water,
        "Superplasticizer": Superplasticizer,
        "Coarse_Aggregate": Coarse_Aggregate,
        "Fine_Aggregate": Fine_Aggregate,
        "Age": Age
    }

    if Cement + Blast_Furnace_Slag + Fly_Ash <= 0:
        st.error(
            "At least one cementitious material must "
            "have a positive quantity."
        )

    else:
        try:
            with st.spinner(
                "Sending data to the prediction server..."
            ):
                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=30
                )

            if response.ok:
                result = response.json()

                prediction = float(result["prediction"])
                unit = result.get("unit", "MPa")

                st.divider()
                st.subheader("Prediction Result")

                st.metric(
                    label="Predicted Compressive Strength",
                    value=f"{prediction:.2f} {unit}"
                )

                st.success("Prediction completed successfully!")

                with st.expander("View submitted inputs"):
                    st.json(payload)

            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get(
                        "error", response.text
                    )
                except ValueError:
                    error_message = response.text

                st.error(
                    f"API Error ({response.status_code}): "
                    f"{error_message}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Flask. Start the Flask "
                "backend and check the API URL."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The prediction request timed out. "
                "Check the Flask terminal."
            )

        except (requests.exceptions.RequestException,
                ValueError, KeyError) as e:
            st.error(f"Request or response error: {e}")

st.divider()

st.caption(
    "Machine learning predictions are estimates and do not "
    "replace laboratory compressive strength testing."
)
