#!/usr/bin/env python3
"""
Minimal pandoc-based static blog generator
"""

import os
import re
import json
import yaml
import subprocess
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Configuration
SITE_URL = "https://analyticinterp.github.io"
SITE_TITLE = "Learning Mechanics"
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
                # Handle old date-based naming: YYYY-MM-DD-slug
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)', filename)
                if date_match:
                    metadata['slug'] = date_match.group(2)
                else:
                    # Handle new number-based naming: NN-slug
                    number_match = re.match(r'(\d+)-(.+)', filename)
                    if number_match:
                        metadata['slug'] = number_match.group(2)
                    else:
                        metadata['slug'] = filename
            
            # Set default sequence_order if not present
            if 'sequence_order' not in metadata:
                metadata['sequence_order'] = 1
            else:
                # Convert to int for sorting
                metadata['sequence_order'] = int(metadata['sequence_order'])
            
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
    
    # Set default sequence_order for fallback case
    metadata['sequence_order'] = 1
    
    return metadata

def build_post(markdown_file, output_dir, metadata, sequence_nav=None):
    """Convert a markdown file to HTML using pandoc"""
    
    # Create output filename based on URL path
    sequence_key = metadata.get('sequence', '')
    if sequence_key and sequence_key != f"standalone-{metadata['slug']}":
        # Create sequence subdirectory
        sequence_dir = output_dir / sequence_key
        sequence_dir.mkdir(exist_ok=True)
        output_file = sequence_dir / f"{metadata['slug']}.html"
    else:
        # Standalone post at root level
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
        '--metadata', f"author={metadata.get('author', AUTHOR)}",
        '--metadata', f"path_prefix={metadata.get('path_prefix', '')}"
    ]
    
    # Add sequence navigation metadata if available
    if sequence_nav:
        cmd.extend([
            '--metadata', f"sequence_title={sequence_nav.get('sequence_title', '')}",
            '--metadata', f"sequence_part={sequence_nav.get('sequence_part', '')}",
            '--metadata', f"sequence_total={sequence_nav.get('sequence_total', '')}",
            '--metadata', f"sequence_first_url={sequence_nav.get('sequence_first_url', '')}",
            '--metadata', f"sequence_order={sequence_nav.get('sequence_part', '')}",
            '--metadata', f"sequence_order_1={sequence_nav.get('sequence_order_1', '')}",
            '--metadata', f"prev_title={sequence_nav.get('prev_title', '')}",
            '--metadata', f"prev_slug={sequence_nav.get('prev_slug', '')}",
            '--metadata', f"prev_url={sequence_nav.get('prev_url', '')}",
            '--metadata', f"prev_part={sequence_nav.get('prev_part', '')}",
            '--metadata', f"next_title={sequence_nav.get('next_title', '')}",
            '--metadata', f"next_slug={sequence_nav.get('next_slug', '')}",
            '--metadata', f"next_url={sequence_nav.get('next_url', '')}",
            '--metadata', f"next_part={sequence_nav.get('next_part', '')}"
        ])
    
    # Run pandoc
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Post-process to add sequence TOC if available
        if sequence_nav and 'toc_posts' in sequence_nav:
            # Generate TOC HTML
            toc_items = []
            for i, post in enumerate(sequence_nav['toc_posts'], 1):
                display_title = post.get('toc_title', post['title'])
                post_url = post.get('url_path', f"{post['slug']}.html")
                if post['slug'] == sequence_nav['current_slug']:
                    toc_items.append(f'<strong>{display_title}</strong>')
                else:
                    toc_items.append(f'<a href="{metadata.get("path_prefix", "")}{post_url}">{display_title}</a>')
            
            # Generate custom CSS for sequence colors if available
            sequence_color = metadata.get('sequence_color')
            sequence_color_dark = metadata.get('sequence_color_dark')
            sequence_key = metadata.get('sequence', '')
            
            if sequence_color and isinstance(sequence_color, list) and len(sequence_color) == 3:
                # Generate unique CSS class for this sequence
                css_class = f'sequence-toc-{sequence_key}'
                light_color = f'rgb({sequence_color[0]}, {sequence_color[1]}, {sequence_color[2]})'
                
                if sequence_color_dark and isinstance(sequence_color_dark, list) and len(sequence_color_dark) == 3:
                    dark_color = f'rgb({sequence_color_dark[0]}, {sequence_color_dark[1]}, {sequence_color_dark[2]})'
                else:
                    dark_color = light_color  # Fallback to light color
                
                # Create CSS with both light and dark mode colors
                sequence_css = f'''
<style>
.{css_class} {{ background-color: {light_color}; }}
[data-theme="dark"] .{css_class} {{ background-color: {dark_color}; }}
</style>'''
                css_class_attr = f' class="sequence-toc {css_class}"'
            else:
                sequence_css = ''
                css_class_attr = ' class="sequence-toc"'
            
            toc_html = f'<hr>{sequence_css}<div{css_class_attr}><h3>{metadata.get("sequence_title", "")}</h3><ol>{"".join(f"<li>{item}</li>" for item in toc_items)}</ol></div><div class="back-to-top"><a href="#top"><i class="fas fa-arrow-circle-up"></i></a></div>'
            
            # Read the generated HTML file
            with open(output_file, 'r') as f:
                html_content = f.read()
            
            # Replace placeholder with TOC
            html_content = html_content.replace('<!-- SEQUENCE_TOC_PLACEHOLDER -->', toc_html)
            
            # Write back
            with open(output_file, 'w') as f:
                f.write(html_content)
        
        print(f"✓ Built: {metadata['slug']}")
        return metadata
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build {markdown_file}: {e.stderr}")
        return None

