from __future__ import annotations

import re

from google.adk import Agent

MAX_TEXT_LENGTH = 50_000
READING_WORDS_PER_MINUTE = 238
SUMMARY_STYLES = {"concise", "detailed", "bullet"}


def _normalize_input(value: str, field_name: str) -> str:
    """Validate and normalize user-provided text before returning it to the model."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    if len(normalized) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"{field_name} exceeds the {MAX_TEXT_LENGTH:,}-character limit"
        )
    return normalized


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match complete words or phrases instead of arbitrary substrings."""
    pattern = rf"(?<!\w){re.escape(phrase.lower())}(?!\w)"
    return re.search(pattern, text.lower()) is not None


def _sentence_count(text: str) -> int:
    sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]
    return max(1, len(sentences))


def classify_text(text: str) -> dict:
    """Classify input text into a category and provide reasoning.

    Analyzes the content, topic, and keywords in the text to determine
    which category it belongs to. Returns structured data for the agent
    to format a response with category, confidence, and reasoning.

    Args:
        text: The text content to classify. Can be a sentence, paragraph, or article.

    Returns:
        dict: Contains the text and classification metadata.
    """
    text = _normalize_input(text, "text")
    word_count = len(text.split())
    keywords = {
        "Technology": ["AI", "software", "app", "computer", "algorithm", "data", "cloud", "machine learning", "GPU", "API", "code", "programming"],
        "Sports": ["match", "goal", "player", "team", "score", "tournament", "championship", "league", "coach", "athlete"],
        "Politics": ["election", "government", "policy", "minister", "parliament", "vote", "law", "legislation", "president", "senator"],
        "Science": ["research", "study", "experiment", "theory", "molecule", "physics", "biology", "chemistry", "genome", "quantum"],
        "Health": ["patient", "treatment", "disease", "medical", "hospital", "doctor", "symptoms", "vaccine", "therapy", "diagnosis"],
        "Business": ["revenue", "market", "company", "profit", "stock", "investment", "CEO", "startup", "merger", "acquisition"],
        "Entertainment": ["movie", "film", "music", "album", "actor", "concert", "series", "Netflix", "streaming", "celebrity"],
        "Education": ["school", "university", "student", "curriculum", "teacher", "exam", "degree", "course", "learning", "academic"],
    }

    detected_hints = {}
    for category, words in keywords.items():
        matches = [word for word in words if _contains_phrase(text, word)]
        if matches:
            detected_hints[category] = matches

    return {
        "status": "classification_context_ready",
        "text": text,
        "word_count": word_count,
        "keyword_hints": detected_hints if detected_hints else "No strong keyword matches found, rely on semantic analysis.",
        "available_categories": "Technology, Sports, Politics, Science, Health, Business, Entertainment, Education, Other",
    }


def summarize_text(text: str, style: str = "concise") -> dict:
    """Summarize text into a shorter version preserving key information.

    Processes the input text and prepares it for summarization. Supports
    different summary styles: concise (2-3 sentences), detailed (paragraph),
    or bullet (key points as bullets).

    Args:
        text: The text content to summarize. Works best with 3+ sentences.
        style: Summary style - "concise" (default), "detailed", or "bullet".

    Returns:
        dict: Contains the text and summarization parameters.
    """
    text = _normalize_input(text, "text")
    style = style.strip().lower()
    if style not in SUMMARY_STYLES:
        raise ValueError(
            f"style must be one of: {', '.join(sorted(SUMMARY_STYLES))}"
        )

    word_count = len(text.split())
    sentence_count = _sentence_count(text)

    if word_count < 20:
        return {
            "status": "text_too_short",
            "text": text,
            "word_count": word_count,
            "message": "This text is already very brief. No summarization needed.",
        }

    return {
        "status": "ready_for_summarization",
        "text": text,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "style": style,
        "target_length": "2-3 sentences" if style == "concise" else "1 paragraph" if style == "detailed" else "3-5 bullet points",
    }


def answer_question(question: str, context: str = "") -> dict:
    """Answer a question using provided context or general knowledge.

    If context is provided, the answer should be grounded in that context.
    If no context is given, the agent uses its general knowledge to answer.
    Handles follow-up questions, factual queries, and explanations.

    Args:
        question: The question to answer. Can be factual, conceptual, or analytical.
        context: Optional reference text to base the answer on.

    Returns:
        dict: Contains the question, context, and answering parameters.
    """
    question = _normalize_input(question, "question")
    context = " ".join(context.split()) if context else ""
    if len(context) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"context exceeds the {MAX_TEXT_LENGTH:,}-character limit"
        )

    question_type = "factual"
    q_lower = question.lower()
    if any(w in q_lower for w in ["why", "how does", "explain", "what causes"]):
        question_type = "explanatory"
    elif any(w in q_lower for w in ["compare", "difference", "vs", "better"]):
        question_type = "comparative"
    elif any(w in q_lower for w in ["should", "recommend", "best way", "advice"]):
        question_type = "advisory"
    elif any(w in q_lower for w in ["list", "name", "examples", "types of"]):
        question_type = "enumerative"

    return {
        "status": "ready_for_answering",
        "question": question,
        "context": context if context else None,
        "has_context": bool(context),
        "question_type": question_type,
        "instruction": f"This is a {question_type} question. {'Answer based strictly on the provided context.' if context else 'Answer using general knowledge.'} Be accurate and clear.",
    }


