# Why this exists: what hurts developers and vibe coders

AI made writing code fast. Understanding it is still as slow as ever, and that is now the bottleneck. This is the research behind codeworld, from November 2026. Several sources are vendors writing about their own market; those are marked.

## The pains, ranked by evidence

| # | Pain | Evidence | Strength |
|---|---|---|---|
| 1 | "Almost right" code is slow to debug | Stack Overflow 2025 survey (49,000+ developers): the #1 frustration (45%) is AI answers that are almost right; 66% spend more time fixing them; trust in AI accuracy fell from 40% to 29% (vendor survey) | strong |
| 2 | Code nobody understands ("comprehension debt") | Anthropic trial, 52 engineers: the AI group scored 50% on a quiz about code they had just written, versus 67% without AI. Developers already spent about 58% of their time understanding code before AI (Xia et al., 78 developers) | strong |
| 3 | Fixes break other features | DORA 2025 (about 5,000 professionals): AI use correlates with more change failures and rework. Columbia DAPLab, 15+ vibe-coded apps: shared state breaks, agents lose track as files grow | medium |
| 4 | Can't tell if the output is right | 35% of non-developers say trust is their biggest challenge; 9% don't verify at all (20i, vendor survey of 600) | medium |
| 5 | The last 20–30% stalls: auth, payments, hosting, security | Addy Osmani's "70% problem"; Veracode found security flaws in about 45% of AI code samples (vendor study) | medium |
| 6 | The "why" evaporates | Builders report agents keep the outcome but lose the reasoning, then reverse sound decisions later | anecdotal |
| 7 | The codebase rots faster | GitClear: duplicated blocks up, refactoring down (vendor data) | medium |
| 8 | Skills fade or never form | Only 16% of senior developers think juniors fully understand the AI code they submit (BairesDev, vendor survey) | medium |
| 9 | Feeling faster isn't being faster | METR 2025: experienced developers were 19% slower with AI while believing they were faster; the 2026 follow-up suggests a small speed-up, with weak evidence | strong |

## The finding that matters most

In Anthropic's trial, the way people used AI mattered more than whether they used it:

| How they worked | Quiz score |
|---|---|
| Generated code, then asked questions about it | 86% |
| Asked for code together with explanations | 68% |
| Asked conceptual questions | 65% |
| No AI at all | 67% |
| Handed the task to AI | 39% |
| Relied on AI more and more | 35% |
| Let AI do the debugging | 24% |

Each pattern had only 2–7 people, the authors say it shows correlation rather than cause, and comprehension was measured right after the task. Still, it points at the lever: make the "engage with it" step cheap and automatic. That is what `explain-back` does.

## When it hurts

1. **Generate:** feels fast; silent choices pile up.
2. **Almost right:** debugging code you didn't write.
3. **Fix loop:** each fix breaks something else.
4. **Change it later:** nobody knows what will break.
5. **Explain it:** to a teammate, reviewer, client or interviewer.

A tool has to show up at those moments. Maps and wikis that wait to be browsed get looked at once.

## What exists, and the gap

| Category | Examples | Gap |
|---|---|---|
| Generated wikis | DeepWiki, Google Code Wiki | Text about structure, not at the moment of change |
| Code review agents | CodeRabbit, Greptile | Talk to reviewers, not to the author |
| Code cities | CodeCity, CodeCharta | Show structure, not behavior; people look once |
| Decision logs | AGENTS.md, ADRs | Manual; the session's "why" usually evaporates |

Nothing yet targets the author, at the moment of change, about behavior and decisions, and also checks they understood.

## Sources

- Anthropic, [How AI assistance impacts the formation of coding skills](https://www.anthropic.com/research/AI-assistance-coding-skills) (2026)
- Stack Overflow, [2025 Developer Survey: AI](https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/)
- Xia et al., [Measuring Program Comprehension](https://xin-xia.github.io/publication/TSE17.pdf), IEEE TSE 2018
- Ahmad, [Comprehension Debt in GenAI-Assisted Software Engineering Projects](https://arxiv.org/html/2604.13277) (2026)
- Google, [DORA 2025 State of AI-assisted Software Development](https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/)
- Columbia DAPLab, [9 Critical Failure Patterns of Coding Agents](https://daplab.cs.columbia.edu/general/2026/01/08/9-critical-failure-patterns-of-coding-agents.html) (2026)
- 20i, [Vibe coding survey](https://www.20i.com/blog/vibe-coding-survey/) (2026)
- Addy Osmani, [The 70% problem](https://addyo.substack.com/p/the-70-problem-hard-truths-about) and [Comprehension Debt](https://addyosmani.com/blog/comprehension-debt/)
- Veracode, [2025 GenAI Code Security Report](https://www.veracode.com/blog/genai-code-security-report/)
- LeadDev on [GitClear's maintainability data](https://leaddev.com/ai/code-maintainability-plummets-in-the-ai-coding-era)
- ITPro on the [BairesDev junior developer survey](https://www.itpro.com/software/development/junior-developer-ai-tools-coding-skills)
- METR, [2025 study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) and [2026 update](https://metr.org/blog/2026-02-24-uplift-update/)
