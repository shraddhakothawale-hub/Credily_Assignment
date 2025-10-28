# Agent Specification Document

## Agent Name
**Credly Credit Point Analyzer Agent**

---

## Description
An autonomous LangGraph-based agent designed to interpret Credly badge URLs, summarize achievements, and identify earned credits or skills.

---

## Components
| Component | Description |
|------------|-------------|
| `AgentState` | Manages input/output message flow |
| `call_model()` | Core function invoking Groq’s LLM |
| `StateGraph` | Defines the flow of tasks (nodes + edges) |
| `ChatGroq` | Connects to the Groq API (Llama 3.3) |

---

## Nodes
- **respond**: Handles user query and generates AI output.

---

## Entry & Exit Points
- **Entry:** HumanMessage (user input)
- **Exit:** LLM-generated output message

---

## Expected Output
A descriptive summary of the Credly badge’s meaning, credit points, and associated skills.

---

## Environment Variables
| Variable | Description |
|-----------|-------------|
| `GROQ_API_KEY` | Required for Groq LLM authentication |

---

