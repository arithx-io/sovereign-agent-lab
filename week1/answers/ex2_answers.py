"""
Exercise 2 — Answers
====================
Fill this in after running exercise2_langgraph.py.
Run `python grade.py ex2` to check for obvious issues.
"""

# ── Task A ─────────────────────────────────────────────────────────────────

# List of tool names called during Task A, in order of first appearance.

TASK_A_TOOLS_CALLED = [
    "check_pub_availability",
    "calculate_catering_cost",
    "get_edinburgh_weather",
    "generate_event_flyer",
]

# Which venue did the agent confirm? Must be one of:
# "The Albanach", "The Haymarket Vaults", or "none"
TASK_A_CONFIRMED_VENUE = "The Albanach"

# Total catering cost the agent calculated. Float, e.g. 5600.0
TASK_A_CATERING_COST_GBP = 5600.0

# Did the weather tool return outdoor_ok = True or False?
TASK_A_OUTDOOR_OK = True

# Optional — anything unexpected.
TASK_A_NOTES = "Used default Qwen/Qwen3-32B. The agent checked both The Albanach and The Haymarket Vaults — both met all constraints — but chose The Albanach for the flyer without comparing the two."

# ── Task B ─────────────────────────────────────────────────────────────────

TASK_B_IMPLEMENTED = True

TASK_B_MODE = "placeholder"

TASK_B_IMAGE_URL = "https://placehold.co/1200x628/1a1a2e/eaeaea?text=The+Haymarket+Vaults+%7C+160+guests&id=2ef939fbbaf6"

TASK_B_PROMPT_USED = "Professional event flyer for Edinburgh AI Meetup, tech professionals, modern venue at The Haymarket Vaults, Edinburgh. 160 guests tonight. Warm lighting, Scottish architecture background, clean modern typography."

TASK_B_WHY_AGENT_SURVIVED = """
The generate_event_flyer tool returns a structured success=True response with a
deterministic placeholder URL when no live image provider is configured, so the
agent's ReAct loop receives the same contract (success, prompt_used, image_url)
regardless of whether the underlying provider exists. The tool's graceful fallback
kept the agent's control flow intact.
"""

# ── Task C ─────────────────────────────────────────────────────────────────

# Scenario 1: first choice unavailable
# Quote the specific message where the agent changed course. Min 20 words.
SCENARIO_1_PIVOT_MOMENT = """
The agent's thinking trace after The Bow Bar returned meets_all_constraints=false
stated: "The Bow Bar's capacity is only 80, which is too small. So, they moved on
to check The Haymarket Vaults." The next action was immediately
[TOOL_CALL] check_pub_availability({"pub_name": "The Haymarket Vaults",
"required_capacity": 160, "requires_vegan": true}) — the pivot happened at the
second tool call with no human intervention.
"""

SCENARIO_1_FALLBACK_VENUE = "The Haymarket Vaults"

# Scenario 2: impossible constraint (300 guests)
SCENARIO_2_HALLUCINATED = False

# Paste the final [AI] message.
SCENARIO_2_FINAL_ANSWER = """
None of the known Edinburgh venues can accommodate 300 people with vegan options.
The maximum capacity among the checked venues is 200 (The Guilford Arms) but it
lacks vegan options, while venues with vegan options (The Albanach, Haymarket
Vaults, Bow Bar) have capacities of 180, 160, and 80 respectively. You may need
to consider alternative venues outside this list or adjust your requirements.
"""

# Scenario 3: out of scope (train times)
SCENARIO_3_TRIED_A_TOOL = False

SCENARIO_3_RESPONSE = "I don't have access to real-time train schedules or transportation data. For the most accurate information about the last train from Edinburgh Waverley to London, I recommend checking: 1. The National Rail website (https://www.nationalrail.co.uk) 2. Train service apps like Citymapper or Trainline 3. The specific train operator's website (e.g., LNER). Would you like help with anything related to Edinburgh pubs, weather, or event planning instead?"

# Would this behaviour be acceptable in a real booking assistant? Min 30 words.
SCENARIO_3_ACCEPTABLE = """
This behaviour is acceptable and desirable. The agent correctly identified that
train times are outside its tool set and did not attempt to hallucinate an answer
or misuse an unrelated tool. It suggested specific alternatives (National Rail,
Trainline, LNER) and then redirected to its actual capabilities. An agent that
admits its boundaries is safer than one that confidently fabricates train times.
"""

# ── Task D ─────────────────────────────────────────────────────────────────

TASK_D_MERMAID_OUTPUT = """
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	agent(agent)
	tools(tools)
	__end__([<p>__end__</p>]):::last
	__start__ --> agent;
	agent -.-> __end__;
	agent -.-> tools;
	tools --> agent;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
"""

# Compare the LangGraph graph to exercise3_rasa/data/flows.yml. Min 30 words.
TASK_D_COMPARISON = """
The LangGraph Mermaid graph shows a single generic loop: start -> agent -> tools ->
agent -> end. The agent node decides everything at runtime — which tool to call, in
what order, when to stop. All routing is implicit in the LLM's reasoning.

Rasa CALM's flows.yml defines two explicit flows (confirm_booking and
handle_out_of_scope). confirm_booking has four named steps: collect guest_count,
collect vegan_count, collect deposit_amount_gbp, then action_validate_booking.
The LLM only decides which flow to start — after that, Rasa executes the steps
deterministically.

LangGraph gives flexibility but unpredictability. Rasa gives auditability but
rigidity. For open-ended research, the flexible loop is essential. For a booking
confirmation where every word has financial consequences, the explicit flow is safer.
"""

# ── Reflection ─────────────────────────────────────────────────────────────

# The most unexpected thing the agent did. Min 40 words.
# Must reference a specific behaviour from your run.

MOST_SURPRISING = """
What stood out to me most was Task A. The agent checked both The Albanach
and The Haymarket Vaults, and both passed the constraints. Albanach had
capacity 180. Haymarket had exactly 160. But once it saw Albanach worked, it
more or less stopped comparing. The trace literally says "The Albanach was
chosen for the flyer," and that was enough for it to keep moving. No
explanation of why Albanach was better for this case, no discussion of
whether the extra 20 seats mattered, nothing.

The full sequence made that even clearer. It called check_pub_availability
twice, then calculate_catering_cost and got £5600, then
get_edinburgh_weather and got 11.8°C, partly cloudy, outdoor_ok true, then
generate_event_flyer and got a placeholder result. Five calls, one pass,
zero human steering. The agent figured out the order itself and executed it
cleanly.

That is what surprised me: it was genuinely autonomous, but it was optimizing
for "good enough" rather than "best". It found a workable answer and kept
going. In a real booking workflow that is risky, because the first acceptable
venue can become the final venue without any real comparison step.
"""
