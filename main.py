import json
from pathlib import Path

import pandas as pd


# =========================
# FILE PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "profile.json"
JOBS_JSON_PATH = BASE_DIR / "jobs.json"


# =========================
# LOAD PROFILE
# =========================
with open(PROFILE_PATH, encoding="utf-8") as f:
    profile = json.load(f)

skills = [s.lower() for s in profile["skills"]]
tools = [t.lower() for t in profile["tools"]]
roles = [r.lower() for r in profile["target_roles"]]
industries = [i.lower() for i in profile.get("industries", [])]


# =========================
# ALIAS MAPS
# =========================
ROLE_ALIASES = {
    "customer success manager": [
        "customer success manager",
        "csm"
    ],
    "customer success analyst": [
        "customer success analyst",
        "cs analyst"
    ],
    "business intelligence analyst": [
        "business intelligence analyst",
        "bi analyst"
    ],
    "revenue operations analyst": [
        "revenue operations analyst",
        "revops analyst",
        "revenue ops analyst"
    ],
    "customer experience manager": [
        "customer experience manager",
        "cx manager"
    ],
    "strategy analyst": [
        "strategy analyst",
        "strategic analyst"
    ]
}

TOOL_ALIASES = {
    "power bi": ["power bi", "pbi"],
    "google sheets": ["google sheets", "gsheets"],
    "salesforce": ["salesforce", "sfdc"],
    "hubspot": ["hubspot", "hub spot"],
    "crm systems": ["crm", "crm systems", "customer relationship management"]
}

INDUSTRY_ALIASES = {
    "saas": ["saas", "software as a service"],
    "tech": ["tech", "technology", "software"],
    "cannabis": ["cannabis", "dispensary", "marijuana"]
}


# =========================
# ROLE PRIORITY WEIGHTS
# =========================
ROLE_WEIGHTS = {
    "customer success manager": 1.15,
    "customer success analyst": 1.00,
    "business intelligence analyst": 1.10,
    "revenue operations analyst": 1.25,
    "customer experience manager": 1.00,
    "strategy analyst": 1.05
}


# =========================
# HELPERS
# =========================
def text_contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def get_fit_tier(score: float) -> str:
    if score >= 1.75:
        return "HIGH"
    elif score >= 1.0:
        return "MEDIUM"
    return "LOW"


def generate_synopsis(row) -> str:
    notes = []

    if row["fit_tier"] == "HIGH":
        notes.append("Clean target with strong overall alignment.")
    elif row["fit_tier"] == "MEDIUM":
        notes.append("Viable target, but not top-tier.")
    else:
        notes.append("Low-priority target unless there is a special reason to pursue it.")

    if row["skill_score"] >= 1.0:
        notes.append("Strong skill alignment.")
    elif row["skill_score"] == 0:
        notes.append("Limited direct business-skill match.")

    if row["tool_score"] >= 2.0:
        notes.append("Strong tools match.")
    elif row["tool_score"] > 0:
        notes.append("Some relevant tool overlap is present.")

    if row["role_score"] >= 2.3:
        notes.append("Role alignment is especially strong.")
    elif row["role_score"] >= 2.0:
        notes.append("Role match is solid.")
    elif row["role_score"] > 0:
        notes.append("Some role alignment is present.")

    if row["industry_score"] > 0:
        notes.append("Industry fit adds confidence.")

    if row["difficulty_penalty"] >= 1.5:
        notes.append("Difficulty signals suggest lower practical ROI.")
    elif row["difficulty_penalty"] > 0:
        notes.append("Some experience or seniority drag is present.")

    if row["entry_bonus"] > 0:
        notes.append("Posting includes entry-friendly signals.")

    if row["penalty"] > 0:
        notes.append("Negative signals reduce attractiveness.")

    return " ".join(notes)


