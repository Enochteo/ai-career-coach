from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    
class SkillReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_type = db.Column(db.String(20))
    job_title = db.Column(db.String(100))
    skills_input =  db.Column(db.Text)
    missing_skills =  db.Column(db.Text)
    resources = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


