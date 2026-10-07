"""CloudScout Flask application entry point."""

import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request


app = Flask(__name__)
load_dotenv()

SERPAPI_URL = "https://serpapi.com/search.json"

# Each key is the name shown to the user. The patterns underneath it capture
# common aliases in job descriptions and form input.  This is intentionally a
# transparent catalog: a skill is reported only when one of these rules finds
# it in a description returned for the current search.
SKILL_PATTERNS = {
    # Programming
    "Python": (r"\bpython\b",),
    "Java": (r"\bjava\b",),
    "C": (r"(?<![A-Za-z0-9+#])c(?![A-Za-z0-9+#])",),
    "C++": (r"\bc\s*\+\+(?!\w)", r"\bcpp\b"),
    "JavaScript": (r"\bjavascript\b", r"\bjs\b"),
    "TypeScript": (r"\btypescript\b", r"\bts\b"),
    # Web
    "HTML": (r"\bhtml(?:5)?\b",),
    "CSS": (r"\bcss(?:3)?\b",),
    "React": (r"\breact(?:\.js)?\b",),
    "Node.js": (r"\bnode(?:\.js|js)?\b",),
    "REST API": (r"\brest(?:ful)?\s+apis?\b", r"\brestful\b"),
    # Data
    "SQL": (r"\bsql\b", r"\bmysql\b", r"\bpostgres(?:ql)?\b"),
    "Excel": (r"\b(?:microsoft )?excel\b", r"\bms excel\b"),
    "Power BI": (r"\bpower\s*bi\b",),
    "Tableau": (r"\btableau\b",),
    "Pandas": (r"\bpandas\b",),
    # Cloud
    "AWS": (r"\baws\b", r"\bamazon web services\b"),
    "Azure": (r"\bazure\b",),
    "Google Cloud": (r"\bgcp\b", r"\bgoogle cloud(?: platform)?\b"),
    "Docker": (r"\bdocker(?:\s+containers?)?\b",),
    "Kubernetes": (r"\bkubernetes\b", r"\bk8s\b"),
    "Terraform": (r"\bterraform\b",),
    # DevOps
    "CI/CD": (r"\bci\s*/\s*cd\b", r"\bcontinuous integration\b", r"\bcontinuous delivery\b", r"\bcontinuous deployment\b"),
    "Jenkins": (r"\bjenkins\b",),
    "GitHub Actions": (r"\bgithub actions\b",),
    "Ansible": (r"\bansible\b",),
    "Linux": (r"\blinux\b",),
    "Bash": (r"\bbash\b", r"\bshell scripting\b"),
    # Security
    "IAM": (r"\biam\b", r"\bidentity and access management\b"),
    "Cloud Security": (r"\bcloud security\b",),
    "Cybersecurity": (r"\bcyber\s*security\b", r"\bcybersecurity\b",),
    "SIEM": (r"\bsiem\b", r"\bsecurity information and event management\b"),
    # General
    "Git": (r"\bgit\b",),
    "GitHub": (r"\bgithub\b",),
    "Networking": (r"\bnetworking\b", r"\bnetwork\s+engineering\b"),
    "Monitoring": (r"\bmonitoring\b",),
}


def extract_skills(text):
    """Return canonical skill names found in a description or form input."""
    text = text or ""
    return {
        skill
        for skill, patterns in SKILL_PATTERNS.items()
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    }


def build_skill_analysis(jobs, current_skills):
    """Count employer demand and compare it with the user's listed skills."""
    total_jobs = len(jobs)
    skill_counts = {skill: 0 for skill in SKILL_PATTERNS}

    for job in jobs:
        # A set ensures a skill is counted at most once for each job.
        for skill in extract_skills(job.get("description")):
            skill_counts[skill] += 1

    top_skills = [
        {
            "name": skill,
            "count": count,
            "percentage": round((count / total_jobs) * 100) if total_jobs else 0,
        }
        for skill, count in skill_counts.items()
        if count
    ]
    top_skills.sort(key=lambda item: (-item["count"], item["name"]))

    user_skill_set = extract_skills(current_skills)
    detected_skill_set = {skill["name"] for skill in top_skills}
    # Keep every displayed insight tied to the live descriptions for this
    # search, including the user's matched skills.
    owned_skills = [
        {"name": skill}
        for skill in sorted(user_skill_set & detected_skill_set)
    ]
    gaps = [skill for skill in top_skills if skill["name"] not in user_skill_set]

    for skill in gaps:
        if skill["percentage"] >= 60:
            skill["demand_level"] = "High demand"
        elif skill["percentage"] >= 30:
            skill["demand_level"] = "Medium demand"
        else:
            skill["demand_level"] = "Lower demand"

    demand_order = {"High demand": 0, "Medium demand": 1, "Lower demand": 2}
    learning_order = sorted(
        gaps,
        key=lambda item: (demand_order[item["demand_level"]], -item["count"], item["name"]),
    )[:10]

    return {
        "top_skills": top_skills,
        "owned_skills": owned_skills,
        "gaps": gaps,
        "learning_order": learning_order,
    }