# =========================
# LOAD JOBS FROM JSON
# =========================
def fetch_jobs_from_json(path: Path) -> list[dict]:
    if not path.exists():
        print(f"❌ jobs.json not found at: {path}")
        return []

    try:
        with open(path, encoding="utf-8") as f:
            jobs = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in jobs.json: {e}")
        return []

    if not isinstance(jobs, list):
        print("❌ jobs.json must contain a list of job objects.")
        return []

    cleaned_jobs = []
    for job in jobs:
        if not isinstance(job, dict):
            continue

        title = str(job.get("title", "")).strip()
        company = str(job.get("company", "")).strip()
        description = str(job.get("description", "")).strip()

        if not title or not company or not description:
            continue

        cleaned_jobs.append({
            "title": title,
            "company": company,
            "description": description,
            "url": str(job.get("url", "")).strip(),
            "location": str(job.get("location", "")).strip(),
            "source": str(job.get("source", "")).strip()
        })

    return cleaned_jobs


# =========================
# SCORING FUNCTION
# =========================
def score_job(job: dict) -> dict:
    text = (job["title"] + " " + job["description"]).lower()
    title_text = job["title"].lower()
    desc_text = job["description"].lower()

    high_value_terms = {
        "arr": 1.5,
        "nrr": 1.5,
        "csat": 1.4,
        "nps": 1.4,
        "churn reduction": 1.8,
        "customer retention": 1.8,
        "retention strategy": 1.7,
        "expansion revenue": 1.7,
        "revenue operations": 1.8,
        "customer lifecycle management": 1.7,
        "customer lifecycle": 1.5,
        "onboarding strategy": 1.4,
        "data storytelling": 1.3,
        "stakeholder communication": 1.2,
        "process optimization": 1.2,
        "saas metrics": 1.5,
        "pipeline management": 1.7,
        "forecasting": 1.6,
        "crm optimization": 1.6,
        "data-driven decision making": 1.5
    }

    skill_score = 0.0
    matched_skills: list[str] = []
    for skill in skills:
        if skill in text:
            weight = high_value_terms.get(skill, 1.0)
            skill_score += weight
            matched_skills.append(skill)

    tool_score = 0.0
    matched_tools: list[str] = []
    for tool in tools:
        aliases = TOOL_ALIASES.get(tool, [tool])
        if text_contains_any(text, aliases):
            tool_score += 1.0
            matched_tools.append(tool)

    role_score = 0.0
    matched_roles: list[str] = []
    for role in roles:
        aliases = ROLE_ALIASES.get(role, [role])
        weight = ROLE_WEIGHTS.get(role, 1.0)

        if text_contains_any(title_text, aliases):
            role_score += 2.0 * weight
            matched_roles.append(role)
        elif text_contains_any(desc_text, aliases):
            role_score += 1.0 * weight
            matched_roles.append(role)

    industry_score = 0.0
    matched_industries: list[str] = []
    for industry in industries:
        aliases = INDUSTRY_ALIASES.get(industry, [industry])
        if text_contains_any(text, aliases):
            industry_score += 0.75
            matched_industries.append(industry)

    negative_signals = [
        "call center",
        "customer support representative",
        "sales associate",
        "retail associate",
        "cashier",
        "help desk"
    ]

    penalty = 0.0
    matched_negative: list[str] = []
    for signal in negative_signals:
        if signal in text:
            penalty += 1.5
            matched_negative.append(signal)

    difficulty_signals = {
        "10+ years": 2.0,
        "8+ years": 1.75,
        "7+ years": 1.5,
        "5+ years": 1.1,
        "phd": 2.0,
        "doctorate": 2.0,
        "director": 1.75,
        "senior director": 2.25,
        "vice president": 2.5,
        "executive": 2.5,
        "manager of managers": 1.75,
        "senior ": 0.9,
        "lead ": 0.8,
        "principal": 1.2
    }

    difficulty_penalty = 0.0
    matched_difficulty: list[str] = []
    for signal, weight in difficulty_signals.items():
        if signal in text:
            difficulty_penalty += weight
            matched_difficulty.append(signal)

    entry_friendly_signals = [
        "junior",
        "associate",
        "entry level",
        "early career",
        "1-3 years",
        "2+ years",
        "new grad",
        "mid-level"
    ]

    entry_bonus = 0.0
    matched_entry: list[str] = []
    for signal in entry_friendly_signals:
        if signal in text:
            entry_bonus += 0.35
            matched_entry.append(signal)

    total_score = (
        (skill_score * 0.5) +
        (tool_score * 0.2) +
        (role_score * 0.3) +
        (industry_score * 0.1) +
        entry_bonus -
        penalty -
        difficulty_penalty
    )

    return {
        "total_score": round(total_score, 2),
        "skill_score": round(skill_score, 2),
        "tool_score": round(tool_score, 2),
        "role_score": round(role_score, 2),
        "industry_score": round(industry_score, 2),
        "penalty": round(penalty, 2),
        "difficulty_penalty": round(difficulty_penalty, 2),
        "entry_bonus": round(entry_bonus, 2),
        "matched_skills": matched_skills,
        "matched_tools": matched_tools,
        "matched_roles": matched_roles,
        "matched_industries": matched_industries,
        "matched_negative": matched_negative,
        "matched_difficulty": matched_difficulty,
        "matched_entry": matched_entry
    }


