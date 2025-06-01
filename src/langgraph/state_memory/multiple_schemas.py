from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# PRIVATE STATE
class OverallState(TypedDict):
    foo: int

class PrivateState(TypedDict):
    baz: int

def node_1(state: OverallState) -> PrivateState:
    print("---Node 1---")
    return {"baz": state['foo'] + 1}

def node_2(state: PrivateState) -> OverallState:
    print("---Node 2---")
    return {"foo": state['baz'] + 1}

# Build graph
builder = StateGraph(OverallState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)
# Add
graph = builder.compile()
# View
print(graph.get_graph())
print(graph.invoke({"foo" : 1}))

# INPUT/OUTPUT SCHEMA
class OverallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking_node(state: OverallState):
    return {"answer": "bye", "notes": "his name is Florentino"}

def answer_node(state: OverallState):
    return {"answer": "bye Florentino"}

graph = StateGraph(OverallState)
graph.add_node("thinking_node", thinking_node)
graph.add_node("answer_node", answer_node)
graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)
graph = graph.compile()
# View
print(graph.get_graph())
print(graph.invoke({"question":"hi", 
                    "notes": "his name is Conny"}))


class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking_node(state: InputState):
    return {"answer": "bye", "notes": "his is name is Florentino"}

def answer_node(state: OverallState) -> OutputState:
    return {"answer": "bye Conny"}

graph = StateGraph(OverallState, input=InputState, output=OutputState)
graph.add_node("thinking_node", thinking_node)
graph.add_node("answer_node", answer_node)
graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)
graph = graph.compile()
# View
print(graph.get_graph())
print(graph.invoke({"question":"hi"}))
