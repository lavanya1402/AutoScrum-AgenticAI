# utils/question_router.py

"""
This module classifies user queries.
For now, it returns 'general' for all questions
to enable flexible, freeform AI answers based on backlog context.
"""

def classify_query(query: str) -> str:
    """
    Classify the user's natural language question.

    Args:
        query (str): The user's input question.

    Returns:
        str: 'general' — indicating the question should be handled by a general-purpose fallback agent.
    """
    return "general"
