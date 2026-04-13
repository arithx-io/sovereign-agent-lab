"""
Exercise 1 — Answers
====================
Fill this in after running exercise1_context.py.
Run `python grade.py ex1` to check for obvious issues before submitting.
"""

# ── Part A ─────────────────────────────────────────────────────────────────

# The exact answer the model gave for each condition.
# Copy-paste from your terminal output (the → "..." part).

PART_A_PLAIN_ANSWER    = "The Haymarket Vaults"
PART_A_XML_ANSWER      = "The Albanach"
PART_A_SANDWICH_ANSWER = "The Albanach"

# Was each answer correct? True or False.
# Correct = contains "Haymarket" or "Albanach" (both satisfy all constraints).

PART_A_PLAIN_CORRECT    = True
PART_A_XML_CORRECT      = True
PART_A_SANDWICH_CORRECT = True

# Explain what you observed. Minimum 30 words.

PART_A_EXPLANATION = """
All three formatting conditions (plain, XML, and sandwich) produced correct answers
on the baseline dataset using Llama-3.3-70B. However, the model chose different
correct venues depending on the format: plain text led to The Haymarket Vaults,
while XML and sandwich formats both returned The Albanach. This suggests that even
when all answers are correct, the structural framing of the data influences which
valid candidate the model selects first, likely because XML tags change how the
model attends to each venue entry.
"""

# ── Part B ─────────────────────────────────────────────────────────────────

PART_B_PLAIN_ANSWER    = "The Haymarket Vaults"
PART_B_XML_ANSWER      = "The Albanach"
PART_B_SANDWICH_ANSWER = "The Albanach"

PART_B_PLAIN_CORRECT    = True
PART_B_XML_CORRECT      = True
PART_B_SANDWICH_CORRECT = True

# Did adding near-miss distractors change any results? True or False.
PART_B_CHANGED_RESULTS = False

# Which distractor was more likely to cause a wrong answer, and why?
# Minimum 20 words.
PART_B_HARDEST_DISTRACTOR = """
The Holyrood Arms is the harder distractor because it matches on both capacity (160)
and vegan options (yes), failing only on status being full. A model skimming for
numerical and dietary matches could easily select it without carefully checking the
availability status field. The New Town Vault is less dangerous because it fails on
vegan (no), which is a more prominent constraint in the question.
"""

# ── Part C ─────────────────────────────────────────────────────────────────

# Did the exercise run Part C (small model)?
# Check outputs/ex1_results.json → "part_c_was_run"
PART_C_WAS_RUN = True

PART_C_PLAIN_ANSWER    = "Haymarket Vaults"
PART_C_XML_ANSWER      = "The Haymarket Vaults"
PART_C_SANDWICH_ANSWER = "The Haymarket Vaults"

# Explain what Part C showed, or why it wasn't needed. Minimum 30 words.
PART_C_EXPLANATION = """
Even the much smaller Gemma-2-2B model got all three conditions correct with the
distractor dataset. This was unexpected because the exercise was designed to show
formatting effects on weaker models. The signal-to-noise ratio in this dataset is
still high enough that even a 2B parameter model can reliably filter venues by
three constraints (capacity, vegan, status). The effect that the Stanford lost-in-
the-middle paper describes may require a longer context or more numerous and subtle
distractors to appear with this particular task.
"""

# ── Core lesson ────────────────────────────────────────────────────────────

# Complete this sentence. Minimum 40 words.
# "Context formatting matters most when..."

CORE_LESSON = """
Context formatting matters most when the context gets noisy or long. In my
run, all three formats got the right answer across both datasets, even the
Gemma 2B model on the distractor set. So on this small venue list,
formatting did not change correctness. What it did change was which correct
venue the model picked. Plain text kept picking Haymarket Vaults, while XML
and sandwich both picked Albanach. Same data, same question, different valid
answer.

Part C made that more interesting. Gemma 2B picked Haymarket in all three
conditions, so the smaller model was actually more consistent here and less
sensitive to the formatting change than the 70B model. The token counts also
moved a lot: Part A was 180 for plain, 251 for XML, 289 for sandwich, and
Part B was 213, 302, and 340. So the extra structure cost more tokens, but
on this task it bought no gain in correctness, only a different valid pick.

My takeaway is that formatting matters most once the context is crowded
enough that the model needs help separating signal from noise. In a short
clean list like this, it mostly nudged attention. In a real agent system full
of tool outputs, chat history, and repeated instructions, that same nudge is
where structure starts preventing actual mistakes.

I ran an extra test on the distractor dataset across five models to see if
this held up. Gemma 2B at 214 tokens, Llama 70B at 213, and Hermes 405B at
202 all answered correctly with clean venue names. Hermes 405B used the
fewest tokens despite being the largest. But the reasoning models were
worse at this task. Qwen 32B dumped its thinking chain instead of just
the venue name, and DeepSeek R1 ran out of the 60 token budget while still
reasoning and never produced an answer. Only Llama 70B showed the
formatting split between plain and XML. The others picked the same venue
either way. So the attention effect is model specific, and bigger does not
mean better for a straightforward extraction task.
"""
