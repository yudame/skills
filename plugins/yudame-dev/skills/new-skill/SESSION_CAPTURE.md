# Session Capture ("skillify")

**Goal:** turn the repeatable process performed in this session into a workflow skill that another session could run and get the same result, carrying forward every correction the user made along the way. If the user described the process, their words are: "$ARGUMENTS".

## 1. Read the session first

Before asking anything, work out from the conversation: the process and its inputs; the distinct steps in order; what proved each step done (an open PR with green CI, not "wrote code"); the tools, permissions, and agents used; and, most valuable of all, every place the user corrected or redirected you. Those corrections are the knowledge a fresh model would not have.

## 2. Confirm with the user

Use AskUserQuestion for these questions, offering concrete choices (the tool already gives the user a free-text option, so don't add a "something else" choice). Ask only what the session didn't already answer, and for a simple process one or two rounds is enough. Cover:

- **Name, description, goal, and done condition** you propose.
- **The steps** as a numbered list, plus suggested arguments if it takes any.
- **Inline or forked:** forked suits self-contained work with no mid-course input; inline suits work the user wants to steer.
- **Where to save it:** this repo (`.claude/skills/<name>/`), a plugin in a shared skills repo (`plugins/<plugin>/skills/<name>/`, invoked as `/<plugin>:<name>`), or personal (`~/.claude/skills/<name>/`). Suggest the plugin for cross-repo workflows and the repo for project-specific ones.
- **Per step, only where unclear:** what it produces for later steps, what proves it succeeded, whether it needs the user's confirmation (irreversible or outward-facing actions), whether it can run in parallel or in a subagent, and any hard rules.
- **Trigger phrases** and any remaining gotchas.

## 3. Write and save

Build the SKILL.md from [WORKFLOW_TEMPLATE.md](WORKFLOW_TEMPLATE.md), with `allowed-tools` set to the permission patterns actually used in the session. Show the complete file in a fenced block, ask a one-line AskUserQuestion ("Save this SKILL.md?"), then write it.

Tell the user where it was saved, how to invoke it (`/<name>` or `/<plugin>:<name>`, with arguments), that it loads in a new session, and that they can edit the file directly to refine it.
