# GitHub Action: Issue Analyzer & Auto-PR

This GitHub Action automatically analyzes new GitHub issues and either:
- **Requests more information** if details are insufficient
- **Generates a blog post** and opens a PR to `staging` if ready

## Setup

### 1. Add ANTHROPIC_API_KEY Secret

1. Go to your GitHub repository: `rabbithole223/web-rabbithole223.com`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your Anthropic API key
6. Click **Add secret**

The workflow automatically uses `GITHUB_TOKEN` (provided by GitHub Actions) for repository operations.

## How It Works

### Workflow Triggers
- **New Issue**: When someone opens a new GitHub issue
- **New Comment**: When someone comments on an issue (allows providing missing info)

### Analysis Flow

The action will:

1. **Fetch Issue Context**
   - Reads issue title, body, labels, and all comments

2. **Extract Model Preference** (optional)
   - Look for `model:` field in issue body (case-insensitive)
   - Supported values:
     - `claude-haiku-4-5-20251001` (default, fastest & cheapest)
     - `claude-sonnet-4-5-20250929`
     - `claude-opus-4-6` (most capable)
   - Example issue body:
     ```
     Title: New guide on contamination prevention

     model: claude-sonnet-4-5-20250929

     I'd like a guide on preventing contamination...
     ```

3. **Send to Claude**
   - Provides context about the blog's structure and content style
   - Asks Claude to determine if enough info exists

4. **Claude Responds with JSON**
   - `action`: either `needs-more-info` or `implement`
   - If `needs-more-info`: list of missing details
   - If `implement`: complete file(s) with YAML front matter and content

5. **Take Action**
   - **needs-more-info**: Adds label + posts comment listing what's needed
   - **implement**: Creates branch → writes files → commits → pushes → opens PR to `staging`

## Blog Post Structure

The action creates blog posts with this structure:

```
content/post/YYYY/my-post.md
```

With YAML front matter:

```markdown
---
title: "Post Title"
description: "Brief description for preview"
date: 2026-02-16
draft: false
categories: ["Beginners", "Cultivation Techniques"]
tags: ["home mushroom cultivation", "DIY", "beginner guide"]
thumbnail: "<thumbnail_url>"
---

Your blog post content here...
```

**Fields:**
- `title`: Post title
- `description`: Short description (shows in previews)
- `date`: Publication date (YYYY-MM-DD)
- `draft`: Set to `false` to publish
- `categories`: List of categories (e.g., "Beginners", "Advanced", "Cultivation Techniques")
- `tags`: List of topic tags
- `thumbnail`: Image URL (placeholder `<thumbnail_url>` if no image available)

**Image Hosting:**
- Images hosted on CloudFront CDN: `https://static.rabbithole223.com/images/`
- Upload images separately; Claude will provide placeholder URLs

## Example Issue

### Minimal Issue (will request more info)

```
Title: New mushroom variety guide
Body: I want to write about growing oyster mushrooms
```

**Result:** Action adds `needs-more-info` label + comments with what's needed:
- Specific variety details
- Difficulty level
- Growing tips/instructions
- Contamination prevention

### Complete Issue (will create PR)

```
Title: Guide to preventing contamination
Body:
I'd like to create a comprehensive guide on preventing contamination in home mushroom grows.

Here's what I want to cover:
1. Sterilization techniques (70% isopropyl alcohol, flame sterilization)
2. Workspace preparation
3. Common contamination sources
4. Prevention best practices
5. Recovery from contamination

Target audience: Beginner to intermediate growers
Style: Practical, experience-based advice (like "Let the alcohol sit for 30-60 seconds")
```

**Result:** Action creates PR to `staging` with:
- New file in `content/post/2026/`
- Complete YAML front matter
- Blog post content
- Title and description ready for preview

## After PR is Created

1. **Review** the PR for accuracy and completeness
2. **Request Changes** if needed (commenter can reply with revisions)
3. **Merge** to `staging` → Amplify preview builds automatically
4. **Verify** in staging preview
5. **Merge** `staging` → `main` when ready to publish

## Skipped Scenarios

The action automatically skips:
- Issues opened by bots
- When running as the bot itself (prevents loops)

## Troubleshooting

If the action doesn't run:

1. Check **Actions** tab → view workflow logs
2. Verify `ANTHROPIC_API_KEY` secret is set
3. Check issue body for valid `model:` field (if specified)
4. Ensure issue is created on `rabbithole223/web-rabbithole223.com` repository

Common errors:
- **"Missing ANTHROPIC_API_KEY"**: Add the secret in Settings → Secrets
- **"Could not find JSON in Claude's response"**: Claude may have returned an error; check logs for details
- **"Branch already exists"**: PR was already created; don't create duplicate branches

## Files

- `.github/workflows/issue-to-pr.yml` - Workflow definition
- `.github/scripts/analyze_issue.py` - Analysis and PR generation script
