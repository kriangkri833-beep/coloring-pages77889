# Coloring Pages — Market-Driven Production & Etsy Listing Plan

**Version:** Pilot v0.1
**Date:** 2026-11-18
**Target repository:** kriangkri833-beep/coloring-pages77889
**Status:** Proposed implementation plan; market assumptions require validation.

## 1. Goal and operating model

Build a repeatable process for researching, producing, quality-checking, packaging, and drafting downloadable Etsy coloring-page listings. The immediate milestone is one complete pilot listing, not bulk production. Produce an approved inventory backlog before scheduling gradual listing releases.

### Roles

- **Claude Code Desktop:** Main orchestrator, research coordination, file handling, metadata, handoff to the existing Etsy draft workflow.
- **ChatGPT image generation:** Create coloring-page images from controlled prompts. Initial browser-mediated use is experimental; verify reliability and applicable platform terms before scaling.
- **Human owner:** Selects products, reviews image quality, approves final packages and publication decisions.
- **GitHub:** Stores specifications, prompts, scripts, QC manifests, and integration documentation; avoid committing large generated assets or secrets.
- **Existing Etsy workflow:** Receives approved products and creates drafts. Do not replace or modify it until its actual input contract is inspected.

## 2. Product and listing strategy

### 2.1 Market-first selection

Research comparable Etsy listings before choosing themes, styles, bundle page counts, and prices. Record listing URLs, observed prices, format, page counts, intended audience, style, review signals, competition, seasonality, and research date. Distinguish observable evidence from inference. A shop's overall sales are not proof of a particular listing's sales.

### 2.2 Portfolio allocation

Use a 90% validated-market / 10% underserved-opportunity portfolio hypothesis. For example, over a rolling cohort of ten planned listings, aim for nine evidence-backed mainstream products and one carefully researched niche experiment. This is a testable operating hypothesis, not a proven optimal ratio.

An underserved niche requires both plausible buyer interest and meaningful differentiation; low competition alone does not establish demand.

### 2.3 Shop sections vs. internal tags

Keep Etsy shop sections understandable to buyers; do not launch unnecessary empty sections. Maintain a richer internal taxonomy using theme, style, audience, season, and difficulty.

Candidate sections for validation and consolidation: Cozy Coloring; Bold & Easy; Kawaii Coloring; Color by Number; Animals & Pets; Flowers & Nature; Fantasy & Magic; Mandala & Patterns; Houses & Interiors; Christmas & Winter; Halloween & Fall; Easter & Spring; Summer & Beach; Kids Coloring; Adult Coloring; Senior Coloring; Mega Bundles; New & Special.

These are 18 working candidates, not confirmed Etsy demand rankings or a commitment to create all sections.

### 2.4 Bundle size and pricing

Set page counts and pricing from the specific competitive set and buyer value proposition. Do not force every product to have 10, 20, or 50 pages. Track promotional price separately from standard price. Avoid unsupported claims such as "bestseller" or guaranteed sales.

## 3. Pilot workflow: one listing end-to-end

1. **Research shortlist:** Claude compiles sourced competitors and three possible concepts. Human chooses one.
2. **Product brief:** Define audience, theme, style, page count, visual constraints, target price hypothesis, and unique page-by-page scene list.
3. **Style proof:** Generate 2–3 sample pages and confirm line weight, simplicity, consistency, and print suitability.
4. **Generate pages:** Run bounded prompts; log image filename, prompt version, attempt number, and generation outcome. Do not assume unlimited browser throughput.
5. **Quality control:** Human checks hands/fingers, anatomy, intersecting objects, stray or broken lines, unexpected black fills or gray shading, cropped elements, duplicates, scene accuracy, and style consistency. Mark each page PASS, REVISE, or REJECT.
6. **Selective repair:** Regenerate or edit failed pages only, retaining an audit trail of revisions.
7. **Print packaging:** Deliver US Letter and A4 variants at a target of 300 DPI. Verify pixel dimensions and printed safe margins, not merely a DPI label. Assemble PDFs, image files, cover/previews, and a manifest.
8. **Inventory gate:** Mark the product READY only after complete package QC and human approval.
9. **Etsy draft handoff:** Send approved package and listing metadata to the existing Claude publishing system, initially creating a draft only. Publication requires separate approval.
10. **Retrospective:** Record generation attempts, pass rate, QC time, packaging issues, and end-to-end elapsed time.

