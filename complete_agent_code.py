"""
Credly AI Assistant - Multi-Agent System with LangGraph
Implements intelligent badge discovery, verification, and career planning.
"""

from typing import TypedDict, List, Dict, Any, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Initialize LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.7
)

# ==================== STATE DEFINITIONS ====================

class AgentState(TypedDict):
    """Global state passed between all agents."""
    messages: List[BaseMessage]
    current_agent: str
    user_intent: str
    agent_outputs: Dict[str, Any]
    conversation_context: Dict[str, Any]


# ==================== MOCK DATA ====================

MOCK_BADGES = {
    "cloud": [
        {
            "id": "aws-cloud-practitioner",
            "name": "AWS Certified Cloud Practitioner",
            "issuer": "Amazon Web Services",
            "level": "beginner",
            "skills": ["Cloud Computing", "AWS Services", "Security", "Pricing"],
            "time_to_earn": "20-30 hours",
            "cost": "$100",
            "description": "Foundational understanding of AWS Cloud",
            "url": "https://credly.com/org/amazon-web-services"
        },
        {
            "id": "azure-fundamentals",
            "name": "Microsoft Azure Fundamentals",
            "issuer": "Microsoft",
            "level": "beginner",
            "skills": ["Azure Services", "Cloud Concepts", "Pricing", "Support"],
            "time_to_earn": "15-25 hours",
            "cost": "$99",
            "description": "Core Azure cloud services understanding",
            "url": "https://credly.com/org/microsoft-certification"
        }
    ],
    "data": [
        {
            "id": "google-data-analytics",
            "name": "Google Data Analytics Professional Certificate",
            "issuer": "Google",
            "level": "beginner",
            "skills": ["Data Analysis", "SQL", "Tableau", "R Programming", "Spreadsheets"],
            "time_to_earn": "6 months",
            "cost": "$39/month",
            "description": "Comprehensive data analytics skills",
            "url": "https://credly.com/org/google"
        },
        {
            "id": "tableau-desktop-specialist",
            "name": "Tableau Desktop Specialist",
            "issuer": "Tableau",
            "level": "intermediate",
            "skills": ["Data Visualization", "Dashboard Creation", "Analytics"],
            "time_to_earn": "40 hours",
            "cost": "$100",
            "description": "Data visualization expertise",
            "url": "https://credly.com/org/tableau"
        }
    ],
    "python": [
        {
            "id": "pcep-python",
            "name": "PCEP – Certified Entry-Level Python Programmer",
            "issuer": "Python Institute",
            "level": "beginner",
            "skills": ["Python Basics", "Data Types", "Control Flow", "Functions"],
            "time_to_earn": "50 hours",
            "cost": "$59",
            "description": "Entry-level Python certification",
            "url": "https://credly.com/org/python-institute"
        }
    ]
}

CAREER_PATHS = {
    "data analyst": {
        "required_skills": ["SQL", "Data Visualization", "Statistics", "Excel", "Python"],
        "recommended_badges": ["google-data-analytics", "tableau-desktop-specialist"],
        "salary_range": "$60K-$90K",
        "growth": "High demand (+25% by 2030)"
    },
    "cloud engineer": {
        "required_skills": ["AWS/Azure", "Networking", "Security", "Linux", "Infrastructure as Code"],
        "recommended_badges": ["aws-cloud-practitioner", "azure-fundamentals"],
        "salary_range": "$80K-$130K",
        "growth": "Very high demand (+30% by 2030)"
    },
    "data scientist": {
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "Deep Learning"],
        "recommended_badges": ["pcep-python", "google-data-analytics"],
        "salary_range": "$90K-$150K",
        "growth": "Extremely high demand (+35% by 2030)"
    }
}


# ==================== ROUTER AGENT ====================

