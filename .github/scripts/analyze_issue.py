#!/usr/bin/env python3
"""
GitHub Issue Analyzer & Auto-PR Generator
Analyzes GitHub issues and either requests more info or generates a PR with implementation
"""

import os
import json
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

import anthropic
import urllib.request
import urllib.error


def get_github_headers():
    """Get headers for GitHub API requests"""
    token = os.environ.get('GITHUB_TOKEN')
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }


def fetch_issue_details(issue_number):
    """Fetch full issue details including comments from GitHub API"""
    owner, repo = 'fitsnips', 'web-rabbithole223.com'

    # Fetch issue details
    issue_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}'
    req = urllib.request.Request(issue_url, headers=get_github_headers())

    try:
        with urllib.request.urlopen(req) as response:
            issue = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error fetching issue: {e}")
        return None

    # Fetch comments
    comments_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
    req = urllib.request.Request(comments_url, headers=get_github_headers())

    try:
        with urllib.request.urlopen(req) as response:
            comments = json.loads(response.read().decode())
    except urllib.error.HTTPError:
        comments = []

    return {
        'issue': issue,
        'comments': comments
    }


def extract_model_from_body(body):
    """Extract model name from issue body if present"""
    if not body:
        return 'claude-haiku-4-5-20251001'

    # Look for model: field (case-insensitive)
    match = re.search(r'model:\s*([^\n]+)', body, re.IGNORECASE)
    if match:
        model = match.group(1).strip()
        valid_models = [
            'claude-haiku-4-5-20251001',
            'claude-sonnet-4-5-20250929',
            'claude-opus-4-6'
        ]
        if model in valid_models:
            return model

    return 'claude-haiku-4-5-20251001'


def should_skip_processing():
    """Check if we should skip processing (bot-related checks)"""
    sender_type = os.environ.get('SENDER_TYPE', '')
    github_actor = os.environ.get('GITHUB_ACTOR', '')
    issue_action = os.environ.get('ISSUE_ACTION', '')

    # Skip if opened by a bot
    if sender_type == 'Bot':
        print("Skipping: issue opened by a bot")
        return True

    # Skip if running as github-actions[bot]
    if github_actor == 'github-actions[bot]':
        print("Skipping: running as github-actions[bot]")
        return True

    return False


def branch_exists(branch_name):
    """Check if a branch already exists"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', f'origin/{branch_name}'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def call_claude_api(issue_details, model):
    """Call Claude API to analyze the issue"""
    issue = issue_details['issue']
    comments = issue_details['comments']

    # Build comment thread for context
    comment_text = ""
    for comment in comments:
        author = comment['user']['login']
        body = comment['body']
        comment_text += f"\n**@{author}**: {body}"

    system_prompt = """You are an assistant that creates blog posts for a Hugo static blog about home mushroom cultivation.

The site structure:
- Content lives in `content/post/YYYY/` as Markdown files with YAML front matter
- YAML fields: title, description, date, draft, categories, tags, thumbnail, author
- Images are hosted on CloudFront CDN: https://static.rabbithole223.com/images/
- Categories are things like "Beginners", "Advanced", "Cultivation Techniques", etc.
- Tags are specific topics like "home mushroom cultivation", "contamination prevention", etc.

Your task: CREATE a blog post from the issue. DO NOT ask for more info unless absolutely critical (like no topic is mentioned).

You have a topic/title = implement. Make reasonable assumptions about content, structure, and tone if details are vague.

Return JSON:
{
  "action": "implement",
  "missing_details": [],
  "files": [{
    "path": "content/post/2026/filename.md",
    "content": "---\ntitle: ...\n---\n...",
    "operation": "create"
  }],
  "pr_title": "...",
  "pr_body": "..."
}

ALWAYS choose "implement" unless the issue is completely empty or nonsensical. Make the post based on what's provided."""

    # Extract author from issue body if present (markdown checkbox format)
    author = "rabbithole223"  # default
    if issue['body']:
        if "- [x] rabbithole223" in issue['body'] or "- [x] rabbithole223 (default)" in issue['body']:
            author = "rabbithole223"
        else:
            author_match = re.search(r'## Author\s*.*?- \[x\]\s*([^\n]+)', issue['body'], re.DOTALL)
            if author_match:
                author = author_match.group(1).strip()

    user_prompt = f"""GitHub Issue Analysis Request

Title: {issue['title']}

Author: {author}

Body:
{issue['body'] or 'No description provided'}

Labels: {', '.join([l['name'] for l in issue['labels']]) or 'None'}

Comments/Discussion:{comment_text or ' No comments yet'}

Create a blog post from this request. Include author in YAML front matter if provided."""

    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    message = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        system=system_prompt
    )

    # Extract JSON from response
    response_text = message.content[0].text

    # Try to parse JSON from the response
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if not json_match:
        print("Error: Could not find JSON in Claude's response")
        print(response_text)
        return None

    try:
        analysis = json.loads(json_match.group())
        return analysis
    except json.JSONDecodeError as e:
        print(f"Error parsing Claude's JSON response: {e}")
        print(response_text)
        return None


