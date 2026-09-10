import random
from datetime import datetime

class DelayPredictor:
    def __init__(self):
        self.weather_factors = {
            "clear": 1.0, "rain": 1.4, "fog": 1.6,
            "flood": 2.5, "storm": 2.0, "heatwave": 1.2
        }
        self.train_priority = {
            "medical_emergency": 10, "defense": 9,
            "high_speed": 8, "express": 7,
            "passenger": 5, "freight": 3, "local": 4
        }

    def calculate_priority_score(self, train_data: dict) -> float:
        base = self.train_priority.get(train_data.get("type", "local"), 4)
        delay_f = min(train_data.get("delay_minutes", 0) / 30, 2.0)
        pass_f = train_data.get("passenger_load", 0) / 100
        weather = train_data.get("weather", "clear")
        weather_f = self.weather_factors.get(weather, 1.0)
        score = ((base * 0.4) + (delay_f * 0.25) + (pass_f * 0.2) + (weather_f * 0.15)) * 10
        return round(min(score, 100), 2)

    def predict_delay(self, train_data: dict) -> dict:
        base_delay = train_data.get("current_delay", 0)
        weather = train_data.get("weather", "clear")
        weather_m = self.weather_factors.get(weather, 1.0)
        track_health = train_data.get("track_health", 100) / 100
        track_impact = (1 - track_health) * 20
        hour = datetime.now().hour
        peak = list(range(7, 10)) + list(range(17, 20))
        time_f = 1.3 if hour in peak else 1.0
        predicted = int((base_delay + track_impact) * weather_m * time_f + random.randint(-5, 5))
        return {
            "predicted_delay_minutes": max(0, predicted),
            "confidence": round(random.uniform(0.75, 0.95), 2),
            "contributing_factors": {
                "weather": weather,
                "track_health": track_health * 100,
                "time_factor": "peak" if hour in peak else "off-peak",
                "base_delay": base_delay
            }
        }
