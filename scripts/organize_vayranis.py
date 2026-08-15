#!/usr/bin/env python3
"""
VAYRANIS Vault Auto-Organizer Script
Organizes markdown files and images from _inbox/ into the proper Obsidian Vault structure.
"""

import os
import re
import shutil
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
INBOX_DIR = VAULT_ROOT / "_inbox"
ART_ASSETS_DIR = VAULT_ROOT / "08_ART_BIBLE" / "assets"
INDEX_FILE = VAULT_ROOT / "INDEX.md"

CATEGORY_MAPPING = {
    "00_CREATOR_BIBLE": ["creator", "vision", "roadmap", "standards", "bible", "overview"],
    "01_WORLD_FOUNDATION": ["world", "cosmology", "magic", "realm", "laws", "foundation", "element"],
    "02_NATURE": ["nature", "geography", "fauna", "flora", "beast", "creature", "climate", "ecosystem", "map"],
    "03_CIVILIZATION": ["civilization", "government", "city", "kingdom", "faction", "empire", "trade", "guild"],
    "04_CULTURE": ["culture", "religion", "language", "custom", "belief", "ritual", "tradition", "lore"],
    "05_HISTORY": ["history", "timeline", "era", "war", "event", "age", "chronicle"],
    "06_CHARACTERS": ["character", "hero", "protagonist", "villain", "npc", "biography", "profile", "roster", "hero character"],
    "07_STORY": ["story", "plot", "scene", "chapter", "arc", "script", "narrative"],
    "08_ART_BIBLE": ["art", "visual", "reference", "palette", "concept", "illustration", "design bible"],
    "09_GAME_DESIGN": ["game", "mechanics", "system", "stats", "level", "item", "inventory", "skill", "combat"],
    "10_REFERENCE": ["reference", "glossary", "term", "source", "notes"]
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

def setup_directories():
    """Ensure all vault subdirectories exist."""
    INBOX_DIR.mkdir(exist_ok=True)
    ART_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for cat in CATEGORY_MAPPING.keys():
        (VAULT_ROOT / cat).mkdir(exist_ok=True)

def categorize_content(filename: str, content: str) -> str:
    """Determine the best category folder based on filename and content keywords."""
    text_lower = f"{filename} {content}".lower()
    
    scores = {cat: 0 for cat in CATEGORY_MAPPING.keys()}
    for cat, keywords in CATEGORY_MAPPING.items():
        for kw in keywords:
            if kw in filename.lower():
                scores[cat] += 5  # Higher weight for filename match
            scores[cat] += text_lower.count(kw)
            
    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return "10_REFERENCE"  # Default fallback category
    return best_category

def rewrite_image_links(content: str) -> str:
    """Convert standard markdown image links ![alt](path) to Obsidian wiki links ![[filename.ext]]."""
    def replace_md_image(match):
        alt = match.group(1)
        path = match.group(2)
        img_name = Path(path).name
        return f"![[{img_name}]]"
        
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_md_image, content)

def update_index(new_notes: list[tuple[str, str]]):
    """Update INDEX.md with links to newly organized notes."""
    if not INDEX_FILE.exists():
        return

    content = INDEX_FILE.read_text(encoding="utf-8")
    updated = False

    for title, cat in new_notes:
        wiki_link = f"- [[{title}]]"
        if wiki_link not in content:
            cat_header = f"## {cat}"
            if cat_header in content:
                content = content.replace(cat_header, f"{cat_header}\n{wiki_link}")
            else:
                content += f"\n\n{cat_header}\n{wiki_link}"
            updated = True

    if updated:
        INDEX_FILE.write_text(content, encoding="utf-8")
        print("Updated INDEX.md with new note links.")

def organize_inbox():
    setup_directories()
    
    inbox_files = [f for f in INBOX_DIR.iterdir() if f.is_file() and f.name != "README.md"]
    
    if not inbox_files:
        print("Inbox is empty! Export ChatGPT notes or images into '_inbox/' and run this script again.")
        return

    # First, move all images to ART_ASSETS_DIR
    moved_images = []
    for f in inbox_files:
        if f.suffix.lower() in IMAGE_EXTENSIONS:
            dest = ART_ASSETS_DIR / f.name
            shutil.move(str(f), str(dest))
            moved_images.append(f.name)
            print(f"Moved image '{f.name}' -> '08_ART_BIBLE/assets/'")

    # Process markdown files
    md_files = [f for f in INBOX_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".md" and f.name != "README.md"]
    new_notes = []

    for md_file in md_files:
        raw_text = md_file.read_text(encoding="utf-8")
        
        # Rewrite image links to Obsidian format
        processed_text = rewrite_image_links(raw_text)
        
        # Categorize
        target_cat = categorize_content(md_file.stem, processed_text)
        target_dir = VAULT_ROOT / target_cat
        target_path = target_dir / md_file.name

        # Save processed note
        target_path.write_text(processed_text, encoding="utf-8")
        md_file.unlink()  # Remove from inbox

        new_notes.append((md_file.stem, target_cat))
        print(f"Organized note '{md_file.name}' -> '{target_cat}/'")

    if new_notes:
        update_index(new_notes)

    print("\nVault organization complete! ✅")

if __name__ == "__main__":
    organize_inbox()
