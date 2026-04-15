"""
Extra — Needle-in-a-Haystack Context Rot Test
===============================================
Adapts the Needle-in-a-Haystack evaluation methodology (Kamradt, 2023)
and the Context Rot findings (Chroma Research, 2025) to venue extraction.

Research context:
  - Stanford (Liu et al., 2023): models lose accuracy when the answer is
    in the middle of long context ("lost in the middle")
  - Chroma Research (2025): "whether information is present in a context
    is not all that matters; what matters more is how that information
    is presented" — coined "context rot"
  - Rod's pineapple-42 experiment: tested the Stanford claim on newer
    models and found they forget the BEGINNING, not the middle

This experiment:
  - The "needle" is The Albanach (the only correct venue)
  - The "haystack" is a growing list of filler venues (none valid)
  - We vary both the needle POSITION (beginning, middle, end) and the
    haystack SIZE (8, 28, 58, 108 venues) across two models
  - We use XML sandwich formatting (the Sovereign Injection Pattern)

Hypothesis:
  If context rot occurs, accuracy should degrade as the haystack grows,
  and the degradation pattern (beginning vs middle vs end) tells us
  where the model's attention weakens first.

Run:
    uv run python week1/extra_needle_haystack.py

Results saved to week1/outputs/needle_haystack.json
"""

import json
import os
import random
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.getenv("NEBIUS_KEY"),
)

OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# ── The needle: only correct venue ────────────────────────────────────────────
TARGET = "The Albanach: capacity=180, vegan=yes, status=available"

# ── Real distractors (Haymarket removed so only Albanach is valid) ────────────
REAL_DISTRACTORS = [
    "The Bow Bar: capacity=80, vegan=yes, status=full",
    "The Guilford Arms: capacity=200, vegan=no, status=available",
    "The Hanging Bat: capacity=70, vegan=yes, status=available",
    "The Grain Store: capacity=170, vegan=no, status=available",
    "The Ensign Ewart: capacity=120, vegan=yes, status=available",
    "The New Town Vault: capacity=162, vegan=no, status=available",
    "The Holyrood Arms: capacity=160, vegan=yes, status=full",
]

# ── Filler venue names ────────────────────────────────────────────────────────
FAKE_NAMES = [
    "Anchor", "Bell", "Crown", "Duke", "Eagle", "Falcon", "Globe",
    "Hound", "Ivy", "Jade", "Kite", "Lion", "Manor", "Noble", "Oak",
    "Pike", "Quill", "Raven", "Shield", "Tower", "Union", "Vale",
    "Wren", "York", "Zenith", "Arch", "Brook", "Castle", "Dawn",
    "Elm", "Forge", "Gate", "Hearth", "Isle", "Jewel", "Keep",
    "Lark", "Mill", "Nest", "Orchard", "Pond", "Ridge", "Stone",
    "Torch", "Urn", "Vault", "Wharf", "Cross", "Dell", "Fern",
]

QUESTION = (
    "Which single venue is available tonight, fits at least 160 guests, "
    "AND has vegan options? Reply with only the venue name, nothing else."
)


def generate_filler(count):
    """Generate fake venues that do NOT satisfy all three constraints."""
    fillers = []
    random.seed(42)
    for i in range(count):
        name = f"The {FAKE_NAMES[i % len(FAKE_NAMES)]} {i + 1}"
        roll = i % 4
        if roll == 0:
            cap, veg, stat = random.randint(40, 120), "yes", "available"
        elif roll == 1:
            cap, veg, stat = random.randint(160, 250), "no", "available"
        elif roll == 2:
            cap, veg, stat = random.randint(160, 250), "yes", "full"
        else:
            cap, veg, stat = random.randint(40, 120), "no", "full"
        fillers.append(f"{name}: capacity={cap}, vegan={veg}, status={stat}")
    return fillers


def build_haystack(position, filler_count):
    """Place the needle (Albanach) at beginning, middle, or end."""
    filler = generate_filler(filler_count)
    all_wrong = REAL_DISTRACTORS + filler

    random.seed(42)
    random.shuffle(all_wrong)

    if position == "beginning":
        venues = [TARGET] + all_wrong
    elif position == "middle":
        mid = len(all_wrong) // 2
        venues = all_wrong[:mid] + [TARGET] + all_wrong[mid:]
    elif position == "end":
        venues = all_wrong + [TARGET]

    return "\n".join(venues)


