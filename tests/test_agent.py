from smart_text_agent import root_agent


def test_root_agent_exposes_all_tools():
    tool_names = {
        tool.name if hasattr(tool, "name") else tool.__name__
        for tool in root_agent.tools
    }

    assert root_agent.name == "smart_text_agent"
    assert tool_names == {
        "summarize_text",
        "answer_question",
        "classify_text",
        "route_request",
        "analyze_text",
    }
