import unittest
from app import app, classify_weather, load_model
import numpy as np

class TestUnit(unittest.TestCase):
	def setUp(self):
		app.testing = True
		self.client = app.test_client()
	
	# Complete this function to test proper handling of missing input field in the input
	def test_post_missing_field(self):
		form_data = {
			'temperature': '270.277',
			'pressure': '1006',
			'humidity': '84',
			# 'wind_speed' is missing
			'wind_deg': '274',
			'rain_1h': '0',
			'rain_3h': '0',
			'snow': '0',
			'clouds': '9'
		}
		response = self.client.post('/', data=form_data)
		# The app should not crash, it should handle the error gracefully
		self.assertEqual(response.status_code, 200)
		# The form should be shown again with an error message
		self.assertIn(b'Error processing input', response.data,
			"No error message shown for missing input field")
		self.assertIn(b'<form', response.data,
			"Input form was not re-displayed after an error")
		# No prediction should be made
		self.assertNotIn(b'Prediction Result', response.data,
			"A prediction was made despite a missing input field")

	# Complete this function to test that the model can be loaded correctly
	def test_model_can_be_loaded(self):
		model = load_model()
		self.assertIsNotNone(model, "Model failed to load")
		self.assertTrue(hasattr(model, 'predict'),
			"Loaded model does not have a predict method")

	# Test model classification is within the 9 classes, each time for a different class with three different inputs
	def test_clear_classification_output(self):
		test_input = np.array([269.686,1002,78,0,23,0,0,0,0]).reshape(1,-1)
		class_result, _ = classify_weather(test_input) 
		# Ensure that 'clear' class is returned
		self.assertEqual(class_result, 'clear',
			f"Expected 'clear' but got '{class_result}'")
		
	def test_rainy_classification_output(self):
		test_input = np.array([279.626,998,99,1,314,0.3,0,0,88]).reshape(1,-1)
		class_result, _ = classify_weather(test_input) 
		# Ensure that 'rainy' class is returned
		self.assertEqual(class_result, 'rainy',
			f"Expected 'rainy' but got '{class_result}'")

	def test_foggy_classification_output(self):

		test_input = np.array([289.47,1015,88,2,300,0,0,0,20]).reshape(1,-1)
		class_result, _ = classify_weather(test_input) 

		# Ensure that 'foggy' class is returned
		self.assertEqual(class_result, 'foggy',
			f"Expected 'foggy' but got '{class_result}'")
		
if __name__ == '__main__':
	unittest.main()