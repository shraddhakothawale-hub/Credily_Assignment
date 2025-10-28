

# 🧩 User-System Interaction Document

## 🎯 Objective
Allow users to input a Credly badge URL and get insights or credit points data using Groq’s LLM through LangGraph.

---

## 🧑 User Actions
1. Enters a Credly badge link.
2. Runs the agent (`python Agent.py`).
3. Receives analyzed response describing:
   - Badge title
   - Skills gained
   - Credit/point summary

---

## 🧠 System Actions
1. Accepts user message via `HumanMessage`.
2. Passes message into the **LangGraph pipeline**.
3. The **Groq LLM** analyzes content and generates a summary.
4. Output message is returned to the user.

---

## 🔁 Example Interaction

| Step | Actor | Action |
|------|--------|--------|
| 1 | User | Enters Credly URL |
| 2 | System | Reads user message |
| 3 | LLM | Processes the badge data |
| 4 | System | Returns summary or insights |
| 5 | User | Reads response about credit points |

---

## ⚙️ Data Flow
**User → LangGraph StateGraph → ChatGroq (LLM) → Response**

---
