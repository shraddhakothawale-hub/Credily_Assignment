from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Securely load your GROQ API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AgentState(TypedDict):
    """
    Defines the state passed between nodes in the agent graph.
    """
    messages: List[BaseMessage]

# Initialize the LLM with the Groq API key and model name
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile"
)

def call_model(state: AgentState) -> AgentState:
    """
    Calls the language model with the current messages and appends the response.
    """
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    return state

# Build the agent graph
builder = StateGraph(AgentState)
builder.add_node("respond", call_model)
builder.set_entry_point("respond")
builder.add_edge("respond", END)
graph = builder.compile()

if __name__ == "__main__":
    # Example input message (you can change the content as needed)
    inputs = {"messages": [HumanMessage(content="Check Credly credit point details from https://www.credly.com/badges/e192db17-f8c5-46aa-8f99-8a565223f1d6?")]}
    print("Response:")
    response = graph.invoke(inputs)
    print(response["messages"][-1].content)
