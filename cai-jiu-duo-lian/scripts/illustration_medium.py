"""Medium illustration specs: resize + PNG optimize for web delivery."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

IllustrationKind = Literal["dish", "step", "ingredient"]

# Long-edge targets (px). Chosen for ~2–3× Retina headroom vs web CSS display sizes.
MEDIUM_LONG_EDGE: dict[IllustrationKind, int] = {
    "dish": 1024,
    "step": 768,
    "ingredient": 512,
}

PNG_COMPRESS_LEVEL = 9
PNG_OPTIMIZE = True


def long_edge_for_kind(kind: IllustrationKind) -> int:
    return MEDIUM_LONG_EDGE[kind]


def infer_kind_from_rel_path(rel: str | Path) -> IllustrationKind | None:
    s = str(rel).replace("\\", "/").lower()
    if "/ingredients/" in s or s.startswith("assets/illustrations/ingredients/"):
        return "ingredient"
    if "/steps/" in s or s.startswith("assets/illustrations/steps/"):
        return "step"
    if "/dishes/" in s or s.startswith("assets/illustrations/dishes/"):
        return "dish"
    return None


def _require_pillow():
    try:
        from PIL import Image  # noqa: WPS433
    except ImportError as exc:
        raise RuntimeError(
            "Pillow 未安装，无法处理 medium 插画。请运行: pip install -r requirements-web.txt"
        ) from exc
    return Image


def _fit_long_edge(width: int, height: int, max_edge: int) -> tuple[int, int]:
    long_edge = max(width, height)
    if long_edge <= max_edge:
        return width, height
    scale = max_edge / long_edge
    return max(1, int(width * scale)), max(1, int(height * scale))


def process_png_bytes(data: bytes, kind: IllustrationKind) -> tuple[bytes, dict[str, Any]]:
    """Resize to medium long-edge (if larger) and re-encode PNG."""
    Image = _require_pillow()
    from io import BytesIO

    before = len(data)
    with Image.open(BytesIO(data)) as im:
        im.load()
        orig_w, orig_h = im.size
        target_w, target_h = _fit_long_edge(orig_w, orig_h, long_edge_for_kind(kind))
        if (target_w, target_h) != (orig_w, orig_h):
            resample = getattr(Image, "Resampling", Image).LANCZOS
            im = im.resize((target_w, target_h), resample)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA")
        out = BytesIO()
        im.save(out, format="PNG", optimize=PNG_OPTIMIZE, compress_level=PNG_COMPRESS_LEVEL)
        result = out.getvalue()
    meta = {
        "kind": kind,
        "longEdge": long_edge_for_kind(kind),
        "width": target_w,
        "height": target_h,
        "bytesBefore": before,
        "bytesAfter": len(result),
    }
    return result, meta


def process_png_file(source: Path, dest: Path, kind: IllustrationKind) -> dict[str, Any]:
    data = source.read_bytes()
    processed, meta = process_png_bytes(data, kind)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(processed)
    meta["dest"] = str(dest)
    return meta


def write_medium_png(source: Path | bytes, dest: Path, kind: IllustrationKind) -> dict[str, Any]:
    if isinstance(source, Path):
        return process_png_file(source, dest, kind)
    processed, meta = process_png_bytes(source, kind)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(processed)
    meta["dest"] = str(dest)
    return meta
