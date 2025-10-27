# TripBuilder - MCP Integration Guide

## Overview
The GoHighLevel MCP (Model Context Protocol) Server provides a **standardized bridge** between AI assistants and GoHighLevel APIs. Instead of using the traditional Python API wrapper, TripBuilder can leverage MCP for **AI-native interactions** with GHL data.

---

## What is GHL MCP?

**Model Context Protocol (MCP)** is an open protocol that allows AI models to interact with data sources and tools through a standardized interface. The GHL MCP Server exposes 21+ tools that let AI agents:
- Query GHL data (contacts, opportunities, conversations, etc.)
- Create and update records
- Search and filter data
- Send messages
- Manage tasks and custom fields

**Key Advantage**: Instead of writing explicit API calls, you describe what you want in natural language, and the AI agent figures out the tool calls.

---

## MCP vs Traditional API Wrapper

### Traditional Approach (Python Wrapper)
```python
# Explicit API calls in application code
from ghl_api_wrapper import GoHighLevelAPI

ghl = GoHighLevelAPI(api_key=API_TOKEN, location_id=LOCATION_ID)

# Manual method calls
contact = ghl.contacts.get(contact_id)
opportunity = ghl.opportunities.create({
    "name": "Trip to Paris",
    "pipeline_id": "IlWdPtOpcczLpgsde2KF",
    "stage_id": "027508e9-939c-4646-bb59-66970fe674fe",
    "contact_id": contact_id
})
```

### MCP Approach (AI-Native)
```python
# AI agent interprets natural language and makes tool calls
response = await agent.ainvoke({
    "messages": [{
        "role": "user",
        "content": "Create a TripBooking opportunity for contact john@example.com for a trip to Paris, starting at FormSubmit stage"
    }]
})
# AI agent automatically:
# 1. Searches for contact by email
# 2. Creates opportunity with correct pipeline_id and stage_id
# 3. Returns structured result
```

---

## MCP Integration Architecture for TripBuilder

### Hybrid Approach (Recommended)
Use **MCP for AI-assisted operations** and **direct API calls for predictable CRUD**:

**Use MCP for**:
- Natural language search ("Find all passengers who haven't submitted passport info")
- Complex queries ("Show me trips with more than 5 passengers departing next month")
- Conversational interfaces (chatbot for staff to query data)
- Automated workflows triggered by natural language rules

**Use Direct API for**:
- Predictable CRUD operations (create trip → create TripBooking opportunity)
- Batch operations with known parameters
- Performance-critical operations
- Operations requiring transactional integrity

---

## MCP Server Configuration

### 1. Obtain Private Integration Token (PIT)
Navigate to **Settings > Private Integrations** in GHL and create a token with these scopes:
- View Contacts, Edit Contacts
- View Opportunities, Edit Opportunities
- View Conversations, Edit Conversations, View/Edit Messages
- View Calendars, View/Edit Calendar Events
- View Custom Fields
- View Locations
- View Payment Orders/Transactions
- View Forms

### 2. Configure MCP Client

**For Python (LangGraph Example)**:
```python
import asyncio
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async def init_mcp_agent():
    client = MultiServerMCPClient({
        "ghl": {
            "url": "https://services.leadconnectorhq.com/mcp/",
            "transport": "streamable_http",
            "headers": {
                "Authorization": f"Bearer {os.getenv('GHL_API_TOKEN')}",
                "locationId": os.getenv('GHL_LOCATION_ID')
            }
        }
    })
    
    tools = await client.get_tools()
    
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    agent = create_react_agent(llm, tools)
    return agent
```

**For Claude Desktop (JSON config)**:
```json
{
  "mcpServers": {
    "ghl-mcp": {
      "url": "https://services.leadconnectorhq.com/mcp/",
      "headers": {
        "Authorization": "Bearer pit-your-token-here",
        "locationId": "your-location-id"
      }
    }
  }
}
```

**For Cursor/Windsurf/OpenAI**:
Add MCP endpoint to agent configuration with Authorization header.

---

## Available MCP Tools for TripBuilder

