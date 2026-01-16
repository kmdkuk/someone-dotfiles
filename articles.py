#!/usr/bin/env python3
import sys
import subprocess
import json
import shutil
import re
from pathlib import Path

# Constants
ARTICLES_DIR = Path("articles")
README_FILE = Path("README.md")
TAGS_FILE = Path("tags.json")
REPOS_DIR = Path("repos")


def load_tags_config():
    """Load tag detection rules from JSON file.
    Returns a tuple (patterns, inferences).
    """
    if not TAGS_FILE.exists():
        print("Warning: tags.json not found. Using empty rules.")
        return {}, {}

    with open(TAGS_FILE, "r") as f:
        try:
            data = json.load(f)
            # Check if using new structure with 'patterns' key
            if "patterns" in data:
                return data.get("patterns", {}), data.get("inferences", {})
            return data, {}  # Backward compatibility
        except json.JSONDecodeError as e:
            print(f"Error parse tags.json: {e}")
            return {}, {}


def run_command(command, cwd=None):
    """Run a shell command and return stdout. Raises error on failure."""
    result = subprocess.run(
        command, shell=True, cwd=cwd, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def get_repo_info(url_or_repo):
    """Extract owner and repo from URL or 'owner/repo' string."""
    # Match patterns like https://github.com/owner/repo or owner/repo
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url_or_repo)
    if match:
        return match.group(1), match.group(2).replace(".git", "")

    parts = url_or_repo.split("/")
    if len(parts) == 2:
        return parts[0], parts[1]

    raise ValueError(f"Invalid repository format: {url_or_repo}")


def fetch_github_metadata(owner, repo):
    """Fetch repository description using gh cli."""
    try:
        cmd = f"gh repo view {owner}/{repo} --json description"
        output = run_command(cmd)
        data = json.loads(output)
        return data.get("description", "") or ""
    except subprocess.CalledProcessError as e:
        print(f"Error fetching metadata for {owner}/{repo}: {e}")
        raise e  # Re-raise to be caught by caller


def fetch_all_github_descriptions(repos):
    """Fetch descriptions for multiple repos using GraphQL batch query."""
    if not repos:
        return {}

    # GraphQL alias must be alphanumeric. Map index to owner/repo.
    # Batches of 50 to avoid limits
    batch_size = 50
    results = {}

    for i in range(0, len(repos), batch_size):
        batch = repos[i : i + batch_size]
        query_parts = []
        slug_map = {}

        for j, (owner, repo) in enumerate(batch):
            alias = f"r{j}"
            query_parts.append(
                f'{alias}: repository(owner: "{owner}", name: "{repo}") {{ description }}'
            )
            slug_map[alias] = f"{owner}/{repo}"

        query = "query { " + " ".join(query_parts) + " }"

        # Construct gh api command
        # Use -f query=... but special chars might be tricky. Using input via stdin is safer or just careful quoting.
        # run_command takes shell=True, so simple string formatting works if careful.
        # But for strictly correct JSON, passing via -f query might be complex with newlines.
        # Let's try passing as a single line string.

        try:
            # gh api graphql -f query='...'
            # Escape single quotes in query if any (unlikely in this constructed query)
            cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
            # Use subprocess.run directly to avoid shell string escaping issues
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"GraphQL batch query failed: {result.stderr}")
                # Continue to process what we can or mark all as failed?
                # If query fails completely, we can't do much for this batch.
                continue

            data = json.loads(result.stdout)

            # Check for errors field (for missing repos etc)
            # GraphQL errors return data as null for that field usually, but if top level fails it might be differnt.
            # partial data is returned in 'data'

            response_data = data.get("data", {})
            if response_data:
                for alias, repo_data in response_data.items():
                    full_name = slug_map.get(alias)
                    if full_name:
                        if repo_data:
                            results[full_name] = repo_data.get("description", "") or ""
                        else:
                            # repo_data is null -> likely repo not found
                            # We can treat description as empty or handle as error?
                            # Previous logic expects string.
                            # If null, it means repo not found, likely.
                            # Let's verify by checking 'errors'
                            results[full_name] = (
                                None  # Mark as None to indicate fetch failure/not found
                            )

        except Exception as e:
            print(f"Error in batch fetch: {e}")

    return results


