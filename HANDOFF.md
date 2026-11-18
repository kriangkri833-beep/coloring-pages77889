# Handoff log (newest on top)

## 2026-11-19 - telephone approved, 3-image test complete
- Owner approved the rotary telephone as style master (manifest: human_approved=true).
- Radio: a01 failed (margin; double cabinet outline; distorted speaker ring), a02 passed. 2 attempts.
- Teapot: a01 failed only safe_margin (structure fine), a02 passed. 2 attempts.
- Totals: 7 generations for 3 objects; 4 automated margin failures caught; 2 structural problems caught by eye only
  (stray hooks on telephone, merged cabinet outline on radio) - the code cannot see those.
- All three have Letter + A4 PNG/PDF in pages_final/, pixel-verified. Radio and teapot are NOT yet owner-approved.
- Observation: ChatGPT drifts toward tight margins on wide objects; put the 8% margin rule in every first prompt (done for radio/teapot, still needed one retry on teapot).
- Next: owner views radio + teapot; then scale to the remaining 17 objects (scene list in specs/CP-001.json is a DRAFT needing owner approval), then package + Etsy listing.json adapter.

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
