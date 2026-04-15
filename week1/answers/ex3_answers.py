"""
Exercise 3 — Answers
====================
Fill this in after completing the three Rasa conversations.
"""

# ── Conversation 1: Happy path ─────────────────────────────────────────────

CONVERSATION_1_TRACE = """
Your input ->  I'm calling to confirm a booking for tonight
How many guests are you confirming for tonight's event?
Your input ->  160 guests
And how many of those guests will need vegan meals?
Your input ->  about 50 need vegan
(WARNING: CompactLLMCommandGenerator.parse_commands - No commands were parsed
 from the LLM actions. Qwen3 thinking tokens confused the command parser.)
I'm sorry I am unable to understand you, could you please rephrase?
And how many of those guests will need vegan meals?
Your input ->  about 50 need vegan
(Provider List warnings from LiteLLM retry loop)
What deposit amount in GBP are you proposing to secure the booking?
Your input ->  200 pound deposit
Thank you — booking confirmed. 160 guests, 50 requiring vegan meals,
£200 deposit accepted. I'll send written confirmation to the organiser shortly.
"""

CONVERSATION_1_OUTCOME = "confirmed"

# ── Conversation 2: Deposit too high ───────────────────────────────────────

CONVERSATION_2_TRACE = """
Your input ->  calling to confirm a booking
How many guests are you confirming for tonight's event?
Your input ->  160 guests
(Provider List warnings from LiteLLM retry loop)
And how many of those guests will need vegan meals?
Your input ->  40 vegan
What deposit amount in GBP are you proposing to secure the booking?
Your input ->  500 pound deposit
I need to check one thing with the organiser before I can confirm.
The issue is: a deposit of £500 exceeds the organiser's authorised limit of £300.
Can I call you back within 15 minutes?
"""

CONVERSATION_2_OUTCOME = "escalated"
CONVERSATION_2_REASON  = "a deposit of £500 exceeds the organiser's authorised limit of £300"

# ── Conversation 3: Out of scope ───────────────────────────────────────────

CONVERSATION_3_TRACE = """
Your input ->  calling about tonight's booking
How many guests are you confirming for tonight's event?
Your input ->  can you arrange parking for the speakers?
I can only help with confirming tonight's venue booking.
For anything else, please contact the event organiser directly.
Would you like to continue with confirm booking?
"""

# Describe what CALM did after the out-of-scope message. Min 20 words.
CONVERSATION_3_WHAT_HAPPENED = """
CALM caught that parking was out of scope. It responded with the utter_out_of_scope
message from flows.yml, said it can only help with venue booking, and offered to
continue where we left off. Did not crash or lose the conversation state.
"""

# Compare Rasa CALM's handling of the out-of-scope request to what
# LangGraph did in Exercise 2 Scenario 3. Min 40 words.
OUT_OF_SCOPE_COMPARISON = """
Very different. In Exercise 2 Scenario 3, LangGraph was asked about train times.
It said it could not help, suggested National Rail and Trainline, and that was it.
The conversation ended there. No way to go back to whatever you were doing before.

CALM caught the parking question, said it can only help with booking, and offered
to continue where we left off. The guest_count was still pending and the agent
picked right back up. That is because CALM has explicit flows with steps, so it
can pause for a digression and resume. LangGraph is just one reasoning loop, so
once it answers, it is done.

For a booking confirmation call, CALM is clearly better here. You do not want the
agent to wander off topic and never come back.
"""

# ── Task B: Cutoff guard ───────────────────────────────────────────────────

TASK_B_DONE = True

# List every file you changed.
TASK_B_FILES_CHANGED = ["exercise3_rasa/actions/actions.py"]

# How did you test that it works? Min 20 words.
TASK_B_HOW_YOU_TESTED = """
Uncommented the four lines in actions.py. Got an IndentationError first (tabs vs
spaces), fixed that. Then changed the condition to 'if True:' to force it to fire.
Restarted the action server, ran a conversation with 160 guests, 40 vegan, 200
deposit. The agent escalated right away with the 16:45 deadline message instead of
confirming. Reverted back to the real datetime check after.
"""

# ── CALM vs Old Rasa ───────────────────────────────────────────────────────

CALM_VS_OLD_RASA = """
Old Rasa needed regex to turn 'about 160 people' into 160.0, plus nlu.yml
for intent examples and rules.yml for every dialogue path. A lot of manual
work just to handle natural speech.

CALM hands all of that to the LLM. The from_llm slot mappings in domain.yml
handle 'about 50 need vegan' or '500 pound deposit' without any regex. Python
only runs the business rules after the slots are filled.

The trade-off showed up in my first conversation. Qwen3 emitted thinking tokens
that confused the CALM command parser, and I got 'No commands were parsed from
the LLM actions.' Had to repeat myself. Old Rasa regex would have either matched
or not, no ambiguity. So you gain flexibility in how people phrase things, but
you lose the determinism in the parsing layer.
"""

# ── The setup cost ─────────────────────────────────────────────────────────

SETUP_COST_VALUE = """
CALM needs config.yml, domain.yml, flows.yml, endpoints.yml, rasa train, two
terminals, and a licence. That is a lot more setup than LangGraph, which was
just a few lines of Python with create_react_agent().

But the setup bought something real: the CALM agent cannot improvise. It cannot
call a tool outside flows.yml. It cannot skip collecting guest_count or vegan_count.
When I asked about parking, it bounced me back to the booking flow. When the deposit
was £500, the Python guard caught it, not the LLM.

A LangGraph agent would have no flow to return to after a digression. It might also
reason around a deposit limit if the prompt did not explicitly forbid it. For a
booking confirmation where money is on the line, the inability to improvise is
exactly what you want. The setup cost buys auditability.
"""
