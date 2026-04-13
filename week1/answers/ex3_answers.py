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
When I asked about parking mid-flow, CALM recognised that the request was outside
the scope of the booking confirmation flow. It triggered the handle_out_of_scope
flow defined in flows.yml, which responded with the utter_out_of_scope message:
'I can only help with confirming tonight's venue booking. For anything else, please
contact the event organiser directly.' Then it offered to return to the confirm_booking
flow by asking 'Would you like to continue with confirm booking?' — preserving the
conversation state rather than crashing or losing context.
"""

# Compare Rasa CALM's handling of the out-of-scope request to what
# LangGraph did in Exercise 2 Scenario 3. Min 40 words.
OUT_OF_SCOPE_COMPARISON = """
The two agents handled out-of-scope requests very differently. In Exercise 2
Scenario 3, the LangGraph agent was asked about train times. It had no train tool,
so it stated it could not answer and suggested external resources (National Rail,
Trainline, LNER) — but the conversation effectively ended there. There was no
concept of returning to a previous task.

Rasa CALM handled it differently: it detected the parking question as out-of-scope,
delivered a clear boundary message ('I can only help with confirming tonight's venue
booking'), and then offered to resume the booking flow with 'Would you like to
continue with confirm booking?'. The conversation state was preserved — guest_count
was still pending, and the agent was ready to continue collecting slots.

This difference reflects their architectures. LangGraph has no concept of 'returning
to a flow' because it has no explicit flows — it is a single reasoning loop that
terminates when it has a final answer. Rasa CALM has explicit flows with steps, so
it can pause, handle a digression, and resume where it left off. For a booking
confirmation call, CALM's behaviour is clearly more appropriate.
"""

# ── Task B: Cutoff guard ───────────────────────────────────────────────────

TASK_B_DONE = True

# List every file you changed.
TASK_B_FILES_CHANGED = ["exercise3_rasa/actions/actions.py"]

# How did you test that it works? Min 20 words.
TASK_B_HOW_YOU_TESTED = """
I uncommented the four lines of the cutoff guard in actions.py. After fixing an
initial IndentationError (tabs vs spaces), I temporarily changed the condition to
'if True:' to force the guard to fire regardless of time. I restarted the action
server, then ran a booking conversation (160 guests, 40 vegan, 200 deposit). The
agent escalated immediately with the message: 'I need to check one thing with the
organiser before I can confirm. The issue is: it is past 16:45 — insufficient time
to process the confirmation before the 5 PM deadline. Can I call you back within
15 minutes?' This confirmed the guard works. I then reverted the condition back to
the real datetime check (if now.hour > 16 or (now.hour == 16 and now.minute >= 45))
and the guard is now active in its production form.
"""

# ── CALM vs Old Rasa ───────────────────────────────────────────────────────

CALM_VS_OLD_RASA = """
In old Rasa, slot extraction required a FormValidationAction with regex methods
like validate_guest_count() to parse 'about 160 people' into 160.0. You also
needed nlu.yml with intent training examples and rules.yml for dialogue paths.
The comments at the top of actions.py (lines 1-48) describe this old approach.

In CALM, the LLM handles all natural language understanding via from_llm slot
mappings in domain.yml. 'About 50 need vegan', '160 guests', and '500 pound
deposit' are all parsed without any regex or training examples. Python only
enforces the business rules (MAX_GUESTS, MAX_DEPOSIT_GBP, vegan ratio).

The simplification is significant: fewer files, no regex maintenance, and the
agent handles phrasing variations automatically. But the cost is that the LLM
can sometimes fail to parse — in my run, the first attempt to set vegan_count
failed because Qwen3's thinking tokens confused the CALM command parser, producing
'No commands were parsed from the LLM actions.' Old Rasa's regex would not have
had that problem — it would have either matched or not, deterministically. The
trade-off is flexibility versus determinism in the language understanding layer.
"""

# ── The setup cost ─────────────────────────────────────────────────────────

SETUP_COST_VALUE = """
CALM's setup (config.yml, domain.yml, flows.yml, endpoints.yml, rasa train,
two terminals, Rasa Pro licence) is significantly heavier than LangGraph, which
needed just a few lines of Python to create a ReAct agent with create_react_agent().
But that setup cost bought something specific: the CALM agent cannot improvise.
It cannot call a tool that is not defined in flows.yml. It cannot skip a business
rule. It cannot decide to confirm a booking without collecting all three required
slots (guest_count, vegan_count, deposit_amount_gbp).

In my run, when I asked about parking, CALM deflected with 'I can only help with
confirming tonight's venue booking' and offered to return to the booking flow. A
LangGraph agent would have no flow to return to — it would just move on. When the
deposit was £500, CALM hit the Python guard deterministically and escalated with
the exact reason. A LangGraph agent might have reasoned around it.

For the confirmation use case — where every word has financial and legal weight —
the inability to improvise is the feature, not the limitation. The setup cost
is the price of auditability.
"""