# =========================
# MAIN ENGINE
# =========================
def run_moneyball() -> None:
    print("\n⚾ Running Moneyball...\n")

    jobs = fetch_jobs_from_json(JOBS_JSON_PATH)
    print(f"Jobs found: {len(jobs)}")

    if not jobs:
        print("❌ No valid jobs found in jobs.json")
        return

    scored_jobs: list[dict] = []

    for job in jobs:
        result = score_job(job)
        job["score"] = result["total_score"]
        job["skill_score"] = result["skill_score"]
        job["tool_score"] = result["tool_score"]
        job["role_score"] = result["role_score"]
        job["industry_score"] = result["industry_score"]
        job["penalty"] = result["penalty"]
        job["difficulty_penalty"] = result["difficulty_penalty"]
        job["entry_bonus"] = result["entry_bonus"]
        job["matched_skills"] = ", ".join(result["matched_skills"])
        job["matched_tools"] = ", ".join(result["matched_tools"])
        job["matched_roles"] = ", ".join(result["matched_roles"])
        job["matched_industries"] = ", ".join(result["matched_industries"])
        job["matched_negative"] = ", ".join(result["matched_negative"])
        job["matched_difficulty"] = ", ".join(result["matched_difficulty"])
        job["matched_entry"] = ", ".join(result["matched_entry"])
        job["fit_tier"] = get_fit_tier(result["total_score"])
        scored_jobs.append(job)

    df = pd.DataFrame(scored_jobs)

    if df.empty or "score" not in df.columns:
        print("❌ No scores calculated.")
        return

    df = df.sort_values(by="score", ascending=False)

    print("\n🔥 TOP MONEYBALL TARGETS:\n")

    for _, row in df.iterrows():
        print(f"{row['score']:.2f} [{row['fit_tier']}] | {row['title']} @ {row['company']}")
        if row.get("location"):
            print(f"   location: {row['location']}")
        if row.get("source"):
            print(f"   source: {row['source']}")
        if row.get("url"):
            print(f"   url: {row['url']}")

        print(f"→ {row['description']}")
        print(
            f"   skills: {row['skill_score']:.2f} | "
            f"tools: {row['tool_score']:.2f} | "
            f"roles: {row['role_score']:.2f} | "
            f"industry: {row['industry_score']:.2f} | "
            f"penalty: {row['penalty']:.2f} | "
            f"difficulty: {row['difficulty_penalty']:.2f} | "
            f"entry: {row['entry_bonus']:.2f}"
        )

        if row["matched_entry"]:
            print(f"   entry signals: {row['matched_entry']}")
        if row["matched_difficulty"]:
            print(f"   difficulty signals: {row['matched_difficulty']}")
        if row["matched_skills"]:
            print(f"   matched skills: {row['matched_skills']}")
        if row["matched_tools"]:
            print(f"   matched tools: {row['matched_tools']}")
        if row["matched_roles"]:
            print(f"   matched roles: {row['matched_roles']}")
        if row["matched_industries"]:
            print(f"   matched industries: {row['matched_industries']}")
        if row["matched_negative"]:
            print(f"   negative signals: {row['matched_negative']}")

        print(f"   synopsis: {generate_synopsis(row)}")
        print()


if __name__ == "__main__":
    run_moneyball()