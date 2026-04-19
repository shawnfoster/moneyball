import pandas as pd
import streamlit as st

from main import (
    JOBS_JSON_PATH,
    fetch_jobs_from_json,
    score_job,
    is_practical_row,
    generate_synopsis,
)

st.set_page_config(page_title="Moneyball Dashboard", layout="wide")

st.title("⚾ Moneyball Dashboard")
st.caption("Top practical job targets ranked for Shawn")

jobs = fetch_jobs_from_json(JOBS_JSON_PATH)

if not jobs:
    st.error("No valid jobs found in jobs.json")
    st.stop()

scored_jobs = []

for job in jobs:
    result = score_job(job)
    scored_job = {
        **job,
        "score": result["total_score"],
        "skill_score": result["skill_score"],
        "tool_score": result["tool_score"],
        "role_score": result["role_score"],
        "industry_score": result["industry_score"],
        "penalty": result["penalty"],
        "difficulty_penalty": result["difficulty_penalty"],
        "entry_bonus": result["entry_bonus"],
        "location_score": result["location_score"],
        "domain_penalty": result["domain_penalty"],
        "matched_skills": ", ".join(result["matched_skills"]),
        "matched_tools": ", ".join(result["matched_tools"]),
        "matched_roles": ", ".join(result["matched_roles"]),
        "matched_industries": ", ".join(result["matched_industries"]),
        "matched_negative": ", ".join(result["matched_negative"]),
        "matched_difficulty": ", ".join(result["matched_difficulty"]),
        "matched_entry": ", ".join(result["matched_entry"]),
        "matched_location_positive": ", ".join(result["matched_location_positive"]),
        "matched_location_negative": ", ".join(result["matched_location_negative"]),
        "matched_domain_mismatch": ", ".join(result["matched_domain_mismatch"]),
    }
    scored_job["fit_tier"] = (
        "HIGH" if result["total_score"] >= 1.75
        else "MEDIUM" if result["total_score"] >= 1.0
        else "LOW"
    )
    scored_jobs.append(scored_job)

df = pd.DataFrame(scored_jobs)

if df.empty:
    st.error("No scores calculated.")
    st.stop()

practical_jobs = df[df.apply(is_practical_row, axis=1)].copy()
practical_jobs = practical_jobs.sort_values(by="score", ascending=False).head(10)

if practical_jobs.empty:
    st.warning("No practical jobs passed the current filter.")
    st.stop()

summary_cols = [
    "score",
    "fit_tier",
    "title",
    "company",
    "location",
    "source",
    "url",
    "skill_score",
    "tool_score",
    "role_score",
    "industry_score",
    "difficulty_penalty",
    "location_score",
]

st.subheader("Top 10 Practical Targets")

table_df = practical_jobs[summary_cols].copy()
table_df["apply"] = table_df["url"].apply(
    lambda x: f'<a href="{x}" target="_blank">🚀 Apply Now</a>'
)

st.write(
    table_df.drop(columns=["url"]).to_html(escape=False, index=False),
    unsafe_allow_html=True
)

st.markdown("---")
st.subheader("Detailed View")

for i, (_, row) in enumerate(practical_jobs.iterrows(), start=1):
    with st.expander(f"#{i} • {row['title']} @ {row['company']} • {row['score']:.2f} [{row['fit_tier']}]"):
        left, right = st.columns([2, 1])

        with left:
            st.markdown(f"**Location:** {row['location']}")
            st.markdown(f"**Source:** {row['source']}")
            st.markdown(f"[🚀 Apply to this job]({row['url']})")
            st.markdown(f"**Synopsis:** {generate_synopsis(row)}")

        with right:
            st.metric("Score", f"{row['score']:.2f}")
            st.metric("Tier", row["fit_tier"])
            st.metric("Location Fit", f"{row['location_score']:.2f}")

        st.markdown("### Score Breakdown")
        breakdown = pd.DataFrame(
            {
                "Metric": [
                    "Skills",
                    "Tools",
                    "Roles",
                    "Industry",
                    "Difficulty",
                    "Entry Bonus",
                    "Location",
                    "Domain Penalty",
                ],
                "Value": [
                    row["skill_score"],
                    row["tool_score"],
                    row["role_score"],
                    row["industry_score"],
                    row["difficulty_penalty"],
                    row["entry_bonus"],
                    row["location_score"],
                    row["domain_penalty"],
                ],
            }
        )
        st.dataframe(breakdown, use_container_width=True, hide_index=True)

        st.markdown("### Match Signals")
        if row["matched_skills"]:
            st.markdown(f"**Matched skills:** {row['matched_skills']}")
        if row["matched_tools"]:
            st.markdown(f"**Matched tools:** {row['matched_tools']}")
        if row["matched_roles"]:
            st.markdown(f"**Matched roles:** {row['matched_roles']}")
        if row["matched_industries"]:
            st.markdown(f"**Matched industries:** {row['matched_industries']}")
        if row["matched_entry"]:
            st.markdown(f"**Entry signals:** {row['matched_entry']}")
        if row["matched_difficulty"]:
            st.markdown(f"**Difficulty signals:** {row['matched_difficulty']}")
        if row["matched_location_positive"]:
            st.markdown(f"**Location positives:** {row['matched_location_positive']}")
        if row["matched_location_negative"]:
            st.markdown(f"**Location negatives:** {row['matched_location_negative']}")
        if row["matched_domain_mismatch"]:
            st.markdown(f"**Domain mismatch signals:** {row['matched_domain_mismatch']}")
        if row["matched_negative"]:
            st.markdown(f"**Negative signals:** {row['matched_negative']}")

        st.markdown("### Job Description Preview")
        st.write(row["description"][:2500])