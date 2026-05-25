import json
import os
from datetime import datetime
from uuid import uuid4


DATA_DIR = "data"
OFFER_PATH = os.path.join(DATA_DIR, "offers.json")
LEAD_PATH = os.path.join(DATA_DIR, "leads.json")
FOLLOWUP_PATH = os.path.join(DATA_DIR, "followups.json")
REPORT_PATH = os.path.join(DATA_DIR, "revenue_report.json")
LEAD_STATUSES = {"new", "contacted", "interested", "quoted", "closed", "lost"}


def _ensure_file(path, root_key):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"version": "1.0", root_key: []}, f, indent=2)


def _read(path, root_key):
    _ensure_file(path, root_key)
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {"version": "1.0", root_key: []}
    data.setdefault(root_key, [])
    return data


def _write(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def create_offer(payload):
    data = _read(OFFER_PATH, "offers")
    offer = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "title": str(payload.get("title", "")).strip(),
        "audience": str(payload.get("audience", "")).strip(),
        "problem": str(payload.get("problem", "")).strip(),
        "solution": str(payload.get("solution", "")).strip(),
        "price": str(payload.get("price", "")).strip(),
        "deliverables": str(payload.get("deliverables", "")).strip(),
        "cta": str(payload.get("cta", "Book a manual review call.")).strip(),
        "status": "draft",
        "review_status": "manual_review",
    }
    if not offer["title"] or not offer["audience"]:
        return {"error": "title and audience are required"}
    data["offers"].append(offer)
    _write(OFFER_PATH, data)
    return offer


def create_lead(payload):
    data = _read(LEAD_PATH, "leads")
    status = str(payload.get("status", "new")).strip().lower()
    lead = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "name": str(payload.get("name", "")).strip(),
        "business": str(payload.get("business", "")).strip(),
        "platform": str(payload.get("platform", "")).strip(),
        "need": str(payload.get("need", "")).strip(),
        "offer_id": str(payload.get("offer_id", "")).strip(),
        "estimated_value": float(payload.get("estimated_value") or 0),
        "status": status if status in LEAD_STATUSES else "new",
        "notes": str(payload.get("notes", "")).strip(),
    }
    if not lead["name"] and not lead["business"]:
        return {"error": "name or business is required"}
    data["leads"].append(lead)
    _write(LEAD_PATH, data)
    return lead


def get_leads():
    leads = sorted(_read(LEAD_PATH, "leads")["leads"], key=lambda x: x.get("updated_at", ""), reverse=True)
    return {"total": len(leads), "leads": leads, "statuses": sorted(LEAD_STATUSES)}


def update_lead(payload):
    lead_id = str(payload.get("id", "")).strip()
    updates = payload.get("updates") if isinstance(payload.get("updates"), dict) else {}
    data = _read(LEAD_PATH, "leads")
    for lead in data["leads"]:
        if lead.get("id") == lead_id:
            for field in ("name", "business", "platform", "need", "offer_id", "notes"):
                if field in updates:
                    lead[field] = str(updates.get(field, "")).strip()
            if "estimated_value" in updates:
                lead["estimated_value"] = float(updates.get("estimated_value") or 0)
            if "status" in updates:
                status = str(updates.get("status", "")).strip().lower()
                if status in LEAD_STATUSES:
                    lead["status"] = status
            lead["updated_at"] = datetime.now().isoformat()
            _write(LEAD_PATH, data)
            return lead
    return {"error": "Lead not found"}


def create_followup(payload):
    data = _read(FOLLOWUP_PATH, "followups")
    followup = {
        "id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "lead_id": str(payload.get("lead_id", "")).strip(),
        "due_at": str(payload.get("due_at", "")).strip(),
        "message": str(payload.get("message", "")).strip(),
        "channel": str(payload.get("channel", "manual")).strip(),
        "status": "manual_review",
        "done": False,
    }
    if not followup["message"]:
        return {"error": "message is required"}
    data["followups"].append(followup)
    _write(FOLLOWUP_PATH, data)
    return followup


def get_followups():
    followups = sorted(_read(FOLLOWUP_PATH, "followups")["followups"], key=lambda x: x.get("due_at", "") or x.get("created_at", ""))
    return {"total": len(followups), "followups": followups}


def mark_followup_done(payload):
    followup_id = str(payload.get("id", "")).strip()
    data = _read(FOLLOWUP_PATH, "followups")
    for followup in data["followups"]:
        if followup.get("id") == followup_id:
            followup["done"] = True
            followup["status"] = "done"
            followup["completed_at"] = datetime.now().isoformat()
            _write(FOLLOWUP_PATH, data)
            return followup
    return {"error": "Follow-up not found"}


def revenue_report():
    leads = _read(LEAD_PATH, "leads")["leads"]
    offers = _read(OFFER_PATH, "offers")["offers"]
    followups = _read(FOLLOWUP_PATH, "followups")["followups"]
    by_status = {status: 0 for status in sorted(LEAD_STATUSES)}
    pipeline_value = 0
    closed_value = 0
    for lead in leads:
        status = lead.get("status", "new")
        by_status[status] = by_status.get(status, 0) + 1
        value = float(lead.get("estimated_value") or 0)
        if status == "closed":
            closed_value += value
        elif status != "lost":
            pipeline_value += value
    report = {
        "generated_at": datetime.now().isoformat(),
        "offers": len(offers),
        "leads": len(leads),
        "lead_statuses": by_status,
        "pipeline_value": pipeline_value,
        "closed_value": closed_value,
        "open_followups": len([f for f in followups if not f.get("done")]),
        "manual_only": True,
    }
    _write(REPORT_PATH, {"version": "1.0", "reports": [report]})
    return report
