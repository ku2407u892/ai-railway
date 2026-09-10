from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .models import User, Block, Train, Alert, OptimizationLog
from .routes import auth, blocks, trains, alerts, optimization
from .routes.auth import get_password_hash
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI RailOps", description="AI-Powered Block Planning for Indian Railways", version="1.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ai-railway.vercel.app"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


app.include_router(auth.router)
app.include_router(blocks.router)
app.include_router(trains.router)
app.include_router(alerts.router)
app.include_router(optimization.router)


@app.on_event("startup")
def on_startup():
    seed()


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        db.add_all([
            User(username="admin", email="admin@railops.com", hashed_password=get_password_hash("railway123"), role="admin"),
            User(username="operator", email="operator@railops.com", hashed_password=get_password_hash("railway123"), role="operator")
        ])
        db.commit()

        block_data = [
            {"name":"AHM-01","location":"Ahmedabad Station","zone":"Western","status":"occupied","track_health":92.5},
            {"name":"DEL-01","location":"Delhi Junction","zone":"Northern","status":"occupied","track_health":94.0},
            {"name":"BOM-01","location":"Mumbai Central","zone":"Western","status":"free","track_health":97.0},
            {"name":"SRT-01","location":"Surat Station","zone":"Western","status":"reserved","track_health":89.5},
            {"name":"HP-01","location":"Shimla (Himachal Pradesh)","zone":"Northern","status":"maintenance","track_health":68.0},
        ]
        for b in block_data:
            db.add(Block(**b))
        db.commit()

        now = datetime.utcnow()
        train_data = [
            {"train_number":"12901","train_name":"Gujarat Express","train_type":"express","origin":"Ahmedabad","destination":"Mumbai","scheduled_departure":now+timedelta(hours=1),"scheduled_arrival":now+timedelta(hours=7),"delay_minutes":25,"status":"delayed","passenger_load":85.0,"priority_score":72.5,"current_block_id":1},
            {"train_number":"12951","train_name":"Rajdhani Express","train_type":"high_speed","origin":"Mumbai","destination":"Delhi","scheduled_departure":now+timedelta(hours=2),"scheduled_arrival":now+timedelta(hours=18),"delay_minutes":0,"status":"on_time","passenger_load":95.0,"priority_score":90.0,"current_block_id":3},
            {"train_number":"19023","train_name":"Firozpur Janta Express","train_type":"express","origin":"Surat","destination":"Delhi","scheduled_departure":now+timedelta(hours=3),"scheduled_arrival":now+timedelta(hours=20),"delay_minutes":40,"status":"delayed","passenger_load":80.0,"priority_score":58.0,"current_block_id":4},
            {"train_number":"14311","train_name":"Kalka Shimla Express","train_type":"passenger","origin":"Delhi","destination":"Shimla","scheduled_departure":now+timedelta(hours=4),"scheduled_arrival":now+timedelta(hours=14),"delay_minutes":15,"status":"delayed","passenger_load":70.0,"priority_score":50.0,"current_block_id":5},
            {"train_number":"09441","train_name":"Vande Bharat Express","train_type":"high_speed","origin":"Ahmedabad","destination":"Mumbai","scheduled_departure":now+timedelta(minutes=30),"scheduled_arrival":now+timedelta(hours=5),"delay_minutes":0,"status":"on_time","passenger_load":98.0,"priority_score":92.0,"current_block_id":None},
            {"train_number":"22932","train_name":"Ahmedabad Surat Intercity","train_type":"passenger","origin":"Ahmedabad","destination":"Surat","scheduled_departure":now+timedelta(hours=1,minutes=30),"scheduled_arrival":now+timedelta(hours=4),"delay_minutes":0,"status":"on_time","passenger_load":76.0,"priority_score":48.0,"current_block_id":2},
        ]
        for t in train_data:
            db.add(Train(**t))
        db.commit()

        alert_data = [
            {"title":"Track Maintenance - Shimla","description":"Block HP-01 (Shimla) at 68% track health. Maintenance window recommended within 24 hours.","severity":"medium","alert_type":"maintenance","block_id":5,"train_id":None},
            {"title":"Train Delay - Surat to Delhi","description":"Firozpur Janta Express (19023) running 40 min late. AI suggests priority clearance at Surat block.","severity":"high","alert_type":"delay","block_id":4,"train_id":3},
            {"title":"Delay Detected - Gujarat Express","description":"Gujarat Express (12901) running 25 min late departing Ahmedabad.","severity":"medium","alert_type":"delay","block_id":1,"train_id":1},
            {"title":"Kalka Shimla Express Delay","description":"Train 14311 running 15 min behind schedule near Shimla hill section.","severity":"low","alert_type":"delay","block_id":5,"train_id":4},
        ]
        for a in alert_data:
            db.add(Alert(**a))
        db.commit()
        print("Database seeded with 5-city data!")
    except Exception as e:
        print(f"Seed error: {e}"); db.rollback()
    finally:
        db.close()
