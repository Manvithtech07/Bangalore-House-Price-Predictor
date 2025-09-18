from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd

# Initialize the Flask app
app = Flask(__name__)

try:
    with open('model/xgb_model.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Error: 'xgb_model.pkl' not found in the 'model' directory.")
    print("Please make sure the model file is in the correct location and the 'Working directory' in your Run Configuration is set to the project root.")
    model = None # Set model to None to prevent further errors on startup

if model:
    preprocessor = model.named_steps['columntransformer']
    ohe_feature_names = preprocessor.named_transformers_['onehotencoder'].get_feature_names_out(['location'])
    locations = sorted([name.split('_')[-1] for name in ohe_feature_names])
else:
    locations = ["Error loading locations"]


@app.route('/')
def home():
    """Renders the home page with the location dropdown."""
    return render_template('index.html', locations=locations)


@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction request from the form."""
    result_text = ""
    try:
        location = request.form.get('location')
        bhk = int(request.form.get('bhk'))
        bath = int(request.form.get('bath'))
        total_sqft = float(request.form.get('total_sqft'))

        # Create a DataFrame from the input, matching the model's training structure
        input_data = pd.DataFrame([[location, total_sqft, bath, bhk]],
                                  columns=['location', 'total_sqft', 'bath', 'bhk'])

        if model:
            prediction = model.predict(input_data)[0]
            # Format the prediction result
            result_text = f"Predicted Price: ₹ {prediction:.2f} Lakhs"
        else:
            result_text = "Error: Model is not loaded."

    except Exception as e:
        result_text = f"Error: Please check your inputs. Details: {e}"

    return render_template('index.html', prediction_text=result_text, locations=locations)


if __name__ == '__main__':
        app.run(debug=True)
