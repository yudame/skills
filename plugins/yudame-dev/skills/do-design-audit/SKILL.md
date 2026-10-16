---
name: do-design-audit
description: "Audit a live web UI against a design rubric: a scored finding per dimension and the top three fixes. Use for 'review this design'."
allowed-tools: mcp__byob__browser_navigate mcp__byob__browser_read mcp__byob__browser_click mcp__byob__browser_screenshot mcp__byob__browser_close_tab mcp__byob__browser_list_tabs mcp__byob__browser_wait_for
context: fork
---

Audit an existing web interface and produce the report below: every rubric dimension rated with a specific finding, then the three fixes that would most improve it. This is the review-time companion to the `frontend-design` skill (where installed), which builds to the same standard. The audit changes no code.

Be opinionated. "Acceptable" is not praise, and a finding names the exact element and what is wrong with it. "Typography could be improved" is not a finding; "the hero heading and the paragraph under it share one font weight, so the page has no hierarchy" is.

## Inputs

- `url` (required): a local dev server or a deployed URL.
- `--pages` (optional): comma-separated paths to capture, e.g. `/,/about,/pricing`. Without it, follow the site's navigation from the start URL and stop at six pages.

## Capturing the pages

The audit runs in the user's real, logged-in Chrome through the BYOB MCP (`mcp__byob__browser_*`), so public pages and authenticated dashboards look exactly as the user sees them. There is no headless fallback. Two sessions driving the real browser at once fight over the active tab and corrupt each other's reads, so don't run this alongside another browser-driving task.

Screenshot the start page right after it loads, before interacting, to capture the first impression. Then visit each page from `--pages`, or discover pages by reading the start page's `interactiveElements` and clicking its nav links:

```text
mcp__byob__browser_navigate(url="<url>", waitUntil="networkidle")
mcp__byob__browser_screenshot(tabId=<tab>, savePath="/tmp/design-audit-01.png")
mcp__byob__browser_read(url="<url>", reuseTab=true, screens=1)          # nav links: role="link"
mcp__byob__browser_click(tabId=<tab>, selector="byob:idx=<nav_link_idx>")
mcp__byob__browser_screenshot(tabId=<tab>, savePath="/tmp/design-audit-<slug>.png")
```

Capture at desktop width only; mobile behavior is predicted from structure (dimension 9), not measured.

## Rubric

Rate each dimension ✅ Premium (deliberate and polished, nothing to do), ⚠️ Acceptable (won't embarrass, won't impress; clear room to improve), or ❌ Needs work (a specific problem with an actionable fix).

1. **Visual hierarchy.** Can a visitor tell in three seconds what the page is for and where to start? Look for a dominant heading or hero moment, scale and contrast directing attention, and real negative space between sections. Fails: everything at similar size and weight, walls of content, no starting point, a primary CTA that blends in.

2. **Typography.** A distinct display face over a complementary body face, sizes on a modular scale, real weight contrast between levels, body lines of 45 to 75 characters with comfortable leading. Fails: Inter, Roboto, Arial, Open Sans or system-ui as the only face; headings and body at near-identical weight; arbitrary size jumps; monospace as a lazy "technical" signal.

3. **Color and contrast.** A committed palette with clear hierarchy (background, surface, accent), neutrals tinted toward the brand hue, accents used sparingly, no pure #000 or #fff, text that meets contrast. Fails: cyan-on-dark or purple-to-blue gradients, gradient text on headings, gray text on colored backgrounds, more than four competing accents, washed-out text, neon-on-dark as the default look.

4. **Spacing and alignment.** A spacing system with rhythm: tight within groups, generous between sections, gaps growing as relationships weaken, content on an implicit column grid. Fails: identical padding everywhere, unexplained misalignments, sections bleeding together, margins not derived from a base unit.

5. **Visual details.** Imagery that is high quality and purposefully cropped, consistent treatment and aspect ratios within grids, decoration (texture, pattern, layering) that fits the tone and rewards a close look. Fails: generic rounded rectangles with drop shadows, glassmorphism everywhere, an icon above every heading, decorative sparklines with no data, the thick one-side colored border, placeholder-grade imagery.

6. **Micro-interactions.** Interactive elements that announce themselves: designed hover and focus states, transitions on state changes, distinct default, hover, active and disabled button states. Where you can't interact, infer from the markup and CSS (transition properties, custom focus styles, aria and disabled attributes). Fails: no hover state, browser-default blue focus rings on custom-styled elements, no feedback on interactive surfaces, every button styled primary.

7. **Consistency.** Repeated elements that clearly belong to one system: a shared vocabulary of buttons, cards and headings, the spacing system applied everywhere, recurring motifs. Fails: two button styles for no reason, sections that look like different templates, mixed corner radii, alternating card styles without logic, heading sizes off-scale across pages.

8. **Trust signals.** Evidence someone cared: real quotes and dashes, no placeholder text, a complete footer (privacy policy, company details), cleanly rendered testimonials and logos, considered error and edge states. Fails: lorem ipsum anywhere, broken images or layout artifacts, misalignment that suggests no QA, a three-word footer, logos cropped or inconsistently sized.

9. **Mobile responsiveness (predicted).** Would the structure survive 375px? Look for flexbox or grid structure, type large enough to scale down, no hover-only interactions, touch targets that look at least 44×44px. Name specific concerns rather than giving a blanket pass. Fails: four-column grids with no visible breakpoint strategy, type that would become unreadable, hover-only menus, full-width decoration that would break when narrow.

10. **AI slop check.** Would someone take this for AI-generated, or ask which studio made it? Intentionality shows as an unexpected aesthetic choice, a non-default typeface, a deliberate grid break, a color that isn't safe. Fails, per the `frontend-design` skill: the hero-metric template (big number, small label, supporting stats, gradient accent); a rounded icon above every heading in a feature grid; cards nested in cards; endless same-sized icon-heading-text cards; cyan-on-dark or purple gradients; neon-on-dark as default; gradient text on headings or metrics; everything centered; every button primary.

## Report

```markdown
## Design Review: [URL]

**Pages reviewed:** [pages captured]

### Evaluation

| Dimension | Rating | Findings |
|-----------|--------|----------|
| Visual hierarchy | ✅/⚠️/❌ | [specific observation] |
| Typography | ✅/⚠️/❌ | [specific observation] |
| Color & contrast | ✅/⚠️/❌ | [specific observation] |
| Spacing & alignment | ✅/⚠️/❌ | [specific observation] |
| Visual details | ✅/⚠️/❌ | [specific observation] |
| Micro-interactions | ✅/⚠️/❌ | [specific observation] |
| Consistency | ✅/⚠️/❌ | [specific observation] |
| Trust signals | ✅/⚠️/❌ | [specific observation] |
| Mobile responsiveness | ✅/⚠️/❌ | [specific observation] |
| AI slop check | ✅/⚠️/❌ | [specific observation] |

### Top 3 Improvements

**1. [The problem, named]**
[What to change, where, and why it matters, concrete enough to act on without a follow-up question. Not "improve spacing" but "increase the gap between the nav bar and the hero from 12px to 48px; right now they read as one block."]

**2. ...**

**3. ...**

### Overall Assessment
[One or two sentences: the quality level stated plainly, the strongest quality, the most critical weakness. No hedging.]
```

Fixes follow the project's own style guide or design system (the house-style skill only where it has none), at the system level when the problem is systemic (type scale, palette); then re-run the audit.