def load_sequence_metadata():
    """Load sequence metadata from sequence-metadata.yaml files in post directories"""
    posts_dir = Path('posts')
    sequence_metadata = {}
    
    if posts_dir.exists():
        for metadata_file in posts_dir.rglob('sequence-metadata.yaml'):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = yaml.safe_load(f)
                    sequence_id = metadata.get('sequence_id')
                    if sequence_id:
                        sequence_metadata[sequence_id] = metadata
            except Exception as e:
                print(f"Warning: Could not load sequence metadata from {metadata_file}: {e}")
    
    return sequence_metadata

def generate_index(posts, output_dir):
    """Generate the index page with list of posts grouped by sequences"""
    # Filter out the about page from the main list
    article_posts = [p for p in posts if p['slug'] != 'about']
    
    # Load sequence metadata
    sequence_metadata = load_sequence_metadata()
    
    # Group posts by sequence
    sequences = {}
    for post in article_posts:
        sequence_key = post.get('sequence', f"standalone-{post['slug']}")
        
        if sequence_key not in sequences:
            # Use sequence metadata if available, otherwise fall back to post metadata
            if sequence_key in sequence_metadata:
                meta = sequence_metadata[sequence_key]
                sequences[sequence_key] = {
                    'title': meta.get('title', post.get('sequence_title', post['title'])),
                    'description': meta.get('description', post.get('sequence_description', post.get('description', ''))),
                    'authors': meta.get('authors', []),
                    'date': meta.get('date', ''),
                    'sequence_color': meta.get('sequence_color', None),
                    'sequence_color_dark': meta.get('sequence_color_dark', None),
                    'posts': []
                }
            else:
                sequences[sequence_key] = {
                    'title': post.get('sequence_title', post['title']),
                    'description': post.get('sequence_description', post.get('description', '')),
                    'authors': [],
                    'date': '',
                    'sequence_color': None,
                    'sequence_color_dark': None,
                    'posts': []
                }
        
        sequences[sequence_key]['posts'].append(post)
    
    # Sort posts within each sequence by sequence_order
    for sequence in sequences.values():
        sequence['posts'].sort(key=lambda p: p.get('sequence_order', 1))
    
    # Sort sequences by date of sequence metadata (newest first), fallback to first post date
    sequence_list = []
    for seq_key, seq_data in sequences.items():
        first_post = seq_data['posts'][0]
        
        # Use sequence metadata date if available, otherwise use first post date
        if not seq_data['date']:
            seq_data['date'] = first_post.get('date', '')
        
        # Use sequence metadata authors if available, otherwise use first post author
        if not seq_data['authors']:
            seq_data['author'] = first_post.get('author', '')
        else:
            # Join multiple authors with commas
            seq_data['author'] = ', '.join(seq_data['authors'])
        
        sequence_list.append(seq_data)
    
    sequence_list.sort(key=lambda s: s.get('date', ''), reverse=True)
    
    # Generate sequence HTML
    post_html = []
    sequence_css_rules = []
    for sequence in sequence_list:
        first_post = sequence['posts'][0]
        # Get the sequence key from the first post
        seq_key = first_post.get('sequence', f"standalone-{first_post['slug']}")
        
        # Format the date nicely
        if 'date' in sequence:
            try:
                dt = datetime.strptime(sequence['date'], '%Y-%m-%d')
                date_str = dt.strftime('%B %d, %Y')
            except:
                date_str = sequence['date']
        else:
            date_str = ''
        
        # Start sequence box with background color if available
        first_post_url = first_post.get('url_path', f"{first_post['slug']}.html")
        sequence_color = sequence.get('sequence_color')
        sequence_color_dark = sequence.get('sequence_color_dark')
        
        if sequence_color and isinstance(sequence_color, list) and len(sequence_color) == 3:
            # Generate unique CSS class for this sequence
            css_class = f'sequence-box-{seq_key}'
            light_color = f'rgb({sequence_color[0]}, {sequence_color[1]}, {sequence_color[2]})'
            
            if sequence_color_dark and isinstance(sequence_color_dark, list) and len(sequence_color_dark) == 3:
                dark_color = f'rgb({sequence_color_dark[0]}, {sequence_color_dark[1]}, {sequence_color_dark[2]})'
            else:
                dark_color = light_color  # Fallback to light color
            
            # Store CSS for later injection into the page
            sequence_css_rules.append(f'''
.{css_class} {{ background-color: {light_color}; }}
[data-theme="dark"] .{css_class} {{ background-color: {dark_color}; }}''')
            
            css_class_attr = f'sequence-box {css_class}'
        else:
            css_class_attr = 'sequence-box'
        
        sequence_html = f'''      <div class="{css_class_attr}" onclick="location.href='{first_post_url}'">
        <div class="sequence-title">{sequence['title']}</div>'''
        
        # Add author and date on separate lines
        if sequence['author'] and sequence['author'] != AUTHOR:
            sequence_html += f'''
        <div class="sequence-author">{sequence['author']}</div>
        <div class="sequence-date">{date_str}</div>'''
        else:
            sequence_html += f'''
        <div class="sequence-date">{date_str}</div>'''
        
        # Add post links within sequence
        if len(sequence['posts']) > 1:
            sequence_html += '''
        <div class="sequence-posts">'''
            for i, post in enumerate(sequence['posts'], 1):
                # Use toc_title if available, otherwise fallback to title
                display_title = post.get('toc_title', post['title'])
                post_url = post.get('url_path', f"{post['slug']}.html")
                sequence_html += f'''
          <a href="{post_url}" class="post-link" onclick="event.stopPropagation()">{i}. {display_title}</a>'''
            sequence_html += '''
        </div>'''
        
        sequence_html += '''
      </div>'''
        
        post_html.append(sequence_html)
    
        # Read template and replace placeholders
    with open('templates/index.html', 'r') as f:
        template = f.read()

    # Generate CSS for sequence colors
    sequence_css = ''
    if sequence_css_rules:
        sequence_css = f'<style>{"".join(sequence_css_rules)}</style>'

    html = template.replace('<!-- POSTS_PLACEHOLDER -->', '\n'.join(post_html))
    
    # Inject sequence CSS into the head (look for </head> tag)
    if sequence_css:
        html = html.replace('</head>', f'  {sequence_css}\n</head>')
    
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
        SubElement(item, 'link').text = f"{SITE_URL}/{post.get('url_path', post['slug'] + '.html')}"
        SubElement(item, 'guid').text = f"{SITE_URL}/{post.get('url_path', post['slug'] + '.html')}"
        
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
    
    # Copy .nojekyll file to prevent Jekyll processing on GitHub Pages
    nojekyll_file = Path('.nojekyll')
    if nojekyll_file.exists():
        (output_dir / '.nojekyll').write_bytes(nojekyll_file.read_bytes())
    
    print("✓ Copied static files")

