from pydantic_ai import Agent

# Initialize the mental health advisor agent
agent = Agent(
    "groq:openai/gpt-oss-20b",
    instructions=(
        "You are a mental health advisor.\n"
        "Help the patient address their problems.\n"
        "Do NOT talk about anything apart from mental health — STRICTLY!\n"
        "Always provide the solution in two parts:\n"
        "  1. The reason for the problem.\n"
        "  2. Actionable steps in bullet points.\n"
        "Maintain a warm, empathetic tone. Avoid medical diagnosis."
    ),
)


async def get_agent_response(user_query: str) -> str:
    """
    Synchronously run the agent on the user's query
    and return the generated text output.
    """
    result = await agent.run(user_query)
    return result.output


if __name__ == '__main__':
    print(get_agent_response("hi"))