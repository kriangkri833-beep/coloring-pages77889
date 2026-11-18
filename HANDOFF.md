# Handoff log (newest on top)

## 2026-11-18 (late) - automation proof of concept, CP-001 rotary telephone
Done (tested, real):
- Claude Code drove ChatGPT in the owner's Chrome: sent prompt, waited, fetched the image, saved it
  losslessly to raw_from_chatgpt/ via clipboard. 3 generations in one chat, no throttling seen.
- tools/qc_lineart.py (automated checks), tools/diagnose.py (failure -> retry prompt, bounded budget),
  tools/make_print.py (Letter + A4, exact pixels, PDFs), specs/CP-001.json (machine-readable spec,
  20-object draft list), manifests/CP-001_rotary_telephone.json.
- Telephone: attempt 1 failed (margin + stray marks), attempt 2 failed visual (stray hooks), attempt 3 passed
  automated + visual. Print files built and pixel-verified. Retry budget used: 3 of 4.

Not done / open:
- Owner has NOT approved the telephone as master image (human_approved=false).
- Radio and teapot not rerun; 17 of 20 objects are a draft list, not market-researched.
- Raw output is ~1086x1448; print files are enlargements. Check a physical print.
- ChatGPT step is semi-attended: needs Chrome open + logged in, and one real click per retrieval.
- No API test (no OPENAI_API_KEY). Etsy draft handoff adapter not built.
See docs/AUTOMATION_FINDINGS.md.

## 2026-11-18 - project opened
- Repo created. Plan + Etsy input contract committed.
