import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from typing import Annotated, List
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_mcp_adapters.tools import load_mcp_tools
import os
import sys
from dotenv import load_dotenv 
import shlex

load_dotenv("./server/.env")
# MCP server launch config
server_params = StdioServerParameters(
    command="python",
    args=["server/weather-server.py"]
)

# LangGraph state definition
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


async def create_graph(session: ClientSession) :
    # Load tools from MCP server
    tools = await load_mcp_tools(session)

    # LLM configuration 
    llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.1,
    api_key=os.getenv('GEMINI_API_KEY')
    )
    
    llm_with_tools = llm.bind_tools(tools)

    # Prompt template with user/assistant chat only
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Donot use inbuilt tool to get data. use only mcp porvidede injected tools that uses tools to get the current weather for a location."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    # Define chat node
    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    # Build LangGraph with tool routing
    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition, {
        "tools": "tool_node",
        "__end__": END
    })
    graph.add_edge("tool_node", "chat_node")

    return graph.compile()

async def list_prompts(session: ClientSession):
    """List available prompts from the MCP server."""
    try:
        prompts_result_from_server = await session.list_prompts()
        if not prompts_result_from_server or not prompts_result_from_server.prompts:
            print("No prompts available from the server.")
            
        # format prompts for display along with their descriptions and arguments
        prompts = []
        print("Available prompts:")
        for prompt in prompts_result_from_server.prompts:
            prompt_info = {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": {arg.name for arg in prompt.arguments}
            }
            print(prompt_info)
            prompts.append(prompt_info)
        
        return
        
    except Exception as e:
        print(f"Error listing prompts: {e}")

async def handle_prompt_selection(session: ClientSession, user_command: str)->str | None:
    """Parse user command to invoke a prompt from the MCP server and get the generated prompt text."""
    try:
        parts = shlex.split(user_command)
        if len(parts) < 2:
            print("Invalid command format. Use: use_prompt <prompt_name> [arg1=value1 arg2=value2 ...]")
            return None

        prompt_name = parts[1]
        user_args = parts[2:]

         # Get available prompts from the server to validate against
        prompt_def_response = await session.list_prompts()
        if not prompt_def_response or not prompt_def_response.prompts:
            print("\nError: Could not retrieve any prompts from the server.")
            return None
        
        # Find the specific prompt definition the user is asking for
        prompt_def = next((p for p in prompt_def_response.prompts if p.name == prompt_name), None)

        if not prompt_def:
            print(f"\nError: Prompt '{prompt_name}' not found on the server.")
            return None

        # Check if the number of user-provided arguments matches what the prompt expects
        if len(user_args) != len(prompt_def.arguments):
            expected_args = [arg.name for arg in prompt_def.arguments]
            print(f"\nError: Invalid number of arguments for prompt '{prompt_name}'.")
            print(f"Expected {len(expected_args)} arguments: {', '.join(expected_args)}")
            return None
        
        # Build the argument dictionary
        arg_dict = {arg.name: val for arg, val in zip(prompt_def.arguments, user_args)}
      
        prompt_response = await session.get_prompt(prompt_name, arg_dict)
        print(prompt_response)
        prompt_text = prompt_response.messages[0].content.text
        print('Generated the prompt text successfully...piping it to the agent now.')
        return prompt_text
    except Exception as e:
        print(f"Error handling prompt selection: {e}")
        return None



# Entry point
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            agent = await create_graph(session)
            
            print("Weather MCP agent is ready.")
             
            print("Type a question, or use one of the following commands:")
            print("  /prompts                           - to list available prompts")
            print("  /prompt <prompt_name> \"args\"...  - to run a specific prompt")

            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break
                  
                try:
                    message_to_agent = ""  
                    if user_input.lower() == "/prompts":
                        await list_prompts(session)
                        continue
                    elif user_input.lower().startswith("/prompt"):
                        message_to_agent = await handle_prompt_selection(session, user_input)
                    else:
                        message_to_agent = user_input

                    if not message_to_agent:
                        continue    
                    response = await agent.ainvoke(
                        {"messages": user_input},
                        
                        # config={"configurable": {"thread_id": "weather-session"}}
                    )
                    print("AI:", response["messages"][-1].content)
                except Exception as e:
                    print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
