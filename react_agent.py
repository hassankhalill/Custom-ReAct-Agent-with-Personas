"""
Custom ReAct Agent Implementation using LangGraph
Building a state-machine based ReAct loop without using pre-built executors
"""

import json
import os
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from tools import TOOL_FUNCTIONS, TOOL_DEFINITIONS


# Load environment variables
load_dotenv()


class AgentState(TypedDict):
    """
    State of the ReAct agent
    """
    messages: Annotated[List, operator.add]  # Conversation history
    thoughts: Annotated[List[str], operator.add]  # Agent's reasoning steps
    actions: Annotated[List[Dict], operator.add]  # Actions taken
    observations: Annotated[List[str], operator.add]  # Observations from tools
    iteration: int  # Current iteration count
    max_iterations: int  # Maximum allowed iterations
    final_answer: Optional[str]  # Final answer to return
    persona_name: str  # Name of the persona being used
    config: Dict[str, Any]  # LLM configuration


class ReActAgent:
    """
    Custom ReAct Agent using LangGraph for state management
    Implements the Thought -> Action -> Observation -> Answer loop
    """

    def __init__(
        self,
        persona_name: str,
        system_prompt: str,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        max_iterations: int = 5
    ):
        """
        Initialize the ReAct agent with a specific persona and configuration

        Args:
            persona_name: Name identifier for the persona
            system_prompt: System prompt defining agent behavior
            model_name: OpenAI model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            top_p: Top-p sampling parameter
            max_iterations: Maximum reasoning iterations
        """
        self.persona_name = persona_name
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations

        # LLM configuration
        self.config = {
            "model_name": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"top_p": top_p}
        )

        # Build the graph
        self.graph = self._build_graph()

        # Logging
        self.interaction_logs = []

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for ReAct loop

        Flow: START -> think -> decide -> [act -> observe -> think] -> respond -> END
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("think", self._think_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("observe", self._observe_node)
        workflow.add_node("respond", self._respond_node)

        # Set entry point
        workflow.set_entry_point("think")

        # Add conditional edges
        workflow.add_conditional_edges(
            "think",
            self._should_act_or_respond,
            {
                "act": "act",
                "respond": "respond",
                "end": END
            }
        )

        workflow.add_edge("act", "observe")
        workflow.add_edge("observe", "think")  # Loop back to think
        workflow.add_edge("respond", END)

        return workflow.compile()

    def _think_node(self, state: AgentState) -> AgentState:
        """
        THINK: Agent reasons about what to do next
        """
        print(f"\n[{self.persona_name}] THINKING (Iteration {state['iteration']})...")

        # Build messages for the LLM with limited context to avoid token limits
        messages = [SystemMessage(content=self.system_prompt)]

        # Only include the original user message to save tokens
        if state["messages"]:
            messages.append(state["messages"][0])  # Original user query

        # Add summarized reasoning context (only recent iterations)
        if state["thoughts"]:
            reasoning_context = "\n\nRecent findings:\n"
            # Only use last 2 iterations to save tokens
            recent_thoughts = state["thoughts"][-2:]
            recent_obs = state["observations"][-2:]
            for i, (thought, obs) in enumerate(zip(recent_thoughts, recent_obs), 1):
                # Truncate long content
                thought_short = thought[:150] + "..." if len(thought) > 150 else thought
                obs_short = obs[:250] + "..." if len(obs) > 250 else obs
                reasoning_context += f"\nStep {i}: {thought_short}\nData: {obs_short}\n"
            messages.append(HumanMessage(content=reasoning_context))

        # Get the model's response
        response = self.llm.invoke(messages)

        # Extract the thought
        thought = response.content

        # Update state
        state["thoughts"].append(thought)
        state["messages"].append(AIMessage(content=thought))

        print(f"Thought: {thought[:200]}...")

        return state

    def _should_act_or_respond(self, state: AgentState) -> str:
        """
        DECIDE: Determine if we should take an action or respond to user
        """
        # Check if we've hit max iterations
        if state["iteration"] >= state["max_iterations"]:
            print(f"[{self.persona_name}] Max iterations reached. Responding with current knowledge.")
            return "respond"

        # Check if the last thought indicates we need to use a tool
        last_thought = state["thoughts"][-1] if state["thoughts"] else ""

        # Look for action indicators in the thought
        # Check if the thought mentions any tool names or action keywords
        action_keywords = [
            "search", "check", "get", "record", "look up", "find",
            "tool", "function", "call", "need to", "should use"
        ]

        tool_names = [tool["name"] for tool in TOOL_DEFINITIONS]

        last_thought_lower = last_thought.lower()

        # Check for tool mentions
        for tool_name in tool_names:
            if tool_name in last_thought_lower:
                print(f"[{self.persona_name}] Decision: ACT (tool '{tool_name}' mentioned)")
                return "act"

        # Check for action keywords
        for keyword in action_keywords:
            if keyword in last_thought_lower:
                print(f"[{self.persona_name}] Decision: ACT (keyword '{keyword}' found)")
                return "act"

        # Check if thought indicates we have enough info to answer
        answer_keywords = [
            "answer:", "response:", "i can tell", "i know that",
            "based on", "the answer is", "i would say"
        ]

        for keyword in answer_keywords:
            if keyword in last_thought_lower:
                print(f"[{self.persona_name}] Decision: RESPOND (answer keyword found)")
                return "respond"

        # Default: if we have observations, respond; otherwise act
        if state["observations"]:
            print(f"[{self.persona_name}] Decision: RESPOND (have observations)")
            return "respond"
        else:
            print(f"[{self.persona_name}] Decision: ACT (need more information)")
            return "act"

    def _act_node(self, state: AgentState) -> AgentState:
        """
        ACT: Execute a tool based on the thought
        """
        print(f"\n[{self.persona_name}] ACTING...")

        # Parse the last thought to determine which tool to call
        last_thought = state["thoughts"][-1]

        # Try to extract tool name and parameters from the thought
        # This is a simple parser - in production you'd want more robust parsing
        action = self._parse_action_from_thought(last_thought)

        if action:
            state["actions"].append(action)
            print(f"Action: {action['tool']}({action['parameters']})")
        else:
            # If we can't parse an action, use a default
            print(f"[{self.persona_name}] Could not parse action, using default search")
            action = {
                "tool": "search_services",
                "parameters": {"query": "all services"}
            }
            state["actions"].append(action)

        return state

    def _observe_node(self, state: AgentState) -> AgentState:
        """
        OBSERVE: Get the result from the tool execution
        """
        print(f"\n[{self.persona_name}] OBSERVING...")

        # Get the last action
        last_action = state["actions"][-1]

        # Execute the tool
        tool_name = last_action["tool"]
        parameters = last_action["parameters"]

        try:
            tool_function = TOOL_FUNCTIONS[tool_name]
            result = tool_function(**parameters)
            # Truncate result to avoid token overflow
            result_str = str(result)
            if len(result_str) > 500:
                result_str = result_str[:500] + "... (truncated)"
            observation = f"Tool '{tool_name}' returned: {result_str}"
        except Exception as e:
            observation = f"Error executing tool '{tool_name}': {str(e)}"

        # Update state with truncated observation
        state["observations"].append(observation)
        # Don't add to messages at all - we'll use observations directly in think node
        # state["messages"].append(AIMessage(content=f"Observation: {observation}"))

        print(f"Observation: {observation[:200]}...")

        # Increment iteration
        state["iteration"] += 1

        return state

    def _respond_node(self, state: AgentState) -> AgentState:
        """
        RESPOND: Generate final answer based on thoughts and observations
        """
        print(f"\n[{self.persona_name}] RESPONDING...")

        # Build concise context summary to avoid token limits
        context = "Based on the information gathered, provide a complete answer.\n\n"

        # Only include key findings, not full history
        if state["observations"]:
            context += "Key findings:\n"
            # Only last observation or summary
            last_obs = state["observations"][-1]
            context += last_obs[:400] + "..." if len(last_obs) > 400 else last_obs

        context += "\n\nProvide a helpful, friendly answer to the user's question."

        # Get final response with minimal context
        messages = [SystemMessage(content=self.system_prompt)]
        # Only original query
        if state["messages"]:
            messages.append(state["messages"][0])
        messages.append(HumanMessage(content=context))

        response = self.llm.invoke(messages)
        final_answer = response.content

        state["final_answer"] = final_answer
        state["messages"].append(AIMessage(content=final_answer))

        print(f"Final Answer: {final_answer[:200]}...")

        return state

    def _parse_action_from_thought(self, thought: str) -> Optional[Dict[str, Any]]:
        """
        Parse action from the agent's thought
        This is a simple heuristic-based parser
        """
        thought_lower = thought.lower()

        # Check for search_services
        if "search" in thought_lower and ("service" in thought_lower or "cleaning" in thought_lower):
            # Extract query
            query = "all services"
            if "allergen" in thought_lower or "allergy" in thought_lower:
                query = "allergen"
            elif "move" in thought_lower:
                query = "move"
            elif "maintenance" in thought_lower or "regular" in thought_lower:
                query = "regular maintenance"
            elif "deep clean" in thought_lower:
                query = "deep cleaning"

            return {
                "tool": "search_services",
                "parameters": {"query": query}
            }

        # Check for check_availability
        if "check" in thought_lower and ("availability" in thought_lower or "location" in thought_lower or "area" in thought_lower):
            # Try to extract location
            location = "downtown"  # default
            for area in ["downtown", "northside", "westend", "eastbridge", "southgate", "riverside", "hilltop", "lakeside"]:
                if area in thought_lower:
                    location = area
                    break

            return {
                "tool": "check_availability",
                "parameters": {"location": location}
            }

        # Check for get_product_info
        if "product" in thought_lower or "ingredient" in thought_lower or "chemical" in thought_lower:
            category = "all"
            if "bathroom" in thought_lower:
                category = "bathroom"
            elif "floor" in thought_lower:
                category = "floor"
            elif "glass" in thought_lower or "window" in thought_lower:
                category = "glass"
            elif "all-purpose" in thought_lower or "all purpose" in thought_lower:
                category = "all_purpose"

            return {
                "tool": "get_product_info",
                "parameters": {"product_category": category}
            }

        # Check for record_customer_interest
        if "record" in thought_lower and ("interest" in thought_lower or "lead" in thought_lower or "contact" in thought_lower):
            # This would need more sophisticated parsing to extract name, email, message
            # For now, we'll skip auto-parsing this and let manual invocation handle it
            return None

        # Check for record_feedback
        if "record" in thought_lower and "feedback" in thought_lower:
            return None

        # Default: search for services
        return {
            "tool": "search_services",
            "parameters": {"query": "all services"}
        }

    def run(self, user_message: str) -> str:
        """
        Run the ReAct agent on a user message

        Args:
            user_message: The user's input message

        Returns:
            The agent's final response
        """
        print(f"\n{'='*80}")
        print(f"RUNNING REACT AGENT: {self.persona_name}")
        print(f"Configuration: {self.config}")
        print(f"{'='*80}")
        print(f"User: {user_message}")

        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=user_message)],
            thoughts=[],
            actions=[],
            observations=[],
            iteration=0,
            max_iterations=self.max_iterations,
            final_answer=None,
            persona_name=self.persona_name,
            config=self.config
        )

        # Log the interaction
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "persona": self.persona_name,
            "config": self.config,
            "user_message": user_message,
            "start_time": datetime.now()
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        # Complete log entry
        log_entry["end_time"] = datetime.now()
        log_entry["duration"] = (log_entry["end_time"] - log_entry["start_time"]).total_seconds()
        log_entry["thoughts"] = final_state["thoughts"]
        log_entry["actions"] = final_state["actions"]
        log_entry["observations"] = final_state["observations"]
        log_entry["final_answer"] = final_state["final_answer"]
        log_entry["iterations"] = final_state["iteration"]

        self.interaction_logs.append(log_entry)

        print(f"\n{'='*80}")
        print(f"AGENT RESPONSE COMPLETE")
        print(f"{'='*80}\n")

        return final_state["final_answer"]

    def get_logs(self) -> List[Dict]:
        """Return interaction logs"""
        return self.interaction_logs

    def save_logs(self, filepath: str = "agent_logs.json"):
        """Save logs to file"""
        # Convert datetime objects to strings
        logs_serializable = []
        for log in self.interaction_logs:
            log_copy = log.copy()
            log_copy["start_time"] = log_copy["start_time"].isoformat()
            log_copy["end_time"] = log_copy["end_time"].isoformat()
            logs_serializable.append(log_copy)

        with open(filepath, 'w') as f:
            json.dump(logs_serializable, f, indent=2)

        print(f"Logs saved to {filepath}")