def router_agent(state: AgentState) -> AgentState:
    """
    Analyzes user intent and routes to appropriate specialist agent.
    """
    last_message = state["messages"][-1].content.lower()
    
    # Intent classification prompt
    classification_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an intent classifier for a Credly badge assistant.
        Classify user queries into ONE of these categories:
        - discovery: Finding, searching, or recommending badges
        - verification: Verifying, validating, or checking badge authenticity
        - planning: Career planning, skill gaps, job transitions
        - management: Accepting, sharing, or managing badges
        - skills: Analyzing skills, comparing competencies
        - general: General questions, greetings, unclear intent
        
        Respond with ONLY the category name, nothing else."""),
        ("user", "{query}")
    ])
    
    chain = classification_prompt | llm
    intent_response = chain.invoke({"query": last_message})
    intent = intent_response.content.strip().lower()
    
    # Store intent
    state["user_intent"] = intent
    state["current_agent"] = intent
    
    print(f"🎯 Router: Classified intent as '{intent}'")
    
    return state


# ==================== DISCOVERY AGENT ====================

def discovery_agent(state: AgentState) -> AgentState:
    """
    Helps users discover and explore relevant badges.
    """
    user_query = state["messages"][-1].content
    
    # Extract keywords for badge search
    search_prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract key search terms from the user's query for badge discovery.
        Focus on: technologies, skills, roles, industries.
        Return as comma-separated words."""),
        ("user", "{query}")
    ])
    
    chain = search_prompt | llm
    keywords_response = chain.invoke({"query": user_query})
    keywords = keywords_response.content.strip().lower()
    
    # Search mock database
    found_badges = []
    for category, badges in MOCK_BADGES.items():
        if any(kw in category for kw in keywords.split(",")):
            found_badges.extend(badges)
    
    # If no direct match, search by skills
    if not found_badges:
        for badges in MOCK_BADGES.values():
            for badge in badges:
                badge_text = " ".join(badge["skills"]).lower() + " " + badge["name"].lower()
                if any(kw.strip() in badge_text for kw in keywords.split(",")):
                    found_badges.append(badge)
    
    # Generate recommendations
    if found_badges:
        recommendation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a badge recommendation expert. Based on the badges found,
            provide a helpful, personalized recommendation to the user.
            
            Format your response with:
            1. Brief introduction
            2. Top 2-3 badge recommendations with emojis
            3. Key benefits
            4. Next steps
            
            Be enthusiastic and helpful!"""),
            ("user", "User asked: {query}\n\nFound badges: {badges}")
        ])
        
        chain = recommendation_prompt | llm
        response = chain.invoke({
            "query": user_query,
            "badges": json.dumps(found_badges, indent=2)
        })
        
        state["agent_outputs"]["discovery"] = {
            "badges": found_badges,
            "response": response.content
        }
    else:
        state["agent_outputs"]["discovery"] = {
            "badges": [],
            "response": "I couldn't find specific badges for that search. Try asking about popular areas like 'cloud computing', 'data analysis', or 'Python programming'."
        }
    
    print(f"🔍 Discovery Agent: Found {len(found_badges)} badges")
    
    return state


# ==================== VERIFICATION AGENT ====================

def verification_agent(state: AgentState) -> AgentState:
    """
    Verifies badge authenticity and provides details.
    """
    user_query = state["messages"][-1].content
    
    # Mock verification (in production, this would call Credly API)
    verification_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a credential verification specialist.
        
        Since we're in demo mode, explain the verification process and what information
        would be checked:
        - Badge ID validation
        - Issuer verification
        - Expiration status
        - Skills and criteria
        - Evidence of achievement
        
        Be professional and thorough."""),
        ("user", "{query}")
    ])
    
    chain = verification_prompt | llm
    response = chain.invoke({"query": user_query})
    
    state["agent_outputs"]["verification"] = {
        "verified": True,
        "details": "Demo mode - In production, this would connect to Credly API",
        "response": response.content
    }
    
    print("✅ Verification Agent: Processed verification request")
    
    return state


# ==================== PLANNING AGENT ====================

