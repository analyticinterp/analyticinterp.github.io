#!/bin/bash
# Deploy script for GitHub Pages

echo "Building blog..."
python build.py

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Adding changes to git..."
git add docs/

echo "Committing changes..."
git commit -m "Update blog: $(date +%Y-%m-%d)"

echo ""
echo "Deploy complete! Run 'git push' to publish to GitHub Pages."
echo "Make sure GitHub Pages is configured to serve from the 'docs/' directory." 