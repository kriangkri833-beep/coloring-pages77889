# Automation Findings — ChatGPT browser vs API (tested 2026-11-18)

## Environment inspected
- Windows 11, Python 3.12.10 with PIL, numpy, OpenCV, scipy, reportlab, PyMuPDF (no scikit-image, no openai SDK).
- Claude in Chrome connected to the owner's Chrome; ChatGPT signed in (Plus plan shown in the sidebar).
- `OPENAI_API_KEY` is **not set** in the environment; the existing `.env` has no OPENAI entry. No API test was possible.

## Browser route — what was actually tested

| Step | Result |
|---|---|
| Open chatgpt.com, send a prompt | Works |
| Wait for image generation | Works; ~35-60 s per image, 3 generations in a row without throttling |
| Read the image in the page | Works; image is a `blob:` URL, PNG ~1.2 MB, **1086x1448 px** |
| Download via the page's download button | **Did not produce a file** in Downloads |
| `a.download` from JS | No file |
| POST image from page to `127.0.0.1` | **Blocked** (site security policy) |
| Return image bytes through the tool | Technically possible but ~1.6M characters per image: not practical |
| **Write to Windows clipboard, read with Python** | **Works**, saved lossless PNG. Needs one real click first (browser requires a user gesture); Claude supplies it by clicking a neutral spot |

Consequences:
- The loop runs unattended **only while Chrome is open, ChatGPT is logged in, and the Claude browser tools are connected**. It is not a background batch job; Claude Code must be actively running it.
- Each retrieval relies on a clipboard trick. It worked 3 of 3 times. It can break if ChatGPT's page changes, if you copy something else mid-run, or if the page loses focus.
- ChatGPT conversation drift: later prompts in one chat are interpreted in context ("redo the same image"). Worked here; across 20 different objects a fresh chat per object is safer (not yet tested).
- Resolution: the image arrives at ~1086x1448, below the 2550x3300 px print target. Print files are interpolated enlargements. Not verified whether the "open in side panel / download" original is larger.
- Unknown and untested: ChatGPT image limits for a Plus account over many images per day; platform terms for automated use of the web interface (the plan already says to verify before scaling).

## API route — not tested, comparison from general knowledge (verify before relying)

- Needs an OpenAI API key with separate billing; a ChatGPT Plus/Pro subscription does **not** include API usage.
- OpenAI's image models may require organisation verification before use.
- Pricing is per image and depends on model, quality and size; roughly cents to a few tens of cents per image. **Check the current pricing page**; these figures were not looked up in this session.
- Advantages: officially supported, scriptable, can run in the background, returns bytes directly (no clipboard), can request larger sizes, has documented rate limits.
- Disadvantages: costs money per image including every retry; needs credentials the owner must create.

**Recommendation:** keep the browser route for the pilot (free with the current subscription, proven for 1 object). If the pilot shows the clipboard step is fragile or the owner wants unattended overnight runs, add the API as a drop-in replacement for steps 1-2 only; QC, diagnosis, print and manifest tools do not change.

## QC: automated vs subjective

Automated (`tools/qc_lineart.py`, thresholds stored in each report): stray grey, white background, cropping, safe margin, tiny regions, stroke thickness/consistency, and per-object count proxies (e.g. dial must show 10 round holes). Print stage (`tools/make_print.py`): exact pixel size, pure black/white, minimum 0.5 in border, PDF page size.

**Not decidable by code:** impossible geometry, accidental overlaps, whether parts are recognisable. These are recorded as `method: visual_judgment` by Claude and are **not** objective proof. The owner approves masters.

Known weakness found in testing: the hole-count proxy gave a false positive (11 vs 10); the circularity threshold was raised from 0.75 to 0.88 afterwards and the change is recorded in the spec. This means the checker was tuned on the object it then passed; a fresh object is needed to judge it fairly.

## Proof-of-concept result (rotary telephone)
- a01: automated FAIL (safe margin 17 px), visual REVISE.
- a02: automated pass after tuning, visual REVISE (stray hook lines).
- a03: automated pass, visual PASS (subjective). Print files built for Letter and A4 and pixel-verified.
- Retry budget used 3 of 4. Not an approved master: owner has not signed off.
