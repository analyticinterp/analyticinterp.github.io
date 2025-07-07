# Analytic Interpretability Blog

Static blog generator using pandoc with LaTeX math support and GitHub comments.


## Prerequisites

- Python 3.6+
- [pandoc](https://pandoc.org/installing.html)

## Usage

### Writing Posts

Create markdown files in `posts/` with this format:

```markdown
---
title: "Your Post Title"
author: "Your Name"
date: "2025-01-21"
description: "Brief description for index/RSS"
---

# Your Post Title

Content with $\LaTeX$ math: $\alpha + \beta = \gamma$

Display equations:
$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
```

### Development

We provide two scripts to preview the site:

**Option 1: Auto-reload development server (recommended)**
```bash
python dev-server.py
```
This server automatically rebuilds and reloads the site whenever you make a change to a markdown file. This allows you to preview your post as it will appear on the site in real time.

**Option 2: Simple file watcher**
```bash
python watch-simple.py
```
This watches for file changes and rebuilds the site, but requires manual browser refresh. Uses only Python standard library (no external dependencies).

**Manual build only:**
```bash
python build.py
```

### Deployment

#### Option 1: Manual Deployment (Recommended for Control)

```bash
# Build the site
python build.py

# Commit your post
git add posts/2025-01-21-my-new-post.md  # Add specific post
git add docs/                            # Add built site
git commit -m "Add: new post about transformers"

# Push to GitHub
git push origin main
```

#### Option 2: Quick Deployment Script

```bash
# Builds site and commits everything
./deploy.sh
git push
```

## Features

- **Math rendering**: KaTeX for LaTeX equations
- **Comments**: GitHub Discussions via Giscus
- **RSS feed**: Automatically generated
- **Fast builds**: Pandoc processing

## File Structure

```
├── posts/             # Markdown files
├── templates/         # HTML templates  
├── static/            # CSS and JS
├── docs/              # Generated site
├── build.py           # Build script
├── dev-server.py      # Development server with auto-reload
├── watch-simple.py    # Simple live preview (manual refresh)
└── deploy.sh          # Deployment script
``` 
