#!/usr/bin/env python3
"""Protect the default branch of one or more book repos.

    python3 tools/protect_repo.py my-book other-book
    python3 tools/protect_repo.py eckko/my-book --check
    python3 tools/protect_repo.py my-book --dry-run

What it sets (one repository ruleset, "Protect default branch"):
  - changes reach the default branch only through a pull request (no
    approval is required, so you can merge your own PRs);
  - the branch cannot be force-pushed or deleted;
  - the repository admin role may bypass all of this, so the owner can
    still push straight to main.

A bare name means the owner eckko. It needs the GitHub CLI (gh) signed in
with admin rights on each repo. Running it again updates the ruleset in
place. Private repositories need GitHub Pro (or Team) for rulesets.

Anyone or anything using an admin token (the owner, or a session or action
that uses the owner's token) can bypass the ruleset. Use a token without
admin rights for automation that must go through pull requests.
"""

import argparse
import json
import subprocess
import sys

DEFAULT_OWNER = "eckko"
RULESET_NAME = "Protect default branch"
ADMIN_ROLE_ID = 5  # GitHub's id for the "Repository admin" role


def ruleset_definition():
    """The ruleset as the GitHub API takes it."""
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "conditions": {
            "ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []},
        },
        "bypass_actors": [{
            "actor_id": ADMIN_ROLE_ID,
            "actor_type": "RepositoryRole",
            "bypass_mode": "always",
        }],
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 0,
                "dismiss_stale_reviews_on_push": False,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_review_thread_resolution": False,
            }},
        ],
    }


def full_name(repo):
    """owner/name for a bare name or an owner/name."""
    return repo if "/" in repo else f"{DEFAULT_OWNER}/{repo}"


def call_github(method, path, body=None):
    """Run one gh api call; return the parsed JSON (None when empty)."""
    command = ["gh", "api", "-X", method, path]
    if body is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command, input=json.dumps(body) if body is not None else None,
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError((result.stdout + result.stderr).strip())
    return json.loads(result.stdout) if result.stdout.strip() else None


def find_ruleset_id(repo):
    """The id of our ruleset in the repo, or None."""
    for ruleset in call_github("GET", f"repos/{repo}/rulesets") or []:
        if ruleset["name"] == RULESET_NAME:
            return ruleset["id"]
    return None


def protect(repo, dry_run):
    """Create or update the ruleset. Returns a line saying what happened."""
    existing = find_ruleset_id(repo)
    verb = "update" if existing else "create"
    if dry_run:
        return f"would {verb} the ruleset"
    path = f"repos/{repo}/rulesets" + (f"/{existing}" if existing else "")
    call_github("PUT" if existing else "POST", path, ruleset_definition())
    return f"{verb}d the ruleset"


def check(repo):
    """Says whether the repo has our ruleset and whether it is active."""
    existing = find_ruleset_id(repo)
    if existing is None:
        return "NOT protected (no ruleset)"
    ruleset = call_github("GET", f"repos/{repo}/rulesets/{existing}")
    return f"ruleset present, enforcement: {ruleset['enforcement']}"


def explain(error):
    """A hint for the errors people hit most."""
    text = str(error)
    if "Upgrade to GitHub Pro" in text or "make this repository public" in text:
        return text + "\n  Hint: rulesets on private repos need GitHub Pro."
    if "Not Found" in text or "404" in text:
        return text + "\n  Hint: check the name and that you have admin rights."
    return text


def main():
    """Apply, check or preview the protection for each repo given."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("repos", nargs="+", help="name or owner/name")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true",
                      help="say what would happen, change nothing")
    mode.add_argument("--check", action="store_true",
                      help="report whether each repo is protected")
    args = parser.parse_args()
    failed = False
    for name in args.repos:
        repo = full_name(name)
        try:
            line = check(repo) if args.check else protect(repo, args.dry_run)
            print(f"{repo}: {line}")
        except RuntimeError as error:
            failed = True
            print(f"{repo}: FAILED: {explain(error)}", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
