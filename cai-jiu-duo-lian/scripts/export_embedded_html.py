"""Self-contained HTML export with base64 images (WorkBuddy HTML preview channel).

WorkBuddy preview panels often run on a different port than :8765, so
http://127.0.0.1:8765/skill-assets/... is blocked. Embedding data URIs avoids
cross-port loads. Do NOT use this as the default for the live web app.
"""
from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path
from typing import Any

from chat_output import asset_url_to_path, _step_label

# Soft warning only — Agent may still write larger files for one-off preview.
DEFAULT_WARN_BYTES = 12 * 1024 * 1024


def file_to_data_uri(path: Path) -> str:
    raw = path.read_bytes()
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def resolve_embed_src(url: str | None, skill_root: Path, *, embed: bool) -> str:
    path_str = asset_url_to_path(url, skill_root)
    if not path_str:
        return ""
    if not embed:
        return Path(path_str).as_uri()
    return file_to_data_uri(Path(path_str))


def _esc(text: Any) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def _img_tag(src: str, *, cls: str, alt: str) -> str:
    if not src:
        return f'<div class="{_esc(cls)} pending">待出图</div>'
    return f'<img class="{_esc(cls)}" src="{src}" alt="{_esc(alt)}" />'


def render_recipe_section(
    recipe: dict[str, Any],
    skill_root: Path,
    *,
    heading: str,
    embed: bool,
    include_ingredient_art: bool,
) -> tuple[str, int]:
    """Return (html_fragment, embedded_image_count)."""
    name = recipe.get("name") or "家常菜"
    book = (recipe.get("source") or {}).get("book") or ""
    tags = "、".join(recipe.get("tags") or []) or "快乐餐"
    time_d = recipe.get("cookTimeDisplay") or recipe.get("cookTime") or "—"
    cost = recipe.get("cost") or "—"
    method = recipe.get("method") or "—"
    servings = recipe.get("servings") or "—"
    count = 0

    hero_url = recipe.get("heroIllustrationUrl") or recipe.get("heroCompositeUrl") or ""
    hero_src = resolve_embed_src(hero_url, skill_root, embed=embed)
    if hero_src.startswith("data:"):
        count += 1

    ing_parts: list[str] = []
    for ing in recipe.get("ingredients") or []:
        iname = ing.get("name") or ""
        amount = ing.get("amount") or ""
        art_html = ""
        if include_ingredient_art:
            art_src = resolve_embed_src(ing.get("artUrl"), skill_root, embed=embed)
            if art_src.startswith("data:"):
                count += 1
            art_html = _img_tag(art_src, cls="ing-art", alt=iname)
        ing_parts.append(
            f'<div class="ing-tile">{art_html}'
            f'<span class="ing-name">{_esc(iname)}</span>'
            f'<span class="ing-amt">{_esc(amount)}</span></div>'
        )

    step_parts: list[str] = []
    for i, step in enumerate(recipe.get("steps") or [], start=1):
        text = (step.get("text") or step.get("step") or "").strip()
        step_url = step.get("stepIllustrationUrl") or step.get("stepArtUrl") or ""
        step_src = resolve_embed_src(step_url, skill_root, embed=embed)
        if step_src.startswith("data:"):
            count += 1
        label = _step_label(i)
        step_parts.append(
            f'<li class="step-card">'
            f'<div class="step-scene">{_img_tag(step_src, cls="step-art", alt=f"步骤{i}")}</div>'
            f'<p class="step-text"><span class="step-index">{_esc(label)}</span>{_esc(text)}</p>'
            f"</li>"
        )

    fragment = f"""
<article class="recipe-card">
  <p class="kicker">{_esc(heading)}</p>
  <h2>{_esc(name)}</h2>
  <p class="meta">📖 《{_esc(book)}》 · {_esc(tags)}</p>
  <p class="meta">⏱ {_esc(time_d)} · 💰 {_esc(cost)} · 🔥 {_esc(method)} · 👤 {_esc(servings)} 人份</p>
  {_img_tag(hero_src, cls="hero-art", alt=f"{name} 成品")}
  <h3>食材</h3>
  <div class="ing-grid">{"".join(ing_parts) or "<p>无</p>"}</div>
  <h3>做法</h3>
  <ol class="steps">{"".join(step_parts) or "<li>暂无步骤</li>"}</ol>
</article>
"""
    return fragment, count


