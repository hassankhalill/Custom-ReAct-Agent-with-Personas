"""
Gradio App for BreatheEasy ReAct Agent
Standalone deployment interface
"""

import gradio as gr
import os
from dotenv import load_dotenv

from react_agent import ReActAgent
from personas import get_persona, PERSONAS

# Load environment variables
load_dotenv()

# Global agent instance
current_agent = None
current_config = {"persona": None, "temperature": None, "model": None}


def create_agent(persona_key, temperature, model_name):
    """Create agent with selected configuration"""
    global current_agent, current_config

    try:
        persona_config = get_persona(persona_key)
        current_agent = ReActAgent(
            persona_name=persona_config["name"],
            system_prompt=persona_config["system_prompt"],
            model_name=model_name,
            temperature=temperature
        )

        current_config = {
            "persona": persona_config["name"],
            "temperature": temperature,
            "model": model_name
        }

        return f"✓ Agent created successfully!\n\nPersona: {persona_config['name']}\nModel: {model_name}\nTemperature: {temperature}"

    except Exception as e:
        return f"❌ Error creating agent: {str(e)}"


def chat(message, history):
    """Chat with the agent"""
    global current_agent

    if current_agent is None:
        return "⚠️ Please create an agent first by selecting a persona and clicking 'Create Agent'"

    try:
        response = current_agent.run(message)
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try again or create a new agent."


def get_agent_info():
    """Get current agent information"""
    global current_config

    if current_config["persona"] is None:
        return "No agent created yet"

    return f"""
**Current Agent:**
- Persona: {current_config['persona']}
- Model: {current_config['model']}
- Temperature: {current_config['temperature']}
"""


# Custom CSS
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}
"""

# Build interface
with gr.Blocks(title="BreatheEasy ReAct Agent", css=custom_css) as demo:

    # Header
    gr.Markdown("""
    <div class="header">
        <h1>🌿 BreatheEasy ReAct Agent</h1>
        <p>Custom ReAct Agent with Multiple Personas - Assignment 4</p>
        <p><em>Hassan Khalil | EECE 503P</em></p>
    </div>
    """)

    gr.Markdown("""
    ## About This Agent

    This is a custom **ReAct (Reasoning and Acting)** agent built with **LangGraph** for BreatheEasy,
    an eco-friendly home cleaning service. The agent can:

    - Answer questions about cleaning services and products
    - Help with allergy-safe cleaning solutions
    - Check service availability in your area
    - Collect customer information for scheduling

    The agent uses a manual ReAct loop: **Think → Decide → Act → Observe → Respond**

    ---
    """)

    with gr.Row():
        # Left column - Configuration
        with gr.Column(scale=1):
            gr.Markdown("### 🎭 Agent Configuration")

            persona_dropdown = gr.Dropdown(
                choices=[
                    ("Friendly Wellness Advisor (Zero-Shot)", "friendly_zero_shot"),
                    ("Friendly Wellness Advisor (Few-Shot)", "friendly_few_shot"),
                    ("Friendly Wellness Advisor (Chain-of-Thought)", "friendly_cot"),
                    ("Professional Health Expert (Zero-Shot)", "expert_zero_shot"),
                    ("Professional Health Expert (Few-Shot)", "expert_few_shot"),
                    ("Professional Health Expert (Chain-of-Thought)", "expert_cot"),
                    ("Cautious Service Guide (Zero-Shot)", "cautious_zero_shot"),
                    ("Cautious Service Guide (Few-Shot)", "cautious_few_shot"),
                    ("Cautious Service Guide (Chain-of-Thought)", "cautious_cot"),
                ],
                value="friendly_few_shot",
                label="Persona & Prompt Type",
                info="Choose the agent's personality and reasoning style"
            )

            with gr.Accordion("Persona Descriptions", open=False):
                gr.Markdown("""
                **Friendly Wellness Advisor:**
                - Warm, empathetic, conversational
                - Focuses on health and wellness benefits
                - Great for customers with health concerns

                **Professional Health Expert:**
                - Scientific, technical, authoritative
                - References certifications and research
                - Best for detailed technical questions

                **Cautious Service Guide:**
                - Careful, thorough, detail-oriented
                - Asks clarifying questions
                - Ensures realistic expectations

                **Prompt Types:**
                - *Zero-Shot:* Basic instructions
                - *Few-Shot:* Includes example patterns
                - *Chain-of-Thought:* Explicit step-by-step reasoning
                """)

            temperature_slider = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.1,
                label="Temperature",
                info="0 = Focused & Consistent | 1 = Creative & Varied"
            )

            model_dropdown = gr.Dropdown(
                choices=["gpt-4o-mini", "gpt-4o"],
                value="gpt-4o-mini",
                label="Model",
                info="gpt-4o-mini is faster and cheaper"
            )

            create_btn = gr.Button("🚀 Create Agent", variant="primary", size="lg")

            status = gr.Textbox(
                label="Status",
                interactive=False,
                lines=5
            )

            create_btn.click(
                fn=create_agent,
                inputs=[persona_dropdown, temperature_slider, model_dropdown],
                outputs=status
            )

        # Right column - Chat
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat with Agent")

            chatbot = gr.ChatInterface(
                fn=chat,
                examples=[
                    "What services do you offer?",
                    "I have severe allergies to dust and pet dander. Can you help me?",
                    "What cleaning products do you use? I'm worried about harsh chemicals.",
                    "Do you service the downtown area?",
                    "I'd like to schedule a deep cleaning for next week",
                    "Tell me about your allergy-safe protocols"
                ],
                title=None,
                description="Ask me anything about BreatheEasy's services!",
                submit_btn="Send",
                retry_btn="🔄 Retry",
                undo_btn="↩️ Undo",
                clear_btn="🗑️ Clear"
            )

    # Footer
    gr.Markdown("""
    ---

    ### 🧪 About the ReAct Implementation

    This agent uses a custom ReAct loop implemented with LangGraph:

    1. **THINK**: Agent reasons about the user's question
    2. **DECIDE**: Determines whether to use a tool or respond directly
    3. **ACT**: Executes tools (search services, check availability, get product info, etc.)
    4. **OBSERVE**: Processes tool results
    5. **RESPOND**: Provides final answer to user

    **Available Tools:**
    - `search_services` - Find cleaning services
    - `check_availability` - Check service areas
    - `get_product_info` - Get product details
    - `record_customer_interest` - Collect leads
    - `record_feedback` - Log questions

    ---

    **Assignment 4 - EECE 503P | Fall 2025-26**
    """)


if __name__ == "__main__":
    print("Starting BreatheEasy ReAct Agent...")
    print("="*60)

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment!")
        print("Please set your API key in the .env file")
    else:
        print("✓ API Key loaded")

    print("✓ Launching Gradio interface...")
    print("="*60)

    demo.launch(
        share=True,  # Create public link
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        show_error=True
    )