def detect_tags(repo_path, patterns):
    """Detect tags based on file structure using rules."""
    tags = set()
    repo_path = Path(repo_path)

    for tag_name, rules in patterns.items():
        for pattern in rules:
            # Use glob with **/ to find matches in subdirectories too
            if any(repo_path.glob(f"**/{pattern}")):
                tags.add(tag_name)
                break  # Found one match for this tag, move to next tag

    return sorted(list(tags))


def apply_inferences(tags, inferences):
    """Apply tag inferences recursively."""
    if not inferences:
        return tags

    current_tags = set(tags)

    while True:
        added = False
        # inferences: {"Parent": ["Child", ...]}
        for parent, children in inferences.items():
            if parent in current_tags:
                continue
            # If any child is present, add parent
            if any(child in current_tags for child in children):
                current_tags.add(parent)
                added = True

        if not added:
            break

    return sorted(list(current_tags))


def prepare_repo_and_detect_tags(owner, repo, patterns):
    """Clone or pull repo in repos/ dir and detect tags."""
    repo_path = REPOS_DIR / owner / repo
    repo_url = f"https://github.com/{owner}/{repo}.git"

    if not repo_path.exists():
        print(f"Cloning {repo_url}...")
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_command(f"git clone --depth 1 {repo_url} {repo_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning {owner}/{repo}: {e}")
            return []
    else:
        print(f"Updating {owner}/{repo}...")
        try:
            run_command("git pull", cwd=repo_path)
        except subprocess.CalledProcessError as e:
            print(f"Error updating {owner}/{repo}: {e}. Re-cloning...")
            shutil.rmtree(repo_path)
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                run_command(f"git clone --depth 1 {repo_url} {repo_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error re-cloning {owner}/{repo}: {e}")
                return []

    return detect_tags(repo_path, patterns)


def upsert_article(owner, repo, description=None):
    """Create or update an article file."""
    slug = f"{owner}-{repo}"
    filename = ARTICLES_DIR / f"{slug}.mdx"

    print(f"Processing {owner}/{repo}...")

    patterns, inferences = load_tags_config()

    # 1. Fetch metadata
    # If description is passed (from batch), use it.
    # usage of 'is None' allows empty string description to be valid
    if description is None:
        try:
            description = fetch_github_metadata(owner, repo)
        except Exception as e:
            raise Exception(f"Failed to fetch metadata: {e}")

    # Escape double quotes for YAML frontmatter
    description = description.replace('"', '\\"')

    tags = prepare_repo_and_detect_tags(owner, repo, patterns)

    existing_content = ""
    ignore_tags = set()
    manual_tags = set()
    source_url = f"https://github.com/{owner}/{repo}"

    # 3. Read existing content if available
    if filename.exists():
        print(f"Updating existing file: {filename}")
        with open(filename, "r") as f:
            content = f.read()
            # Split by '---' to separate frontmatter and body
            parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
            if len(parts) >= 3:
                existing_content = parts[2]  # Keep everything after the second ---

                # Parse frontmatter
                frontmatter_text = parts[1]

                # Parse ignore_tags
                ignore_match = re.search(
                    r"ignore_tags:\s*\[(.*?)\]", frontmatter_text, re.DOTALL
                )
                if ignore_match:
                    raw_ignores = ignore_match.group(1).split(",")
                    ignore_tags = {tag.strip() for tag in raw_ignores if tag.strip()}

                # Parse manual_tags
                manual_match = re.search(
                    r"manual_tags:\s*\[(.*?)\]", frontmatter_text, re.DOTALL
                )
                if manual_match:
                    raw_manuals = manual_match.group(1).split(",")
                    manual_tags = {tag.strip() for tag in raw_manuals if tag.strip()}

            else:
                existing_content = content
    else:
        print(f"Creating new file: {filename}")
        # Default body for new files
        existing_content = f"\n# {owner}/{repo}\n\n{description}\n"

        # Append to README if new
        update_readme(owner, repo, filename)

    # Add manual tags
    if manual_tags:
        tags.extend(list(manual_tags))

    # Apply inferences
    tags = apply_inferences(tags, inferences)

    # Deduplicate and sort
    tags = sorted(list(set(tags)))

    # Filter ignored tags
    tags = [tag for tag in tags if tag not in ignore_tags]

    # Prepare tags YAML
    tags_yaml = "\n".join([f"  - {tag}" for tag in tags])

    # Prepare ignore_tags YAML line if needed
    ignore_tags_line = ""
    if ignore_tags:
        ignore_tags_list = ", ".join(sorted(list(ignore_tags)))
        ignore_tags_line = f"ignore_tags: [{ignore_tags_list}]\n"

    # Prepare manual_tags YAML line if needed
    manual_tags_line = ""
    if manual_tags:
        manual_tags_list = ", ".join(sorted(list(manual_tags)))
        manual_tags_line = f"manual_tags: [{manual_tags_list}]\n"

    frontmatter = f"""---
slug: {slug}
repository: {owner}/{repo}
description: "{description}"
tags:
{tags_yaml}
{ignore_tags_line}{manual_tags_line}source: {source_url}
---
"""

    # 4. Write new file
    # Ensure existing content starts with newline if it doesn't
    if existing_content and not existing_content.startswith("\n"):
        existing_content = "\n" + existing_content

    with open(filename, "w") as f:
        f.write(frontmatter + existing_content)


