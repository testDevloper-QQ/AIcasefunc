"""Search web + LLM for high-frequency Chinese home cooking recipes."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from typing import Any

SCENE_LABELS = {
    "bento": "便当",
    "light-meal": "轻食",
    "seasonal": "时令",
    "regional": "地方味",
    "health": "调理",
    "happy": "快乐餐",
}

USER_AGENT = "Mozilla/5.0 (compatible; CaiJiuDuoLian/1.3; +recipe-skill)"


def _http_get(url: str, timeout: float = 12.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def web_search_snippets(query: str, *, max_results: int = 6) -> list[str]:
    """Fetch search result snippets (DuckDuckGo HTML lite)."""
    q = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{q}"
    try:
        html = _http_get(url, timeout=15)
    except (urllib.error.URLError, TimeoutError, OSError):
        return []

    snippets: list[str] = []
    for block in re.findall(r'class="result__snippet".*?</(?:a|td|div)>', html, re.S | re.I):
        text = unescape(re.sub(r"<[^>]+>", " ", block))
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 20:
            snippets.append(text[:400])
        if len(snippets) >= max_results:
            break

    if not snippets:
        for m in re.finditer(r'class="result__a"[^>]*>([^<]+)</a>', html, re.I):
            title = unescape(m.group(1)).strip()
            if title and len(title) > 4:
                snippets.append(title)
            if len(snippets) >= max_results:
                break
    return snippets


def _openai_chat(system: str, user: str) -> str | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
    except (urllib.error.URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError, IndexError):
        return None


def _parse_recipe_json(raw: str, ingredients: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None

    name = (data.get("name") or "").strip()
    steps = data.get("steps") or []
    if not name or not steps:
        return None

    hay = name + " ".join(
        (i.get("name", "") if isinstance(i, dict) else str(i)) for i in (data.get("ingredients") or [])
    )
    if not all(ing in hay or any(ing in s for s in steps) for ing in ingredients):
        return None

    ing_rows = []
    for item in data.get("ingredients") or []:
        if isinstance(item, dict):
            ing_rows.append({"name": item.get("name", ""), "amount": item.get("amount", "适量")})
        elif isinstance(item, str):
            ing_rows.append({"name": item, "amount": "适量"})

    for ing in ingredients:
        if not any(ing in r["name"] for r in ing_rows):
            ing_rows.insert(0, {"name": ing, "amount": "约120克"})

    return {
        "name": name,
        "method": (data.get("method") or "炒").strip(),
        "cook_time": (data.get("cook_time") or data.get("cookTime") or "25min").strip(),
        "cost": (data.get("cost") or "约15元").strip(),
        "ingredients": ing_rows,
        "steps": [str(s).strip() for s in steps if str(s).strip()],
        "source_hint": (data.get("source_hint") or "网络高频家常菜").strip(),
    }


def search_and_generate_recipe(
    ingredients: list[str],
    scene: str,
    *,
    servings: int = 2,
) -> dict[str, Any] | None:
    """Web search + LLM structuring. Returns raw recipe dict or None."""
    if not ingredients:
        return None
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        return None

    joined = " ".join(ingredients)
    scene_label = SCENE_LABELS.get(scene, scene)
    query = f"{joined} 家常做法 简单 高频"
    snippets = web_search_snippets(query)
    if not snippets:
        snippets = web_search_snippets(f"{joined} 怎么做 家常菜")

    search_context = "\n".join(f"- {s}" for s in snippets) or "（未能抓取搜索结果，请基于常见中国家常菜知识生成）"

    system = (
        "你是中国家常菜助手。根据用户食材与网络搜索摘要，输出一道高频、可在家做的中国家常菜。"
        "必须使用用户提供的全部食材。计量用中文：克、毫升、℃。"
        "烹饪时间不超过60分钟。仅输出 JSON，不要 markdown。"
    )
    user = f"""食材：{'、'.join(ingredients)}
场景偏好：{scene_label}
人份：{servings}

网络搜索摘要：
{search_context}

请输出 JSON：
{{
  "name": "菜名",
  "method": "炒/炖/蒸等",
  "cook_time": "25min",
  "cost": "约15元",
  "ingredients": [{{"name":"食材","amount":"约120克"}}],
  "steps": ["步骤1","步骤2"],
  "source_hint": "参考来源简述"
}}"""

    llm_raw = _openai_chat(system, user)
    if not llm_raw:
        return None

    parsed = _parse_recipe_json(llm_raw, ingredients)
    if not parsed:
        return None

    return {
        "id": f"llm-home-{'-'.join(ingredients)}",
        "name": parsed["name"],
        "scene": [scene],
        "tags": ["网络家常", scene_label, *ingredients],
        "servings": servings,
        "cook_time": parsed["cook_time"],
        "cost": parsed["cost"],
        "method": parsed["method"],
        "ingredients": parsed["ingredients"],
        "steps": parsed["steps"],
        "source": {
            "book": "网络高频家常菜（LLM）",
            "chapter": parsed.get("source_hint") or f"{'、'.join(ingredients)}",
        },
        "line_art": "",
        "generated": True,
        "llmGenerated": True,
    }
