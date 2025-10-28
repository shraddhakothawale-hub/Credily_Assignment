# Agent Specification Document
## Credly AI Assistant - Multi-Agent System

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Overview
The system implements a **hierarchical multi-agent architecture** using LangGraph, where a Router Agent coordinates five specialized agents to handle different aspects of digital credential management.

### 1.2 Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│                     USER INPUT                          │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  ROUTER AGENT                           │
│  - Intent Classification                                │
│  - Agent Selection                                      │
│  - Context Management                                   │
└────┬─────────┬──────────┬──────────┬──────────┬────────┘
     │         │          │          │          │
     ▼         ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Discovery│ │Verific- │ │Planning │ │Manage-  │ │Skills   │
│ Agent   │ │ation    │ │ Agent   │ │ment     │ │Analysis │
│         │ │ Agent   │ │         │ │ Agent   │ │ Agent   │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              RESPONSE SYNTHESIZER                       │
│  - Aggregates agent outputs                             │
│  - Formats final response                               │
│  - Adds recommendations                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  USER OUTPUT                            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. AGENT SPECIFICATIONS

### 2.1 Router Agent

**Purpose**: Central coordinator that analyzes user queries and routes them to appropriate specialized agents.

**Responsibilities**:
- Intent classification
- Agent selection and orchestration
- Context maintenance across conversation turns
- Error handling and fallback logic

**Input**: User query + conversation history

**Output**: Routing decision + context

**Decision Logic**:
```python
Intent Classification Rules:
- "find", "recommend", "search", "discover" → Discovery Agent
- "verify", "check", "validate", "authentic" → Verification Agent
- "career", "path", "become", "job" → Planning Agent
- "accept", "share", "manage", "profile" → Management Agent
- "skills", "gap", "missing", "compare" → Skills Analysis Agent
- Ambiguous → Ask clarifying question
- Out of scope → Polite decline + suggestion
```

**State Management**:
```python
class RouterState(TypedDict):
    messages: List[BaseMessage]
    user_intent: str
    selected_agent: str
    context: Dict[str, Any]
    conversation_history: List[Dict]
```

**Implementation**:
- Uses LLM for intent classification
- Maintains conversation context
- Implements confidence thresholds (>0.7 for routing)
- Fallback to clarification if confidence < 0.5

---

### 2.2 Discovery Agent

**Purpose**: Helps users find and explore relevant badges based on their interests and goals.

**Capabilities**:
1. Badge search by keyword/skill/industry
2. Personalized recommendations based on:
   - Career goals
   - Current skill level
   - Learning history
   - Industry trends
3. Badge comparison
4. Learning path suggestions

**Input Schema**:
```python
class DiscoveryInput(TypedDict):
    search_query: str
    user_profile: Optional[Dict]  # Current badges, skills
    filters: Optional[Dict]        # Level, cost, time, industry
    context: str                   # Career goal, interest area
```

**Output Schema**:
```python
class DiscoveryOutput(TypedDict):
    recommendations: List[BadgeRecommendation]
    reasoning: str
    learning_paths: List[LearningPath]
    next_steps: List[str]
```

**Badge Recommendation Structure**:
```python
class BadgeRecommendation:
    badge_id: str
    name: str
    issuer: str
    description: str
    skills: List[str]
    level: str              # beginner/intermediate/advanced
    time_to_earn: str       # hours/weeks
    cost: str               # free/paid amount
    prerequisites: List[str]
    relevance_score: float  # 0-1
    reasoning: str          # Why recommended
    earn_url: str
```

**Search Strategy**:
1. Keyword matching (skills, technologies)
2. Career path alignment
3. Skill progression logic
4. Industry demand analysis
5. Peer recommendation patterns

**Data Sources**:
- Mock badge database (for demo)
- Credly API (production)
- Industry skill mappings
- Career pathway data

---

### 2.3 Verification Agent

**Purpose**: Validates badge authenticity and retrieves detailed credential information.

**Capabilities**:
1. Badge ID/URL verification
2. Issuer validation
3. Expiration status checking
4. Metadata extraction (skills, criteria, evidence)
5. OpenBadge compliance verification

