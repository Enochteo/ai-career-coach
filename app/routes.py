from flask import request, redirect, url_for, Blueprint, render_template
from .models import Goal
from .models import db
from openai import OpenAI
import os


main = Blueprint("main", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@main.route("/")
def home():
    return "<h1>Welcome to my app</h1>"

@main.route("/goals", methods=["GET", "POST"])
def goals_page():
    if request.method == "POST":
        goal_text = request.form.get("goal")
        if goal_text:
            new_goal = Goal(text=goal_text)
            db.session.add(new_goal)
            db.session.commit()
        return redirect(url_for("main.goals_page"))
    
    all_goals = Goal.query.all()
    return render_template("goal_tracking.html", goals=all_goals)

@main.route("/goals/delete/<int:goal_id>", methods=["POST"])
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for("main.goals_page"))

@main.route("/skills", methods=["GET", "POST"])
def skills_page():
    result = None
    if request.method == "POST":
        user_skills = request.form.get("skills")
        desired_job = request.form.get("job")

        prompt = f""" 
        The user has these skills: {user_skills}
        They want to become a {desired_job}.
        1. List the missing skills they need to develop.
        2. Suggest top learning resources (courses, books, or tutorials) to close those gaps.
        Format as:
        Missing Skills:
        - skill 1
        - skill 2

        Resources:
        - resource 1
        - resource 2
        """

        response = client.chat.completions.create(
            model="gpt-4", 
            messages=[{"role":"user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        split_response = content.split("Resources:")
        result = {
            "gaps": split_response[0].replace("Missing Skills:", "").strip(),
            "resources": split_response[1].strip() if len(split_response) > 1 else "None found"
        }
    return render_template("skill_gap.html", result=result)