def planning_agent(state: AgentState) -> AgentState:
    """
    Provides career planning and skill gap analysis.
    """
    user_query = state["messages"][-1].content
    
    # Extract target role
    role_prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract the target job role/career from the user's query.
        Return just the role name (e.g., 'data analyst', 'cloud engineer').
        If unclear, return 'unknown'."""),
        ("user", "{query}")
    ])
    
    chain = role_prompt | llm
    role_response = chain.invoke({"query": user_query})
    target_role = role_response.content.strip().lower()
    
    # Get career path data
    career_data = CAREER_PATHS.get(target_role, None)
    
    if career_data:
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a career planning expert. Create a personalized roadmap
            for the user based on their target role.
            
            Include:
            1. Skills needed
            2. Recommended badges with timeline
            3. Expected outcomes (salary, growth)
            4. Action steps
            
            Use emojis and be motivating!"""),
            ("user", "User wants to become: {role}\n\nCareer data: {data}")
        ])
        
        chain = planning_prompt | llm
        response = chain.invoke({
            "role": target_role,
            "data": json.dumps(career_data, indent=2)
        })
        
        state["agent_outputs"]["planning"] = {
            "career_path": career_data,
            "response": response.content
        }
    else:
        state["agent_outputs"]["planning"] = {
            "career_path": None,
            "response": f"I can help with career planning! Popular paths I know well are: {', '.join(CAREER_PATHS.keys())}. Which interests you?"
        }
    
    print(f"📊 Planning Agent: Analyzed career path for '{target_role}'")
    
    return state


# ==================== MANAGEMENT AGENT ====================

def management_agent(state: AgentState) -> AgentState:
    """
    Assists with badge management tasks.
    """
    user_query = state["messages"][-1].content
    
    management_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a badge management assistant. Help users with:
        - Accepting badges from Credly emails
        - Sharing badges to LinkedIn, Twitter, etc.
        - Managing profile settings
        - Privacy controls
        
        Provide step-by-step instructions with clear numbering.
        Be friendly and encouraging!"""),
        ("user", "{query}")
    ])
    
    chain = management_prompt | llm
    response = chain.invoke({"query": user_query})
    
    state["agent_outputs"]["management"] = {
        "response": response.content
    }
    
    print("⚙️ Management Agent: Provided guidance")
    
    return state


# ==================== SKILLS ANALYSIS AGENT ====================

def skills_analysis_agent(state: AgentState) -> AgentState:
    """
    Analyzes skills and identifies gaps.
    """
    user_query = state["messages"][-1].content
    
    skills_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a skills analysis expert. Help users understand:
        - Their current skill set
        - Skills gaps for target roles
        - Trending skills in their industry
        - Personalized learning recommendations
        
        Be analytical but encouraging. Use progress bars and percentages."""),
        ("user", "{query}")
    ])
    
    chain = skills_prompt | llm
    response = chain.invoke({"query": user_query})
    
    state["agent_outputs"]["skills"] = {
        "response": response.content
    }
    
    print("📈 Skills Analysis Agent: Completed analysis")
    
    return state


# ==================== GENERAL AGENT ====================

