import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from weather_predict_api import app  # Importera din app

client = TestClient(app)

class TestWeatherPredictionAPI(unittest.TestCase):

    @patch('weather_predict_api.pickle.load')  # Mocka modellens laddning
    @patch('builtins.open')  # Mocka open-funktionen
    def test_predict_weather_success(self, mock_open, mock_pickle_load):
        # Ställ in mockar för att returnera en fejkad modell
        mock_model = MagicMock()
        mock_model.predict.return_value = [11.125000000000002]  # Exempel på prediktion
        mock_pickle_load.return_value = mock_model

        input_data = {
            "clouds": 50.0,
            "max_temp_ts": 300.0,
            "max_wind_spd": 12.0,
            "min_temp": 280.0,
            "snow": 0.0,
            "solar_rad": 200.0,
            "wind_gust_spd": 20.0,
            "wind_spd": 10.0
        }

        response = client.post("/predict/", json=input_data)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn("predicted_temperature", response_json)
        self.assertEqual(response_json["predicted_temperature"], 11.125000000000002)

if __name__ == '__main__':
    unittest.main()