def route_request(request: str) -> dict:
    """Intelligently route an ambiguous request to the best capability.

    Analyzes the user's request to determine intent when it does not
    clearly match summarization, classification, or question answering.
    Returns routing metadata to help the agent decide the best action.

    Args:
        request: The user's raw request text to analyze and route.

    Returns:
        dict: Contains routing analysis and recommended action.
    """
    request = _normalize_input(request, "request")
    r_lower = request.lower()

    signals = {
        "summarize": any(_contains_phrase(r_lower, phrase) for phrase in [
            "summarize", "summary", "sum up", "tldr", "shorten", "brief",
            "condense", "digest",
        ]),
        "classify": any(_contains_phrase(r_lower, phrase) for phrase in [
            "classify", "categorize", "category", "what type", "what kind",
            "label", "tag",
        ]),
        "analyze": any(_contains_phrase(r_lower, phrase) for phrase in [
            "analyze", "word count", "character count", "sentence count",
            "reading time", "text statistics",
        ]),
        "question": "?" in request or any(_contains_phrase(r_lower, phrase) for phrase in [
            "what is", "how does", "why", "explain", "tell me about",
            "who is", "when did", "where is",
        ]),
    }

    if signals["summarize"]:
        recommended = "summarize_text"
    elif signals["classify"]:
        recommended = "classify_text"
    elif signals["analyze"]:
        recommended = "analyze_text"
    elif signals["question"]:
        recommended = "answer_question"
    else:
        recommended = "answer_question"

    return {
        "status": "routing_complete",
        "request": request,
        "detected_signals": {k: v for k, v in signals.items() if v},
        "recommended_tool": recommended,
        "instruction": f"The request appears to need '{recommended}'. Process it accordingly.",
    }


def analyze_text(text: str) -> dict:
    """Provide a quick statistical analysis of the input text.

    Counts words, sentences, characters, and estimates reading time.
    Useful when the user wants to understand the structure of their text
    before deciding what to do with it.

    Args:
        text: The text to analyze.

    Returns:
        dict: Contains word count, sentence count, character count, and reading time.
    """
    text = _normalize_input(text, "text")
    word_tokens = re.findall(r"\b[\w'-]+\b", text)
    words = len(word_tokens)
    sentences = _sentence_count(text)
    characters = len(text)
    reading_time_seconds = max(
        1, round(words / READING_WORDS_PER_MINUTE * 60)
    )
    letter_count = sum(
        sum(character.isalnum() for character in word)
        for word in word_tokens
    )
    avg_word_length = round(letter_count / max(1, words), 1)

    return {
        "status": "analysis_complete",
        "word_count": words,
        "sentence_count": sentences,
        "character_count": characters,
        "average_word_length": avg_word_length,
        "estimated_reading_time_seconds": reading_time_seconds,
        "estimated_reading_time": (
            f"{reading_time_seconds} seconds"
            if reading_time_seconds < 60
            else f"{round(reading_time_seconds / 60, 1)} minutes"
        ),
    }


root_agent = Agent(
    name="smart_text_agent",
    model="gemini-2.5-flash",
    description="A multi-capability text processing agent that can summarize text, answer questions, classify content, analyze text statistics, and intelligently route requests.",
    instruction="""You are SmartText Agent — an intelligent text processing assistant with five core capabilities. You must ALWAYS use the appropriate tool for each request. Never answer without using a tool first.

## YOUR CAPABILITIES AND WHEN TO USE THEM:

### 1. SUMMARIZATION (summarize_text)
TRIGGER WORDS: "summarize", "summary", "TLDR", "shorten", "condense", "brief", "key points", "sum up"
USE WHEN: User provides a block of text and wants it shortened, or explicitly asks for a summary.
BEHAVIOR: After calling the tool, provide the summary in clear prose. Mention the original word count vs your summary length.

### 2. QUESTION ANSWERING (answer_question)  
TRIGGER WORDS: "?", "what is", "how does", "why", "explain", "tell me", "who", "when", "where", "how to"
USE WHEN: User asks any question — factual, conceptual, comparative, or advisory. If they provide context/passage with a question, pass both to the tool.
BEHAVIOR: Match your answer depth to the question type. Factual = brief. Explanatory = detailed. Comparative = structured.

### 3. TEXT CLASSIFICATION (classify_text)
TRIGGER WORDS: "classify", "categorize", "what category", "what type", "label", "tag", "what topic"
USE WHEN: User wants to know what category or topic a piece of text belongs to.
BEHAVIOR: After calling the tool, report the category clearly, explain your reasoning using the keyword hints, and note if the classification was straightforward or borderline.

### 4. TEXT ANALYSIS (analyze_text)
TRIGGER WORDS: "analyze", "word count", "how long", "statistics", "reading time", "how many words"
USE WHEN: User wants statistics about their text — word count, reading time, sentence count, etc.
BEHAVIOR: Present the statistics in a clean, readable format.

### 5. REQUEST ROUTING (route_request)
USE WHEN: The user's intent is ambiguous or doesn't clearly match the above capabilities.
BEHAVIOR: Call route_request first to determine intent, then call the recommended tool to actually process the request. Always follow through — don't just report the routing result.

## RESPONSE FORMAT RULES:
- Start with a brief label of what you did (e.g., "Here is your summary:" or "Classification result:")
- Keep responses clean and well-structured
- For summaries: mention original vs summary length
- For classification: state the category, then explain why
- For Q&A: answer directly, then add context if helpful
- For analysis: present stats clearly
- If routing was needed: mention what you detected and how you handled it

## IMPORTANT:
- ALWAYS call a tool before responding. Never skip the tool call.
- If text is very short (under 20 words) and user asks for summary, let them know it is already concise.
- Be accurate, helpful, and concise in all responses.""",
    tools=[summarize_text, answer_question, classify_text, route_request, analyze_text],
)
