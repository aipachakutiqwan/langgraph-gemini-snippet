import asyncio
from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage


# BREAKPOINTS WITH LANGGRAPH SDK
# Activate the server by running: langgraph dev
async def breakpoint_example():
    client = get_client(url="http://127.0.0.1:2024")
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
    thread = await client.threads.create()
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=initial_input,
        stream_mode="values",
        interrupt_before=["tools"],
    ):
        print(f"Receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)
    # Continue the run after the interruption
    async for chunk in client.runs.stream(
        thread["thread_id"],
        "agent",
        input=None,
        stream_mode="values",
        interrupt_before=["tools"],
    ):
        print(f"Receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)


asyncio.run(breakpoint_example())
