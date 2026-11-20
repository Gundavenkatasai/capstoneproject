"""
CivicMind AI — Curated Municipal Research Benchmark Dataset (v1)
Provides an empirical, scientifically consistent municipal benchmark of 500 cases
for reproducible offline training, cross-validation, and performance evaluation.
"""

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import pandas as pd

from ml.data.normalization import (
    STANDARD_CATEGORIES,
    STANDARD_DEPARTMENTS,
    CATEGORY_TO_DEPARTMENT,
    PRIORITY_SLA_HOURS,
    combine_title_description,
)

# Canonical municipal templates by category
CATEGORY_TEMPLATES = {
    "Road Infrastructure": [
        ("Massive pothole causing bike skids", "Deep crater on main road near junction, multiple two-wheelers slipping daily after rain.", "Potholes & Road Damage", "critical", 1.8),
        ("Damaged pedestrian footpath paving", "Paver blocks are broken and displaced on sidewalk, elderly citizens struggling to walk.", "Footpath & Pavements", "medium", 3.5),
        ("Dangerous cave-in near storm drain", "Road sub-base collapsed near the culvert, immediate risk of vehicle wheel trap.", "Road Collapse & Cave-in", "critical", 1.5),
        ("Missing storm manhole cover on highway", "Open manhole on outer ring road service lane without barricading.", "Missing Manhole Cover", "critical", 1.2),
        ("Unmarked hazardous speed breaker", "Newly laid asphalt speed hump has no white thermoplastic zebra stripes.", "Traffic Calming & Speed Humps", "low", 4.5),
        ("Cracked concrete bridge flyover expansion joint", "Flyover expansion joint gap has widened and metal strip is rattling loudly.", "Bridges & Flyovers", "high", 2.8),
        ("Road resurfacing left unpaved with loose gravel", "Contractor scraped road top 3 weeks ago and left gravel unrolled, causing skids.", "Incomplete Road Work", "high", 3.0),
        ("Dividing median damaged by truck collision", "Concrete divider blocks knocked into oncoming lane on arterial corridor.", "Dividers & Medians", "medium", 3.2),
    ],
    "Sanitation & Waste Management": [
        ("Overflowing dumper bin spilling onto road", "Garbage collection bin full for 4 days, strays scattering food waste across street.", "Garbage Dump Overflow", "high", 2.2),
        ("Dead stray animal carcass lying in lane", "Dead canine carcass lying on sidewalk emitting terrible stench in residential pocket.", "Animal Carcass Removal", "critical", 0.9),
        ("Illegal commercial debris dumping at night", "Construction debris and plaster dumped along lake bund overnight.", "Illegal Waste Dumping", "medium", 3.8),
        ("Door-to-door waste collection vehicle skipped ward", "Waste pickup vehicle did not visit Sector 4 houses for three consecutive mornings.", "Collection Schedule Failure", "low", 2.5),
        ("Burning garbage and plastic causing toxic smoke", "Open plastic incineration behind market complex, dense choking fumes entering homes.", "Open Waste Burning", "critical", 1.1),
        ("Public community bin broken and rusty", "Secondary collection container is rusted through and leaking dirty leachate.", "Damaged Waste Infrastructure", "medium", 4.0),
        ("Street sweeping dust left in heaps", "Sanitation workers swept leaves and dust but left piles in corner without lifting.", "Street Sweeping Incomplete", "low", 2.0),
        ("Bio-medical waste dumped in public alley", "Used syringes and clinic dressings discarded in normal open bin.", "Hazardous / Bio Waste", "critical", 1.3),
    ],
    "Water Supply & Drainage": [
        ("Burst water supply pipeline gushing potable water", "Main distribution pipe burst under pressure, flooding road with clean drinking water.", "Pipeline Rupture", "critical", 1.4),
        ("Severe sewage backflow into residential basements", "Blocked municipal main causing dark sewage to overflow through floor drains.", "Sewage Backflow", "critical", 1.6),
        ("Contaminated drinking water with pungent odor", "Tap water supplied this morning is turbid and smells of sewage mix.", "Water Contamination", "critical", 1.5),
        ("Extremely low municipal tap pressure for past week", "Water trickling at ground level, overhead tanks cannot fill even after two hours.", "Low Water Pressure", "medium", 4.2),
        ("Blocked storm drain overflowing onto cross road", "Storm drain choked with silt and plastic, first shower causes gutter spill.", "Storm Drain Blockage", "high", 2.5),
        ("Leaking sluice valve at distribution point", "Sluice valve packing gland leaking steady stream, water logging road corner.", "Distribution Valve Leak", "medium", 3.2),
        ("Sewer manhole bubbling and overflowing during peak hours", "Chamber lid lifted by sewage surge, foul liquid running into gutter.", "Manhole Overflow", "high", 2.0),
        ("Non-supply of piped water in layout for 5 days", "Total shutdown of water line without advance public notice to residents.", "Total Water Stoppage", "critical", 1.8),
    ],
    "Urban Electricity & Street Lighting": [
        ("All 15 streetlights non-functional along main avenue", "Complete blackout on 800-meter stretch of arterial road, pedestrian danger.", "Streetlight Outage", "high", 2.4),
        ("High-voltage wire snapped and hanging low over lane", "Live 11kV conductor snapped and dangling within arm reach of pedestrians.", "Hanging / Snapped Wire", "critical", 0.8),
        ("Distribution transformer sparking violently with smoke", "Pole-mounted transformer unit crackling loudly with intermittent blue sparks.", "Transformer Malfunction", "critical", 1.0),
        ("Streetlight glowing continuously during daytime", "Timer relay stuck closed, ten LED fixtures burning in broad sunlight wasting energy.", "Timer Relay Fault", "low", 4.0),
        ("Feeder pillar box door missing with live terminals", "Roadside electrical junction box open, copper busbars exposed to children.", "Exposed Junction Box", "critical", 1.2),
        ("Fluctuating voltage blowing residential electronics", "Phase imbalance causing voltage swings between 160V and 290V.", "Phase Surge / Fluctuation", "high", 2.0),
        ("Fallen electric pole blocking residential entrance", "Storm wind uprooted rusted steel lighting pole across driveway.", "Fallen Utility Pole", "high", 1.8),
        ("Underground cable splice failure causing dark pocket", "Armored cable short circuit cut power to 6 consecutive street poles.", "Cable Fault", "medium", 3.0),
    ],
    "Health & Public Safety": [
        ("Aggressive stray dog pack biting pedestrians near park", "Pack of 8 unvaccinated strays attacking morning joggers and children on bicycles.", "Stray Animal Menace", "high", 2.8),
        ("Mosquito breeding in stagnant wastewater pool", "Large stagnant cesspool near construction site generating swarms of mosquitoes.", "Vector & Mosquito Control", "medium", 3.5),
        ("Food safety violation at roadside restaurant", "Kitchen preparing food with contaminated grease and foul-smelling uninspected meat.", "Food Safety & Hygiene", "high", 2.2),
        ("Dilapidated balcony wall ready to collapse", "Old masonry parapet on second floor cracked outwards over busy bazaar walkway.", "Hazardous Structure", "critical", 1.5),
        ("Unhygienic open butchery waste dumped in storm drain", "Slaughterhouse draining blood and animal viscera directly into public drain.", "Public Health Hazard", "critical", 1.8),
        ("Non-functioning community clinic dispensary", "Primary health clinic closed during official OPD working hours with no doctor.", "Clinic Service Deficiency", "high", 3.0),
        ("Public park water cooler water causing gastroenteritis", "Chilled community drinking station filter choked with black algae slime.", "Contaminated Drinking Unit", "high", 2.0),
        ("Illegal chemical storage emitting noxious fumes", "Warehouse storing pesticide barrels leaking pungent vapor causing eye burning.", "Toxic Chemical Hazard", "critical", 1.4),
    ],
    "Parks & Horticulture": [
        ("Huge banyan tree branch cracked and hanging over road", "Heavy limb fractured during thunderstorm, precarious over high-traffic street.", "Dangerous Tree Branch", "critical", 1.2),
        ("Children play equipment broken with sharp edges", "Metal slide cracked and swing chains snapped, risk of serious child laceration.", "Damaged Playground", "medium", 3.8),
        ("Complete drying up of public park lawns and shrubs", "Automated sprinkler system broken, flower beds and saplings dying of thirst.", "Park Maintenance Deficit", "low", 4.5),
        ("Overgrown thorny bushes obscuring traffic view at curve", "Unpruned shrubs covering intersection sight triangle, causing near collisions.", "Sight Triangle Obstruction", "high", 2.5),
        ("Fallen tree blocking entire two-lane sector road", "Uprooted gulmohar tree lying across both lanes after heavy squall.", "Uprooted Tree Removal", "critical", 1.0),
        ("Stray cattle grazing and destroying saplings in civic garden", "Broken park boundary fence allows cows to enter and trample public garden.", "Park Encroachment / Fence", "low", 3.5),
        ("Missing benches and broken walking track surface", "Jogging track paver tiles uprooted by tree roots, causing tripping hazard.", "Track & Furniture Repairs", "low", 4.0),
        ("Dead tree liable to fall during next rain", "Completely hollowed dry trunk leaning towards overhead electricity wires.", "Dead Tree Extraction", "high", 2.2),
    ],
    "Revenue & Property Tax": [
        ("Discrepancy in online property tax assessment portal", "System computed commercial tariff for purely residential ancestral house.", "Tax Assessment Error", "low", 5.0),
        ("Double debit of property tax payment online", "Bank account debited twice on payment gateway but receipt shows pending status.", "Payment Gateway Failure", "medium", 3.5),
        ("Delay in issuing municipal birth registration certificate", "Application submitted 45 days ago with all proofs, still pending verification.", "Vital Records Delay", "medium", 4.0),
        ("Trade license renewal portal failing at digital signature", "Server throws internal error 500 when uploading signed renewal affidavit.", "Trade License Tech Glitch", "low", 4.5),
        ("Wrong owner name reflected in municipal mutation record", "Typographical error in transferred title name despite registered sale deed.", "Title / Mutation Error", "low", 5.5),
        ("Unfair penalty charged on on-time property tax payment", "Challan paid within rebate period but penalty added in next demand note.", "Penalty Ledger Correction", "low", 4.2),
    ],
    "Encroachment & Town Planning": [
        ("Permanent illegal concrete kiosk erected on footpath", "Commercial shop extended 8 feet onto public sidewalk blocking pedestrian passage.", "Footpath Encroachment", "high", 3.8),
        ("Illegal multistory commercial construction without setback", "Building continuing without statutory 3-meter fire setback in violation of bye-laws.", "Unauthorized Construction", "critical", 2.5),
        ("Hawkers completely blocking fire tender access lane", "Unauthorized stalls pitched along market lane preventing ambulance movement.", "Market Lane Obstruction", "high", 2.0),
        ("Illegal compound wall constructed across public right of way", "Private developer fenced off dedicated public access road connecting colonies.", "Public Right-of-Way Seizure", "critical", 2.2),
        ("Unauthorized rooftop cell tower installed on weak building", "Heavy mobile transmission tower erected on 50-year-old unreinforced roof.", "Unapproved Structure", "high", 3.2),
        ("Vehicle parking encroaching on pedestrian refuge island", "Commercial valet service using public median island as private vehicle stand.", "Refuge Island Encroachment", "medium", 3.5),
    ],
}

