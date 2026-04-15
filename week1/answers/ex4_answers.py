"""
Exercise 4 — Answers
====================
Fill this in after running exercise4_mcp_client.py.
"""

# ── Basic results ──────────────────────────────────────────────────────────

# Tool names as shown in "Discovered N tools" output.
TOOLS_DISCOVERED = ["search_venues", "get_venue_details"]

QUERY_1_VENUE_NAME    = "The Haymarket Vaults"
QUERY_1_VENUE_ADDRESS = "1 Dalry Road, Edinburgh"

QUERY_2_FINAL_ANSWER  = """It seems there are no Edinburgh venues currently available that can accommodate 300 guests with vegan options. Would you like me to:
1. Search for venues with a lower minimum capacity (e.g., 200-250 people)?
2. Look for venues without vegan requirements but with other dietary options?
3. Check availability for a different date?

Let me know how you'd like to proceed!"""

# ── The experiment ─────────────────────────────────────────────────────────

EX4_EXPERIMENT_DONE = True

# What changed, and which files did or didn't need updating? Min 30 words.
EX4_EXPERIMENT_RESULT = """
When I changed The Albanach's status from 'available' to 'full' in
mcp_venue_server.py, Query 1 returned only 1 match (The Haymarket Vaults at
1 Dalry Road) instead of the original 2 matches (Albanach + Haymarket). The
Albanach was filtered out by the server-side search because it was no longer
available. Crucially, exercise4_mcp_client.py was not modified at all, the
agent code stayed identical. The agent then recommended Haymarket Vaults as
the best match instead of Albanach. This demonstrates that MCP decouples
data from agent logic: you update one file (the server) and every connected
client sees the new state instantly without any code changes on their side.

The trace also shows resilience to tool errors. Query 1 hit 2 pydantic
validation errors before the agent figured out the correct argument format
(wrapping parameters inside an 'input' key). Query 2 hit 1 error before
recovering. The agent learned from its own failures within the same session
without any human correction.
"""

# ── MCP vs hardcoded ───────────────────────────────────────────────────────

LINES_OF_TOOL_CODE_EX2 = 5    # exercise2_langgraph.py: 4 import lines + 1 run_research_agent call - tool definitions live in venue_tools.py
LINES_OF_TOOL_CODE_EX4 = 50   # exercise4_mcp_client.py: ~23 lines _make_mcp_caller + ~16 discover_tools + ~11 extract_trace - zero tool definitions

# What does MCP buy you beyond "the tools are in a separate file"? Min 30 words.
MCP_VALUE_PROPOSITION = """
MCP provides dynamic tool discovery - the client connects, calls list_tools(),
and wraps whatever it finds as LangChain StructuredTools at runtime. This means
you can add, remove, or change tools on the server without touching any client
code. My experiment proved this: I changed one venue's status in the MCP server
and the agent's results changed immediately with zero edits to the client.

More importantly, multiple different clients (a LangGraph research agent AND a
Rasa confirmation agent) can connect to the same MCP server and share the same
venue data and tools. This solves the M-times-N integration problem from the
Week 2 lecture: instead of maintaining 3 models x 10 tools = 30 integrations,
you maintain 3 clients + 10 MCP server tools = 13 things. When venue data
changes, every client sees the update with zero code changes on their side.
"""

# ── PyNanoClaw architecture - SPECULATION QUESTION ─────────────────────────

