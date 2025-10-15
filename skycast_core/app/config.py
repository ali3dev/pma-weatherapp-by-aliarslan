from dotenv import load_dotenv
import os 


load_dotenv()  # Load environment variables from .env file

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_masked_api_key():
	"""Return a masked version of the API key suitable for safe logging.

	If the key is missing, returns None. If present, shows first 4 and last 4
	characters with the middle replaced by asterisks.
	"""
	if not OPENWEATHER_API_KEY:
		return None
	key = OPENWEATHER_API_KEY
	if len(key) <= 8:
		# For short keys, mask everything except first and last character
		return key[0] + "*" * (len(key) - 2) + key[-1]
	return key[:4] + "*" * (len(key) - 8) + key[-4:]