**Input Schema**:
```python
class VerificationInput(TypedDict):
    badge_identifier: str  # ID or URL
    verification_type: str # full/quick/issuer_only
```

**Output Schema**:
```python
class VerificationOutput(TypedDict):
    is_valid: bool
    status: str            # active/expired/revoked/invalid
    badge_details: BadgeDetails
    issuer_info: IssuerInfo
    verification_timestamp: str
    warnings: List[str]
```

**Badge Details Structure**:
```python
class BadgeDetails:
    badge_id: str
    name: str
    description: str
    issuer: str
    issued_date: str
    expiration_date: Optional[str]
    earner_name: str
    skills: List[str]
    evidence: List[Evidence]
    image_url: str
    public_url: str
    criteria: str
    openbadge_version: str
```

**Verification Process**:
```
1. Parse badge identifier (ID or URL)
2. Call Credly API endpoint:
   GET /v1/badges/{badge_id}
   or GET /v1/obi/v2/badge_assertions/{id}
3. Validate response structure
4. Check issuer verification status
5. Verify OpenBadge compliance
6. Check expiration status
7. Extract and format metadata
8. Return structured result
```

**Error Handling**:
- Invalid badge ID format
- Badge not found (404)
- Revoked badges
- Expired credentials
- API connection issues

---

### 2.4 Planning Agent

**Purpose**: Provides career path guidance and badge sequencing recommendations.

**Capabilities**:
1. Career path mapping
2. Skill gap identification
3. Badge progression planning
4. ROI analysis (time/cost vs outcomes)
5. Job market alignment

**Input Schema**:
```python
class PlanningInput(TypedDict):
    current_badges: List[str]      # User's current credentials
    target_role: str                # Desired job title
    target_company: Optional[str]   # Specific employer
    timeline: Optional[str]         # Desired timeframe
    constraints: Optional[Dict]     # Budget, time availability
```

**Output Schema**:
```python
class PlanningOutput(TypedDict):
    career_paths: List[CareerPath]
    skill_gaps: List[SkillGap]
    recommended_sequence: List[BadgeRecommendation]
    timeline: Timeline
    roi_analysis: ROIAnalysis
```

**Career Path Structure**:
```python
class CareerPath:
    role_title: str
    match_percentage: float
    current_skills: List[str]
    missing_skills: List[str]
    required_badges: List[str]
    estimated_timeline: str
    salary_range: str
    job_openings: int
    growth_trend: str
```

**Planning Algorithm**:
```
1. Analyze current badge portfolio
2. Extract verified skills from badges
3. Match against target role requirements
4. Identify skill gaps
5. Find badges that fill gaps
6. Sequence badges by:
   - Prerequisites
   - Difficulty progression
   - Time efficiency
   - Cost optimization
7. Calculate ROI metrics
8. Generate timeline with milestones
```

**Decision Factors**:
- Skill transferability
- Industry demand trends
- Badge recognition value
- Learning curve difficulty
- Cost-benefit ratio
- Time to completion

---

### 2.5 Management Agent

**Purpose**: Assists users with badge acceptance, sharing, and profile management.

**Capabilities**:
1. Badge acceptance guidance
2. Multi-platform sharing instructions
3. Profile optimization tips
4. Privacy settings management
5. Badge portfolio organization

**Input Schema**:
```python
class ManagementInput(TypedDict):
    action_type: str  # accept/share/organize/privacy
    platform: Optional[str]  # linkedin/twitter/facebook/email
    badge_id: Optional[str]
    preferences: Optional[Dict]
```

**Output Schema**:
```python
class ManagementOutput(TypedDict):
    instructions: List[Step]
    tips: List[str]
    templates: Optional[Dict[str, str]]  # Post templates
    best_practices: List[str]
```

**Action Workflows**:

**Accept Badge**:
```
1. Check email from admin@credly.com
2. Click acceptance link
3. Create/login to Credly account
4. Confirm email verification
5. Customize badge visibility
6. Add to profile
```

**Share to LinkedIn**:
```
1. Navigate to badge page
2. Click Share button
3. Select LinkedIn
4. Authorize Credly app (first time)
5. Customize post text
6. Add relevant hashtags
7. Post to feed
```

