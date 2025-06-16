from flask import current_app, request, redirect, url_for, Blueprint, render_template
from .models import db, Goal, SkillReport
from openai import OpenAI
import os
import pdfplumber
from werkzeug.utils import secure_filename


main = Blueprint("main", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@main.route("/")
def home():
    return render_template("home.html")

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
        report = SkillReport(
            input_type="manual",
            job_title=desired_job,
            skills_input=user_skills,
            missing_skills=result["gaps"],
            resources=result["resources"]
        )
        db.session.add(report)
        db.session.commit()
    return render_template("skill_gap.html", result=result)

@main.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    result = None
    if request.method == "POST":
        file = request.files.get("resume")
        desired_job = request.form.get("job")

        if file and file.filename.endswith("pdf"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            with pdfplumber.open(filepath) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

            prompt = f"""Here is the user's resume:
            ---
            {text}
            ---

            The user wants to become a {desired_job}.
            1. What are their missing skills?
            2. Suggest 3–5 top resources to fill those gaps.
            Format your answer as:

            Missing Skills:
            - ...
            - ...

            Resources:
            - ...
            """
            response = client.chat.completions.create(
                model = "gpt-4",
                messages = [{"role": "user", "content": prompt}],
                max_tokens = 700,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            split_response = content.split("Resources:")
            result = {
                "gaps":split_response[0].replace("Missing Skills:", "").strip(),
                "resources": split_response[1].strip() if len(split_response) > 1 else "None found"            }
        report = SkillReport(
                input_type="resume",
                job_title=desired_job,
                skills_input=text,
                missing_skills=result["gaps"],
                resources=result["resources"]
            )
        db.session.add(report)
        db.session.commit()
    return render_template("upload_resume.html", result=result)

@main.route("/reports")
def view_reports():
    reports = SkillReport.query.order_by(SkillReport.timestamp.desc()).all()
    return render_template("view_reports.html", reports=reports)

@main.route("/career", methods=["GET", "POST"])
def career_recommendation():
    result = None
    if request.method == "POST":
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        level = request.form.get("level")

        prompt = f"""A user with the following background is seeking career guidance:
        - Skills: {skills}
        - Interests: {interests}
        - Professional Level: {level}

        Please suggest 3 tailored career paths. For each one, include:
        1. Job title and brief explanation.
        2. Key skills required.
        3. One actionable next step.

        Format the response clearly under separate headings."""
        response = client.chat.completions.create(
            model="gpt-4",
            messages = [{"role":"user", "content": prompt}],
            temperature = 0.7,
            max_tokens = 700
        )
        result = response.choice[0].message.content.strip()
    return render_template("career_recommendation.html", result=result)