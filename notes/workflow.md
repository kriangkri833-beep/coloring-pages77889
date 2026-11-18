# Workflow ChatGPT <-> Claude

ChatGPT: makes images -> owner saves to raw_from_chatgpt/
Claude:  cleans, checks, builds pages_final/ + PDF + listing -> commits + pushes
Owner:   carries files, pastes HANDOFF entries, decides theme/size/count

Connecting ChatGPT to this repo:
- Option A (private repo): ChatGPT > Settings > Connected apps > GitHub,
  authorize, pick this repo. ChatGPT can then read it (not push).
- Option B: owner pastes CHATGPT_INSTRUCTIONS.md + latest HANDOFF.md by hand.
- Option C: make repo public so any ChatGPT chat can read the raw file URLs.
