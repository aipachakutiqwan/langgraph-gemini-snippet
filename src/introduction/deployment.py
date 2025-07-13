import asyncio
from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage

# This example demonstrates how to use the LangGraph SDK to interact with a LangGraph server.
# Go to src/introduction/studio and activate the server by running: langgraph dev 

async def load_langgraph_sdk():
    # This is the URL of the local development server
    URL = "http://127.0.0.1:2024"
    client = get_client(url=URL)
    assistants = await client.assistants.search()
    print(f"last assistants: {assistants[-3]}")
    thread = await client.threads.create()
    print(f"thread created: {thread}")
    input = {"messages": [HumanMessage(content="Multiply 3 by 2.")]}
    async for chunk in client.runs.stream(
        thread_id=thread["thread_id"],
        assistant_id="agent",
        input=input,
        stream_mode="values",
    ):
        if chunk.data and chunk.event != "metadata":
            print("Received chunk:")
            print(chunk.data["messages"][-1])

asyncio.run(load_langgraph_sdk())
