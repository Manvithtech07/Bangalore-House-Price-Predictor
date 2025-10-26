from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd

#initialize the Flask app
app = Flask(__name__)
with open('model/xgb_model.pkl', 'rb') as f:
    model = pickle.load(f)

if model:
    preprocessor = model.named_steps['columntransformer']
    ohe_feature_names = preprocessor.named_transformers_['onehotencoder'].get_feature_names_out(['location'])
    locations = sorted([name.split('_')[-1] for name in ohe_feature_names])
else:
    locations = ["Error loading locations"]


@app.route('/')
def home():
    return render_template('index.html', locations=locations)


@app.route('/predict', methods=['POST'])
def predict():
    result_text = ""
    try:
        location = request.form.get('location')
        bhk = int(request.form.get('bhk'))
        bath = int(request.form.get('bath'))
        total_sqft = float(request.form.get('total_sqft'))

        input_data = pd.DataFrame([[location, total_sqft, bath, bhk]],
                                  columns=['location', 'total_sqft', 'bath', 'bhk'])

        if model:
            prediction = model.predict(input_data)[0]
            result_text = f"Predicted Price: ₹ {prediction:.2f} Lakhs"
        else:
            result_text = "Error."

    except Exception as e:
        result_text = f"Error{e}"

    return render_template('index.html', prediction_text=result_text, locations=locations)


if __name__ == '__main__':
        app.run(debug=True)

