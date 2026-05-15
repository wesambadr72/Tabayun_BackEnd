from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


DEMO_COUNTRIES = ["uk", "de"]

DEMO_CATEGORIES = [
    {
        "id": 1,
        "name": "traffic",
        "description": "قواعد المرور والمخالفات اليومية للسائح.",
        "icon": "car",
    },
    {
        "id": 2,
        "name": "visa_residency",
        "description": "أنظمة التأشيرات والإقامة ومدة الزيارة.",
        "icon": "passport",
    },
    {
        "id": 3,
        "name": "public_decency",
        "description": "السلوك العام وما يجب فعله أو تجنبه.",
        "icon": "shield",
    },
    {
        "id": 4,
        "name": "food",
        "description": "القواعد المرتبطة بالأغذية والسلامة.",
        "icon": "utensils",
    },
]

DEMO_COMPARISONS = [
    {
        "id": 101,
        "title": "استخدام الهاتف أثناء القيادة",
        "simplified_description": "في السعودية يعد استخدام الهاتف أثناء القيادة مخالفة واضحة وقد يترتب عليها غرامة.",
        "summary": "تحقق من أنظمة المرور قبل القيادة، فبعض التفاصيل تختلف عن بلدك.",
        "category_id": 1,
        "foreign_country": "uk",
    },
    {
        "id": 102,
        "title": "الالتزام بالذوق العام في الأماكن العامة",
        "simplified_description": "السلوك العام في السعودية له ضوابط محددة، خصوصا في الأماكن العائلية والسياحية.",
        "summary": "بعض السلوكيات المألوفة في بلدك قد تكون مقيدة محليا.",
        "category_id": 3,
        "foreign_country": "de",
    },
    {
        "id": 103,
        "title": "مدة الإقامة ونوع التأشيرة",
        "simplified_description": "مدة الزيارة ونوع التأشيرة يحددان ما يسمح لك به داخل المملكة.",
        "summary": "راجع نوع التأشيرة قبل العمل أو التمديد أو التنقل لأغراض مختلفة.",
        "category_id": 2,
        "foreign_country": "uk",
    },
    {
        "id": 104,
        "title": "اشتراطات السلامة الغذائية",
        "simplified_description": "تختلف إجراءات سلامة الغذاء والتداول التجاري بين الدول.",
        "summary": "إذا كنت تبيع أو تنقل أغذية، تحقق من المتطلبات المحلية أولا.",
        "category_id": 4,
        "foreign_country": "de",
    },
]

DEMO_USERS_FILE = Path(__file__).resolve().parents[2] / ".demo_users.json"


def _read_users() -> list[dict[str, Any]]:
    if not DEMO_USERS_FILE.exists():
        return []
    try:
        return json.loads(DEMO_USERS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write_users(users: list[dict[str, Any]]) -> None:
    DEMO_USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "country": user["country"],
        "language": user.get("language", "Arabic"),
        "is_active": True,
        "is_verified": False,
        "is_admin": False,
        "role": "user",
    }


def register_user(user_in: Any) -> dict[str, Any]:
    payload = user_in.model_dump() if hasattr(user_in, "model_dump") else dict(user_in)
    email = payload["email"].lower()
    users = _read_users()
    if any(user["email"] == email for user in users):
        raise ValueError("The user with this email already exists in the system.")

    user = {
        "id": max([item["id"] for item in users], default=0) + 1,
        "email": email,
        "password": payload["password"],
        "full_name": payload["full_name"],
        "country": payload["country"],
        "language": payload.get("language") or "Arabic",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    users.append(user)
    _write_users(users)
    return _public_user(user)


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    normalized_email = email.lower()
    for user in _read_users():
        if user["email"] == normalized_email and user.get("password") == password:
            return _public_user(user)
    return None


def is_email_available(email: str) -> bool:
    normalized_email = email.lower()
    return all(user["email"] != normalized_email for user in _read_users())


def get_user(email: str) -> SimpleNamespace | None:
    normalized_email = email.lower()
    for user in _read_users():
        if user["email"] == normalized_email:
            return SimpleNamespace(**_public_user(user))
    return None


def get_priority_comparisons() -> list[dict[str, Any]]:
    return DEMO_COMPARISONS


def get_comparisons_by_category(category_id: int, country: str | None = None) -> list[dict[str, Any]]:
    results = [item for item in DEMO_COMPARISONS if item["category_id"] == category_id]
    if country:
        country_matches = [item for item in results if item["foreign_country"] == country]
        return country_matches or results
    return results


def get_comparison_detail(comparison_id: int) -> dict[str, Any] | None:
    item = next((comparison for comparison in DEMO_COMPARISONS if comparison["id"] == comparison_id), None)
    if not item:
        return None

    return {
        "id": item["id"],
        "title": item["title"],
        "summary": item["summary"],
        "comparison_text": item["summary"],
        "category_id": item["category_id"],
        "saudi_law": {
            "id": item["id"] * 10,
            "title": item["title"],
            "text": item["simplified_description"],
            "simplified_text": item["simplified_description"],
            "country": "sa",
            "category_id": item["category_id"],
            "source_url": "",
            "article_number": "Demo",
        },
        "foreign_law": {
            "id": item["id"] * 10 + 1,
            "title": item["title"],
            "text": item["summary"],
            "simplified_text": item["summary"],
            "country": item["foreign_country"],
            "category_id": item["category_id"],
            "source_url": "",
            "article_number": "Demo",
        },
    }