def build_job_fit(jobs, analysis, experience_level):
    """Build a transparent profile summary from the current job descriptions."""
    frequent_skills = [
        skill for skill in analysis["top_skills"] if skill["percentage"] >= 30
    ]
    owned_names = {skill["name"] for skill in analysis["owned_skills"]}

    prior_experience_pattern = re.compile(
        r"\b(?:\d+\s*(?:-|–|to)\s*\d+\+?\s*(?:years?|yrs?)|"
        r"\d+\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience|"
        r"minimum of \d+\s+(?:years?|yrs?)|prior experience)\b",
        re.IGNORECASE,
    )
    entry_level_pattern = re.compile(
        r"\b(?:entry[- ]level|freshers?|new grad(?:uate)?|recent grad(?:uate)?|"
        r"graduate trainee|0\s*(?:-|–|to)\s*2\s+(?:years?|yrs?))\b",
        re.IGNORECASE,
    )
    descriptions = [job.get("description") or "" for job in jobs]
    prior_experience_count = sum(
        bool(prior_experience_pattern.search(description))
        for description in descriptions
    )
    entry_level_count = sum(
        bool(entry_level_pattern.search(description))
        for description in descriptions
    )
    majority = (len(jobs) + 1) // 2
    if prior_experience_count >= majority:
        experience_signal = "Many analyzed jobs mention prior experience."
    elif entry_level_count >= majority:
        experience_signal = (
            "Most analyzed jobs mention entry-level or fresher-friendly language."
        )
    else:
        experience_signal = "Experience requirements vary across the current results."

    return {
        "experience_level": experience_level,
        "analyzed_jobs": len(jobs),
        "strong_matches": [
            skill for skill in frequent_skills if skill["name"] in owned_names
        ],
        "skill_gaps": [
            skill for skill in frequent_skills if skill["name"] not in owned_names
        ],
        "experience_signal": experience_signal,
    }


def search_jobs(role, location):
    """Request jobs for the submitted role from SerpApi."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return [], "The SerpApi key is missing. Add SERPAPI_KEY to your local .env file."

    try:
        response = requests.get(
            SERPAPI_URL,
            params={
                "engine": "google_jobs",
                "q": role,
                "location": location,
                "api_key": api_key,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        # Log only the exception class. Request URLs can include the API key.
        app.logger.warning("SerpApi request failed: %s", type(exc).__name__)
        return [], "CloudScout could not reach SerpApi. Please try again shortly."
    except ValueError as exc:
        app.logger.warning("SerpApi returned invalid JSON: %s", type(exc).__name__)
        return [], "SerpApi returned an unexpected response. Please try again."

    if data.get("error"):
        return [], "SerpApi could not complete the search. Check your API key and try again."

    jobs = []
    for job in data.get("jobs_results", []):
        # Google Jobs can provide a share link or an application link, depending
        # on the job source. Use whichever is available.
        apply_options = job.get("apply_options", [])
        application_link = apply_options[0].get("link") if apply_options else None
        jobs.append(
            {
                "title": job.get("title", "Untitled role"),
                "company": job.get("company_name", "Company not listed"),
                "location": job.get("location", "Location not listed"),
                "description": job.get("description"),
                "link": job.get("share_link") or application_link,
            }
        )

    return jobs, None


@app.route("/", methods=["GET", "POST"])
def index():
    """Show the job-search form and any matching jobs."""
    jobs = []
    error = None
    searched = False
    form_data = {
        "role": "",
        "location": "",
        "skills": "",
        "experience_level": "Student",
        "experience_details": "",
    }
    analysis = None
    job_fit = None

    if request.method == "POST":
        searched = True
        form_data = {
            "role": request.form.get("role", "").strip(),
            "location": request.form.get("location", "").strip(),
            "skills": request.form.get("skills", "").strip(),
            "experience_level": request.form.get("experience_level", "Student"),
            "experience_details": request.form.get("experience_details", "").strip(),
        }
        if not form_data["role"] or not form_data["location"]:
            error = "Please enter both a job role and a location."
        else:
            jobs, error = search_jobs(form_data["role"], form_data["location"])
            if not error and jobs:
                # Project text contributes only skills recognized by the same
                # transparent catalog used for the current-skills field.
                profile_text = "\n".join(
                    (form_data["skills"], form_data["experience_details"])
                )
                analysis = build_skill_analysis(jobs, profile_text)
                job_fit = build_job_fit(
                    jobs, analysis, form_data["experience_level"]
                )

    return render_template(
        "index.html",
        jobs=jobs,
        error=error,
        searched=searched,
        form_data=form_data,
        analysis=analysis,
        job_fit=job_fit,
    )


if __name__ == "__main__":
    # Keep one predictable local server process for the browser preview.
    app.run(debug=True, use_reloader=False)
