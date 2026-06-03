"""The agent wires the LLM with our tools and a system prompt.

Single source of truth for model choice, tool list, and routing instructions.
ChatAnthropic reads ANTHROPIC_API_KEY from os.environ, so load_dotenv()
must have run before build_agent() is called.
"""

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

from artefact_ai_assistant.tools.calculator import calculator
from artefact_ai_assistant.tools.currency import currency_converter


SYSTEM_PROMPT = """\
You are a helpful AI assistant. You answer questions from your own knowledge
when possible, and use external tools when they would give a more accurate
or up-to-date answer.

Available tools:
- calculator: for arithmetic, percentages, or any numerical computation.
- currency_converter: for converting amounts between currencies. Use this
  whenever the user asks about currency conversion — exchange rates change
  daily and you can't know the current ones from memory.

When the question is general knowledge (history, science, definitions,
opinion), answer directly without tools. You can also chain tools when it
helps — e.g. convert a currency, then apply a fee with the calculator.

Be concise. Respond in the same language as the user.
"""


def build_agent(model: str = "claude-haiku-4-5"):
    llm = ChatAnthropic(model=model)
    return create_agent(
        llm,
        tools=[calculator, currency_converter],
        system_prompt=SYSTEM_PROMPT,
    )