Proposed statuses: RESEARCHED → SELECTED → BRIEF_APPROVED → GENERATING → QC_PENDING → REVISION_NEEDED / QC_APPROVED → PACKAGED → READY → DRAFTED → PUBLISHED.

## 4. Production specifications

For each product, maintain:

```yaml
product_id: CP-0001
portfolio_bucket: market # or niche
research_checked_at: YYYY-MM-DD
research_sources: [] # exact Etsy listing URLs / observations
theme: ""
subtheme: ""
style: "bold-and-simple"
audience: ""
difficulty: ""
etsy_section: ""
bundle_page_count: null # set after competitor research
target_price_usd: null # hypothesis with supporting evidence
page_plan: [] # distinct scenes, one per page
formats: [US_LETTER, A4]
target_dpi: 300
status: RESEARCHED
qc_approved: false
human_approved: false
handoff_path: null
```

Default art direction (subject to product brief): Clean black outlines on white, no accidental shading or grayscale, consistent line weight, readable large shapes, uncluttered composition, and no cut-off objects. For seniors, favor high contrast and lower visual complexity where research supports that audience need.

Print validation: US Letter = 8.5 × 11 in (2550 × 3300 px at 300 DPI); A4 = 210 × 297 mm (approximately 2480 × 3508 px at 300 DPI). Check actual resolution, scaling, bleed/safe margins, PDF page size, and page order.

## 5. Listing content and handoff

For every approved product, prepare:

- A factual, searchable title and description (without keyword stuffing or invented claims).
- Etsy tags and attributes within current platform limits, validated before submission.
- Cover image, preview images, and a clear description of what buyers receive.
- Bundle page count, file formats, sizes, printing guidance, and digital-download disclosure.
- Price recommendation with evidence, not an assumed fixed price.
- File manifest and READY approval flag.

**Critical boundary:** The existing Claude Etsy system is the authority for draft submission. First inspect its real expected input files/fields; create an adapter only after that inspection. Do not invent an Etsy API integration or publish automatically.

## 6. Inventory and release cadence

Separate production from publication. Store fully approved listings in a backlog and release them deliberately. Pilot goal: one draft-ready listing per day, subject to actual quality and workload. The longer-term aspiration of ten listings per day is not a throughput commitment; scale only after measuring quality, time, and bottlenecks.

Use a rolling ten-listing portfolio view to evaluate the 90/10 hypothesis. Review listing performance only once real publication data exists.

## 7. Metrics and gates

Track per product:

- Total generated images and accepted images.
- Acceptance rate = accepted images / total generated images (define whether retries count; use consistently).
- Retry count and most common failure types.
- Human QC minutes, generation time, and packaging time.
- Final page count, file-size and dimension checks, and draft handoff success.
- After publishing: visits, conversion, orders, revenue, and buyer feedback where available.

**Scale gate:** Only increase throughput when print quality, human review capacity, generation reliability, and draft handoff remain acceptable. Do not use fabricated sales forecasts as evidence.

## 8. Suggested repository layout (future; not yet implemented)

```
docs/           # plans, integration contract
research/       # sourced competitor observations
specs/          # approved product briefs
prompts/        # versioned generation prompts
qc/             # checklists and pass/fail logs
manifests/      # approved package metadata
integration/    # interface to existing Claude Etsy workflow
```

Generated images and large PDF bundles should normally live in a separate artifact store; keep paths and checksums in manifests. Never commit API keys, cookies, OAuth tokens, or browser profiles.

## 9. First tasks for Claude Code

1. Read this plan; do not immediately build a large automation framework.
2. Inspect the existing Etsy draft workflow and document its actual accepted input contract.
3. Produce a concise, sourced shortlist for the first coloring-page listing.
4. Ask the owner to select the pilot concept.
5. Create the first product brief and 2–3-page style proof.
6. Request QC feedback before generating the complete bundle.

Human approval is mandatory before publishing, altering the existing Etsy pipeline, or starting bulk generation.

---

This document records an implementation concept and test plan. Market claims and operational capacity must be established with evidence from the pilot.