def add_label_and_comment(issue_number, missing_details):
    """Add 'needs-more-info' label and post a comment to the issue"""
    owner, repo = 'fitsnips', 'web-rabbithole223.com'

    # Add label
    label_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/labels'
    label_data = json.dumps(['needs-more-info']).encode()
    req = urllib.request.Request(label_url, data=label_data, headers=get_github_headers(), method='POST')

    try:
        urllib.request.urlopen(req)
        print("Added 'needs-more-info' label")
    except urllib.error.HTTPError as e:
        print(f"Warning: Could not add label: {e}")

    # Post comment
    comment_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'

    comment_body = "Thanks for the issue! 🍄\n\nTo help us create the best content, we need a bit more information:\n\n"
    for detail in missing_details:
        comment_body += f"- {detail}\n"

    comment_body += "\nPlease reply with these details, and we'll get your post created!"

    comment_data = json.dumps({'body': comment_body}).encode()
    req = urllib.request.Request(comment_url, data=comment_data, headers=get_github_headers(), method='POST')

    try:
        urllib.request.urlopen(req)
        print("Posted comment requesting more information")
    except urllib.error.HTTPError as e:
        print(f"Error posting comment: {e}")


def create_branch_and_pr(issue_number, analysis, issue_title):
    """Create a branch, write files, commit, push, and open a PR"""
    owner, repo = 'fitsnips', 'web-rabbithole223.com'

    # Create branch name from issue number and title slug
    slug = re.sub(r'[^a-z0-9]+', '-', issue_title.lower()).strip('-')[:30]
    branch_name = f'issue-{issue_number}-{slug}'

    # Check if branch already exists
    if branch_exists(branch_name):
        print(f"Branch {branch_name} already exists, skipping PR creation")
        return

    # Configure git
    subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True, capture_output=True)

    # Create and checkout new branch from stage
    try:
        subprocess.run(['git', 'fetch', 'origin', 'stage'], check=True, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', branch_name, 'origin/stage'], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch: {e}")
        return

    # Write files
    files_written = []
    for file_info in analysis.get('files', []):
        file_path = file_info['path']
        content = file_info['content']

        # Create parent directories if needed
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

        files_written.append(file_path)
        print(f"Wrote file: {file_path}")

    if not files_written:
        print("No files to write, skipping commit and PR")
        return

    # Stage files
    for file_path in files_written:
        subprocess.run(['git', 'add', file_path], check=True, capture_output=True)

    # Commit (use simple one-liner to avoid subprocess escaping issues)
    pr_title = analysis.get('pr_title', f'Content from issue #{issue_number}')
    commit_message = f"Add blog post: {pr_title} (closes #{issue_number})"

    subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)

    # Push branch
    try:
        result = subprocess.run(['git', 'push', '-u', 'origin', branch_name], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error pushing branch: {result.stderr}")
            return
        print(f"Pushed branch {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error pushing branch: {e}")
        return

    # Create PR using gh CLI
    pr_title = analysis.get('pr_title', f"Content from issue #{issue_number}")
    pr_body = analysis.get('pr_body', "See issue for details") + f"\n\nCloses #{issue_number}"

    try:
        subprocess.run([
            'gh', 'pr', 'create',
            '--base', 'stage',
            '--head', branch_name,
            '--title', pr_title,
            '--body', pr_body
        ], check=True, capture_output=True)
        print(f"Created PR from {branch_name} to stage")
    except subprocess.CalledProcessError as e:
        print(f"Error creating PR: {e}")


def main():
    """Main entry point"""
    # Check if we should skip
    if should_skip_processing():
        return

    issue_number = os.environ.get('ISSUE_NUMBER')
    if not issue_number:
        print("Error: ISSUE_NUMBER not set")
        sys.exit(1)

    print(f"Analyzing issue #{issue_number}")

    # Fetch issue details
    issue_details = fetch_issue_details(issue_number)
    if not issue_details:
        print("Failed to fetch issue details")
        sys.exit(1)

    # Extract model
    model = extract_model_from_body(issue_details['issue']['body'])
    print(f"Using model: {model}")

    # Call Claude API
    analysis = call_claude_api(issue_details, model)
    if not analysis:
        print("Failed to analyze issue with Claude")
        sys.exit(1)

    print(f"Analysis result: {analysis['action']}")

    # Act on result
    if analysis['action'] == 'needs-more-info':
        add_label_and_comment(issue_number, analysis['missing_details'])
    elif analysis['action'] == 'implement':
        issue_title = issue_details['issue']['title']
        create_branch_and_pr(issue_number, analysis, issue_title)
    else:
        print(f"Unknown action: {analysis['action']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
