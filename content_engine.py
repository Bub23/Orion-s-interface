import json
import os
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional


class PlatformFormatter:
    """Formats content for different social media platforms."""

    PLATFORM_SPECS = {
        "tiktok": {
            "max_chars": 2200,
            "max_hashtags": 30,
            "title": "TikTok",
            "description": "Short video platform - focus on hooks and trend awareness",
        },
        "facebook": {
            "max_chars": 63206,
            "max_hashtags": 30,
            "title": "Facebook",
            "description": "Long-form content - community and engagement focused",
        },
        "instagram": {
            "max_chars": 2200,
            "max_hashtags": 30,
            "title": "Instagram",
            "description": "Visual platform - short captions with hashtags",
        },
        "threads": {
            "max_chars": 500,
            "max_hashtags": 5,
            "title": "Threads",
            "description": "Twitter alternative - concise, threaded conversations",
        },
        "youtube": {
            "max_chars": 5000,
            "max_hashtags": 15,
            "title": "YouTube",
            "description": "Video platform - detailed descriptions with timestamps",
        },
    }

    @staticmethod
    def format_for_platform(content: str, platform: str) -> Dict[str, Any]:
        """Format content for a specific platform."""
        if platform not in PlatformFormatter.PLATFORM_SPECS:
            return {"error": f"Unknown platform: {platform}"}

        spec = PlatformFormatter.PLATFORM_SPECS[platform]
        formatted = content[: spec["max_chars"]]

        return {
            "platform": platform,
            "title": spec["title"],
            "formatted_content": formatted,
            "char_count": len(formatted),
            "max_chars": spec["max_chars"],
            "is_truncated": len(content) > spec["max_chars"],
        }

    @staticmethod
    def format_all_platforms(content: str) -> Dict[str, Dict[str, Any]]:
        """Format content for all platforms."""
        return {
            platform: PlatformFormatter.format_for_platform(content, platform)
            for platform in PlatformFormatter.PLATFORM_SPECS.keys()
        }


