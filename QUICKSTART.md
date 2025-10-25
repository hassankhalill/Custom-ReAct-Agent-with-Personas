# Quick Start Guide

**Assignment 4: Custom ReAct Agent with Personas**

Get up and running in 5 minutes!

---

## ⚡ Quick Start

### 1. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key (1 minute)

The `.env` file is already configured with your API key:
```
OPENAI_API_KEY=sk-proj-gHmNkdTi...
```

### 3. Choose Your Path

#### Option A: Interactive Notebook (Recommended)

```bash
jupyter notebook react_agent_assignment.ipynb
```

Then run all cells to:
- ✅ See the complete implementation
- ✅ Test individual components
- ✅ Compare personas side-by-side
- ✅ Run experiments
- ✅ Launch interactive interface

**Time:** 30 minutes to explore

---

#### Option B: Quick Demo with Gradio

```bash
python app.py
```

Opens a web interface where you can:
- ✅ Select personas and configurations
- ✅ Chat with the agent in real-time
- ✅ Test different settings instantly

**Time:** 5 minutes to try

---

#### Option C: Run Experiments

```bash
python experiment_runner.py
```

Runs comprehensive testing suite:
- ✅ Tests all 9 persona variants
- ✅ Compares temperatures and models
- ✅ Generates comparison tables
- ✅ Saves detailed logs

**Time:** 10-15 minutes (automated)

---

#### Option D: Direct Python Usage

```python
from react_agent import ReActAgent
from personas import get_persona

# Create agent
persona = get_persona("friendly_few_shot")
agent = ReActAgent(
    persona_name=persona["name"],
    system_prompt=persona["system_prompt"],
    model_name="gpt-4o-mini",
    temperature=0.7
)

# Run query
response = agent.run("What services do you offer?")
print(response)
```

**Time:** 2 minutes

---

## 📁 File Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `react_agent_assignment.ipynb` | Complete walkthrough | Start here! |
| `app.py` | Web interface | Quick demo |
| `experiment_runner.py` | Run all tests | Reproduce results |
| `tools.py` | Business tools | Reference |
| `react_agent.py` | Core ReAct logic | Implementation details |
| `personas.py` | Persona definitions | See prompts |

---

## 🎯 Key Features to Try

### 1. Compare Personas

In the notebook, run the "Persona Comparison" section to see how Friendly, Expert, and Cautious personas respond differently to the same query.

### 2. Test Prompt Engineering

Compare Zero-Shot vs Few-Shot vs Chain-of-Thought prompting to see the differences in reasoning quality.

### 3. Experiment with Temperature

Try the same query at temperatures 0.3, 0.7, and 1.0 to see creativity vs consistency trade-offs.

### 4. Watch the ReAct Loop

Enable verbose logging to see the agent's thought process:
```python
agent.run("What services do you offer?")
# Prints:
# [THINKING]...
# [ACTING]...
# [OBSERVING]...
# [RESPONDING]...
```

---

## 🐛 Troubleshooting

### API Key Error
```
Error: OpenAI API key not found
```
**Fix:** Check that `.env` file exists and contains your key

### Import Error
```
ModuleNotFoundError: No module named 'langgraph'
```
**Fix:** Run `pip install -r requirements.txt`

### Port Already in Use (Gradio)
```
Error: Address already in use
```
**Fix:** Change port in `app.py`: `demo.launch(server_port=7861)`

---

## 💡 Example Queries

Try these with the agent:

**Service Questions:**
- "What services do you offer?"
- "What's the difference between deep cleaning and regular maintenance?"

**Health/Allergy Concerns:**
- "I have severe allergies. Can you help?"
- "Are your products safe for kids?"
- "I'm allergic to dust and pet dander. What do you recommend?"

**Product Information:**
- "What cleaning products do you use?"
- "Are your products eco-friendly?"
- "Can I see ingredient lists?"

**Service Areas:**
- "Do you service the downtown area?"
- "What areas do you cover?"

**Booking:**
- "I'd like to schedule a cleaning"
- "How do I book a service?"

---

## 📊 Understanding Results

After running experiments, check:

1. **experiment_results/comparison_table.csv** - Quick metrics overview
2. **experiment_results/experiment_*.json** - Detailed logs per experiment
3. **customer_leads.json** - Any leads collected during testing
4. **customer_feedback.json** - Unanswered questions logged

---

## 🎓 Learning Path

1. **Start:** Open notebook, read through implementation
2. **Understand:** Run individual cells, see how components work
3. **Experiment:** Try different personas and configurations
4. **Analyze:** Run experiment suite, compare results
5. **Read:** Review README.md and REFLECTION.md for insights

---

## 📝 What to Submit

For the assignment, ensure you have:

- ✅ `react_agent_assignment.ipynb` - Complete and runnable
- ✅ `README.md` - Project documentation
- ✅ `REFLECTION.md` - Answers to reflection questions
- ✅ All Python files (`tools.py`, `react_agent.py`, `personas.py`, etc.)
- ✅ `requirements.txt` - Dependencies
- ✅ `business_data/` - Business information files

**Do NOT submit:**
- ❌ `.env` file (contains API key)
- ❌ `experiment_results/` (too large, can be regenerated)
- ❌ `customer_leads.json`, `customer_feedback.json` (generated files)

---

## 🚀 Next Steps

After completing the basic requirements:

1. **Optional:** Deploy to HuggingFace Spaces
2. **Optional:** Create a video demo
3. **Optional:** Add more personas or tools
4. **Optional:** Improve action parsing with function calling API

---

## ❓ Questions?

Refer to:
- `README.md` - Full documentation
- `REFLECTION.md` - Implementation insights
- Code comments - Detailed explanations

---

**Time to complete assignment:** 2-3 hours
- Implementation: Already done ✅
- Testing: 30 minutes
- Documentation review: 30 minutes
- Final checks: 30 minutes

**Good luck!** 🌿
