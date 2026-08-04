"""Generate minimal ingredient line-art SVG files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "assets" / "line-art"

SHAPES = {
    "avocado": '<path d="M128 48 C88 48, 64 96, 64 144 C64 192, 96 220, 128 220 C160 220, 192 192, 192 144 C192 96, 168 48, 128 48 Z" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><circle cx="128" cy="120" r="20" stroke="#4A4035" stroke-width="3" fill="none"/>',
    "tomato": '<circle cx="128" cy="136" r="72" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M128 64 C118 84, 108 76, 98 88 M128 64 C138 84, 148 76, 158 88" stroke="#4A4035" stroke-width="4" stroke-linecap="round" fill="none"/>',
    "cucumber": '<ellipse cx="128" cy="128" rx="90" ry="40" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "chicken": '<ellipse cx="128" cy="140" rx="70" ry="55" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><circle cx="168" cy="100" r="22" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "egg": '<ellipse cx="128" cy="136" rx="55" ry="70" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "rice": '<path d="M80 160 Q128 80 176 160" stroke="#4A4035" stroke-width="4" fill="none"/><path d="M90 170 Q128 100 166 170" stroke="#4A4035" stroke-width="3" fill="none"/>',
    "noodle": '<path d="M70 180 C90 100, 110 200, 130 100 S170 200, 186 120" stroke="#4A4035" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "potato": '<ellipse cx="128" cy="136" rx="65" ry="50" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "broccoli": '<circle cx="128" cy="110" r="35" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M128 145 L128 200 M108 170 L148 170" stroke="#4A4035" stroke-width="4" stroke-linecap="round"/>',
    "spinach": '<path d="M128 200 L128 120 M100 140 Q128 90 156 140 M95 160 Q128 110 161 160" stroke="#4A4035" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "quinoa": '<circle cx="100" cy="130" r="8" fill="#4A4035"/><circle cx="128" cy="120" r="8" fill="#4A4035"/><circle cx="156" cy="130" r="8" fill="#4A4035"/><circle cx="115" cy="150" r="8" fill="#4A4035"/><circle cx="141" cy="150" r="8" fill="#4A4035"/>',
    "salmon": '<ellipse cx="128" cy="128" rx="90" ry="35" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M50 128 L70 118 L70 138 Z" fill="#4A4035"/>',
    "beef": '<rect x="70" y="110" width="116" height="60" rx="12" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "pork": '<rect x="75" y="115" width="106" height="50" rx="10" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "tofu": '<rect x="85" y="95" width="86" height="86" rx="4" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "mushroom": '<ellipse cx="128" cy="150" rx="50" ry="30" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><rect x="118" y="80" width="20" height="70" rx="8" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "carrot": '<path d="M128 200 L128 110 M128 110 L150 130 M128 110 L106 130" stroke="#4A4035" stroke-width="4" stroke-linecap="round" fill="none"/>',
    "corn": '<ellipse cx="128" cy="130" rx="35" ry="70" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "lemon": '<circle cx="128" cy="128" r="60" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M128 68 L128 88" stroke="#4A4035" stroke-width="3"/>',
    "garlic": '<ellipse cx="128" cy="130" rx="40" ry="55" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "onion": '<circle cx="128" cy="128" r="55" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M128 73 Q118 100 128 128 Q138 100 128 73" stroke="#4A4035" stroke-width="3" fill="none"/>',
    "walnut": '<circle cx="128" cy="128" r="50" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M128 78 Q108 128 128 178 Q148 128 128 78" stroke="#4A4035" stroke-width="3" fill="none"/>',
    "strawberry": '<path d="M128 200 L128 120 Q100 100 128 80 Q156 100 128 120" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "pumpkin": '<ellipse cx="128" cy="140" rx="70" ry="60" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M118 80 Q128 60 138 80" stroke="#4A4035" stroke-width="4" fill="none"/>',
    "zucchini": '<ellipse cx="128" cy="128" rx="40" ry="80" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "kale": '<path d="M128 200 L128 100 M100 130 Q128 70 156 130 M95 155 Q128 95 161 155" stroke="#4A4035" stroke-width="4" fill="none" stroke-linecap="round"/>',
    "oats": '<rect x="80" y="120" width="96" height="60" rx="8" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "shrimp": '<path d="M80 150 Q128 80 176 150 Q128 120 80 150" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/>',
    "turkey": '<ellipse cx="128" cy="145" rx="75" ry="50" stroke="#4A4035" stroke-width="4" fill="#FFF8E7"/><path d="M170 110 L190 90" stroke="#4A4035" stroke-width="4"/>',
}

TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">
  {body}
</svg>
'''

def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, body in SHAPES.items():
        (ROOT / f"{name}.svg").write_text(TEMPLATE.format(body=body), encoding="utf-8")
    print(f"created {len(SHAPES)} SVGs in {ROOT}")

if __name__ == "__main__":
    main()
