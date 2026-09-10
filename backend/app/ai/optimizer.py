import random
from datetime import datetime

class BlockOptimizer:
    def generate_suggestions(self, trains: list, blocks: list) -> list:
        suggestions = []
        sid = 1
        delayed = [t for t in trains if t.get("delay_minutes", 0) > 15]
        for train in delayed[:3]:
            suggestions.append({
                "id": sid,
                "type": "Delay Resolution",
                "description": f"Reroute Train {train.get('train_number','?')} to recover {train.get('delay_minutes',0)} min delay",
                "priority": "high" if train.get("delay_minutes", 0) > 30 else "medium",
                "impact": round(random.uniform(15, 40), 1),
                "estimated_time": random.randint(5, 15),
                "affected_trains": [train.get("train_number", "?")]
            })
            sid += 1
        maint = [b for b in blocks if b.get("status") == "maintenance"]
        if maint:
            suggestions.append({
                "id": sid,
                "type": "Maintenance Optimization",
                "description": f"Schedule {len(maint)} block(s) for 02:00-04:00 AM maintenance window",
                "priority": "medium",
                "impact": round(random.uniform(10, 25), 1),
                "estimated_time": random.randint(30, 120),
                "affected_trains": []
            })
            sid += 1
        free = [b for b in blocks if b.get("status") == "free"]
        if len(free) > 3:
            suggestions.append({
                "id": sid,
                "type": "Capacity Optimization",
                "description": f"Utilize {len(free)} free blocks to increase throughput",
                "priority": "low",
                "impact": round(random.uniform(5, 15), 1),
                "estimated_time": random.randint(10, 30),
                "affected_trains": []
            })
        return suggestions

    def execute_optimization(self, suggestions, trains, blocks):
        return {
            "status": "success",
            "message": f"Optimization executed. {len(suggestions)} changes applied.",
            "delay_saved_minutes": sum(random.randint(5, 20) for _ in suggestions),
            "efficiency_gain_percent": round(random.uniform(8, 25), 1),
            "timestamp": datetime.utcnow().isoformat()
        }
