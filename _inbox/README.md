# VAYRANIS Inbox Directory

Drop your exported ChatGPT `.md` files and downloaded images (`.png`, `.jpg`, `.webp`) here.

Then run the organizer script from your terminal:

```bash
python scripts/organize_vayranis.py
```

The script will automatically:
1. Categorize markdown notes into `00_CREATOR_BIBLE` through `10_REFERENCE`.
2. Move concept images into `08_ART_BIBLE/assets/` and rewrite links to `![[image_name.png]]`.
3. Update `INDEX.md` with links to your new notes.