WEEK_5_ARCHITECTURE = """
- The Planner is a strong-reasoning model (e.g. Qwen3-Next-80B-Thinking or
  Nemotron-3-Super) that takes Rod's raw WhatsApp message and decomposes it into
  an ordered list of subgoals (find venue, check weather, calculate costs, generate
  flyer, confirm booking). It lives upstream of the ReAct loop in the autonomous
  half of PyNanoClaw, ensuring the Executor never receives an ambiguous task.
  (PROGRESS.md: pynanoclaw/agents/planner.py)

- The Executor is research_agent.py extended with real web search and file
  operations. It runs the ReAct loop against individual subgoals from the Planner,
  calling tools via MCP. It lives in the autonomous-loop half and is the fast
  worker that does the actual venue searching, weather checking, and flyer
  generation. (PROGRESS.md: pynanoclaw/agents/executor.py)

- The Shared MCP Tool Server is mcp_venue_server.py extended to cover every
  capability both halves need: live web search, venue lookups, calendar access,
  email sending, and booking confirmation triggers. It lives in the shared layer
  between both halves so neither agent needs to know where tools come from.
  My Ex4 experiment showed this decoupling in action.

- The Handoff Bridge routes tasks between the two halves. When the autonomous
  loop discovers that a human conversation is needed (e.g., the pub manager
  calls back to negotiate a deposit), it hands off to the Rasa structured agent.
  When the structured agent needs research (e.g., the manager asks about
  alternative dates), it hands back to the loop. (PROGRESS.md:
  pynanoclaw/bridge/handoff.py)

- The Rasa Digital Employee is exercise3_rasa/ extended with MCP tool access,
  a RAG knowledge base for questions flows.yml does not cover, and optionally
  a voice pipeline (Whisper STT -> Rasa CALM -> TTS). It handles the pub
  manager call with deterministic business rules enforced in Python, as I saw
  in Ex3 when the £500 deposit was rejected by the Python guard, not by the LLM.

- Persistent Memory combines a filesystem-backed store (for conversation history
  and task state) with a vector store (for RAG retrieval in the structured agent).
  Both halves read and write to this memory layer so the Executor knows what the
  structured agent confirmed and vice versa.
  (PROGRESS.md: pynanoclaw/memory/persistent_store.py + vector_store.py)

- Observability wraps the entire system with tracing (LangSmith), cost tracking
  (token usage per subgoal), and safety guardrails (spending limits, content
  filters) so Rod can audit what happened while he was away.
  (PROGRESS.md: pynanoclaw/observability/)
"""

# ── The guiding question ───────────────────────────────────────────────────

GUIDING_QUESTION_ANSWER = """
After running both agents, the split is clear to me. LangGraph handles the
research side. Rasa CALM handles the call. They are not interchangeable, and
swapping them would make both worse.

For research, the agent has to work out its own path. In my Ex2 Task A run,
it decided for itself to check Albanach first, then Haymarket, then catering
at £35 per head which came back as £5600, then weather which came back 11.8°C
with outdoor_ok true, then the flyer. Nobody gave it that order. In Scenario
1, when The Bow Bar came back full with capacity 80, it pivoted straight to
Haymarket. In Scenario 2, with 300 guests, it checked all four venues, found
none that fit, and said so instead of inventing an answer. That is exactly
what you want on the research side: open-ended reasoning, tool use, and the
ability to adjust when the first option fails.

The confirmation call is the opposite. In Ex3, the Rasa agent followed the
flow in flows.yml step by step: guest count, vegan count, deposit, then
validation. When the manager said £500, the Python guard caught it, not the
LLM. MAX_DEPOSIT_GBP is 300, so that rule fires the same way every time no
matter how the manager phrases it. That is why CALM makes more sense for the
call. Once money and commitments are involved, you want explicit steps and
hard checks, not a model deciding on the fly what sounds reasonable.

The difference also shows up at the edges. In Scenario 3, when I asked the
LangGraph agent about train times, it said it did not have the right tools
and redirected me elsewhere, but there was no real flow state to resume
because it is just one reasoning loop. When I asked CALM about parking in the
middle of booking, it set a boundary, said it could only help with confirming
the booking, and then offered to continue where we left off. That is much
better behaviour for a live confirmation call.

Ex4 made the overall architecture clearer too. Both halves can sit on top of
the same MCP tool layer. When I changed Albanach to full on the server, the
client code did not change, but the result did. The MCP client even recovered
from the initial validation error and kept going. So the clean split for me
is: LangGraph does the messy discovery work, CALM handles the structured
commitment, and MCP is the shared layer that lets both use the same tools and
data.
"""
