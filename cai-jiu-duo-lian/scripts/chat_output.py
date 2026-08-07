"""Render recommend JSON as inline Markdown for Cursor / WorkBuddy chat (not sidebar-only)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

_CIRCLED = ("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩")


def asset_url_to_path(url: str | None, skill_root: Path) -> str:
    """Map /skill-assets/... URL to absolute PNG path for chat markdown."""
    if not url:
        return ""
    rel = str(url).replace("/skill-assets/", "").split("?", 1)[0].replace("\\", "/")
    path = (skill_root / rel).resolve()
    if path.is_file():
        return path.as_posix()
    return ""


def asset_url_to_http(url: str | None, skill_root: Path, base_url: str = "http://127.0.0.1:8765") -> str:
    if not url:
        return ""
    rel = str(url).replace("/skill-assets/", "").split("?", 1)[0]
    path = (skill_root / rel).resolve()
    if path.is_file():
        return f"{base_url.rstrip('/')}/skill-assets/{rel.replace(chr(92), '/')}"
    return ""


def _pick_image_src(url: str | None, skill_root: Path, *, mode: str, base_url: str) -> str:
    if mode == "http":
        return asset_url_to_http(url, skill_root, base_url) or asset_url_to_path(url, skill_root)
    return asset_url_to_path(url, skill_root)


def _step_label(index: int) -> str:
    if 1 <= index <= len(_CIRCLED):
        return _CIRCLED[index - 1]
    return f"{index}."


def render_recipe_markdown(
    recipe: dict[str, Any],
    skill_root: Path,
    *,
    heading: str = "推荐",
    image_mode: str = "path",
    base_url: str = "http://127.0.0.1:8765",
) -> str:
    """One recipe: hero above ingredients; step image above each step text."""
    name = recipe.get("name") or "家常菜"
    book = (recipe.get("source") or {}).get("book") or ""
    scene_tags = "、".join(recipe.get("tags") or []) or "快乐餐"
    time_d = recipe.get("cookTimeDisplay") or recipe.get("cookTime") or ""
    cost = recipe.get("cost") or "—"
    method = recipe.get("method") or "—"
    servings = recipe.get("servings") or "—"

    lines: list[str] = [
        f"## 🍳 {heading}：{name}",
        f"📖 出处：《{book}》· {scene_tags}",
        f"⏱ {time_d} · 💰 {cost} · 🔥 {method} · 👤 {servings} 人份",
        "",
    ]

    hero_url = recipe.get("heroIllustrationUrl") or recipe.get("heroCompositeUrl") or ""
    hero_src = _pick_image_src(hero_url, skill_root, mode=image_mode, base_url=base_url)
    if hero_src:
        lines.extend([f"![{name} 成品]({hero_src})", ""])
    else:
        lines.extend(["*(成品插画待生成 — 须先完成 Step 4.6 补图)*", ""])

    lines.append(f"### 🥬 食材（{servings} 人份）")
    lines.append("")
    for ing in recipe.get("ingredients") or []:
        iname = ing.get("name") or ""
        amount = ing.get("amount") or ""
        art_src = _pick_image_src(ing.get("artUrl"), skill_root, mode=image_mode, base_url=base_url)
        if art_src:
            lines.append(f"![{iname}]({art_src})")
        lines.append(f"- **{iname}** {amount}")
        lines.append("")

    lines.append("### 👩‍🍳 做法")
    lines.append("")
    steps = recipe.get("steps") or []
    if not steps:
        lines.append("*(暂无步骤)*")
    for i, step in enumerate(steps, start=1):
        text = (step.get("text") or step.get("step") or "").strip()
        step_url = step.get("stepIllustrationUrl") or step.get("stepArtUrl") or ""
        step_src = _pick_image_src(step_url, skill_root, mode=image_mode, base_url=base_url)
        label = _step_label(i)
        if step_src:
            lines.append(f"![步骤{i}]({step_src})")
        lines.append(f"**{label}** {text}")
        if not step_src:
            lines.append("*(步骤插画待生成)*")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_recommend_markdown(
    result: dict[str, Any],
    skill_root: Path,
    *,
    image_mode: str = "path",
    base_url: str = "http://127.0.0.1:8765",
) -> str:
    """Primary + all alternates as inline markdown blocks."""
    parts: list[str] = []
    primary = result.get("primary")
    if primary:
        parts.append(render_recipe_markdown(primary, skill_root, heading="推荐", image_mode=image_mode, base_url=base_url))
    why = (result.get("why") or "").strip()
    if why:
        parts.append(f"**推荐理由：** {why}\n")

    alternates = result.get("alternates") or []
    for idx, alt in enumerate(alternates, start=1):
        parts.append(
            render_recipe_markdown(
                alt,
                skill_root,
                heading=f"备选 {idx}",
                image_mode=image_mode,
                base_url=base_url,
            )
        )
    return "\n---\n\n".join(p for p in parts if p.strip())
