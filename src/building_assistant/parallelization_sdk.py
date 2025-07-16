import asyncio
from langgraph_sdk import get_client


# USING LANGGRAPH API
async def search():
    print("Running parallelization example with LangGraph API")
    client = get_client(url="http://127.0.0.1:2024")
    thread = await client.threads.create()
    input_question = {"question": "How were Nvidia Q2 2024 earnings?"}
    async for event in client.runs.stream(
        thread["thread_id"],
        assistant_id="parallelization",
        input=input_question,
        stream_mode="values",
    ):
        # Check if answer has been added to state
        answer = event.data.get("answer", None)
        if answer:
            print(answer["content"])


asyncio.run(search())
