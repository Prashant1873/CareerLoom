"""WCAG 2.2 AA automated contrast ratio verification script for CareerLoom.
Evaluates both Dark (Obsidian Charcoal) and Light (Obsidian Porcelain) themes.
"""

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    clean_hex = hex_str.lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join([c * 2 for c in clean_hex])
    return (
        int(clean_hex[0:2], 16),
        int(clean_hex[2:4], 16),
        int(clean_hex[4:6], 16),
    )


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculates relative luminance according to WCAG 2.1 / 2.2 specification."""
    srgb = []
    for c in rgb:
        v = c / 255.0
        if v <= 0.04045:
            srgb.append(v / 12.92)
        else:
            srgb.append(((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2]


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Computes contrast ratio between two hex color codes."""
    lum1 = relative_luminance(hex_to_rgb(hex1))
    lum2 = relative_luminance(hex_to_rgb(hex2))
    l_max = max(lum1, lum2)
    l_min = min(lum1, lum2)
    return (l_max + 0.05) / (l_min + 0.05)


def blend_alpha(fg_hex: str, alpha: float, bg_hex: str) -> str:
    """Blends an rgba color over a solid background to produce a flattened hex."""
    fg = hex_to_rgb(fg_hex)
    bg = hex_to_rgb(bg_hex)
    r = round(fg[0] * alpha + bg[0] * (1 - alpha))
    g = round(fg[1] * alpha + bg[1] * (1 - alpha))
    b = round(fg[2] * alpha + bg[2] * (1 - alpha))
    return f"#{r:02x}{g:02x}{b:02x}"


# Theme Color Definitions
THEMES = {
    "Dark Mode (Obsidian Charcoal)": {
        "bg_base": "#0b0d11",
        "bg_surface": "#131720",
        "bg_elevated": "#1a202c",
        "pairs": [
            ("Primary Text on Canvas", "#f3f4f6", "#0b0d11", 14.0, "AAA"),
            ("Primary Text on Surface", "#f3f4f6", "#131720", 12.0, "AAA"),
            ("Secondary Text on Surface", "#9ca3af", "#131720", 6.0, "AA"),
            ("Muted Text on Surface", "#6b7280", "#131720", 3.0, "AA-large"),
            ("Primary Accent on Canvas", "#10b981", "#0b0d11", 7.0, "AAA"),
            ("Cyan Accent on Surface", "#22d3ee", "#131720", 8.0, "AAA"),
            ("Amber Accent on Surface", "#fbbf24", "#131720", 9.0, "AAA"),
            ("Indigo Accent on Surface", "#818cf8", "#131720", 6.0, "AA"),
            ("Rose Accent on Surface", "#fb7185", "#131720", 6.0, "AA"),
        ],
    },
    "Light Mode (Obsidian Porcelain)": {
        "bg_base": "#f8fafc",
        "bg_surface": "#ffffff",
        "bg_elevated": "#f1f5f9",
        "pairs": [
            ("Primary Text on Canvas", "#0f172a", "#f8fafc", 13.0, "AAA"),
            ("Primary Text on Surface", "#0f172a", "#ffffff", 14.0, "AAA"),
            ("Secondary Text on Surface", "#334155", "#ffffff", 7.0, "AAA"),
            ("Muted Text on Surface", "#64748b", "#ffffff", 4.5, "AA"),
            ("Emerald Accent on Surface", "#047857", "#ffffff", 4.5, "AA"),
            ("Emerald Hover on Surface", "#065f46", "#ffffff", 7.0, "AAA"),
            ("Emerald Badge Text on White", "#047857", "#ffffff", 4.5, "AA"),
            ("Cyan Badge Text on White", "#0e7490", "#ffffff", 4.5, "AA"),
            ("Amber Badge Text on White", "#b45309", "#ffffff", 4.5, "AA"),
            ("Indigo Badge Text on White", "#4f46e5", "#ffffff", 4.5, "AA"),
            ("Rose Badge Text on White", "#be123c", "#ffffff", 4.5, "AA"),
            (
                "Emerald on Pastel Pill",
                "#047857",
                blend_alpha("#10b981", 0.12, "#ffffff"),
                4.5,
                "AA",
            ),
            (
                "Cyan on Pastel Pill",
                "#0e7490",
                blend_alpha("#06b6d4", 0.12, "#ffffff"),
                4.5,
                "AA",
            ),
            (
                "Amber on Pastel Pill",
                "#b45309",
                blend_alpha("#f59e0b", 0.14, "#ffffff"),
                4.5,
                "AA",
            ),
            (
                "Indigo on Pastel Pill",
                "#4f46e5",
                blend_alpha("#6366f1", 0.12, "#ffffff"),
                4.5,
                "AA",
            ),
            (
                "Rose on Pastel Pill",
                "#be123c",
                blend_alpha("#f43f5e", 0.12, "#ffffff"),
                4.5,
                "AA",
            ),
        ],
    },
}


def run_verification() -> bool:
    all_passed = True
    logging.info("Starting WCAG 2.2 AA Contrast Verification Suite...\n")

    for theme_name, data in THEMES.items():
        print(f"=== {theme_name} ===")
        print(
            f"{'Pair Description':<32} | {'Foreground':<10} | {'Background':<10} | {'Ratio':<7} | {'Required':<8} | {'Status'}"
        )
        print("-" * 88)

        for desc, fg, bg, req, level in data["pairs"]:
            ratio = contrast_ratio(fg, bg)
            passed = ratio >= req
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_passed = False
            print(
                f"{desc:<32} | {fg:<10} | {bg:<10} | {ratio:>5.2f}:1 | >={req:>4.1f}:1 ({level:<3}) | {status}"
            )
        print()

    if all_passed:
        logging.info(
            "All tested foreground/background color pairs passed WCAG 2.2 AA compliance!"
        )
    else:
        logging.error("Some color pairs failed the contrast thresholds.")

    return all_passed


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