def update_readme(owner, repo, filepath):
    """Append link to README.md."""
    link = f"- [{owner}/{repo}](./{filepath})"

    with open(README_FILE, "r") as f:
        lines = f.readlines()

    # Check if link already exists
    for line in lines:
        if f"[{owner}/{repo}]" in line:
            return

    # Append to the end
    # Find the last list item to check where to append? Or just append to file end?
    # The requirement says "append", let's append to the end of the list matching the format.
    # The README has a list of links.

    with open(README_FILE, "a") as f:
        f.write(f"\n{link}")
    print(f"Appended {owner}/{repo} to README.md")


def update_all():
    """Update all existing articles."""
    if not ARTICLES_DIR.exists():
        print("No articles directory found.")
        return

    # 1. Collect all repos from files
    repos = []
    failed_repos = []

    files = list(ARTICLES_DIR.glob("*.mdx"))
    for filename in files:
        with open(filename, "r") as f:
            content = f.read()
            match = re.search(r"repository:\s*(\S+)", content)
            if match:
                repo_full = match.group(1)
                try:
                    owner, repo = get_repo_info(repo_full)
                    repos.append((owner, repo))
                except Exception:
                    print(f"Skipping {filename}: Invalid repo format {repo_full}")

    # 2. Batch fetch descriptions
    descriptions = fetch_all_github_descriptions(repos)

    # 3. Process each repo
    for owner, repo in repos:
        full_name = f"{owner}/{repo}"
        desc = descriptions.get(full_name)

        # If desc is None, it means batch fetch returned null for this repo (e.g. not found)
        # OR multiple batches failed.
        # If it was simply an empty description, it would be "".
        # But fetch_all... returns None for missing lookup.

        # If it failed to fetch, we might want to try individually or just log error?
        # Trying individually is safer if batch partial failure logic is complex.
        # But for "Update All", fast is better.

        if desc is None:
            # Try fallback or mark as failed?
            # Let's mark as failed for summary if it really failed.
            # But wait, if description is just not in result dict, maybe we didn't query it?
            # logic above queries all 'repos'.
            # So safely assume error.
            # However, let's treat it as empty string if we can't distinguish?
            # No, better to error.
            pass

        try:
            # Pass desc. IF desc is None, upsert_article will try to fetch individually!
            # Which is a good fallback.
            upsert_article(owner, repo, description=desc)
        except Exception as e:
            print(f"Failed to update {full_name}: {e}")
            failed_repos.append({"repo": full_name, "error": str(e)})

    # 4. Print Summary
    if failed_repos:
        print("\n" + "=" * 30)
        print("update-all Error Summary")
        print("=" * 30)
        for fail in failed_repos:
            print(f"- {fail['repo']}: {fail['error']}")
        print("=" * 30)
        print(f"Total failures: {len(failed_repos)}")
    else:
        print("\nAll repositories updated successfully!")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 articles.py update-all")
        print("  python3 articles.py update <url_or_repo>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "update-all":
        update_all()
    elif command == "update":
        if len(sys.argv) < 3:
            print("Error: Missing URL or repository name.")
            sys.exit(1)
        url = sys.argv[2]
        owner, repo = get_repo_info(url)
        try:
            upsert_article(owner, repo)
        except Exception as e:
            print(f"Error updating {owner}/{repo}: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
