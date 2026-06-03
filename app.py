"""Chainlit chat interface for the assistant."""

from dotenv import load_dotenv

load_dotenv()

import chainlit as cl

from artefact_ai_assistant.agent import build_agent

agent = build_agent()


@cl.on_chat_start
async def on_start():
    await cl.Message(
        content=(
            "Hi! I can answer questions directly or use tools "
            "(calculator, currency converter). What would you like to know?"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    cb = cl.LangchainCallbackHandler()
    result = await agent.ainvoke(
        {"messages": [("user", message.content)]},
        config={"callbacks": [cb]},
    )
    await cl.Message(content=result["messages"][-1].content).send()