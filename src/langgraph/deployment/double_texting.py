import asyncio
import httpx
from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client
from langchain_core.messages import convert_to_messages

def get_local_client():
    url_for_cli_deployment = "http://localhost:8123"
    client = get_client(url=url_for_cli_deployment)
    return client


async def double_texting():
    client = get_local_client()
    # REJECT
    # Create a thread
    thread = await client.threads.create()
    # Create to dos
    user_input_1 = "Add a ToDo to follow-up with DI Repairs."
    user_input_2 = "Add a ToDo to mount dresser to the wall."
    config = {"configurable": {"user_id": "Test-Double-Texting"}}
    graph_name = "task_maistro" 
    run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_1)]}, 
        config=config,
    )
    try:
        await client.runs.create(
            thread["thread_id"],
            graph_name,
            input={"messages": [HumanMessage(content=user_input_2)]}, 
            config=config,
            multitask_strategy="reject",
        )
    except httpx.HTTPStatusError as e:
        print("Failed to start concurrent run", e)
    
    # Wait until the original run completes
    await client.runs.join(thread["thread_id"], run["run_id"])
    # Get the state of the thread
    state = await client.threads.get_state(thread["thread_id"])
    for m in convert_to_messages(state["values"]["messages"]):
        m.pretty_print()

    # ENQUEUE
    # Create a new thread
    thread = await client.threads.create()
    # Create new ToDos
    user_input_1 = "Send Erik his t-shirt gift this weekend."
    user_input_2 = "Get cash and pay nanny for 2 weeks. Do this by Friday."
    config = {"configurable": {"user_id": "Test-Double-Texting"}}
    graph_name = "task_maistro" 
    first_run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_1)]}, 
        config=config,
    )
    second_run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_2)]}, 
        config=config,
        multitask_strategy="enqueue",
    )
    # Wait until the second run completes
    print("Wait until the second run completes")
    await client.runs.join(thread["thread_id"], second_run["run_id"])
    # Get the state of the thread
    state = await client.threads.get_state(thread["thread_id"])
    for m in convert_to_messages(state["values"]["messages"]):
        m.pretty_print()
    
    # INTERRUPT
    # Create a new thread
    thread = await client.threads.create()
    # Create new ToDos
    user_input_1 = "Give me a summary of my ToDos due tomrrow."
    user_input_2 = "Never mind, create a ToDo to Order Ham for Thanksgiving by next Friday."
    config = {"configurable": {"user_id": "Test-Double-Texting"}}
    graph_name = "task_maistro" 
    interrupted_run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_1)]}, 
        config=config,
    )
    # Wait for some of run 1 to complete so that we can see it in the thread 
    await asyncio.sleep(1)
    second_run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_2)]}, 
        config=config,
        multitask_strategy="interrupt",
    )
    # Wait until the second run completes
    await client.runs.join(thread["thread_id"], second_run["run_id"])
    # Get the state of the thread
    state = await client.threads.get_state(thread["thread_id"])
    for m in convert_to_messages(state["values"]["messages"]):
        m.pretty_print()
    # Confirm that the first run was interrupted
    print((await client.runs.get(thread["thread_id"], interrupted_run["run_id"]))["status"])

    # ROLLBACK
    # Create a new thread
    thread = await client.threads.create()
    # Create new ToDos
    user_input_1 = "Add a ToDo to call to make appointment at Yoga."
    user_input_2 = "Actually, add a ToDo to drop by Yoga in person on Sunday."
    config = {"configurable": {"user_id": "Test-Double-Texting"}}
    graph_name = "task_maistro" 
    rolled_back_run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_1)]}, 
        config=config,
    )
    second_run = await client.runs.create(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input_2)]}, 
        config=config,
        multitask_strategy="rollback",
    )
    # Wait until the second run completes
    await client.runs.join(thread["thread_id"], second_run["run_id"])
    # Get the state of the thread
    state = await client.threads.get_state(thread["thread_id"])
    for m in convert_to_messages(state["values"]["messages"]):
        m.pretty_print()
    # Confirm that the original run was deleted
    try:
        await client.runs.get(thread["thread_id"], rolled_back_run["run_id"])
    except httpx.HTTPStatusError as _:
        print("Original run was correctly deleted")


asyncio.run(double_texting())