**Profile Optimization**:
```
1. Upload professional photo
2. Write compelling bio (500 chars)
3. Add current position/company
4. List skill specializations
5. Set badge visibility preferences
6. Enable badge notifications
```

---

### 2.6 Skills Analysis Agent

**Purpose**: Analyzes user's skill portfolio and provides gap analysis.

**Capabilities**:
1. Skill extraction from badges
2. Skill gap identification
3. Competitive analysis
4. Trend analysis
5. Personalized upskilling recommendations

**Input Schema**:
```python
class SkillsAnalysisInput(TypedDict):
    user_badges: List[str]
    comparison_target: str  # role/person/company
    analysis_type: str      # gap/trend/competitive
```

**Output Schema**:
```python
class SkillsAnalysisOutput(TypedDict):
    current_skills: List[SkillWithLevel]
    skill_gaps: List[SkillGap]
    trending_skills: List[TrendingSkill]
    recommendations: List[str]
    match_score: float
```

**Skill Structure**:
```python
class SkillWithLevel:
    name: str
    category: str  # technical/soft/domain
    level: str     # beginner/intermediate/expert
    verified_by: List[str]  # Badge names
    demand_score: float     # 0-1
    
class SkillGap:
    skill_name: str
    importance: str      # critical/important/nice-to-have
    market_demand: float
    badges_to_fill: List[str]
    estimated_time: str
```

**Analysis Methods**:

1. **Skill Extraction**:
   - Parse badge metadata
   - Extract skill tags
   - Normalize skill names
   - Categorize by domain

2. **Gap Analysis**:
   - Compare current vs required
   - Prioritize by importance
   - Consider market demand
   - Factor in learning curve

3. **Trend Analysis**:
   - Track emerging skills
   - Identify declining skills
   - Monitor industry shifts
   - Predict future needs

---

## 3. INTER-AGENT COMMUNICATION

### 3.1 Message Format
```python
class AgentMessage(TypedDict):
    sender: str           # Agent ID
    receiver: str         # Target agent or "router"
    message_type: str     # request/response/error
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: str   # Track request chains
```

### 3.2 Communication Patterns

**Sequential Processing**:
```
User → Router → Agent A → Router → Response
```

**Parallel Processing**:
```
User → Router → [Agent A, Agent B, Agent C] → Aggregator → Response
```

**Chained Processing**:
```
User → Router → Agent A → Agent B → Agent C → Response
```

---

## 4. STATE MANAGEMENT

### 4.1 Global State Schema
```python
class GlobalState(TypedDict):
    messages: List[BaseMessage]
    user_profile: Optional[UserProfile]
    conversation_context: Dict[str, Any]
    active_agents: List[str]
    agent_outputs: Dict[str, Any]
    metadata: Dict[str, Any]
```

### 4.2 User Profile
```python
class UserProfile:
    user_id: str
    earned_badges: List[str]
    skills: List[str]
    career_goal: Optional[str]
    industry: Optional[str]
    experience_level: str
    preferences: Dict[str, Any]
```

### 4.3 Context Preservation
- Conversation history maintained across turns
- User preferences cached during session
- Badge search history tracked
- Previous recommendations stored

---

## 5. LANGGRAPH IMPLEMENTATION

### 5.1 Graph Structure
```python
from langgraph.graph import StateGraph, END

# Define state
class AgentState(TypedDict):
    messages: List[BaseMessage]
    current_agent: str
    agent_outputs: Dict[str, Any]
    final_response: str

# Build graph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("router", router_agent)
builder.add_node("discovery", discovery_agent)
builder.add_node("verification", verification_agent)
builder.add_node("planning", planning_agent)
builder.add_node("management", management_agent)
builder.add_node("skills", skills_analysis_agent)
builder.add_node("synthesizer", response_synthesizer)

# Add conditional edges
builder.add_conditional_edges(
    "router",
    route_to_agent,
    {
        "discovery": "discovery",
        "verification": "verification",
        "planning": "planning",
        "management": "management",
        "skills": "skills",
        "end": END
    }
)

# Connect agents to synthesizer
for agent in ["discovery", "verification", "planning", "management", "skills"]:
    builder.add_edge(agent, "synthesizer")

builder.add_edge("synthesizer", END)
builder.set_entry_point("router")
```

