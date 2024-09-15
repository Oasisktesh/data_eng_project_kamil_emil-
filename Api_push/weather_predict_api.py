import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd  # Ensure pandas is imported

# Load the trained model
with open('/app/random_forest_model_v1_5_1.pkl', 'rb') as f:
    model = pickle.load(f)

# Initialize the FastAPI app
app = FastAPI()

# Define the expected input data structure
class WeatherInput(BaseModel):
    clouds: float
    max_temp_ts: float
    max_wind_spd: float
    min_temp: float
    snow: float
    solar_rad: float
    wind_gust_spd: float
    wind_spd: float

@app.post("/predict/")
async def predict_weather(input_data: WeatherInput):
    try:
        # Convert input data to a pandas DataFrame
        input_df = pd.DataFrame([{
            'clouds': input_data.clouds,
            'max_temp_ts': input_data.max_temp_ts,
            'max_wind_spd': input_data.max_wind_spd,
            'min_temp': input_data.min_temp,
            'snow': input_data.snow,
            'solar_rad': input_data.solar_rad,
            'wind_gust_spd': input_data.wind_gust_spd,
            'wind_spd': input_data.wind_spd
        }])
        
        # Predict using the loaded model
        predicted_temperature = model.predict(input_df)[0]
        
        # Return the predicted temperature
        return {"predicted_temperature": predicted_temperature}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))