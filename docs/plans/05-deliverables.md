# Plan 05 — Deliverables & Documentation

## Objective
Produce the academic deliverables: diagrams, the 10-minute Vietnamese
PowerPoint, the video materials, the AI usage disclosure, and the final report.

## Tasks
1. Diagrams (Mermaid): lab architecture, stored-XSS PoC sequence, self-propagation
   sequence + data-flow, HTTP profile workflow.
2. Analysis docs: stored-XSS, HTTP/profile workflows, self-propagation.
3. PowerPoint `deliverables/Self_Propagation_XSS_Group_Presentation.pptx`
   (Vietnamese, 10–12 slides, speaker notes, AI disclosure slide).
4. Video materials: `video_script.md`, `video_shotlist.md`, `video_checklist.md`,
   `youtube_submission.md`.
5. `docs/AI_USAGE_LOG.md` with the three assignment-defined AI levels.
6. Evidence index + pending-screenshot checklist.
7. Final Vietnamese report (root `BAO_CAO.md`).

## Dependencies
- Analysis outputs; captured logs; pptx tooling.

## Acceptance criteria
- PPT opens and matches the required structure with notes.
- Video script totals ~10 minutes, narration split across 3 members.
- AI disclosure present in repo, PPT, and video script.
- Final report lists real commands, real test results, and remaining manual tasks.

## Tests
- Manual review; `python3 -c "from pptx import Presentation; ..."` sanity load.

## Expected evidence
- Files under `deliverables/` and `docs/`.

## Proposed Git commit
`docs(deliverables): diagrams, PPT, video materials, AI log, final report`
