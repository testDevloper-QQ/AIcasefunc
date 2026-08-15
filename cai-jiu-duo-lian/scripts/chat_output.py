"""Render recommend JSON for chat hosts (WorkBuddy present_files / Cursor markdown / HTTP)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CIRCLED = ("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩")

# WorkBuddy: Markdown does not render ![](local path); use present_files.
# Cursor / others may use path or http inline markdown.
IMAGE_MODES = ("present", "path", "http")
PRESENT_FILES_START = "<!-- PRESENT_FILES"
PRESENT_FILES_END = "PRESENT_FILES -->"


def asset_url_to_path(url: str | None, skill_root: Path) -> str:
    """Map /skill-assets/... URL to absolute PNG path."""
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
    if mode == "present":
        return asset_url_to_path(url, skill_root)
    if mode == "http":
        return asset_url_to_http(url, skill_root, base_url) or asset_url_to_path(url, skill_root)
    return asset_url_to_path(url, skill_root)


def _step_label(index: int) -> str:
    if 1 <= index <= len(_CIRCLED):
        return _CIRCLED[index - 1]
    return f"{index}."


def _append_present_item(
    items: list[dict[str, str]],
    *,
    role: str,
    label: str,
    path: str,
    recipe: str,
) -> None:
    if not path:
        return
    items.append({"role": role, "label": label, "path": path, "recipe": recipe})


def collect_recipe_present_files(
    recipe: dict[str, Any],
    skill_root: Path,
    *,
    heading: str = "推荐",
) -> list[dict[str, str]]:
    """Ordered PNG list for WorkBuddy present_files (hero → ingredients → steps)."""
    name = recipe.get("name") or "家常菜"
    recipe_key = f"{heading}:{name}"
    items: list[dict[str, str]] = []

    hero_url = recipe.get("heroIllustrationUrl") or recipe.get("heroCompositeUrl") or ""
    hero_src = asset_url_to_path(hero_url, skill_root)
    _append_present_item(items, role="hero", label=f"{name} 成品", path=hero_src, recipe=recipe_key)

    for ing in recipe.get("ingredients") or []:
        iname = ing.get("name") or ""
        art_src = asset_url_to_path(ing.get("artUrl"), skill_root)
        _append_present_item(items, role="ingredient", label=iname or "食材", path=art_src, recipe=recipe_key)

    for i, step in enumerate(recipe.get("steps") or [], start=1):
        step_url = step.get("stepIllustrationUrl") or step.get("stepArtUrl") or ""
        step_src = asset_url_to_path(step_url, skill_root)
        _append_present_item(
            items,
            role="step",
            label=f"步骤{i}",
            path=step_src,
            recipe=recipe_key,
        )
    return items


def collect_recommend_present_files(
    result: dict[str, Any],
    skill_root: Path,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    primary = result.get("primary")
    if primary:
        items.extend(collect_recipe_present_files(primary, skill_root, heading="推荐"))
    for idx, alt in enumerate(result.get("alternates") or [], start=1):
        items.extend(collect_recipe_present_files(alt, skill_root, heading=f"备选 {idx}"))
    return items


def format_present_files_block(items: list[dict[str, str]]) -> str:
    """Machine-readable block: Agent must call present_files with paths[] in order."""
    paths = [x["path"] for x in items if x.get("path")]
    payload = {
        "tool": "present_files",
        "instruction": (
            "WorkBuddy Markdown does not render local image embeds. "
            "Call present_files with paths in order; do not rely on sidebar-only attachments. "
            "User-visible text is the markdown above this block."
        ),
        "paths": paths,
        "items": items,
    }
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"{PRESENT_FILES_START}\n{body}\n{PRESENT_FILES_END}\n"


def render_recipe_markdown(
    recipe: dict[str, Any],
    skill_root: Path,
    *,
    heading: str = "推荐",
    image_mode: str = "present",
    base_url: str = "http://127.0.0.1:8765",
) -> str:
    """One recipe: text structure; images via present_files / markdown / http by mode."""
    if image_mode not in IMAGE_MODES:
        image_mode = "present"

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
    if image_mode == "present":
        if hero_src:
            lines.extend([f"*成品配图 → present_files（{name} 成品）*", ""])
        else:
            lines.extend(["*(成品插画待生成 — 须先完成 Step 4.6 补图)*", ""])
    elif hero_src:
        lines.extend([f"![{name} 成品]({hero_src})", ""])
    else:
        lines.extend(["*(成品插画待生成 — 须先完成 Step 4.6 补图)*", ""])

    lines.append(f"### 🥬 食材（{servings} 人份）")
    lines.append("")
    for ing in recipe.get("ingredients") or []:
        iname = ing.get("name") or ""
        amount = ing.get("amount") or ""
        art_src = _pick_image_src(ing.get("artUrl"), skill_root, mode=image_mode, base_url=base_url)
        if image_mode == "present":
            if art_src:
                lines.append(f"- **{iname}** {amount} *(配图 → present_files)*")
            else:
                lines.append(f"- **{iname}** {amount}")
        else:
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
        if image_mode == "present":
            if step_src:
                lines.append(f"*步骤{i}配图 → present_files*")
            lines.append(f"**{label}** {text}")
            if not step_src:
                lines.append("*(步骤插画待生成)*")
        else:
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
    image_mode: str = "present",
    base_url: str = "http://127.0.0.1:8765",
) -> str:
    """Primary + alternates as chat markdown; present mode appends present_files block."""
    if image_mode not in IMAGE_MODES:
        image_mode = "present"

    parts: list[str] = []
    primary = result.get("primary")
    if primary:
        parts.append(
            render_recipe_markdown(
                primary, skill_root, heading="推荐", image_mode=image_mode, base_url=base_url
            )
        )
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
    body = "\n---\n\n".join(p for p in parts if p.strip())

    if image_mode == "present":
        items = collect_recommend_present_files(result, skill_root)
        body = body.rstrip() + "\n\n" + format_present_files_block(items)
    return body