### Contacts
- `contacts_get-contacts` - Get all contacts
- `contacts_get-contact` - Fetch specific contact
- `contacts_create-contact` - Create new contact
- `contacts_update-contact` - Update contact details
- `contacts_upsert-contact` - Create or update contact
- `contacts_add-tags` - Add tags to contact
- `contacts_remove-tags` - Remove tags
- `contacts_get-all-tasks` - Get contact tasks

### Opportunities
- `opportunities_search-opportunity` - Search opportunities by criteria
- `opportunities_get-pipelines` - Get all pipelines (TripBooking, Passenger)
- `opportunities_get-opportunity` - Get specific opportunity
- `opportunities_update-opportunity` - Update opportunity (including stage progression)

### Custom Fields
- `locations_get-custom-fields` - Get custom field definitions

### Conversations
- `conversations_search-conversation` - Search conversations
- `conversations_get-messages` - Get messages by conversation ID
- `conversations_send-a-new-message` - Send message to contact

### Calendars
- `calendars_get-calendar-events` - Get calendar events
- `calendars_get-appointment-notes` - Get appointment notes

### Payments
- `payments_get-order-by-id` - Get order details
- `payments_list-transactions` - List transactions

---

## Integration Patterns for TripBuilder

### Pattern 1: AI-Assisted Search
**Use Case**: Staff searches for passengers with incomplete details

```python
# Flask route with MCP agent
@app.route('/ai-search', methods=['POST'])
async def ai_search():
    query = request.json['query']  # "Find passengers missing passport info"
    
    agent = await init_mcp_agent()
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    # Parse response and return structured data
    return jsonify(response)
```

**Example Queries**:
- "Show me all passengers for the Italy trip"
- "Find contacts who haven't completed health details"
- "List trips departing in the next 30 days"

### Pattern 2: Automated Stage Progression
**Use Case**: AI determines when to move opportunity to next stage based on criteria

```python
async def auto_progress_passenger(passenger_id):
    agent = await init_mcp_agent()
    
    prompt = f"""
    Check passenger opportunity {passenger_id}:
    - Are all required custom fields filled (passport, health details, emergency contact)?
    - If yes, progress to 'DetailsSubmitted' stage
    - If no, list missing fields
    """
    
    response = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    return response
```

### Pattern 3: Conversational Interface
**Use Case**: Staff chatbot for querying data

```python
@app.route('/chat', methods=['POST'])
async def chat():
    user_message = request.json['message']
    
    agent = await init_mcp_agent()
    response = await agent.ainvoke({
        "messages": [
            {"role": "system", "content": "You are a TripBuilder assistant helping staff manage trips and passengers."},
            {"role": "user", "content": user_message}
        ]
    })
    
    return jsonify({"reply": response})
```

**Example Conversations**:
- User: "How many passengers are on the Spain trip?"
- AI: Uses `opportunities_search-opportunity` to find Passenger opportunities linked to Spain trip
- User: "Send them all a reminder about passport submission"
- AI: Uses `conversations_send-a-new-message` for each passenger

### Pattern 4: Bulk Operations
**Use Case**: Tag all passengers at a specific stage

```python
async def tag_passengers_by_stage(stage_name, tag):
    agent = await init_mcp_agent()
    
    prompt = f"""
    1. Find all Passenger opportunities at stage '{stage_name}'
    2. For each opportunity, get the contact_id
    3. Add tag '{tag}' to each contact
    4. Return count of contacts tagged
    """
    
    response = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    return response
```

---

## Implementation in TripBuilder

### Step 1: Add MCP Dependencies
```bash
pip install langchain-openai langchain-mcp-adapters langgraph
```

### Step 2: Create MCP Service Module
**File: `services/mcp_service.py`**
```python
import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

class MCPService:
    def __init__(self):
        self.agent = None
        
    async def initialize(self):
        client = MultiServerMCPClient({
            "ghl": {
                "url": "https://services.leadconnectorhq.com/mcp/",
                "transport": "streamable_http",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('GHL_API_TOKEN')}",
                    "locationId": os.getenv('GHL_LOCATION_ID')
                }
            }
        })
        
        tools = await client.get_tools()
        
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.agent = create_react_agent(llm, tools)
    
    async def query(self, prompt: str, system_prompt: str = None):
        if not self.agent:
            await self.initialize()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.agent.ainvoke({"messages": messages})
        return response

# Global instance
mcp = MCPService()
```

