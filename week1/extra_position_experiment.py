"""
Extra — Venue Position vs Context Length Experiment
====================================================
Tests whether models lose track of the correct venue depending on
WHERE it appears in the list and HOW LONG the list is.

Rod's pineapple experiment showed newer models forget the beginning
as context grows, contradicting the Stanford 2023 U-shaped finding.

This experiment tests that claim with venue data.
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

TARGET = "The Albanach: capacity=180, vegan=yes, status=available"

REAL_DISTRACTORS = [
    "The Bow Bar: capacity=80, vegan=yes, status=full",
    "The Guilford Arms: capacity=200, vegan=no, status=available",
    "The Hanging Bat: capacity=70, vegan=yes, status=available",
    "The Haymarket Vaults: capacity=160, vegan=yes, status=available",
    "The Grain Store: capacity=170, vegan=no, status=available",
    "The Ensign Ewart: capacity=120, vegan=yes, status=available",
    "The New Town Vault: capacity=162, vegan=no, status=available",
    "The Holyrood Arms: capacity=160, vegan=yes, status=full",
]

FILLER_TEMPLATE = [
    "The {name}: capacity={cap}, vegan={veg}, status={stat}",
]

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

ACCEPTABLE = {"albanach"}  # only Albanach this time, we remove Haymarket in padded lists


def generate_filler(count):
    """Generate fake venues that do NOT satisfy all three constraints."""
    fillers = []
    random.seed(42)
    for i in range(count):
        name = f"The {FAKE_NAMES[i % len(FAKE_NAMES)]} {i+1}"
        # Make sure none satisfy all constraints
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


def build_venue_list(position, total_filler):
    """Place Albanach at beginning, middle, or end of a padded list."""
    # Use only distractors that do NOT satisfy all constraints
    safe_distractors = [
        d for d in REAL_DISTRACTORS
        if "Haymarket" not in d  # remove Haymarket so only Albanach is correct
    ]
    filler = generate_filler(total_filler)
    all_wrong = safe_distractors + filler

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


def build_xml_prompt(venues_text, question):
    lines = venues_text.strip().splitlines()
    tags = "\n".join(
        f'  <venue id="{i+1}">{line}</venue>' for i, line in enumerate(lines)
    )
    return (
        f"<query>{question}</query>\n"
        f"<venues>\n{tags}\n</venues>\n"
        f"<query_reminder>{question}</query_reminder>\n"
    )


def test(model, venues_text, fmt):
    if fmt == "plain":
        prompt = venues_text + "\nQuestion: " + QUESTION
    else:
        prompt = build_xml_prompt(venues_text, QUESTION)

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
        "answer": answer[:100],
        "tokens": tokens,
        "found_albanach": found,
    }


def main():
    print("Venue Position vs Context Length Experiment")
    print("=" * 65)
    print()
    print("Rod's pineapple experiment: models forget the BEGINNING as")
    print("context grows, not the middle (contradicts Stanford 2023).")
    print("Testing with venue data across positions and list sizes.")
    print()

    models = [
        "google/gemma-2-2b-it",
        "meta-llama/Llama-3.3-70B-Instruct",
    ]

    filler_counts = [0, 20, 50, 100]
    positions = ["beginning", "middle", "end"]

    results = {}

    for model in models:
        print(f"\n{'='*65}")
        print(f"  {model}")
        print(f"{'='*65}")
        results[model] = {}

        for filler_count in filler_counts:
            total_venues = filler_count + 8  # 7 distractors + fillers + 1 target
            print(f"\n  --- {total_venues} venues total ({filler_count} filler) ---")
            results[model][str(filler_count)] = {}

            for pos in positions:
                venues_text = build_venue_list(pos, filler_count)
                fmt = "sandwich"  # use sandwich for best chance
                try:
                    r = test(model, venues_text, "xml")
                    icon = "Y" if r["found_albanach"] else "N"
                    print(f"    {pos:10s} | {icon} | {r['tokens']:5d} tok | {r['answer'][:50]}")
                    results[model][str(filler_count)][pos] = r
                except Exception as e:
                    print(f"    {pos:10s} | ERROR: {str(e)[:60]}")
                    results[model][str(filler_count)][pos] = {"error": str(e)[:200]}

    # Analysis
    print(f"\n{'='*65}")
    print("ANALYSIS")
    print(f"{'='*65}")

    for model in models:
        print(f"\n  {model}:")
        for filler_count in filler_counts:
            fc = str(filler_count)
            if fc not in results[model]:
                continue
            b = results[model][fc].get("beginning", {}).get("found_albanach", "?")
            m = results[model][fc].get("middle", {}).get("found_albanach", "?")
            e = results[model][fc].get("end", {}).get("found_albanach", "?")
            total = filler_count + 8
            print(f"    {total:3d} venues | beginning={b} middle={m} end={e}")

    out_path = OUTPUTS_DIR / "position_experiment.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
