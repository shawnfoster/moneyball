import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# LOAD PROFILE
with open("profile.json") as f:
    profile = json.load(f)

skills = [s.lower() for s in profile["skills"]]
tools = [t.lower() for t in profile["tools"]]
roles = [r.lower() for r in profile["target_roles"]]

def fetch_jobs(query="customer success", location="remote"):
    return [
        {
            "title": "Customer Success Manager",
            "company": "Test SaaS Co",
            "description": "SQL Tableau ARR churn customer success"
        },
        {
            "title": "BI Analyst",
            "company": "DataCorp",
            "description": "Python SQL dashboards Power BI analytics"
        }
    ]

def score_job(job):
    text = (job["title"] + " " + job["description"]).lower()
    title_text = job["title"].lower()
    desc_text = job["description"].lower()

    # Higher-value business signals
    high_value_terms = {
        "arr": 1.5,
        "nrr": 1.5,
        "csat": 1.4,
        "nps": 1.4,
        "churn reduction": 1.8,
        "customer retention": 1.8,
        "expansion revenue": 1.7,
        "revenue operations": 1.6,
        "customer lifecycle management": 1.7,
        "onboarding strategy": 1.4,
        "data storytelling": 1.3,
        "stakeholder communication": 1.2,
        "process optimization": 1.2,
        "saas metrics": 1.5
    }

    # Standard skill scoring
    skill_score = 0.0
    matched_skills = []
    for skill in skills:
        if skill in text:
            weight = high_value_terms.get(skill, 1.0)
            skill_score += weight
            matched_skills.append(skill)

    # Tool scoring stays lighter than business skill scoring
    tool_score = 0.0
    matched_tools = []
    for tool in tools:
        if tool in text:
            tool_score += 1.0
            matched_tools.append(tool)

    # Role/title alignment gets stronger weight in the actual title
    role_score = 0.0
    matched_roles = []
    for role in roles:
        if role in title_text:
            role_score += 2.0
            matched_roles.append(role)
        elif role in desc_text:
            role_score += 1.0
            matched_roles.append(role)

    # Penalty for weak/generic support-style roles
    negative_signals = [
        "call center",
        "customer support representative",
        "sales associate",
        "retail associate",
        "cashier",
        "help desk"
    ]

    penalty = 0.0
    matched_negative = []
    for signal in negative_signals:
        if signal in text:
            penalty += 1.5
            matched_negative.append(signal)

    total_score = (
        (skill_score * 0.5) +
        (tool_score * 0.2) +
        (role_score * 0.3) -
        penalty
    )

    return {
        "total_score": round(total_score, 2),
        "skill_score": round(skill_score, 2),
        "tool_score": round(tool_score, 2),
        "role_score": round(role_score, 2),
        "penalty": round(penalty, 2),
        "matched_skills": matched_skills,
        "matched_tools": matched_tools,
        "matched_roles": matched_roles,
        "matched_negative": matched_negative
    }

def run_moneyball():
    print("\n⚾ Running Moneyball...\n")

    jobs = fetch_jobs()
    print(f"Jobs found: {len(jobs)}")

    # ✅ Safety check (prevents ALL crashes)
    if not jobs:
        print("❌ No jobs found — scraper failed or blocked.")
        return

    scored_jobs = []

    for job in jobs:
        result = score_job(job)
        job["score"] = result["total_score"]
        job["skill_score"] = result["skill_score"]
        job["tool_score"] = result["tool_score"]
        job["role_score"] = result["role_score"]
        job["penalty"] = result["penalty"]
        job["matched_skills"] = ", ".join(result["matched_skills"])
        job["matched_tools"] = ", ".join(result["matched_tools"])
        job["matched_roles"] = ", ".join(result["matched_roles"])
        job["matched_negative"] = ", ".join(result["matched_negative"])
        scored_jobs.append(job)

    # ✅ Create DataFrame safely
    df = pd.DataFrame(scored_jobs)

    # ✅ Double safety check
    if df.empty or "score" not in df.columns:
        print("❌ No scores calculated.")
        return

    df = df.sort_values(by="score", ascending=False)

    top_jobs = df.head(20)

    print("\n🔥 TOP MONEYBALL TARGETS:\n")

    for _, row in top_jobs.iterrows():
        print(f"{row['score']:.2f} | {row['title']} @ {row['company']}")
        print(f"→ {row['description'][:120]}...")
        print(f"   skills: {row['skill_score']:.2f} | tools: {row['tool_score']:.2f} | roles: {row['role_score']:.2f} | penalty: {row['penalty']:.2f}")

    if row["matched_skills"]:
        print(f"   matched skills: {row['matched_skills']}")
    if row["matched_tools"]:
        print(f"   matched tools: {row['matched_tools']}")
    if row["matched_roles"]:
        print(f"   matched roles: {row['matched_roles']}")
    if row["matched_negative"]:
        print(f"   negative signals: {row['matched_negative']}")

    print()

if __name__ == "__main__":
    run_moneyball()