class ContentStorage:
    """Manages local JSON storage for content drafts."""

    def __init__(self, storage_path: str = "data/content_history.json"):
        self.storage_path = storage_path
        self._ensure_storage_dir()
        self._ensure_storage_file()

    def _ensure_storage_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        directory = os.path.dirname(self.storage_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _ensure_storage_file(self) -> None:
        """Create storage file if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump({"version": "1.0", "drafts": []}, f, indent=2)

    def _read_storage(self) -> Dict[str, Any]:
        """Read the storage file."""
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"version": "1.0", "drafts": []}

    def _write_storage(self, data: Dict[str, Any]) -> None:
        """Write to the storage file."""
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def save_draft(
        self,
        content: str,
        platforms: Optional[List[str]] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Save a content draft."""
        draft_id = str(uuid4())
        timestamp = datetime.now().isoformat()

        if platforms is None:
            platforms = list(PlatformFormatter.PLATFORM_SPECS.keys())

        formatted_content = {
            platform: PlatformFormatter.format_for_platform(content, platform)
            for platform in platforms
        }

        draft = {
            "id": draft_id,
            "title": title or f"Draft {timestamp[:10]}",
            "content": content,
            "formatted": formatted_content,
            "platforms": platforms,
            "created_at": timestamp,
            "updated_at": timestamp,
            "metadata": metadata or {},
        }

        storage = self._read_storage()
        storage["drafts"].append(draft)
        self._write_storage(storage)

        return draft

    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific draft by ID."""
        storage = self._read_storage()
        for draft in storage["drafts"]:
            if draft["id"] == draft_id:
                return draft
        return None

    def get_all_drafts(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        platform_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all drafts with optional filtering."""
        storage = self._read_storage()
        drafts = storage["drafts"]

        if platform_filter:
            drafts = [d for d in drafts if platform_filter in d["platforms"]]

        total = len(drafts)
        drafts = sorted(drafts, key=lambda x: x["created_at"], reverse=True)

        paginated = drafts[offset : offset + limit] if limit else drafts

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "drafts": paginated,
        }

    def update_draft(
        self, draft_id: str, content: str, title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an existing draft."""
        storage = self._read_storage()

        for draft in storage["drafts"]:
            if draft["id"] == draft_id:
                draft["content"] = content
                if title:
                    draft["title"] = title
                draft["updated_at"] = datetime.now().isoformat()
                draft["formatted"] = {
                    platform: PlatformFormatter.format_for_platform(content, platform)
                    for platform in draft["platforms"]
                }
                self._write_storage(storage)
                return draft

        return None

    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft."""
        storage = self._read_storage()
        initial_count = len(storage["drafts"])

        storage["drafts"] = [d for d in storage["drafts"] if d["id"] != draft_id]
        self._write_storage(storage)

        return len(storage["drafts"]) < initial_count

    def search_drafts(self, query: str) -> List[Dict[str, Any]]:
        """Search drafts by title or content."""
        storage = self._read_storage()
        query = query.lower()

        results = [
            d
            for d in storage["drafts"]
            if query in d["title"].lower() or query in d["content"].lower()
        ]

        return sorted(results, key=lambda x: x["created_at"], reverse=True)


class JsonDraftStorage:
    """Small JSON store for manual-review revenue workflows."""

    def __init__(self, storage_path: str, root_key: str):
        self.storage_path = storage_path
        self.root_key = root_key
        self._ensure_storage_dir()
        self._ensure_storage_file()

    def _ensure_storage_dir(self) -> None:
        directory = os.path.dirname(self.storage_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _ensure_storage_file(self) -> None:
        if not os.path.exists(self.storage_path):
            self._write({"version": "1.0", self.root_key: []})

    def _read(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = {"version": "1.0", self.root_key: []}
        data.setdefault(self.root_key, [])
        return data

    def _write(self, data: Dict[str, Any]) -> None:
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def save(self, item: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read()
        data[self.root_key].append(item)
        self._write(data)
        return item

    def all(self) -> List[Dict[str, Any]]:
        return sorted(
            self._read()[self.root_key],
            key=lambda item: item.get("created_at", ""),
            reverse=True,
        )

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        for item in self._read()[self.root_key]:
            if item.get("id") == item_id:
                return item
        return None


class CampaignDraftEngine:
    """Generates safe campaign drafts for manual approval."""

    def __init__(self, storage_path: str = "data/campaign_history.json"):
        self.storage = JsonDraftStorage(storage_path, "campaigns")

    def create_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = str(payload.get("title", "")).strip()
        goal = str(payload.get("goal", "")).strip()
        offer = str(payload.get("offer", "")).strip()
        audience = str(payload.get("audience", "")).strip()
        platforms = payload.get("platforms") or []

        if not title or not goal or not offer or not audience:
            return {"error": "title, goal, offer, and audience are required"}

        if not isinstance(platforms, list) or not platforms:
            platforms = ["facebook", "instagram", "tiktok", "youtube", "threads"]

        campaign = {
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "title": title,
            "goal": goal,
            "offer": offer,
            "audience": audience,
            "platforms": platforms,
            "status": "draft",
            "review_status": "manual_review",
            "generated_posts": self._posts(title, goal, offer, audience, platforms),
            "followup_messages": self._followups(offer, audience),
            "lead_angles": self._lead_angles(goal, offer, audience),
            "cta_options": self._ctas(offer),
        }
        return self.storage.save(campaign)

    def history(self) -> Dict[str, Any]:
        campaigns = self.storage.all()
        return {"total": len(campaigns), "campaigns": campaigns}

    def get(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        return self.storage.get(campaign_id)

    def _posts(self, title, goal, offer, audience, platforms):
        return [
            {
                "platform": platform,
                "status": "draft",
                "review_status": "manual_review",
                "copy": (
                    f"{title}: {audience} needs a cleaner path to {goal}. "
                    f"{offer} is built to move fast without guessing. Message manually to review the next step."
                ),
            }
            for platform in platforms
        ]

    def _followups(self, offer, audience):
        return [
            f"Quick follow-up for {audience}: still want the direct path for {offer}?",
            f"If timing is tight, I can send the short version of how {offer} works.",
        ]

    def _lead_angles(self, goal, offer, audience):
        return [
            f"Help {audience} reach {goal} faster.",
            f"Position {offer} as the no-fluff next move.",
            f"Lead with the cost of waiting, then offer the manual next step.",
        ]

    def _ctas(self, offer):
        return [
            f"Reply manually if you want {offer}.",
            "Send me the details and I will map the next move.",
            "Book a quick review before this window closes.",
        ]


class LeadDraftEngine:
    """Creates manual copy/paste lead messages without automation."""

    def __init__(self, storage_path: str = "data/lead_history.json"):
        self.storage = JsonDraftStorage(storage_path, "leads")

    def draft_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        business_type = str(payload.get("business_type", "")).strip()
        target_customer = str(payload.get("target_customer", "")).strip()
        offer = str(payload.get("offer", "")).strip()
        pain_point = str(payload.get("pain_point", "")).strip()
        tone = str(payload.get("tone", "professional")).strip() or "professional"
        platform = str(payload.get("platform", "facebook")).strip() or "facebook"

        if not business_type or not target_customer or not offer or not pain_point:
            return {"error": "business_type, target_customer, offer, and pain_point are required"}

        opener = "Blunt version" if tone.lower() == "blunt" else "Quick question"

        return {
            "business_type": business_type,
            "target_customer": target_customer,
            "offer": offer,
            "pain_point": pain_point,
            "tone": tone,
            "platform": platform,
            "generated_message": (
                f"{opener}: are you still dealing with {pain_point}? "
                f"I help {target_customer} through {business_type} with {offer}. "
                "If it makes sense, I can send the short version here for manual review."
            ),
            "followup_1": f"Following up once: want the short breakdown for {offer}?",
            "followup_2": "Last touch from me. If this is not a fit, no problem.",
            "status": "draft",
            "review_status": "manual_review",
        }

    def save(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        draft = self.draft_message(payload)
        if "error" in draft:
            return draft
        draft["id"] = str(uuid4())
        draft["created_at"] = datetime.now().isoformat()
        return self.storage.save(draft)

    def history(self) -> Dict[str, Any]:
        leads = self.storage.all()
        return {"total": len(leads), "leads": leads}


class EmpireQueueEngine:
    """Manual approval posting queue for empire content assets."""

    def __init__(self, storage_path: str = "data/empire_queue.json"):
        self.storage = JsonDraftStorage(storage_path, "queue")

    def create_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "title": str(payload.get("title", "Empire Draft")).strip() or "Empire Draft",
            "platform": str(payload.get("platform", "manual")).strip() or "manual",
            "content_type": str(payload.get("content_type", "post")).strip() or "post",
            "body": payload.get("body", payload.get("content", "")),
            "metadata": payload.get("metadata", {}),
            "status": "draft",
            "review_status": "manual_review",
            "approved": False,
        }
        return self.storage.save(item)

    def history(self) -> Dict[str, Any]:
        queue = self.storage.all()
        return {"total": len(queue), "queue": queue}

    def mark_approved(self, item_id: str) -> Optional[Dict[str, Any]]:
        data = self.storage._read()
        for item in data[self.storage.root_key]:
            if item.get("id") == item_id:
                item["approved"] = True
                item["status"] = "approved"
                item["review_status"] = "manual_approved"
                item["updated_at"] = datetime.now().isoformat()
                self.storage._write(data)
                return item
        return None


class ContentEngine:
    """Main content engine orchestrator."""

    def __init__(self, storage_path: str = "data/content_history.json"):
        self.storage = ContentStorage(storage_path)
        self.formatter = PlatformFormatter()

    def create_content(
        self,
        content: str,
        title: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create and save a new content draft."""
        if not content.strip():
            return {"error": "Content cannot be empty"}

        draft = self.storage.save_draft(
            content=content, platforms=platforms, title=title, metadata=metadata
        )

        return {
            "success": True,
            "draft_id": draft["id"],
            "title": draft["title"],
            "platforms": draft["platforms"],
            "content": draft["content"],
            "created_at": draft["created_at"],
        }

    def get_content_history(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        platform_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve content history."""
        history = self.storage.get_all_drafts(
            limit=limit, offset=offset, platform_filter=platform_filter
        )

        return {
            "total": history["total"],
            "offset": history["offset"],
            "limit": history["limit"],
            "drafts": history["drafts"],
        }

    def get_platform_pack(self, draft_id: str) -> Dict[str, Any]:
        """Get platform-specific versions of a draft."""
        draft = self.storage.get_draft(draft_id)

        if not draft:
            return {"error": f"Draft not found: {draft_id}"}

        return {
            "draft_id": draft_id,
            "title": draft["title"],
            "original_content": draft["content"],
            "platforms": draft["formatted"],
        }

    def search_content(self, query: str) -> Dict[str, Any]:
        """Search content by title or content."""
        results = self.storage.search_drafts(query)

        return {
            "query": query,
            "total_results": len(results),
            "drafts": results,
        }

    def get_draft_details(self, draft_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific draft."""
        draft = self.storage.get_draft(draft_id)

        if not draft:
            return {"error": f"Draft not found: {draft_id}"}

        return draft