### 5.2 Router Logic
```python
def route_to_agent(state: AgentState) -> str:
    """
    Determines which agent should handle the query.
    """
    last_message = state["messages"][-1].content.lower()
    
    # Intent keywords
    if any(word in last_message for word in ["find", "recommend", "search", "discover", "looking for"]):
        return "discovery"
    elif any(word in last_message for word in ["verify", "check", "validate", "authentic", "real"]):
        return "verification"
    elif any(word in last_message for word in ["career", "path", "become", "job", "role", "transition"]):
        return "planning"
    elif any(word in last_message for word in ["accept", "share", "post", "linkedin", "manage"]):
        return "management"
    elif any(word in last_message for word in ["skills", "gap", "missing", "compare", "analyze"]):
        return "skills"
    else:
        # Use LLM for complex classification
        return classify_with_llm(last_message)
```

---

## 6. TOOL INTEGRATIONS

### 6.1 Credly API Tools
```python
class CredlyAPITools:
    """
    Wrapper for Credly API endpoints.
    """
    
    @tool
    def search_badges(query: str, filters: Dict) -> List[Dict]:
        """Search badges by keyword and filters."""
        
    @tool
    def get_badge_details(badge_id: str) -> Dict:
        """Retrieve detailed badge information."""
        
    @tool
    def verify_badge(badge_id: str) -> Dict:
        """Verify badge authenticity."""
        
    @tool
    def get_issuer_info(issuer_id: str) -> Dict:
        """Get issuer organization details."""
```

### 6.2 External Data Tools
```python
@tool
def get_job_market_data(role: str, location: str) -> Dict:
    """Fetch job market insights for a role."""
    
@tool
def get_skill_trends(skill: str, timeframe: str) -> Dict:
    """Get skill demand trends."""
    
@tool
def get_salary_data(role: str, skills: List[str]) -> Dict:
    """Estimate salary based on skills."""
```

---

## 7. PERFORMANCE SPECIFICATIONS

### 7.1 Response Time Targets
- Router decision: < 200ms
- Simple queries: < 2 seconds
- Complex queries: < 5 seconds
- API calls: < 1 second each

### 7.2 Accuracy Targets
- Intent classification: > 95%
- Badge recommendations: > 90% relevance
- Skill gap analysis: > 95% accuracy
- Verification: 100% accuracy

### 7.3 Scalability
- Concurrent users: 1000+
- Messages per second: 100+
- API rate limits: Handled with retries
- Cache hit rate: > 70%

---

## 8. ERROR HANDLING

### 8.1 Error Types
```python
class AgentError(Exception):
    """Base agent error."""
    
class RoutingError(AgentError):
    """Cannot determine intent."""
    
class APIError(AgentError):
    """External API failure."""
    
class ValidationError(AgentError):
    """Invalid input data."""
```

### 8.2 Fallback Strategies
- **Unclear intent**: Ask clarifying question
- **API failure**: Use cached data or inform user
- **Invalid input**: Request correction with example
- **Timeout**: Return partial results + retry option

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests
- Each agent independently
- Router logic
- Tool functions
- State management

### 9.2 Integration Tests
- Multi-agent workflows
- API integrations
- Error scenarios
- Edge cases

### 9.3 End-to-End Tests
- Complete user journeys
- Performance benchmarks
- Stress testing
- User acceptance testing

---

## 10. MONITORING & LOGGING

### 10.1 Metrics to Track
- Agent selection accuracy
- Response times per agent
- API call success rates
- User satisfaction scores
- Conversation completion rates

### 10.2 Logging Format
```python
{
    "timestamp": "2025-10-28T10:30:00Z",
    "conversation_id": "conv_123",
    "agent": "discovery",
    "action": "search_badges",
    "input": {...},
    "output": {...},
    "duration_ms": 450,
    "success": true
}
```

---
