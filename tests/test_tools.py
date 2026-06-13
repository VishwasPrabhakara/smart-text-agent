import pytest

from smart_text_agent.agent import (
    MAX_TEXT_LENGTH,
    analyze_text,
    answer_question,
    classify_text,
    route_request,
    summarize_text,
)


def test_classification_uses_whole_word_matches():
    result = classify_text("The children were happy after the picnic.")

    assert result["keyword_hints"] == (
        "No strong keyword matches found, rely on semantic analysis."
    )


def test_classification_returns_relevant_keyword_hints():
    result = classify_text(
        "The cloud platform exposes an API for machine learning workloads."
    )

    assert result["keyword_hints"]["Technology"] == [
        "cloud",
        "machine learning",
        "API",
    ]


@pytest.mark.parametrize(
    ("user_input", "expected"),
    [
        ("Summarize this article", "summarize_text"),
        ("Classify this paragraph", "classify_text"),
        ("Give me the word count", "analyze_text"),
        ("Why is the sky blue?", "answer_question"),
        ("Help me understand this text", "answer_question"),
    ],
)
def test_route_request(user_input, expected):
    assert route_request(user_input)["recommended_tool"] == expected


def test_summarize_text_validates_style():
    text = " ".join(["word"] * 25)

    with pytest.raises(ValueError, match="style must be one of"):
        summarize_text(text, style="haiku")


def test_short_text_does_not_request_summarization():
    result = summarize_text("This sentence is already short.")

    assert result["status"] == "text_too_short"


def test_analyze_text_reports_correct_statistics():
    result = analyze_text("Hello world. This is a test!")

    assert result["word_count"] == 6
    assert result["sentence_count"] == 2
    assert result["character_count"] == 28
    assert result["average_word_length"] == 3.5
    assert result["estimated_reading_time_seconds"] == 2


def test_question_type_detection():
    result = answer_question("Compare Python vs Java")

    assert result["question_type"] == "comparative"
    assert result["has_context"] is False


@pytest.mark.parametrize(
    "tool,args",
    [
        (classify_text, ("   ",)),
        (summarize_text, ("",)),
        (answer_question, ("",)),
        (route_request, ("\n\t",)),
        (analyze_text, ("",)),
    ],
)
def test_tools_reject_empty_input(tool, args):
    with pytest.raises(ValueError):
        tool(*args)


def test_tools_reject_oversized_input():
    with pytest.raises(ValueError, match="character limit"):
        analyze_text("x" * (MAX_TEXT_LENGTH + 1))
