from app.models.entities import Lead, WebsiteStatus

LOCAL_SERVICE_HINTS = (
    "dentist",
    "clinic",
    "salon",
    "restaurant",
    "repair",
    "plumber",
    "electrician",
    "lawyer",
    "real estate",
    "spa",
    "gym",
    "hotel",
)


def calculate_seo_score(lead: Lead) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []
    if lead.website_status == WebsiteStatus.NO_WEBSITE:
        score += 50
        reasons.append("no website found")
    if lead.website_status == WebsiteStatus.SOCIAL_ONLY:
        score += 30
        reasons.append("only social/profile website found")
    if lead.website_status == WebsiteStatus.BAD_WEBSITE:
        score += 25
        reasons.append("website appears broken, slow, non-HTTPS, or unavailable")
    if lead.phone_normalized:
        score += 15
        reasons.append("phone available")
    if lead.rating and lead.rating > 4.0:
        score += 10
        reasons.append(f"{lead.rating:.1f} rating")
    if lead.review_count and lead.review_count > 20:
        score += 10
        reasons.append(f"{lead.review_count} reviews")
    if lead.business_status == "OPERATIONAL":
        score += 10
        reasons.append("active business")
    category = (lead.category or "").lower()
    if any(hint in category for hint in LOCAL_SERVICE_HINTS):
        score += 10
        reasons.append("strong local service category")
    return min(score, 100), ", ".join(reasons).capitalize() + "."