_EMBEDDED_CSS = """
:root {
  --bg: #FFF8E7; --text: #4A4035; --muted: #8A7F72; --accent: #E8A838;
  --stroke: #5C4F42; --white: #fff;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 20px 16px 48px; max-width: 560px; margin-inline: auto;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text);
}
header { text-align: center; margin-bottom: 20px; }
header h1 { font-size: 1.75rem; margin: 0; transform: rotate(-1.5deg); }
header p { color: var(--muted); font-size: 0.9rem; }
.note {
  background: #fff8; border: 1px dashed var(--stroke); border-radius: 12px;
  padding: 10px 12px; font-size: 0.8rem; color: var(--muted); margin-bottom: 16px;
}
.recipe-card {
  background: var(--white); border: 2px solid var(--stroke); border-radius: 18px;
  padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(74,64,53,.08);
}
.kicker { color: var(--accent); font-size: 0.85rem; margin: 0 0 4px; }
h2 { margin: 0 0 8px; font-size: 1.45rem; }
h3 {
  display: inline-block; margin: 16px 0 10px; padding: 4px 10px;
  background: #111; color: #fff; border-radius: 6px; font-size: 0.95rem;
}
.meta { color: var(--muted); font-size: 0.88rem; margin: 4px 0; }
.hero-art, .step-art { width: 100%; border-radius: 12px; display: block; }
.hero-art { margin: 12px 0; max-height: 360px; object-fit: cover; }
.pending {
  background: #f3e9d8; border: 1px dashed var(--muted); border-radius: 12px;
  padding: 28px; text-align: center; color: var(--muted); margin: 12px 0;
}
.ing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.ing-tile {
  border: 1px dashed var(--stroke); border-radius: 10px; padding: 8px;
  text-align: center; background: #fffdf8;
}
.ing-art { width: 64px; height: 64px; object-fit: contain; margin: 0 auto 6px; display: block; }
.ing-name { display: block; font-weight: 600; font-size: 0.85rem; }
.ing-amt { display: block; color: var(--muted); font-size: 0.75rem; }
.steps { list-style: none; padding: 0; margin: 0; }
.step-card {
  display: grid; grid-template-columns: 120px 1fr; gap: 12px;
  margin-bottom: 14px; align-items: start;
}
.step-scene .step-art { max-height: 120px; object-fit: cover; }
.step-index { font-weight: 700; margin-right: 6px; }
.step-text {
  margin: 0; padding: 8px 10px; border-radius: 8px;
  background: linear-gradient(180deg, #fff6c8 0%, #ffe9a8 100%);
  line-height: 1.55;
}
@media (max-width: 480px) {
  .ing-grid { grid-template-columns: repeat(2, 1fr); }
  .step-card { grid-template-columns: 1fr; }
}
"""


def render_recommend_embedded_html(
    result: dict[str, Any],
    skill_root: Path,
    *,
    embed_images: bool = True,
    include_ingredient_art: bool = True,
    title: str = "菜就多练 · 预览",
) -> tuple[str, dict[str, Any]]:
    """Build a single-file HTML document. Returns (html, stats)."""
    sections: list[str] = []
    total_imgs = 0

    primary = result.get("primary")
    if primary:
        frag, n = render_recipe_section(
            primary,
            skill_root,
            heading="今日推荐",
            embed=embed_images,
            include_ingredient_art=include_ingredient_art,
        )
        sections.append(frag)
        total_imgs += n

    for idx, alt in enumerate(result.get("alternates") or [], start=1):
        frag, n = render_recipe_section(
            alt,
            skill_root,
            heading=f"也可以试试 · 备选 {idx}",
            embed=embed_images,
            include_ingredient_art=include_ingredient_art,
        )
        sections.append(frag)
        total_imgs += n

    why = (result.get("why") or "").strip()
    why_html = f'<p class="meta"><strong>推荐理由：</strong>{_esc(why)}</p>' if why else ""

    channel_note = (
        "本页图片已 base64 内嵌，不依赖 8765 端口，供 WorkBuddy HTML 预览使用。"
        if embed_images
        else "本页使用 file:// 图片路径（非内嵌）。"
    )

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{_esc(title)}</title>
<style>{_EMBEDDED_CSS}</style>
</head>
<body>
<header>
  <h1>菜就多练</h1>
  <p>先定场景，再出好菜</p>
</header>
<div class="note">{_esc(channel_note)} 日常网页仍请用同端口 Web 服务（/skill-assets/）。</div>
{why_html}
{"".join(sections)}
</body>
</html>
"""
    raw = doc.encode("utf-8")
    stats = {
        "embeddedImages": total_imgs,
        "bytes": len(raw),
        "embedImages": embed_images,
        "includeIngredientArt": include_ingredient_art,
        "warnOverBytes": len(raw) >= DEFAULT_WARN_BYTES,
        "channel": "html_embedded" if embed_images else "html_file_uri",
    }
    return doc, stats


def write_recommend_embedded_html(
    result: dict[str, Any],
    skill_root: Path,
    out_path: Path,
    *,
    embed_images: bool = True,
    include_ingredient_art: bool = True,
) -> dict[str, Any]:
    doc, stats = render_recommend_embedded_html(
        result,
        skill_root,
        embed_images=embed_images,
        include_ingredient_art=include_ingredient_art,
    )
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    stats["htmlPath"] = out_path.as_posix()
    stats["ok"] = True
    return stats
