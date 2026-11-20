import unittest
from app import app  # Import your Flask app instance


class TestModelAppIntegration(unittest.TestCase):

	def setUp(self):
		app.testing = True
		self.client = app.test_client()
		
	def test_model_app_integration(self):
		# Valid test input that should work with the trained model
		form_data = {
			'temperature': '275.15',   # Kelvin
			'pressure': '1013',        # hPa
			'humidity': '85',          # %
			'wind_speed': '3.6',       # m/s
			'wind_deg': '180',         # degrees
			'rain_1h': '0',            # mm
			'rain_3h': '0',            # mm
			'snow': '0',               # mm
			'clouds': '20'             # %
		}

		response = self.client.post('/', data=form_data)
	
		# Complete below
		# The request should succeed and return the result page, not the form with an error
		self.assertEqual(response.status_code, 200)
		self.assertNotIn(b'Error processing input', response.data,
			"App returned an error instead of a prediction")
		self.assertIn(b'Prediction Result', response.data,
			"Result page was not rendered")

		# Ensure that the result page (response.data) should include a weather prediction
		self.assertIn(b'The weather is:', response.data,
			"Result page does not include a weather prediction")
	
		# Ensure that the result page should include a prediction time
		self.assertIn(b'Prediction time:', response.data,
			"Result page does not include a prediction time")
		self.assertRegex(response.data.decode('utf-8'), r'\d+(\.\d+)?\s*ms',
			"Prediction time is not a number in ms")

		html_text = response.data.decode('utf-8').lower()
		valid_classes = [
			'clear', 'cloudy', 'drizzly', 'foggy', 'hazey',
			'misty', 'rainy', 'smokey', 'thunderstorm'
		]
		found = any(weather in html_text for weather in valid_classes)
		
		# Ensure that classification is in valid classes, provide an error message if not.
		self.assertTrue(found,
			f"Prediction is not one of the valid weather classes: {valid_classes}")
		

if __name__ == '__main__':
	unittest.main()