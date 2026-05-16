import json
from typing import List, Dict, Any


# -----------------------------------
# Load Catalog
# -----------------------------------

def load_catalog(path: str) -> List[Dict[str, Any]]:
    """
    Load SHL assessment catalog from JSON file.
    """

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------
# Search Catalog
# -----------------------------------

def search_catalog(
    filters: Dict[str, Any],
    catalog: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Search and rank assessments
    based on extracted filters.
    """

    scored_results = []

    for item in catalog:

        score = 0

        # -----------------------------------
        # Skill Matching
        # -----------------------------------

        for skill in filters.get("skills", []):

            skill_lower = skill.lower()

            # Assessment name match
            if skill_lower in item.get(
                "name",
                ""
            ).lower():

                score += 8

            # Skills metadata match
            for catalog_skill in item.get(
                "skills",
                []
            ):

                if skill_lower in catalog_skill.lower():

                    score += 6

            # Description match
            if skill_lower in item.get(
                "description",
                ""
            ).lower():

                score += 4

            # Category match
            if skill_lower in item.get(
                "category",
                ""
            ).lower():

                score += 2

        # -----------------------------------
        # Assessment Type Matching
        # -----------------------------------

        for assessment_type in filters.get(
            "types",
            []
        ):

            if assessment_type.lower() in item.get(
                "test_type",
                ""
            ).lower():

                score += 5

        # -----------------------------------
        # Seniority Matching
        # -----------------------------------

        if filters.get("seniority"):

            for level in item.get(
                "job_levels",
                []
            ):

                if filters["seniority"].lower() in level.lower():

                    score += 3

        # -----------------------------------
        # Keep relevant results only
        # -----------------------------------

        if score >= 5:

            scored_results.append(
                (
                    score,
                    {
                        "name": item.get("name"),
                        "url": item.get("url"),
                        "test_type": item.get(
                            "test_type",
                            "General"
                        )
                    }
                )
            )

    # -----------------------------------
    # Sort by score
    # -----------------------------------

    scored_results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    # -----------------------------------
    # Remove duplicates
    # -----------------------------------

    seen = set()

    final_results = []

    for _, result in scored_results:

        if result["name"] not in seen:

            seen.add(result["name"])

            final_results.append(result)

        # Maximum 10 recommendations
        if len(final_results) >= 10:
            break

    return final_results


# -----------------------------------
# Compare Assessments
# -----------------------------------

def compare_assessments(
    query: str,
    catalog: List[Dict[str, Any]]
) -> str:
    """
    Compare two SHL assessments.
    """

    query_lower = query.lower()

    matched = []

    # Find matching assessments
    for item in catalog:

        if item["name"].lower() in query_lower:

            matched.append(item)

    # Need at least two assessments
    if len(matched) < 2:

        return (
            "Please mention two valid SHL assessments to compare."
        )

    a = matched[0]
    b = matched[1]

    # Clean compact comparison response
    return (
        f"{a['name']} ({a.get('test_type', 'General')}) "
        f"vs "
        f"{b['name']} ({b.get('test_type', 'General')}). "
        f"{a['name']} focuses on "
        f"{', '.join(a.get('skills', []))}. "
        f"{b['name']} focuses on "
        f"{', '.join(b.get('skills', []))}. "
        f"Duration: {a.get('duration', 'N/A')} vs "
        f"{b.get('duration', 'N/A')}."
    )