def main():
    """Main build process"""
    print("Building minimal blog...\n")
    
    # Setup directories
    posts_dir = Path('posts')
    output_dir = Path('build')
    output_dir.mkdir(exist_ok=True)
    
    # Find all markdown files (including in subdirectories)
    markdown_files = list(posts_dir.rglob('*.md'))
    
    if not markdown_files:
        print("No markdown files found in posts/")
        return
    
    # Load sequence metadata
    sequence_metadata = load_sequence_metadata()
    
    # First pass: collect metadata from all posts and generate URL paths
    posts_metadata = []
    file_to_metadata = {}
    for md_file in markdown_files:
        metadata = extract_metadata(md_file)
        if metadata:
            # Inject sequence metadata if the post belongs to a sequence
            sequence_key = metadata.get('sequence', '')
            if sequence_key and sequence_key in sequence_metadata:
                seq_meta = sequence_metadata[sequence_key]
                metadata['sequence_title'] = seq_meta.get('title', '')
                metadata['sequence_description'] = seq_meta.get('description', '')
                metadata['sequence_color'] = seq_meta.get('sequence_color', None)
                metadata['sequence_color_dark'] = seq_meta.get('sequence_color_dark', None)
            
            # Generate URL path and path prefix
            if sequence_key and sequence_key != f"standalone-{metadata['slug']}":
                metadata['url_path'] = f"{sequence_key}/{metadata['slug']}.html"
                metadata['path_prefix'] = "../"
            else:
                metadata['url_path'] = f"{metadata['slug']}.html"
                metadata['path_prefix'] = ""
            
            posts_metadata.append(metadata)
            file_to_metadata[str(md_file)] = metadata
    
    # Group posts by sequence to calculate navigation
    sequences = {}
    for metadata in posts_metadata:
        sequence_key = metadata.get('sequence', f"standalone-{metadata['slug']}")
        if sequence_key not in sequences:
            sequences[sequence_key] = []
        sequences[sequence_key].append(metadata)
    
    # Sort posts within each sequence by sequence_order
    for sequence in sequences.values():
        sequence.sort(key=lambda p: p.get('sequence_order', 1))
    
    # Second pass: build posts with navigation info
    posts = []
    for md_file in markdown_files:
        metadata = file_to_metadata[str(md_file)]
        sequence_nav = None
        
        # Calculate sequence navigation and TOC if part of multi-post sequence
        sequence_key = metadata.get('sequence', f"standalone-{metadata['slug']}")
        sequence_toc = None
        if sequence_key in sequences and len(sequences[sequence_key]) > 1:
            sequence_posts = sequences[sequence_key]
            current_index = next(i for i, p in enumerate(sequence_posts) if p['slug'] == metadata['slug'])
            
            # Get URL paths for navigation
            prev_url = sequence_posts[current_index - 1]['url_path'] if current_index > 0 else ''
            next_url = sequence_posts[current_index + 1]['url_path'] if current_index < len(sequence_posts) - 1 else ''
            
            sequence_nav = {
                'sequence_title': metadata.get('sequence_title', ''),
                'sequence_part': current_index + 1,
                'sequence_total': len(sequence_posts),
                'sequence_first_url': sequence_posts[0]['url_path'],
                'sequence_order_1': current_index == 0,
                'prev_title': sequence_posts[current_index - 1]['title'] if current_index > 0 else '',
                'prev_slug': sequence_posts[current_index - 1]['slug'] if current_index > 0 else '',
                'prev_url': prev_url,
                'prev_part': current_index if current_index > 0 else '',
                'next_title': sequence_posts[current_index + 1]['title'] if current_index < len(sequence_posts) - 1 else '',
                'next_slug': sequence_posts[current_index + 1]['slug'] if current_index < len(sequence_posts) - 1 else '',
                'next_url': next_url,
                'next_part': current_index + 2 if current_index < len(sequence_posts) - 1 else ''
            }
            
            # Store sequence TOC data for build_post
            sequence_nav['toc_posts'] = sequence_posts
            sequence_nav['current_slug'] = metadata['slug']
        
        built_metadata = build_post(md_file, output_dir, metadata, sequence_nav)
        if built_metadata:
            posts.append(built_metadata)
    
    # Generate index and RSS
    if posts:
        generate_index(posts, output_dir)
        generate_rss(posts, output_dir)
    
    # Copy static files
    copy_static_files(output_dir)
    
    print(f"\n✓ Build complete! Generated {len(posts)} posts.")
    print(f"  Output in: {output_dir.absolute()}")
    print(f"  Ready for GitHub Pages deployment from build/ directory")

if __name__ == '__main__':
    main() 