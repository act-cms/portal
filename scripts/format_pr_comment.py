#!/usr/bin/env python3
"""Format a friendly PR comment from a build_site.py run.

Usage:
    python scripts/format_pr_comment.py <outcome> <build_log> [output]

<outcome> is "success" or "failure" (the GitHub step outcome).
<build_log> is the captured stdout+stderr of `python scripts/build_site.py`.
The rendered Markdown is written to <output> (default: pr_comment.md).

The comment is intended for lesson authors who may not be developers, so it
leads with a clear pass/fail and surfaces only the actionable lines (errors and
warnings) rather than the full, noisy build log.
"""

import sys

# Stable marker so the workflow can find-and-update its own comment instead of
# posting a new one on every push.
MARKER = "<!-- act-cms-lesson-check -->"

ERROR_PREFIXES = ("Error:", "❌")
WARNING_PREFIXES = ("WARNING:", "Warning:")


def collect(log_text):
    errors, warnings = [], []
    for raw in log_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(ERROR_PREFIXES):
            errors.append(line)
        elif line.startswith(WARNING_PREFIXES):
            warnings.append(line)
    return errors, warnings


def render(outcome, log_text):
    errors, warnings = collect(log_text)
    passed = outcome == "success"

    lines = [MARKER, "## ACT-CMS Lesson Portal — PR check", ""]

    if passed:
        lines.append("✅ **All checks passed.** Your lesson validates and the "
                     "portal pages render correctly. It's ready to merge once a "
                     "maintainer approves.")
    else:
        lines.append("❌ **Checks failed.** Please fix the items below and push "
                     "an update to this branch — the check re-runs automatically.")
        if errors:
            lines += ["", "### Errors (must fix)", "```"]
            lines += errors
            lines.append("```")
        else:
            lines += ["", "The build failed but no specific error lines were "
                      "captured. See the full log in the **Actions** tab."]

    if warnings:
        lines += ["", "### Warnings (review, not blocking)", "```"]
        lines += warnings
        lines.append("```")

    lines += [
        "",
        "---",
        "See `template.yaml` for the full field reference. Common pitfalls: "
        "fields like `platforms`, `authors`, and `scientific_objectives` must be "
        "YAML lists (`- item`), and `recommended_platform` must be exactly one "
        "name that matches an entry in `platforms`.",
    ]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 3:
        print("usage: format_pr_comment.py <outcome> <build_log> [output]", file=sys.stderr)
        return 2
    outcome = sys.argv[1]
    log_path = sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else "pr_comment.md"

    try:
        with open(log_path, encoding="utf-8") as f:
            log_text = f.read()
    except OSError:
        log_text = ""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render(outcome, log_text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
