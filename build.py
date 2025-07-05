#!/usr/bin/env python3
"""
Minimal pandoc-based static blog generator
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuration
SITE_URL = "https://analyticinterp.github.io"
SITE_TITLE = "Analytic Interpretability"
SITE_DESCRIPTION = "Understanding deep learning through theory"
AUTHOR = "Analytic Interpretability Team"

def extract_metadata(filepath):
    """Extract YAML frontmatter from markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for YAML frontmatter
    if content.startswith('---\n'):
        end = content.find('\n---\n', 4)
        if end != -1:
            frontmatter = content[4:end]
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"\'')
            
            # Ensure slug is set
            if 'slug' not in metadata:
                filename = Path(filepath).stem
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)', filename)
                if date_match:
                    metadata['slug'] = date_match.group(2)
                else:
                    metadata['slug'] = filename
            
            return metadata
    
    # Fallback: extract from filename and first heading
    filename = Path(filepath).stem
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)', filename)
    
    metadata = {}
    if date_match:
        metadata['date'] = date_match.group(1)
        metadata['slug'] = date_match.group(2)
    else:
        metadata['date'] = datetime.now().strftime('%Y-%m-%d')
        metadata['slug'] = filename
    
    # Try to extract title from first H1
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if h1_match:
        metadata['title'] = h1_match.group(1)
    else:
        metadata['title'] = metadata['slug'].replace('-', ' ').title()
    
    return metadata

def build_post(markdown_file, output_dir):
    """Convert a markdown file to HTML using pandoc"""
    metadata = extract_metadata(markdown_file)
    
    # Create output filename
    output_file = output_dir / f"{metadata['slug']}.html"
    
    # Build pandoc command
    cmd = [
        'pandoc',
        str(markdown_file),
        '-o', str(output_file),
        '--template=templates/post.html',
        '--mathjax',  # This preserves math delimiters for KaTeX
        '--highlight-style=kate',
        '--metadata', f"title={metadata.get('title', 'Untitled')}",
        '--metadata', f"date={metadata.get('date', '')}",
        '--metadata', f"author={metadata.get('author', AUTHOR)}"
    ]
    
    # Run pandoc
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Built: {metadata['slug']}")
        return metadata
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build {markdown_file}: {e.stderr}")
        return None

def generate_index(posts, output_dir):
    """Generate the index page with list of posts"""
    # Sort posts by date (newest first)
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    
    # Filter out the about page from the main list
    article_posts = [p for p in posts if p['slug'] != 'about']
    
    # Group posts by month/year
    post_groups = {}
    for post in article_posts:
        if 'date' in post:
            try:
                dt = datetime.strptime(post['date'], '%Y-%m-%d')
                month_key = dt.strftime('%B %Y')
            except:
                month_key = 'Undated'
        else:
            month_key = 'Undated'
        
        if month_key not in post_groups:
            post_groups[month_key] = []
        post_groups[month_key].append(post)
    
    # Generate post list HTML with rich formatting
    post_html = []
    for month_key, month_posts in post_groups.items():
        # Add date header
        post_html.append(f'      <div class="date-header">{month_key}</div>')
        
        # Add posts for this month
        for post in month_posts:
            # Format the date nicely
            if 'date' in post:
                try:
                    dt = datetime.strptime(post['date'], '%Y-%m-%d')
                    date_str = dt.strftime('%B %d, %Y')
                except:
                    date_str = post['date']
            else:
                date_str = ''
            
            # Build the post entry
            entry_html = f'''      <a href="/{post['slug']}.html" class="post-entry">
        <h3>{post['title']}</h3>'''
            
            # Add author if different from default
            if 'author' in post and post['author'] != AUTHOR:
                entry_html += f'''
        <div class="post-byline">{post['author']}, {date_str}</div>'''
            else:
                entry_html += f'''
        <div class="post-byline">{date_str}</div>'''
            
            # Add description if available
            if 'description' in post:
                entry_html += f'''
        <div class="post-description">{post['description']}</div>'''
            
            entry_html += '''
      </a>'''
            
            post_html.append(entry_html)
    
    # About content
    about_content = """
      <p>Analytic Interpretability is a team of scientists scattered all over the world trying to understand the mysteries of deep learning. As Jamie put it, we're all exploring a big maze, looking for the exit. Most people in our field are wandering around rather unproductively (or are carefully mapping regions of the maze we know don't contain the exit). A few of us have been earnestly exploring the maze for several years now and have good ideas for promising places to look next. It makes sense to develop a collective map of the regions we've explored, flag the crucial splits, and start saying "you go left, I'll go right, report back."</p>
      
      <p>The team is made up of various PhD students/postdocs/profs:</p>
      
      <ul>
        <li><a href="https://abatanasov.com/">Alex Atanasov</a></li>
        <li><a href="https://jeremybernste.in/">Jeremy Bernstein</a></li>
        <li><a href="https://blakebordelon.github.io/">Blake Bordelon</a></li>
        <li><a href="https://jmcohen.github.io/">Jeremy Cohen</a></li>
        <li><a href="https://web.math.princeton.edu/~ad27/">Alex Damian</a></li>
        <li><a href="https://nikhil-ghosh-berkeley.github.io/">Nikhil Ghosh</a></li>
        <li><a href="https://florentinguth.github.io/">Florentin Guth</a></li>
        <li><a href="https://sites.google.com/view/arthurjacot">Arthur Jacot</a></li>
        <li><a href="https://dkarkada.xyz/">Dhruva Karkada</a></li>
        <li><a href="https://daniel-kunin.com/">Daniel Kunin</a></li>
        <li><a href="https://alexandrumeterez.github.io/">Alex Meterez</a></li>
        <li><a href="https://ericjmichaud.com/">Eric Michaud</a></li>
        <li><a href="https://misiakie.github.io/">Theodor Misiakiewicz</a></li>
        <li><a href="https://berkan.xyz/">Berkan Ottlik</a></li>
        <li><a href="https://aditradha.com/">Adit Radha</a></li>
        <li><a href="https://james-simon.github.io/">Jamie Simon</a></li>
        <li><a href="https://www.linkedin.com/in/joey-turnbull/">Joey Turnbull</a></li>
        <li><a href="https://jzv.io/">Jacob Zavatone-Veth</a></li>
      </ul>
    """
    
    # Read template and replace placeholders
    with open('templates/index.html', 'r') as f:
        template = f.read()
    
    html = template.replace('<!-- POSTS_PLACEHOLDER -->', '\n'.join(post_html))
    html = html.replace('<!-- ABOUT_PLACEHOLDER -->', about_content)
    
    # Write index file
    with open(output_dir / 'index.html', 'w') as f:
        f.write(html)
    
    print("✓ Generated index.html")

