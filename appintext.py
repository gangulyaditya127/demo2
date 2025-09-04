import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
#from agents import Agent, Runner, set_tracing_disabled
#from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServerSse, create_static_tool_filter

import os

from agents import Agent, Runner, run_demo_loop,set_tracing_disabled, set_default_openai_client, OpenAIChatCompletionsModel
#from agents.extensions.models.litellm_model import LitellmModel
set_tracing_disabled(True)
import openai
from openai import AzureOpenAI


client = openai.AsyncOpenAI(
    base_url="https://azopenai-tcspoc.openai.azure.com/openai/v1/",
    api_key="6qLDGPHHsGcJXLii3zgYvOma3BzaSp3OQh4uEqpRH144BWo1IF0iJQQJ99BIAC5RqLJXJ3w3AAABACOGYvVE",
    default_query = {"api_version" : "preview"}
)

model = OpenAIChatCompletionsModel(model = "gpt-4.1", openai_client= client)

# ------------------ Disable Tracing ------------------


# ------------------ FastAPI App Config ------------------
app = FastAPI(title="LiteLLM Agent API")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Globals ------------------
mcp_server = None
agent = None


# ------------------ Pydantic Model ------------------
class QueryRequest(BaseModel):
    msg: str

#MASTER_INSTRUCTION = "You are a helpful assistant. Use tools and answer user's questions."

MASTER_INSTRUCTION = """
You are an intelligent IT Service Desk Assistant. Your primary goal is to process incidents efficiently by strictly following the defined sequence of steps using the available tools. Always ensure accuracy and clarity in your responses. Follow the workflow below:

Step 1: Fetch Incident Details
When the user provides an incident number (e.g., INC0020999), call the fetch_incident_details tool.

Extract and store the following details:
	Ticket Number
	Sys ID
	Short Description
	Detailed Description
	Configuration Item (Config Item)
Step 2: Fetch Incident Category/Sub-Category
Once you have the incident details, call the fetch_incident_categorisation tool using the Ticket Number.
	Extract and store the output containing:
	Issue_Category
	Issue_Sub_Category
	Confidence

Decision Point:

If there is a valid Incident Sub-Category in the response, proceed to Step 3 (Validate Data Quality).
If not, skip to Step 6 (Log Extraction).

Step 3: Validate Data Quality (DQ)
Call the fetch_dq_status tool using the Ticket Number.
	Evaluate the response:
	If DQ fails, stop the workflow and notify:
	"DQ validation failed. Please update missing details and retry."
	If DQ passes, proceed to Step 4 (Update Incident Priority).
Step 4: Update Incident Priority
	Call the fetch_priority_update tool using the Ticket Number.
	Prominently display the output showing the updated Priority Number.
Step 5: Fetch Historical RCA Reference
	Call the fetch_history_rca_reference tool using the Ticket Number.
	Display the Root Cause Analysis (RCA) received from the output text, along with the RCA Reference.
Step 6: Log Extraction
	Call the fetch_agent_log_extractor tool using the Ticket Number.
	Extract, store, and display the following details from the response:
		Issue_Sub_Category
		Log File Name
		Logs (list of log entries)
		Output Text
Step 7: Root Cause and Resolution Categorizer
	Call the fetch_root_cause_cat_resolution_category tool using the Ticket Number.
	Display the response received, showing the Root Cause, Resolution Category, and Resolution Sub-Category.
Step 8: Incident Resolution Recommendation
	Call the fetch_incident_resolution_recommendation tool using the Ticket Number.
	From the response, display the recommended Resolution Steps for the provided Incident/Ticket Number.
"""


# ------------------ FastAPI Startup Event ------------------
@app.on_event("startup")
async def startup_event():
    global mcp_server, agent

    TOOL_URL = "http://localhost:8000/sse"  # MCP SSE server endpoint

    # -------- MCP Client Connection ----------
    mcp_server = MCPServerSse(
        {"url": TOOL_URL},
        client_session_timeout_seconds=300,
        tool_filter=create_static_tool_filter(
            allowed_tool_names=["fetch_incident_details", "fetch_incident_categorisation", "fetch_dq_status", "fetch_priority_update", "fetch_history_rca_reference", "fetch_agent_log_extractor", "fetch_root_cause_cat_resolution_category", "fetch_incident_resolution_recommendation"]
        )
    )
    await mcp_server.connect()

    # -------- LiteLLM Agent Config -----------
    # agent = Agent(
    #     name="Test Agent",
    #     instructions=MASTER_INSTRUCTION,
    #     model=LitellmModel(
    #         model="gpt-4o-mini",
    #         base_url="http://10.170.21.213:20119",  # LiteLLM Gateway URL
    #         api_key="sk-y_eb5RkDq2f1IPKJpb5eLg"      # Replace with secure ENV variable later
    #     ),
    #     mcp_servers=[mcp_server]
    # )

    agent = Agent(name="Assistant", model=model, instructions=MASTER_INSTRUCTION)

    

    print("🚀 MCP Server connected & Agent initialized!")


# ------------------ API Endpoint ------------------
@app.post("/agent-query")
async def agent_query(request: QueryRequest):
    try:
        global agent
        #result = await Runner.run(starting_agent=agent, input=request.msg)
        result = await Runner.run(agent, request.msg)
        return {"user_msg": request.msg, "assistant_response": result.final_output}
    except Exception as e:
        return {"error": str(e)}


# ------------------ FastAPI Shutdown Event ------------------
@app.on_event("shutdown")
async def shutdown_event():
    global mcp_server
    if mcp_server:
        await mcp_server.cleanup()
        print("🛑 MCP Server connection closed")
