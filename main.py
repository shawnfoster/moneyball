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
# ALIASES
# =========================
ROLE_ALIASES = {
    "customer success manager": [
        "customer success manager",
        "csm",
        "customer success"
    ],
    "customer success analyst": [
        "customer success analyst",
        "cs analyst"
    ],
    "business intelligence analyst": [
        "business intelligence analyst",
        "bi analyst",
        "data analyst"
    ],
    "revenue operations analyst": [
        "revenue operations analyst",
        "revops analyst",
        "revenue ops analyst",
        "rev ops",
        "revenue operations"
    ],
    "customer experience manager": [
        "customer experience manager",
        "cx manager"
    ],
    "strategy analyst": [
        "strategy analyst",
        "strategic analyst",
        "strategy & operations",
        "strategy and operations",
        "operations analyst"
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
    "customer success manager": 1.10,
    "customer success analyst": 1.00,
    "business intelligence analyst": 1.10,
    "revenue operations analyst": 1.35,
    "customer experience manager": 1.00,
    "strategy analyst": 1.15
}


# =========================
# LOCATION SCORING
# =========================
PREFERRED_LOCATION_SIGNALS = {
    "remote": 0.75,
    "us-remote": 0.75,
    "us - remote": 0.75,
    "united states": 0.35,
    "u.s.": 0.35,
    "illinois": 0.75,
    "chicago": 1.00,
    "hybrid": 0.20
}

LOCATION_PENALTY_SIGNALS = {
    "mexico city": 1.50,
    "mexico": 1.25,
    "tokyo": 2.00,
    "japan": 2.00,
    "bangalore": 2.00,
    "bengaluru": 2.00,
    "india": 2.00,
    "vancouver": 1.50,
    "bc": 1.25,
    "dublin": 1.50,
    "ireland": 1.50,
    "sydney": 1.75,
    "australia": 1.75,
    "seoul": 1.75,
    "south korea": 1.75,
    "singapore": 1.75,
    "jakarta": 1.75,
    "indonesia": 1.75,
    "sao paulo": 1.75,
    "brazil": 1.75,
    "toronto": 1.25,
    "canada": 1.25,
    "luxembourg": 1.75,
    "germany": 1.50,
    "san francisco": 0.60,
    "new york city": 0.60,
    "new york": 0.50,
    "seattle": 0.50,
    "boston": 0.35,
    "denver": 0.25
}


# =========================
# DOMAIN MISMATCH PENALTIES
# =========================
DOMAIN_MISMATCH_SIGNALS = {
    "credit risk": 1.75,
    "underwriting": 1.75,
    "internal audit": 2.25,
    "sox": 2.00,
    "security engineer": 1.75,
    "attorney": 2.25,
    "account executive": 1.75,
    "sales engineering": 1.75,
    "field enablement": 1.50,
    "risk strategy": 1.50,
    "financial crimes": 1.75,
    "compliance analyst": 1.50,
    "people operations": 1.75,
    "human resources": 2.00,
    "hr ": 1.50,
    "fp&a": 1.25,
    "finance partner": 1.25
}


# =========================
# TITLE / PRACTICAL FILTERS
# =========================
HARD_BLOCK_TITLE_TERMS = [
    "senior ",
    "principal",
    "director",
    "head of",
    "vice president",
    "vp ",
    "staff ",
    "engineering",
    "engineer",
    "account executive",
    "attorney",
    "legal",
    "compliance",
    "risk",
    "fp&a",
    "people operations",
    "human resources"
]

SOFT_BLOCK_TITLE_TERMS = [
    "manager,",
    "manager -",
    "manager –",
    "manager:"
]

PREFERRED_TITLE_TERMS = [
    "strategy",
    "operations",
    "analyst",
    "revenue operations",
    "rev ops",
    "customer success",
    "sales systems",
    "gtm planning",
    "program manager"
]


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

    if row["entry_bonus"] > 0:
        notes.append("Posting includes entry-friendly signals.")

    if row["location_score"] > 0.5:
        notes.append("Location fit improves practicality.")
    elif row["location_score"] < 0:
        notes.append("Location reduces practical fit.")

    if row["domain_penalty"] > 0:
        notes.append("Domain mismatch lowers real relevance.")

    if row["difficulty_penalty"] >= 1.5:
        notes.append("Difficulty signals suggest lower practical ROI.")
    elif row["difficulty_penalty"] > 0:
        notes.append("Some experience or seniority drag is present.")

    if row["penalty"] > 0:
        notes.append("Negative signals reduce attractiveness.")

    return " ".join(notes)


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
    location_text = job.get("location", "").lower()
    text = (job["title"] + " " + job["description"] + " " + location_text).lower()
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
        "15+ years": 2.5,
        "10+ years": 2.0,
        "8+ years": 1.75,
        "7+ years": 1.5,
        "5+ years": 1.1,
        "4-6 years": 0.60,
        "phd": 2.0,
        "doctorate": 2.0,
        "director": 1.75,
        "senior director": 2.25,
        "vice president": 2.5,
        "executive": 2.5,
        "manager of managers": 1.75,
        "senior ": 0.9,
        "lead ": 0.8,
        "principal": 1.2,
        "people leadership": 1.0
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
        "1+ years",
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

    domain_penalty = 0.0
    matched_domain_mismatch: list[str] = []
    for signal, weight in DOMAIN_MISMATCH_SIGNALS.items():
        if signal in text:
            domain_penalty += weight
            matched_domain_mismatch.append(signal)

    location_score = 0.0
    matched_location_positive: list[str] = []
    matched_location_negative: list[str] = []

    for signal, weight in PREFERRED_LOCATION_SIGNALS.items():
        if signal in text:
            location_score += weight
            matched_location_positive.append(signal)

    for signal, weight in LOCATION_PENALTY_SIGNALS.items():
        if signal in text:
            location_score -= weight
            matched_location_negative.append(signal)

    total_score = (
        (skill_score * 0.5) +
        (tool_score * 0.2) +
        (role_score * 0.3) +
        (industry_score * 0.1) +
        entry_bonus +
        location_score -
        penalty -
        difficulty_penalty -
        domain_penalty
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
        "location_score": round(location_score, 2),
        "domain_penalty": round(domain_penalty, 2),
        "matched_skills": matched_skills,
        "matched_tools": matched_tools,
        "matched_roles": matched_roles,
        "matched_industries": matched_industries,
        "matched_negative": matched_negative,
        "matched_difficulty": matched_difficulty,
        "matched_entry": matched_entry,
        "matched_location_positive": matched_location_positive,
        "matched_location_negative": matched_location_negative,
        "matched_domain_mismatch": matched_domain_mismatch
    }


# =========================
# PRACTICAL FILTER
# =========================
def is_practical_row(row) -> bool:
    title = str(row["title"]).lower()
    location = str(row["location"]).lower()

    if row["fit_tier"] == "LOW":
        return False
    if row["location_score"] < 0.25:
        return False
    if row["difficulty_penalty"] > 1.25:
        return False
    if row["domain_penalty"] > 0.50:
        return False

    if any(term in title for term in HARD_BLOCK_TITLE_TERMS):
        return False
    if any(term in title for term in SOFT_BLOCK_TITLE_TERMS):
        return False

    if any(term in location for term in [
        "vancouver", "bc", "canada", "jakarta", "indonesia", "bengaluru", "bangalore",
        "india", "germany", "dublin", "ireland", "sydney", "australia", "seoul",
        "korea", "singapore", "brazil", "mexico", "toronto", "luxembourg"
    ]):
        return False

    if not any(term in title for term in PREFERRED_TITLE_TERMS):
        return False

    return True


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
        job["location_score"] = result["location_score"]
        job["domain_penalty"] = result["domain_penalty"]
        job["matched_skills"] = ", ".join(result["matched_skills"])
        job["matched_tools"] = ", ".join(result["matched_tools"])
        job["matched_roles"] = ", ".join(result["matched_roles"])
        job["matched_industries"] = ", ".join(result["matched_industries"])
        job["matched_negative"] = ", ".join(result["matched_negative"])
        job["matched_difficulty"] = ", ".join(result["matched_difficulty"])
        job["matched_entry"] = ", ".join(result["matched_entry"])
        job["matched_location_positive"] = ", ".join(result["matched_location_positive"])
        job["matched_location_negative"] = ", ".join(result["matched_location_negative"])
        job["matched_domain_mismatch"] = ", ".join(result["matched_domain_mismatch"])
        job["fit_tier"] = get_fit_tier(result["total_score"])
        scored_jobs.append(job)

    df = pd.DataFrame(scored_jobs)

    if df.empty or "score" not in df.columns:
        print("❌ No scores calculated.")
        return

    df = df.sort_values(by="score", ascending=False)
    practical_jobs = df[df.apply(is_practical_row, axis=1)].copy()

    if practical_jobs.empty:
        print("❌ No practical jobs passed the current filter.")
        return

    practical_jobs = practical_jobs.sort_values(by="score", ascending=False).head(10)

    print("\n🎯 TOP PRACTICAL MONEYBALL TARGETS:\n")

    for _, row in practical_jobs.iterrows():
        print(f"{row['score']:.2f} [{row['fit_tier']}] | {row['title']} @ {row['company']}")
        if row.get("location"):
            print(f"   location: {row['location']}")
        if row.get("source"):
            print(f"   source: {row['source']}")
        if row.get("url"):
            print(f"   url: {row['url']}")

        print(f"→ {row['description'][:1200]}...")
        print(
            f"   skills: {row['skill_score']:.2f} | "
            f"tools: {row['tool_score']:.2f} | "
            f"roles: {row['role_score']:.2f} | "
            f"industry: {row['industry_score']:.2f} | "
            f"penalty: {row['penalty']:.2f} | "
            f"difficulty: {row['difficulty_penalty']:.2f} | "
            f"entry: {row['entry_bonus']:.2f} | "
            f"location: {row['location_score']:.2f} | "
            f"domain: {row['domain_penalty']:.2f}"
        )

        if row["matched_entry"]:
            print(f"   entry signals: {row['matched_entry']}")
        if row["matched_difficulty"]:
            print(f"   difficulty signals: {row['matched_difficulty']}")
        if row["matched_location_positive"]:
            print(f"   location positives: {row['matched_location_positive']}")
        if row["matched_location_negative"]:
            print(f"   location negatives: {row['matched_location_negative']}")
        if row["matched_domain_mismatch"]:
            print(f"   domain mismatch signals: {row['matched_domain_mismatch']}")
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