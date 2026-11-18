# Workflow ChatGPT <-> Claude (updated 2026-11-18)

Per image, driven by Claude Code:
1. Prompt built from specs/CP-001.json (structure + style rules) -> sent to ChatGPT in Chrome
2. Image retrieved to raw_from_chatgpt/<id>_aNN.png (never overwritten)
3. python tools/qc_lineart.py ... (automated)  +  visual review recorded in qc/*.visual_review.json (subjective)
4. python tools/diagnose.py <stem> -> RETRY with amendment, or ESCALATE after 4 attempts
5. Accepted -> python tools/make_print.py -> pages_final/{US_LETTER,A4}/, manifest in manifests/
6. Owner approves; adapter writes listing.json for the existing Etsy draft workflow (not built yet)

Owner decides theme/size/count and approves masters and publication. Nothing publishes automatically.

Connecting ChatGPT to this repo (optional, read-only for ChatGPT):
- ChatGPT > Settings > Connected apps > GitHub, or paste CHATGPT_INSTRUCTIONS.md by hand.