def build_sandwich_prompt(venues_text, question):
    """Sovereign Injection Pattern: query at top, XML venues, query reminder at bottom."""
    lines = venues_text.strip().splitlines()
    tags = "\n".join(
        f'  <venue id="{i + 1}">{line}</venue>' for i, line in enumerate(lines)
    )
    return (
        f"<query>{question}</query>\n"
        f"<venues>\n{tags}\n</venues>\n"
        f"<query_reminder>{question}</query_reminder>\n"
    )


def test_model(model, venues_text):
    prompt = build_sandwich_prompt(venues_text, QUESTION)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0,
    )
    answer = resp.choices[0].message.content.strip() if resp.choices[0].message.content else ""
    tokens = resp.usage.total_tokens
    found = "albanach" in answer.lower()
    return {
        "answer": answer[:120],
        "tokens": tokens,
        "found_needle": found,
    }


def main():
    print("Needle-in-a-Haystack Context Rot Test")
    print("=" * 65)
    print()
    print("Needle: The Albanach (only venue satisfying all 3 constraints)")
    print("Haystack: 7 real distractors + N generated filler venues")
    print("Format: Sovereign Injection Pattern (XML sandwich)")
    print("Models: Gemma 2B (weak) vs Llama 70B (strong)")
    print()

    models = [
        ("google/gemma-2-2b-it", "Gemma-2B"),
        ("meta-llama/Llama-3.3-70B-Instruct", "Llama-70B"),
    ]

    filler_counts = [0, 20, 50, 100]
    positions = ["beginning", "middle", "end"]

    results = {}

    for model_id, model_label in models:
        print(f"\n{'=' * 65}")
        print(f"  {model_label} ({model_id})")
        print(f"{'=' * 65}")
        results[model_label] = {}

        for filler_count in filler_counts:
            total = filler_count + len(REAL_DISTRACTORS) + 1
            print(f"\n  Haystack size: {total} venues ({filler_count} filler)")
            results[model_label][str(total)] = {}

            for pos in positions:
                haystack = build_haystack(pos, filler_count)
                try:
                    r = test_model(model_id, haystack)
                    icon = "Y" if r["found_needle"] else "N"
                    print(
                        f"    needle at {pos:10s} | {icon} | "
                        f"{r['tokens']:5d} tok | {r['answer'][:50]}"
                    )
                    results[model_label][str(total)][pos] = r
                except Exception as e:
                    print(f"    needle at {pos:10s} | ERROR: {str(e)[:60]}")
                    results[model_label][str(total)][pos] = {
                        "error": str(e)[:200]
                    }

    # ── Analysis ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print("CONTEXT ROT ANALYSIS")
    print(f"{'=' * 65}")

    for model_id, model_label in models:
        print(f"\n  {model_label}:")
        for filler_count in filler_counts:
            total = filler_count + len(REAL_DISTRACTORS) + 1
            key = str(total)
            if key not in results[model_label]:
                continue
            b = results[model_label][key].get("beginning", {}).get("found_needle", "?")
            m = results[model_label][key].get("middle", {}).get("found_needle", "?")
            e = results[model_label][key].get("end", {}).get("found_needle", "?")
            b_tok = results[model_label][key].get("beginning", {}).get("tokens", "?")
            print(
                f"    {total:3d} venues ({b_tok:>5} tok) | "
                f"beginning={str(b):5s}  middle={str(m):5s}  end={str(e):5s}"
            )

    # ── Supplementary: CoT rescue test ────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print("SUPPLEMENTARY: Does chain-of-thought prompting rescue Gemma 2B?")
    print(f"{'=' * 65}")

    Q_COT = (
        "Which single venue is available tonight, fits at least 160 guests, "
        "AND has vegan options? Check each venue one by one against all three "
        "constraints. Then give only the venue name."
    )

    haystack_8 = build_haystack("beginning", 0)
    for label, question in [("standard", QUESTION), ("chain-of-thought", Q_COT)]:
        prompt = build_sandwich_prompt(haystack_8, question)
        resp = client.chat.completions.create(
            model="google/gemma-2-2b-it",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0,
        )
        ans = resp.choices[0].message.content.strip() if resp.choices[0].message.content else ""
        found = "albanach" in ans.lower()
        icon = "Y" if found else "N"
        print(f"  {label:20s} | {icon} | {ans[:80]}")

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = OUTPUTS_DIR / "needle_haystack.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