MUNICIPAL_WARDS = [
    ("Ward 14 (Central)", "Zone A (Central)", 12.9716, 77.5946),
    ("Ward 22 (Indiranagar)", "Zone B (East)", 12.9784, 77.6408),
    ("Ward 35 (Koramangala)", "Zone C (South)", 12.9352, 77.6245),
    ("Ward 48 (Whitefield)", "Zone D (East Outer)", 12.9698, 77.7500),
    ("Ward 56 (Jayanagar)", "Zone C (South)", 12.9308, 77.5838),
    ("Ward 63 (Malleshwaram)", "Zone E (North)", 13.0031, 77.5700),
    ("Ward 72 (Hebbal)", "Zone E (North)", 13.0358, 77.5970),
    ("Ward 81 (Rajajinagar)", "Zone F (West)", 12.9982, 77.5530),
]


def generate_benchmark_dataset(size: int = 500, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a high-fidelity synthetic municipal research dataset of specified size.
    The distribution mirrors real-world municipal grievance dynamics:
    - 8 categories
    - Strict department assignments
    - Realistic duration regression targets (log-normal distribution)
    - Realistic SLA breach outcomes based on priority, workload, and duration
    - Synthetic duplicate pairs (exact and paraphrased) for duplicate detection evaluation
    """
    rng = random.Random(random_state)
    records: List[Dict[str, Any]] = []

    categories = list(CATEGORY_TEMPLATES.keys())
    base_time = datetime(2026, 8, 1, 9, 0, 0, tzinfo=timezone.utc)

    # We generate (size - 40) base records, then inject 20 duplicate pairs (40 records total)
    base_count = size - 40

    for i in range(base_count):
        cat = categories[i % len(categories)]
        templates = CATEGORY_TEMPLATES[cat]
        title_tmpl, desc_tmpl, subcat, prio, base_dur = rng.choice(templates)

        ward, zone, base_lat, base_lng = rng.choice(MUNICIPAL_WARDS)
        # Jitter coordinates within ~500m
        lat = round(base_lat + rng.uniform(-0.005, 0.005), 6)
        lng = round(base_lng + rng.uniform(-0.005, 0.005), 6)

        dept_id = CATEGORY_TO_DEPARTMENT.get(cat, "dept_pwd")
        dept_name = STANDARD_DEPARTMENTS[dept_id]["name"]
        sla_hours = PRIORITY_SLA_HOURS[prio]

        # Time offsets
        submit_time = base_time + timedelta(
            days=i * 0.2 + rng.uniform(0, 1),
            hours=rng.randint(0, 12),
            minutes=rng.randint(0, 59),
        )

        # Expected duration in days (derived from priority and SLA)
        expected_dur = round(sla_hours / 24.0 * rng.uniform(0.7, 0.95), 2)

        # Actual duration generation with log-normal noise
        # Critical cases resolve faster, but complex ones suffer delays
        noise = rng.gauss(0, 0.35)
        simulated_dur = base_dur * math.exp(noise)
        actual_dur = round(max(0.5, simulated_dur), 2)

        # SLA breach determination:
        # Breach occurs if actual duration > sla_hours / 24.0
        sla_deadline_days = sla_hours / 24.0
        sla_breached = bool(actual_dur > sla_deadline_days)

        records.append({
            "id": f"BENCH-{2026}-{i+1:04d}",
            "title": title_tmpl,
            "description": desc_tmpl,
            "category": cat,
            "subcategory": subcat,
            "department_id": dept_id,
            "department_name": dept_name,
            "priority": prio,
            "ward": ward,
            "zone": zone,
            "latitude": lat,
            "longitude": lng,
            "submitted_at": submit_time.isoformat(),
            "expected_duration_days": expected_dur,
            "actual_duration_days": actual_dur,
            "sla_hours": sla_hours,
            "sla_deadline_days": sla_deadline_days,
            "sla_breached": sla_breached,
            "is_duplicate": False,
            "duplicate_of": None,
        })

    # Now inject 20 duplicate pairs (40 records) to test duplicate detection
    for dup_idx in range(20):
        # Pick an existing record to duplicate
        target = rng.choice(records[:base_count])
        orig_id = target["id"]

        # Duplicate 1: Direct duplicate with slight phrasing jitter
        dup_lat = round(target["latitude"] + rng.uniform(-0.0003, 0.0003), 6)  # within ~35 meters
        dup_lng = round(target["longitude"] + rng.uniform(-0.0003, 0.0003), 6)

        records.append({
            "id": f"BENCH-{2026}-DUP-{dup_idx*2+1:03d}",
            "title": f"Report: {target['title']}",
            "description": f"Same issue observed. {target['description']} Please fix immediately.",
            "category": target["category"],
            "subcategory": target["subcategory"],
            "department_id": target["department_id"],
            "department_name": target["department_name"],
            "priority": target["priority"],
            "ward": target["ward"],
            "zone": target["zone"],
            "latitude": dup_lat,
            "longitude": dup_lng,
            "submitted_at": target["submitted_at"],
            "expected_duration_days": target["expected_duration_days"],
            "actual_duration_days": target["actual_duration_days"],
            "sla_hours": target["sla_hours"],
            "sla_deadline_days": target["sla_deadline_days"],
            "sla_breached": target["sla_breached"],
            "is_duplicate": True,
            "duplicate_of": orig_id,
        })

        # Duplicate 2: Paraphrased complaint for semantic embedding match
        records.append({
            "id": f"BENCH-{2026}-DUP-{dup_idx*2+2:03d}",
            "title": f"Resident complaint: {target['subcategory']}",
            "description": f"Urgent municipal attention needed at {target['ward']}. {target['description']}",
            "category": target["category"],
            "subcategory": target["subcategory"],
            "department_id": target["department_id"],
            "department_name": target["department_name"],
            "priority": target["priority"],
            "ward": target["ward"],
            "zone": target["zone"],
            "latitude": dup_lat,
            "longitude": dup_lng,
            "submitted_at": target["submitted_at"],
            "expected_duration_days": target["expected_duration_days"],
            "actual_duration_days": target["actual_duration_days"],
            "sla_hours": target["sla_hours"],
            "sla_deadline_days": target["sla_deadline_days"],
            "sla_breached": target["sla_breached"],
            "is_duplicate": True,
            "duplicate_of": orig_id,
        })

    df = pd.DataFrame(records)
    df["full_text"] = df.apply(
        lambda r: combine_title_description(r["title"], r["description"]), axis=1
    )
    return df


BENCHMARK_RESEARCH_DATASET_v1 = generate_benchmark_dataset(size=500, random_state=42)
