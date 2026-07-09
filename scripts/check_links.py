#!/usr/bin/env python3
"""Link and placeholder checker for lesson YAML submissions.

Usage:
    python scripts/check_links.py [lessons/foo.yml lessons/bar.yml ...]

With no arguments, every ``lessons/*.yml`` file is checked. In CI we pass only
the lesson files changed by the pull request so we don't hammer the network for
unrelated lessons (and so an unrelated, already-broken link can't fail a PR that
didn't touch it).

Two classes of problem are reported, using the same ``Error:`` / ``WARNING:``
line prefixes that ``format_pr_comment.py`` collects for the PR comment:

1. Unreplaced template placeholders — text copied verbatim from ``template.yaml``
   that the author forgot to fill in (e.g. ``"Your Module Title Here"``,
   ``act-cms/your-lesson-repo``). These are **errors**: the lesson is incomplete.

2. Broken links — every ``http(s)`` URL in the file is requested. A definitive
   ``4xx``/``5xx`` response is an **error** (the link is wrong). A network/timeout
   problem where we can't get a verdict is a **warning** (don't fail a PR over a
   flaky network or a host that blocks CI).

Exit status is non-zero if any errors were reported, so the CI step fails.
"""

import re
import sys
from pathlib import Path

import yaml

try:
    import requests
except ImportError:  # pragma: no cover - requests is installed in CI
    requests = None


# Substrings/patterns that only appear in unedited template.yaml placeholder
# text. Matched case-insensitively against the *values* in the lesson (parsed
# YAML, not raw text — so comments copied from the template don't trip it).
# Keep these specific to avoid flagging legitimate content; add new ones here
# when template.yaml grows new placeholder phrasing.
PLACEHOLDER_PATTERNS = [
    r"your[\s-]*module[\s-]*(title|name)",
    r"your[\s-]*lesson[\s-]*repo",
    r"\bprof\.?\s+your\s+name\b",
    r"\bdr\.?\s+collaborator\s+name\b",
    r"\byour\s+name\b",
    r"\bcollaborator\s+name\b",
    r"instructor-access@university\.edu",
    r"brief description of what (this notebook covers|students will learn)",
    r"description of second notebook",
    r"provide a more detailed description",
    r"specific skill students will develop",
    r"another concrete learning outcome",
    r"third measurable objective",
    r"advanced skill development",
    r"application of concepts from part",
    r"understand molecular property x",
    r"use library x to perform",
    r"\b0[12]-(intro|advanced)\.ipynb\b",
    r"\{lesson-filename\}",
    r"<[^>]*your[^>]*>",
    r"\b(TODO|FIXME|XXX|PLACEHOLDER)\b",
]
PLACEHOLDER_RE = [re.compile(p, re.IGNORECASE) for p in PLACEHOLDER_PATTERNS]

URL_RE = re.compile(r"^https?://", re.IGNORECASE)

REQUEST_TIMEOUT = 15  # seconds
# A browser-ish UA: some hosts (incl. GitHub) 403 the bare python-requests UA.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; act-cms-link-check/1.0; "
        "+https://github.com/act-cms/portal)"
    )
}


def walk_strings(node, path="$"):
    """Yield (yaml_path, string_value) for every string leaf in the structure."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from walk_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from walk_strings(item, f"{path}[{i}]")


def find_placeholders(strings):
    """Return a sorted list of placeholder strings still present in the lesson."""
    found = {}
    for _, value in strings:
        for pattern in PLACEHOLDER_RE:
            if pattern.search(value):
                # Collapse to a short, recognisable snippet for the report.
                snippet = value.strip().splitlines()[0][:80]
                found[snippet] = True
                break
    return sorted(found)


def collect_urls(strings):
    """Return the unique set of http(s) URLs referenced in the lesson values."""
    urls = {}
    for _, value in strings:
        candidate = value.strip()
        if URL_RE.match(candidate):
            urls[candidate] = True
    return list(urls)


def check_url(url):
    """Probe a URL.

    Returns (status, detail):
      status == 'ok'      link resolved (2xx/3xx)
      status == 'broken'  definitive client/server error (we have a verdict)
      status == 'unknown' couldn't reach it (network/timeout) — don't fail on it
    """
    if requests is None:
        return "unknown", "the 'requests' library is not installed"

    def attempt(method):
        return requests.request(
            method, url, allow_redirects=True, timeout=REQUEST_TIMEOUT,
            headers=HEADERS,
        )

    try:
        resp = attempt("HEAD")
        # Many hosts don't implement HEAD properly; retry with GET on 4xx/5xx.
        if resp.status_code >= 400:
            resp = attempt("GET")
    except requests.RequestException as exc:
        try:
            resp = attempt("GET")
        except requests.RequestException:
            return "unknown", f"could not connect ({exc.__class__.__name__})"

    if resp.status_code < 400:
        return "ok", str(resp.status_code)
    return "broken", f"HTTP {resp.status_code}"


def check_lesson(path):
    """Check one lesson file. Returns the number of errors reported."""
    name = path.name
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        # build_site.py already reports YAML parse errors; don't double-report.
        print(f"WARNING: {name}: could not parse for link/placeholder check; "
              f"see validation errors above.")
        return 0

    if not isinstance(data, (dict, list)):
        return 0

    strings = list(walk_strings(data))
    errors = 0

    for snippet in find_placeholders(strings):
        print(f"Error: {name}: unreplaced template placeholder: \"{snippet}\". "
              f"Fill in your own content (see template.yaml).")
        errors += 1

    for url in collect_urls(strings):
        status, detail = check_url(url)
        if status == "broken":
            print(f"Error: {name}: broken link ({detail}): {url}")
            errors += 1
        elif status == "unknown":
            print(f"WARNING: {name}: could not verify link ({detail}): {url}")

    if errors == 0:
        print(f"check_links: {name}: placeholders clear, links reachable.")
    return errors


def main():
    args = sys.argv[1:]
    if args:
        files = [Path(a) for a in args if a.strip()]
    else:
        lessons_dir = Path(__file__).resolve().parent.parent / "lessons"
        files = sorted(lessons_dir.glob("*.yml"))

    files = [f for f in files if f.exists()]
    if not files:
        print("check_links: no lesson files to check.")
        return 0

    total_errors = 0
    for path in files:
        total_errors += check_lesson(path)

    if total_errors:
        print(f"Error: link/placeholder check found {total_errors} problem(s).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
