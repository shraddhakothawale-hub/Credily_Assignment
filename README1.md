# Credly AI Assistant - LangGraph Implementation

## 🎯 Project Overview

An intelligent AI assistant built with LangGraph to help users navigate the Credly digital credentialing platform. This system provides personalized badge recommendations, credential verification, career path planning, and skill gap analysis.

## 🔍 Identified Use Cases

### 1. **Badge Discovery & Recommendation Agent**
- Analyzes user's current skills and career goals
- Recommends relevant badges from 4,000+ organizations
- Matches badges to job requirements
- Provides learning pathways

### 2. **Credential Verification Agent**
- Verifies badge authenticity via Credly API
- Checks badge expiration status
- Validates issuer credibility
- Retrieves badge metadata (skills, criteria, evidence)

### 3. **Career Path Planning Agent**
- Maps current badges to career opportunities
- Identifies skill gaps for target roles
- Suggests badge sequences for career progression
- Analyzes labor market insights

### 4. **Badge Management Assistant**
- Helps users accept/reject badges
- Guides badge sharing to LinkedIn, Twitter, etc.
- Manages badge privacy settings
- Tracks badge statistics (views, shares)

### 5. **Skills Intelligence Agent**
- Analyzes skill tags across user's badges
- Compares skills with industry trends
- Identifies emerging skill requirements
- Provides personalized upskilling recommendations

## 🏗️ System Architecture

The system uses a **multi-agent architecture** with LangGraph:

```
User Query → Router Agent → Specialized Agents → Response Synthesis
                  ↓
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
Discovery    Verification   Planning
 Agent         Agent         Agent
    ↓             ↓             ↓
         Response Aggregator
                  ↓
           Final Output
```

## 🚀 Features

- **Natural Language Interface**: Chat with the assistant in plain English
- **Context-Aware**: Maintains conversation history for better responses
- **API Integration**: Real Credly API integration (sandbox/production)
- **Multi-Agent Workflow**: Specialized agents for different tasks
- **Intelligent Routing**: Automatically routes queries to appropriate agents
- **Credential Validation**: OpenBadge 2.0/3.0 compliant verification


## ⚙️ Configuration

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here

```

## 💻 Usage

### Basic Example

```python
from credly_agent import CredlyAssistant

# Initialize the assistant
assistant = CredlyAssistant()

# Ask questions
response = assistant.chat("What badges should I earn for a data science career?")
print(response)

# Verify a badge
response = assistant.chat("Verify badge ID: abc123xyz")
print(response)

# Get career advice
response = assistant.chat("I have AWS and Python badges. What's my career path?")
print(response)
```


## 🏛️ System Components

### 1. Router Agent
- Analyzes user intent
- Routes to appropriate specialized agent
- Manages conversation flow

### 2. Discovery Agent
- Searches badge database
- Provides recommendations
- Analyzes skill requirements

### 3. Verification Agent
- Validates credentials
- Checks badge status
- Retrieves metadata

### 4. Planning Agent
- Career path analysis
- Skill gap identification
- Learning recommendations

### 5. Management Agent
- Badge acceptance guidance
- Sharing instructions
- Privacy settings help

