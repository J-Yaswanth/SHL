from typing import List, Tuple, Dict, Any
from app.catalog import search_catalog, compare_assessments


# -----------------------------------
# Main Agent Logic
# -----------------------------------

def get_agent_reply(
    messages: List[Dict[str, str]],
    catalog: List[Dict[str, Any]]
) -> Tuple[str, List[Dict[str, str]], bool]:
    """
    Main conversational recommendation logic.

    Returns:
    (
        reply,
        recommendations,
        end_of_conversation
    )
    """

    user_messages = [
        m["content"]
        for m in messages
        if m["role"] == "user"
    ]

    last_user = (
        user_messages[-1]
        if user_messages
        else ""
    )

    # -----------------------------------
    # Out-of-scope Handling
    # -----------------------------------

    blocked_topics = [
        "medical",
        "doctor",
        "weather",
        "movie",
        "politics",
        "cricket",
        "football"
    ]

    if any(
        topic in last_user.lower()
        for topic in blocked_topics
    ):

        return (
            "I can only assist with SHL assessment recommendations and hiring-related queries.",
            [],
            False
        )

    # -----------------------------------
    # Vague Query Handling
    # -----------------------------------

    conversation_text = " ".join(user_messages)
    if is_vague(conversation_text):
        return (
            "Could you please specify the job role, skills, seniority level, or assessment type?",
            [],
            False
        )
    # -----------------------------------
    # Comparison Handling
    # -----------------------------------

    if is_comparison_request(last_user):

        comparison_reply = compare_assessments(
            last_user,
            catalog
        )

        return comparison_reply, [], False

    # -----------------------------------
    # Extract Filters
    # -----------------------------------

    filters = extract_filters(messages)

    # -----------------------------------
    # Search Catalog
    # -----------------------------------

    recommendations = search_catalog(
        filters,
        catalog
    )

    # -----------------------------------
    # Recommendation Response
    # -----------------------------------

    if recommendations:

        reply = (
            f"Here are {len(recommendations)} SHL assessments "
            f"that match your requirements."
        )

        return (
            reply,
            recommendations,
            False
        )

    # -----------------------------------
    # No Results
    # -----------------------------------

    return (
        "I could not find strong matching assessments. "
        "Could you provide more details about the role or skills required?",
        [],
        False
    )


# -----------------------------------
# Vague Query Detection
# -----------------------------------

def is_vague(text: str) -> bool:
    """
    Detect vague queries only when
    no meaningful hiring context exists.
    """

    text = text.lower()

    vague_phrases = [
        "assessment",
        "test",
        "exam",
        "need",
        "suggest",
        "recommend"
    ]

    meaningful_keywords = [

        # Technical
        "java",
        "python",
        "javascript",
        "sql",
        "backend",
        "frontend",

        # Personality
        "leadership",
        "communication",
        "teamwork",
        "behavioral",

        # Cognitive
        "reasoning",
        "analytical",
        "logical",
        "problem solving",
        "cognitive"
    ]

    has_vague_phrase = any(
        phrase in text
        for phrase in vague_phrases
    )

    has_meaningful_context = any(
        keyword in text
        for keyword in meaningful_keywords
    )

    return (
        has_vague_phrase
        and not has_meaningful_context
        and len(text.split()) < 5
    )

# -----------------------------------
# Comparison Query Detection
# -----------------------------------

def is_comparison_request(text: str) -> bool:

    text = text.lower()

    comparison_keywords = [
        "compare",
        "difference between",
        "vs",
        "versus"
    ]

    return any(
        keyword in text
        for keyword in comparison_keywords
    )


# -----------------------------------
# Filter Extraction
# -----------------------------------

def extract_filters(
    messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Extract filters from the FULL
    conversation history.
    """

    filters = {
        "skills": [],
        "seniority": None,
        "types": []
    }

    # -----------------------------------
    # Combine Conversation
    # -----------------------------------

    all_text = " ".join(
        [
            m["content"].lower()
            for m in messages
            if m["role"] == "user"
        ]
    )

    # -----------------------------------
    # Skill Extraction
    # -----------------------------------

    skill_keywords = {

        # Technical
        "java": "Java",
        "python": "Python",
        "javascript": "JavaScript",
        "sql": "SQL",
        "backend": "Backend",
        "frontend": "Frontend",
        "data science": "Data Science",
        "analytics": "Analytics",
        "aws": "AWS",
        "cloud": "Cloud Computing",
        "devops": "DevOps",
        "agile": "Agile",

        # Personality
        "leadership": "Leadership",
        "communication": "Communication",
        "teamwork": "Teamwork",
        "behavioral": "Behavioral",
        "motivation": "Motivation",
        "collaboration": "Collaboration",

        # Cognitive
        "reasoning": "Reasoning",
        "problem solving": "Problem Solving",
        "analytical": "Analytical Thinking",
        "logical": "Logical Thinking",
        "decision making": "Decision Making",
        "critical thinking": "Critical Thinking"
    }

    for keyword, value in skill_keywords.items():

        if keyword in all_text:

            filters["skills"].append(value)

    # -----------------------------------
    # Seniority Extraction
    # -----------------------------------

    if (
        "mid-level" in all_text
        or "mid level" in all_text
    ):

        filters["seniority"] = "Mid-level"

    elif "senior" in all_text:

        filters["seniority"] = "Senior"

    elif "junior" in all_text:

        filters["seniority"] = "Junior"

    elif "entry-level" in all_text:

        filters["seniority"] = "Entry-level"

    # -----------------------------------
    # Assessment Type Extraction
    # -----------------------------------

    if "personality" in all_text:

        filters["types"].append(
            "Personality"
        )

    if "technical" in all_text:

        filters["types"].append(
            "Technical"
        )

    if "cognitive" in all_text:

        filters["types"].append(
            "Cognitive"
        )

    if "behavioral" in all_text:

        filters["types"].append(
            "Behavioral"
        )

    return filters
