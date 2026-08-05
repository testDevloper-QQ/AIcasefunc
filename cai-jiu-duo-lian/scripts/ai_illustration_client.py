"""OpenAI-compatible image generation for hand-journal recipe illustrations."""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MAX_CANDIDATES = 3

STYLE_PREFIX = (
    "Chinese food journal scrapbook illustration on warm cream paper (#FFF8E7), "
    "soft digital watercolor and colored marker strokes, cozy hand-drawn food art, "
    "appetizing, gentle shadows, organic brush lines, no text, no letters, no watermark, "
    "not a photo, not flat vector icons"
)

INGREDIENT_LINE_ART_PREFIX = (
    "Single food ingredient hand-drawn line art icon on warm cream paper (#FFF8E7), "
    "clean brown ink outlines (#5C4F42) with soft watercolor wash fill, "
    "centered isolated subject, journal recipe card style, "
    "no text, no letters, no watermark, not a photo, not 3D render"
)


def _openai_config() -> tuple[str, str, str] | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_IMAGE_MODEL", "dall-e-3").strip() or "dall-e-3"
    return key, base, model


def build_dish_prompt(recipe: dict[str, Any]) -> str:
    name = recipe.get("name") or "家常菜"
    method = recipe.get("method") or ""
    tags = "、".join(recipe.get("tags") or [])
    ingredients = "、".join(
        i.get("name", "") for i in (recipe.get("ingredients") or [])[:8] if i.get("name")
    )
    parts = [f"Finished dish hero illustration: {name}."]
    if method:
        parts.append(f"Cooking style: {method}.")
    if ingredients:
        parts.append(f"Visible ingredients: {ingredients}.")
    if tags:
        parts.append(f"Mood: {tags}.")
    parts.append("Single centered plated dish, generous portion, inviting presentation.")
    return f"{STYLE_PREFIX}. {' '.join(parts)}"


def build_step_prompt(recipe: dict[str, Any], step_index: int, step_text: str) -> str:
    name = recipe.get("name") or "家常菜"
    return (
        f"{STYLE_PREFIX}. "
        f"Recipe cooking step scene for 「{name}」, step {step_index}: {step_text}. "
        "Small narrative kitchen illustration showing the action clearly, "
        "composition suitable for left column of a recipe card. "
        "Chinese home cooking context; metric units (℃/克/毫升) only; "
        "no nutrition labels, no calorie tables, no text overlays."
    )


def build_ingredient_prompt(name: str, art_key: str) -> str:
    return (
        f"{INGREDIENT_LINE_ART_PREFIX}. "
        f"Ingredient: {name} ({art_key}). "
        "Recognizable single item for a recipe ingredient grid, square composition."
    )


def _download_bytes(url: str, timeout: float = 60.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "CaiJiuDuoLian/1.7"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _generate_one(prompt: str, *, size: str, model: str, key: str, base: str) -> bytes:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    if model.startswith("dall-e-3"):
        payload["quality"] = os.environ.get("OPENAI_IMAGE_QUALITY", "standard")

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/images/generations",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    item = (body.get("data") or [{}])[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        return _download_bytes(item["url"])
    raise RuntimeError("image API returned no b64_json or url")


def generate_image_candidates(
    prompt: str,
    *,
    candidates: int = 1,
    size: str | None = None,
) -> list[bytes]:
    """Generate up to MAX_CANDIDATES (3) image bytes for one prompt."""
    cfg = _openai_config()
    if not cfg:
        raise RuntimeError("OPENAI_API_KEY 未配置，无法调用 AI 出图")

    key, base, model = cfg
    n = min(max(1, candidates), MAX_CANDIDATES)
    img_size = size or os.environ.get("OPENAI_IMAGE_SIZE", "1024x1024")

    results: list[bytes] = []
    for i in range(n):
        variant_prompt = prompt if i == 0 else f"{prompt} Slight composition variant {i + 1}."
        results.append(_generate_one(variant_prompt, size=img_size, model=model, key=key, base=base))
    return results


def select_best_candidate(paths: list[Path]) -> Path:
    """Pick one candidate without vision API — largest PNG usually has more detail."""
    existing = [p for p in paths if p.is_file() and p.stat().st_size > 0]
    if not existing:
        raise FileNotFoundError("no candidate images on disk")
    if len(existing) == 1:
        return existing[0]
    return max(existing, key=lambda p: p.stat().st_size)


def save_png(data: bytes, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path
