from langchain_core.messages import HumanMessage

# TEST GEMINI INTEGRATION
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

print(f"Gemini model: {llm}")
msg = HumanMessage(content="Hello world", name="Lance")
messages = [msg]
res = llm.invoke(messages)
print(res.content)

# TEST TAVILY INTEGRATION
from langchain_community.tools.tavily_search import TavilySearchResults

tavily_search = TavilySearchResults(max_results=3)
search_docs = tavily_search.invoke("What is LangGraph?")
print(search_docs)