def general_agent(state: AgentState) -> AgentState:
    """
    Handles general queries and unclear intents.
    """
    user_query = state["messages"][-1].content
    
    general_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly Credly assistant. Help users with:
        - General questions about Credly and digital badges
        - Greetings and casual conversation
        - Clarification of unclear requests
        
        Suggest specific ways you can help:
        - Badge discovery
        - Verification
        - Career planning
        - Badge management
        - Skills analysis"""),
        ("user", "{query}")
    ])
    
    chain = general_prompt | llm
    response = chain.invoke({"query": user_query})
    
    state["agent_outputs"]["general"] = {
        "response": response.content
    }
    
    print("💬 General Agent: Handled query")
    
    return state


# ==================== RESPONSE SYNTHESIZER ====================

def response_synthesizer(state: AgentState) -> AgentState:
    """
    Aggregates agent outputs and formats final response.
    """
    agent = state["current_agent"]
    output = state["agent_outputs"].get(agent, {})
    
    if "response" in output:
        final_response = output["response"]
    else:
        final_response = "I'm here to help with Credly badges! What would you like to know?"
    
    # Add response to messages
    state["messages"].append(AIMessage(content=final_response))
    
    print(f"🔄 Synthesizer: Generated final response\n")
    
    return state


# ==================== ROUTING LOGIC ====================

def route_to_agent(state: AgentState) -> str:
    """
    Determines which specialized agent to route to.
    """
    intent = state.get("user_intent", "general")
    
    routing_map = {
        "discovery": "discovery",
        "verification": "verification",
        "planning": "planning",
        "management": "management",
        "skills": "skills",
        "general": "general"
    }
    
    return routing_map.get(intent, "general")


# ==================== BUILD LANGGRAPH ====================

def create_credly_assistant():
    """
    Creates and compiles the multi-agent LangGraph.
    """
    # Initialize state
    builder = StateGraph(AgentState)
    
    # Add all agent nodes
    builder.add_node("router", router_agent)
    builder.add_node("discovery", discovery_agent)
    builder.add_node("verification", verification_agent)
    builder.add_node("planning", planning_agent)
    builder.add_node("management", management_agent)
    builder.add_node("skills", skills_analysis_agent)
    builder.add_node("general", general_agent)
    builder.add_node("synthesizer", response_synthesizer)
    
    # Set entry point
    builder.set_entry_point("router")
    
    # Add conditional routing from router to specialized agents
    builder.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "discovery": "discovery",
            "verification": "verification",
            "planning": "planning",
            "management": "management",
            "skills": "skills",
            "general": "general"
        }
    )
    
    # Connect all agents to synthesizer
    builder.add_edge("discovery", "synthesizer")
    builder.add_edge("verification", "synthesizer")
    builder.add_edge("planning", "synthesizer")
    builder.add_edge("management", "synthesizer")
    builder.add_edge("skills", "synthesizer")
    builder.add_edge("general", "synthesizer")
    
    # End after synthesizer
    builder.add_edge("synthesizer", END)
    
    # Compile graph
    graph = builder.compile()
    
    return graph


# ==================== ASSISTANT CLASS ====================

class CredlyAssistant:
    """
    Main assistant class for interacting with the multi-agent system.
    """
    
    def __init__(self):
        self.graph = create_credly_assistant()
        self.conversation_history = []
        print("✅ Credly AI Assistant initialized!\n")
    
    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the assistant's response.
        """
        # Create initial state
        state = {
            "messages": [HumanMessage(content=user_message)],
            "current_agent": "",
            "user_intent": "",
            "agent_outputs": {},
            "conversation_context": {}
        }
        
        # Add conversation history
        state["messages"] = self.conversation_history + state["messages"]
        
        # Run the graph
        result = self.graph.invoke(state)
        
        # Extract response
        response = result["messages"][-1].content
        
        # Update conversation history (keep last 6 messages)
        self.conversation_history = result["messages"][-6:]
        
        return response
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []
        print("🔄 Conversation history cleared.\n")


# ==================== INTERACTIVE MODE ====================

def interactive_mode():
    """
    Run the assistant in interactive command-line mode.
    """
    assistant = CredlyAssistant()
    
    print("=" * 70)
    print("🎓 Welcome to Credly AI Assistant!")
    print("=" * 70)
    print("\nI can help you with:")
    print("  🔍 Discovering relevant badges")
    print("  ✅ Verifying credentials")
    print("  📊 Planning your career path")
    print("  ⚙️  Managing your badges")
    print("  📈 Analyzing your skills")
    print("\nType 'quit' or 'exit' to end the conversation.")
    print("Type 'reset' to clear conversation history.")
    print("=" * 70)
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using Credly AI Assistant! Goodbye!\n")
                break
            
            # Check for reset
            if user_input.lower() == 'reset':
                assistant.reset()
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Get response
            print()
            response = assistant.chat(user_input)
            print(f"Assistant: {response}\n")
            print("-" * 70)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using Credly AI Assistant! Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            print("Please try again or type 'quit' to exit.\n")


# ==================== DEMO EXAMPLES ====================

def run_demo_examples():
    """
    Run predefined examples to demonstrate capabilities.
    """
    assistant = CredlyAssistant()
    
    examples = [
        "What badges should I get to learn cloud computing?",
        "I want to become a data analyst. What's my path?",
        "Can you verify a badge for me?",
        "How do I share my badge on LinkedIn?",
        "What skills am I missing for a data scientist role?"
    ]
    
    print("=" * 70)
    print("🎯 RUNNING DEMO EXAMPLES")
    print("=" * 70)
    print()
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}/{len(examples)}")
        print(f"User: {example}\n")
        
        response = assistant.chat(example)
        print(f"Assistant: {response}\n")
        print("=" * 70)
        print()
        
        # Reset for next example
        assistant.reset()


# ==================== MAIN EXECUTION ====================

def main():
    """
    Main entry point with mode selection.
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo mode
        run_demo_examples()
    else:
        # Run interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()