### Step 3: Add AI Search Route
**In `app.py`**:
```python
from services.mcp_service import mcp

@app.route('/ai-search')
@login_required
async def ai_search_page():
    return render_template('ai_search.html')

@app.route('/api/ai-search', methods=['POST'])
@login_required
async def ai_search_api():
    query = request.json.get('query')
    
    system_prompt = """
    You are a TripBuilder assistant. You have access to GoHighLevel data.
    When searching for trips, use pipeline_id IlWdPtOpcczLpgsde2KF (TripBooking).
    When searching for passengers, use pipeline_id fnsdpRtY9o83Vr4z15bE (Passenger).
    Return results in a structured JSON format.
    """
    
    response = await mcp.query(query, system_prompt)
    return jsonify(response)
```

### Step 4: Create AI Search UI
**Template: `templates/ai_search.html`**
```html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>AI-Powered Search</h2>
    <div class="card">
        <div class="card-body">
            <form id="ai-search-form">
                <div class="mb-3">
                    <label for="query" class="form-label">Ask a question</label>
                    <textarea class="form-control" id="query" rows="3" 
                              placeholder="e.g., Find all passengers on the Italy trip who haven't submitted passport info"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Search</button>
            </form>
            
            <div id="results" class="mt-4"></div>
        </div>
    </div>
</div>

<script>
document.getElementById('ai-search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('query').value;
    
    const response = await fetch('/api/ai-search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query})
    });
    
    const data = await response.json();
    document.getElementById('results').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
});
</script>
{% endblock %}
```

---

## Environment Variables

Add to `.env`:
```
GHL_API_TOKEN=pit-your-private-integration-token
GHL_LOCATION_ID=your-location-id
OPENAI_API_KEY=sk-your-openai-api-key
```

---

## Recommended Hybrid Architecture

```
TripBuilder Application
├── Traditional API Wrapper (ghl-api-wrapper-complete.py)
│   └── Used for: CRUD operations, predictable workflows
│
└── MCP Service (services/mcp_service.py)
    └── Used for: AI search, natural language queries, automated decisions
    
Routes:
├── /trips (traditional CRUD)
├── /contacts (traditional CRUD)
├── /passengers (traditional CRUD)
└── /ai-search (MCP-powered)
```

---

## Benefits of MCP Integration

1. **Natural Language Interface**: Staff can query data without knowing database structure
2. **Flexible Queries**: AI determines the right tools and parameters
3. **Multi-Step Automation**: Chain multiple operations through conversation
4. **Reduced Code Complexity**: Less boilerplate for complex queries
5. **Future-Proof**: As GHL adds MCP tools, gain new capabilities without code changes

---

## Limitations & Considerations

1. **Latency**: MCP calls involve LLM inference (1-3 seconds per query)
2. **Cost**: OpenAI API costs per query
3. **Determinism**: AI responses may vary; use traditional API for critical operations
4. **Token Limits**: Complex queries may hit context window limits
5. **Error Handling**: AI may misinterpret queries; validate results

---

## Roadmap

GHL MCP plans to expand to **250+ tools** and add:
- NPX package for clients not supporting HTTP Streamable
- OAuth support
- Unified orchestration layer

---

## Testing MCP Integration

```python
# Test script
import asyncio
from services.mcp_service import mcp

async def test_mcp():
    # Test 1: Get all contacts
    result = await mcp.query("Show me all contacts")
    print("Contacts:", result)
    
    # Test 2: Search opportunities
    result = await mcp.query("Find all TripBooking opportunities")
    print("Trips:", result)
    
    # Test 3: Get custom fields
    result = await mcp.query("List all custom fields for opportunities")
    print("Custom Fields:", result)

if __name__ == "__main__":
    asyncio.run(test_mcp())
```

Run: `python test_mcp.py`

---

## Summary

**MCP adds an AI-native layer to TripBuilder**, enabling:
- Conversational data access
- Automated workflows based on natural language rules
- Flexible search without hardcoded queries
- Future extensibility as GHL expands MCP capabilities

**Combine with traditional API** for best results: use MCP for flexibility, use direct API for performance and reliability.