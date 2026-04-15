"""
Extra Experiments — Findings Summary
=====================================
All experiments are reproducible: seed=42, temperature=0, Nebius Token Factory.

These experiments extend Exercise 1 to test claims from the lectures about
context engineering, model selection, and attention patterns.

Run any experiment:
    uv run python week1/extra_position_experiment.py
    uv run python week1/extra_needle_haystack.py

─────────────────────────────────────────────────────────────────────────────
EXPERIMENT 1: 5-Model Comparison
─────────────────────────────────────────────────────────────────────────────
Dataset: Exercise 1 distractor set (9 venues, 2 near-miss)
Formats: plain text vs XML
Models: Gemma 2B, Qwen 32B, Llama 70B, DeepSeek R1, Hermes 405B

Results:
  google/gemma-2-2b-it          | plain: Y 214tok | xml: Y 316tok | Haymarket both
  Qwen/Qwen3-32B               | plain: Y 259tok | xml: Y 349tok | thinking dump, cut off
  meta-llama/Llama-3.3-70B     | plain: Y 213tok | xml: Y 302tok | Haymarket/Albanach split
  deepseek-ai/DeepSeek-R1-0528 | plain: N 251tok | xml: N 341tok | reasoning ate budget
  NousResearch/Hermes-4-405B   | plain: Y 202tok | xml: Y 292tok | Haymarket both, fewest tokens

Findings:
  - Only Llama 70B showed the formatting split (plain->Haymarket, XML->Albanach)
  - Hermes 405B used fewest tokens despite being largest dense model
  - Reasoning models (DeepSeek R1, Qwen 32B) failed or produced messy output
  - Gemma 2B followed instructions best despite being smallest

─────────────────────────────────────────────────────────────────────────────
EXPERIMENT 2: Needle-in-a-Haystack Position Test
─────────────────────────────────────────────────────────────────────────────
Methodology: Adapted from Kamradt (2023) needle-in-a-haystack and
Chroma Research (2025) context rot paper referenced in course slides.
Needle: The Albanach (only correct venue, Haymarket removed)
Haystack: 7 real distractors + 0/20/50/100 generated filler venues
Positions: beginning, middle, end
Format: XML sandwich (Sovereign Injection Pattern)

Results (Gemma 2B):
    8 venues  | beginning=N  middle=N  end=N
   28 venues  | beginning=N  middle=Y  end=N
   58 venues  | beginning=Y  middle=Y  end=N
  108 venues  | beginning=N  middle=N  end=N

Results (Llama 70B):
    8 venues  | beginning=Y  middle=Y  end=Y
   28 venues  | beginning=Y  middle=Y  end=Y
   58 venues  | beginning=Y  middle=Y  end=Y
  108 venues  | beginning=Y  middle=Y  end=Y

Findings:
  - Gemma 2B failed at 8 venues with 0 filler. It picked Holyrood Arms
    (capacity=160, vegan=yes, status=FULL) every time. It cannot reliably
    check the status field when there are multiple near-matches.
  - At 108 venues Gemma 2B collapsed completely, picking random filler venues.
  - Llama 70B was perfect at every position and size up to 108 venues (2831 tokens).
  - No clear position effect for either model at these context lengths.
    Rod's "10 pages" threshold (~8000 tokens) was not reached.

Critical observation:
  In Exercise 1, Gemma 2B always picked Haymarket (correct). When Haymarket
  was removed and only Albanach was valid, it failed. The Exercise 1
  accept-either evaluation (ACCEPTABLE = {"haymarket", "albanach"}) masked
  that Gemma 2B was not robustly solving the 3-constraint problem.

─────────────────────────────────────────────────────────────────────────────
EXPERIMENT 3: Constraint Isolation
─────────────────────────────────────────────────────────────────────────────
Test: Can models correctly refuse when no venue satisfies all constraints?

  2 venues (1 full, 1 available):
    Gemma 2B:  picked Albanach correctly (trivial comparison)
    Llama 70B: picked Albanach correctly

  1 venue only (full):
    Gemma 2B:  picked Holyrood Arms anyway (wrong, will not refuse)
    Llama 70B: picked Holyrood Arms anyway (wrong, will not refuse)

  5 venues, none valid, with "if none qualify reply NONE":
    Gemma 2B:  picked Ensign Ewart (wrong, capacity=120 < 160)
    Llama 70B: replied NONE (correct)

Findings:
  - Both models refuse to say "no answer" unless explicitly given permission
  - Even Llama 70B hallucinated when forced to pick from only invalid options
  - Adding "if none qualify, reply NONE" fixed Llama 70B but not Gemma 2B
  - This is a context engineering finding: the instruction to allow refusal
    changed the outcome more than XML formatting did

─────────────────────────────────────────────────────────────────────────────
EXPERIMENT 4: Query Injection Mid-Context
─────────────────────────────────────────────────────────────────────────────
Technique from slides: "If a critical piece of info is buried among similar
content, use Query Injection (repeating the question mid-context)"

Test: Insert <query_reminder> tag at the midpoint of the venue list.
Compare sandwich-only vs sandwich + mid-injection on Gemma 2B.

Results (Gemma 2B):
  8 venues:
    beginning  | sandwich=N | +mid_inject=Y | RESCUED
    middle     | sandwich=N | +mid_inject=N | same
    end        | sandwich=N | +mid_inject=N | same
  28 venues:
    beginning  | sandwich=N | +mid_inject=N | same
    middle     | sandwich=Y | +mid_inject=Y | same
    end        | sandwich=Y | +mid_inject=Y | same
  58 venues:
    beginning  | sandwich=N | +mid_inject=N | same
    middle     | sandwich=Y | +mid_inject=N | BROKE
    end        | sandwich=N | +mid_inject=N | same

Results (Llama 70B):
  8 venues middle:  Y
  58 venues middle: Y

Findings:
  - Mid-context query injection rescued 1/9 failing Gemma 2B cases
  - It also BROKE 1 case that was previously working (58 venues, middle)
  - The technique assumes enough model capacity to use the reminder.
    Below that threshold, extra structure adds noise instead of signal.
  - Llama 70B does not need query injection at these context lengths.

─────────────────────────────────────────────────────────────────────────────
EXPERIMENT 5: Chain-of-Thought Rescue
─────────────────────────────────────────────────────────────────────────────
Test: Replace "reply with only the venue name" with "check each venue
one by one against all three constraints, then give only the venue name."

Results (Gemma 2B, 8 venues, Haymarket removed):
  plain + standard:  Albanach (correct)
  sandwich + standard: Holyrood Arms (wrong)
  plain + CoT:       Albanach (correct)
  sandwich + CoT:    Albanach (correct)

Findings:
  - Chain-of-thought prompting fixed sandwich formatting for Gemma 2B
  - XML sandwich WITHOUT CoT made Gemma 2B worse (picked Holyrood Arms)
  - XML sandwich WITH CoT worked correctly
  - Telling the model HOW to reason was more effective than structural
    formatting alone. This aligns with the lecture point that prompt
    engineering for system prompts (agent developers) still matters,
    even if it matters less for end users.

─────────────────────────────────────────────────────────────────────────────
EXPERIMENT 6: Constraint Isolation — Capacity vs Status
─────────────────────────────────────────────────────────────────────────────
Test: Which constraint does Gemma 2B actually fail on? Isolate each one.

Setup: 2 venues, both vegan=yes and status=available, different capacities.

Results:
  capacity 150 vs 180:         Gemma 2B correct (Albanach), Llama 70B correct
  capacity 159 vs 160:         Gemma 2B correct (Albanach), Llama 70B correct
  capacity 160 vs 159 reversed: Gemma 2B correct (Albanach), Llama 70B correct

Findings:
  - Both models handle numerical capacity comparison perfectly, even at
    the 159/160 boundary (1 guest difference).
  - Vegan (binary yes/no) is also handled correctly by both models.
  - The failure is specifically the status field under noise. When there
    are 8+ venues with near-miss distractors, Gemma 2B ignores status=full
    and picks the closest numerical match.
  - Constraint difficulty hierarchy for weak models:
    numerical comparison > binary field > semantic field.
    As noise grows, the semantic constraint (status) drops first.
  - This confirms the PART_B_HARDEST_DISTRACTOR prediction: Holyrood Arms
    is dangerous because it fails only on status, the weakest-checked field.
"""