def generate_rss(posts, output_dir):
    """Generate RSS feed"""
    # Create root element
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')
    
    # Add channel info
    SubElement(channel, 'title').text = SITE_TITLE
    SubElement(channel, 'link').text = SITE_URL
    SubElement(channel, 'description').text = SITE_DESCRIPTION
    SubElement(channel, 'language').text = 'en-us'
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    
    # Add items
    for post in posts[:20]:  # Latest 20 posts
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post['title']
        SubElement(item, 'link').text = f"{SITE_URL}/{post['slug']}.html"
        SubElement(item, 'guid').text = f"{SITE_URL}/{post['slug']}.html"
        
        if 'description' in post:
            SubElement(item, 'description').text = post['description']
        
        if 'date' in post:
            # Convert date to RFC822 format
            dt = datetime.strptime(post['date'], '%Y-%m-%d')
            SubElement(item, 'pubDate').text = dt.strftime('%a, %d %b %Y 00:00:00 +0000')
    
    # Pretty print XML
    xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent='  ')
    
    # Write feed
    with open(output_dir / 'feed.xml', 'w') as f:
        f.write(xml_str)
    
    print("✓ Generated feed.xml")

def copy_static_files(output_dir):
    """Copy static files to output directory"""
    static_dir = Path('static')
    output_static = output_dir / 'static'
    
    # Create static directory
    output_static.mkdir(exist_ok=True)
    
    # Copy all files
    for file in static_dir.glob('*'):
        if file.is_file():
            content = file.read_bytes()
            (output_static / file.name).write_bytes(content)
    
    print("✓ Copied static files")

def main():
    """Main build process"""
    print("Building minimal blog...\n")
    
    # Setup directories
    posts_dir = Path('posts')
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    # Find all markdown files
    markdown_files = list(posts_dir.glob('*.md'))
    
    if not markdown_files:
        print("No markdown files found in posts/")
        return
    
    # Build all posts
    posts = []
    for md_file in markdown_files:
        metadata = build_post(md_file, output_dir)
        if metadata:
            posts.append(metadata)
    
    # Generate index and RSS
    if posts:
        generate_index(posts, output_dir)
        generate_rss(posts, output_dir)
    
    # Copy static files
    copy_static_files(output_dir)
    
    print(f"\n✓ Build complete! Generated {len(posts)} posts.")
    print(f"  Output in: {output_dir.absolute()}")
    print(f"  Ready for GitHub Pages deployment from docs/ directory")

if __name__ == '__main__':
    main() 