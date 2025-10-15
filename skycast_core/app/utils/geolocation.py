import requests


def get_location_from_ip():
        """Get approximate user location using IP-based lookup."""
        try:
                res = requests.get("https://ipapi.co/json/")
                if res.status_code == 200:
                        data = res.json()
                        return data.get("city", "unknown")
        except Exception as e:
                print(f"Error fetching location: {e}")
                return "unknown"
