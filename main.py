import json
import pandas as pd


# -------------------------
# LOAD PROFILE
# -------------------------
with open("profile.json") as f:
    profile = json.load(f)

skills = [s.lower() for s in profile["skills"]]
tools = [t.lower() for t in profile["tools"]]
roles = [r.lower() for r in profile["target_roles"]]
industries = [i.lower() for i in profile.get("industries", [])]


# -------------------------
# ALIAS MAPS
# -------------------------
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


# -------------------------
# TEST JOB DATA
# -------------------------
def fetch_jobs(query: str = "customer success", location: str = "remote") -> list[dict]:
    return [
        {
            "title": "Customer Success Manager",
            "company": "Test SaaS Co",
            "description": "SQL Tableau ARR churn customer success SaaS"
        },
        {
            "title": "BI Analyst",
            "company": "DataCorp",
            "description": "Python SQL dashboards Power BI analytics technology"
        },
        {
            "title": "RevOps Analyst",
            "company": "GrowthTech",
            "description": "SFDC CRM systems revenue ops pipeline reporting software"
        }
    ]


# -------------------------
# HELPERS
# -------------------------
def text_contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


# -------------------------
# SCORING FUNCTION
# -------------------------
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
        "expansion revenue": 1.7,
        "revenue operations": 1.6,
        "customer lifecycle management": 1.7,
        "onboarding strategy": 1.4,
        "data storytelling": 1.3,
        "stakeholder communication": 1.2,
        "process optimization": 1.2,
        "saas metrics": 1.5
    }

    # Skills
    skill_score = 0.0
    matched_skills: list[str] = []
    for skill in skills:
        if skill in text:
            weight = high_value_terms.get(skill, 1.0)
            skill_score += weight
            matched_skills.append(skill)

    # Tools with aliases
    tool_score = 0.0
    matched_tools: list[str] = []
    for tool in tools:
        aliases = TOOL_ALIASES.get(tool, [tool])
        if text_contains_any(text, aliases):
            tool_score += 1.0
            matched_tools.append(tool)

    # Roles with aliases
    role_score = 0.0
    matched_roles: list[str] = []
    for role in roles:
        aliases = ROLE_ALIASES.get(role, [role])

        if text_contains_any(title_text, aliases):
            role_score += 2.0
            matched_roles.append(role)
        elif text_contains_any(desc_text, aliases):
            role_score += 1.0
            matched_roles.append(role)

    # Industries with aliases
    industry_score = 0.0
    matched_industries: list[str] = []
    for industry in industries:
        aliases = INDUSTRY_ALIASES.get(industry, [industry])
        if text_contains_any(text, aliases):
            industry_score += 0.75
            matched_industries.append(industry)

    # Negative signals
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

    total_score = (
        (skill_score * 0.5) +
        (tool_score * 0.2) +
        (role_score * 0.3) +
        (industry_score * 0.1) -
        penalty
    )

    return {
        "total_score": round(total_score, 2),
        "skill_score": round(skill_score, 2),
        "tool_score": round(tool_score, 2),
        "role_score": round(role_score, 2),
        "industry_score": round(industry_score, 2),
        "penalty": round(penalty, 2),
        "matched_skills": matched_skills,
        "matched_tools": matched_tools,
        "matched_roles": matched_roles,
        "matched_industries": matched_industries,
        "matched_negative": matched_negative
    }


# -------------------------
# MAIN ENGINE
# -------------------------
def run_moneyball() -> None:
    print("\n⚾ Running Moneyball...\n")

    jobs = fetch_jobs()
    print(f"Jobs found: {len(jobs)}")

    if not jobs:
        print("❌ No jobs found — scraper failed or blocked.")
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
        job["matched_skills"] = ", ".join(result["matched_skills"])
        job["matched_tools"] = ", ".join(result["matched_tools"])
        job["matched_roles"] = ", ".join(result["matched_roles"])
        job["matched_industries"] = ", ".join(result["matched_industries"])
        job["matched_negative"] = ", ".join(result["matched_negative"])
        scored_jobs.append(job)

    df = pd.DataFrame(scored_jobs)

    if df.empty or "score" not in df.columns:
        print("❌ No scores calculated.")
        return

    df = df.sort_values(by="score", ascending=False)
    top_jobs = df.head(20)

    print("\n🔥 TOP MONEYBALL TARGETS:\n")

    for _, row in top_jobs.iterrows():
        print(f"{row['score']:.2f} | {row['title']} @ {row['company']}")
        print(f"→ {row['description'][:120]}...")
        print(
            f"   skills: {row['skill_score']:.2f} | "
            f"tools: {row['tool_score']:.2f} | "
            f"roles: {row['role_score']:.2f} | "
            f"industry: {row['industry_score']:.2f} | "
            f"penalty: {row['penalty']:.2f}"
        )

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

        print()


if __name__ == "__main__":
    run_moneyball()