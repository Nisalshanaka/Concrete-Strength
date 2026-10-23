
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.pipeline.Predict import CustomData, PredictPipeline


class ConcreteStrengthApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Concrete Strength Predictor")
        self.resize(650, 720)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f7fb;
            }
            QLabel {
                color: #243247;
                font-size: 14px;
            }
            QLabel#heading {
                font-size: 25px;
                font-weight: bold;
                color: #17365d;
            }
            QLabel#subtitle {
                color: #607086;
                font-size: 13px;
            }
            QFrame#panel {
                background-color: white;
                border: 1px solid #dce4ef;
                border-radius: 12px;
            }
            QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background-color: white;
                min-width: 120px;
            }
            QPushButton {
                background-color: #1769aa;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 7px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #12578e;
            }
            QLabel#result {
                font-size: 23px;
                font-weight: bold;
                color: #1769aa;
                padding: 12px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        heading = QLabel("Concrete Strength Predictor")
        heading.setObjectName("heading")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(heading)

        subtitle = QLabel(
            "Estimate concrete compressive strength using machine learning"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        panel = QFrame()
        panel.setObjectName("panel")
        form = QFormLayout(panel)
        form.setContentsMargins(22, 22, 22, 22)
        form.setVerticalSpacing(13)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.inputs = {}

        fields = [
            ("Cement", "Cement (kg/m³)", 350),
            ("Blast_Furnace_Slag", "Blast Furnace Slag (kg/m³)", 100),
            ("Fly_Ash", "Fly Ash (kg/m³)", 50),
            ("Water", "Water (kg/m³)", 180),
            ("Superplasticizer", "Superplasticizer (kg/m³)", 8),
            ("Coarse_Aggregate", "Coarse Aggregate (kg/m³)", 1000),
            ("Fine_Aggregate", "Fine Aggregate (kg/m³)", 750),
            ("Age", "Age (days)", 28),
        ]

        for key, label_text, default in fields:
            spin = QDoubleSpinBox()
            spin.setRange(1 if key == "Age" else 0, 5000)
            spin.setDecimals(0 if key == "Age" else 2)
            spin.setSingleStep(1 if key == "Age" else 10)
            spin.setValue(default)
            spin.setMinimumWidth(160)

            self.inputs[key] = spin
            form.addRow(label_text, spin)

        main_layout.addWidget(panel)

        self.predict_button = QPushButton("Predict Compressive Strength")
        self.predict_button.clicked.connect(self.predict_strength)
        main_layout.addWidget(self.predict_button)

        self.result_label = QLabel("Enter the mix details and predict.")
        self.result_label.setObjectName("result")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        main_layout.addWidget(self.result_label)

        note = QLabel(
            "Units: material quantities in kg/m³; age in days; "
            "predicted strength in MPa. Predictions are estimates, "
            "not a substitute for laboratory testing."
        )
        note.setObjectName("subtitle")
        note.setWordWrap(True)
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(note)

    def predict_strength(self):
        values = {
            key: widget.value()
            for key, widget in self.inputs.items()
        }

        if (
            values["Cement"]
            + values["Blast_Furnace_Slag"]
            + values["Fly_Ash"]
            <= 0
        ):
            QMessageBox.warning(
                self,
                "Invalid input",
                "At least one cementitious material must be greater than zero.",
            )
            return

        self.predict_button.setEnabled(False)
        self.predict_button.setText("Predicting...")

        try:
            custom_data = CustomData(**values)
            input_df = custom_data.get_data_as_data_frame()

            pipeline = PredictPipeline()
            prediction = pipeline.predict(input_df)

            strength = float(prediction[0])

            self.result_label.setText(
                f"Predicted Compressive Strength\n{strength:.2f} MPa"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Prediction Error",
                f"Could not predict concrete strength.\n\n{error}",
            )
            self.result_label.setText("Prediction failed. Check the error details.")

        finally:
            self.predict_button.setEnabled(True)
            self.predict_button.setText("Predict Compressive Strength")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConcreteStrengthApp()
    window.show()
    sys.exit(app.exec())
