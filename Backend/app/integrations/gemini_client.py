
from google import genai

from app.core.config import settings


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
)


# ==========================================
# GENERATE ARTICLE SUMMARY
# ==========================================

def generate_article_summary(
    content: str,
) -> str:
    """
    Generate an article summary using Gemini AI.
    """

    prompt = f"""
    You are an AI assistant that summarizes articles.

    Summarize the following article clearly and accurately.

    Instructions:
    - Identify the main topic.
    - Focus on the most important information.
    - Remove unnecessary details.
    - Use simple and understandable language.
    - Do not add information that is not present in the article.

    Article:
    {content}
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned an empty summary")

    return response.text.strip()


# ==========================================
# GENERATE ARTICLE KEY POINTS
# ==========================================

def generate_article_key_points(
    content: str,
) -> str:
    """
    Generate important key points from an article using Gemini AI.
    """

    prompt = f"""
    You are an AI assistant that extracts key points from articles.

    Identify the 5 most important points from the article.

    Instructions:
    - Return exactly 5 key points when the content allows.
    - Keep each point concise and informative.
    - Use simple and understandable language.
    - Focus only on important information.
    - Do not add information that is not present in the article.
    - Format the result as a numbered list.

    Article:
    {content}
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned empty key points")

    return response.text.strip()
