#!/usr/bin/env python3
"""
Simple file watcher for live development - no external dependencies
Uses basic polling to check for file changes
"""

import os
import time
import subprocess
import threading
from pathlib import Path

class SimpleFileWatcher:
    def __init__(self, directories):
        self.directories = directories
        self.file_times = {}
        self.last_rebuild = 0
        self.rebuild_delay = 1.0  # Debounce rebuilds
        
    def get_file_times(self):
        """Get modification times for all watched files"""
        times = {}
        for directory in self.directories:
            if not Path(directory).exists():
                continue
                
            for file_path in Path(directory).rglob('*'):
                if file_path.is_file():
                    # Only watch relevant files
                    if file_path.suffix in {'.md', '.html', '.css', '.js', '.py'}:
                        try:
                            times[str(file_path)] = file_path.stat().st_mtime
                        except OSError:
                            pass
        return times
    
    def check_changes(self):
        """Check if any files have changed"""
        current_times = self.get_file_times()
        
        # First run - just store times
        if not self.file_times:
            self.file_times = current_times
            return False
            
        # Check for changes
        changed = False
        for file_path, mtime in current_times.items():
            if file_path not in self.file_times or self.file_times[file_path] != mtime:
                changed = True
                print(f"📝 Changed: {file_path}")
                break
                
        # Check for deleted files
        for file_path in self.file_times:
            if file_path not in current_times:
                changed = True
                print(f"🗑️  Deleted: {file_path}")
                break
                
        self.file_times = current_times
        return changed
    
    def rebuild_site(self):
        """Rebuild the site and show status"""
        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_rebuild < self.rebuild_delay:
            return
            
        self.last_rebuild = current_time
        
        try:
            print(f"\n🔄 Rebuilding site... ({time.strftime('%H:%M:%S')})")
            
            # Run build script
            result = subprocess.run(['python', 'build.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Build complete! Refresh your browser to see changes.")
            else:
                print(f"❌ Build failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Build error: {e}")

def start_preview_server():
    """Start a simple HTTP server in a separate thread"""
    import http.server
    import socketserver
    from pathlib import Path
    
    PORT = 8000
    DIRECTORY = "docs"
    
    class SimpleHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    # Check if docs directory exists
    if not Path(DIRECTORY).exists():
        print(f"Error: {DIRECTORY} directory not found!")
        return
    
    # Try to start server on available port
    for attempt_port in range(PORT, PORT + 10):
        try:
            httpd = socketserver.TCPServer(("", attempt_port), SimpleHandler)
            print(f"Serving blog at http://localhost:{attempt_port}")
            if attempt_port != PORT:
                print(f"(Port {PORT} was busy, using {attempt_port} instead)")
            print("Press Ctrl+C to stop")
            
            httpd.serve_forever()
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                continue
            else:
                raise
        except KeyboardInterrupt:
            httpd.shutdown()
            break
    else:
        print(f"❌ Could not find an available port between {PORT} and {PORT + 9}")

def main():
    print("🚀 Starting simple live preview...")
    print("📁 Watching: posts/, templates/, static/")
    print("🌐 Preview server starting at http://localhost:8000")
    print("💡 Edit your markdown files and refresh browser to see changes!")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Initial build
    print("🔄 Initial build...")
    subprocess.run(['python', 'build.py'])
    
    # Start preview server in background thread
    server_thread = threading.Thread(target=start_preview_server, daemon=True)
    server_thread.start()
    
    # Small delay to let server start
    time.sleep(1)
    
    # Set up file watcher
    watch_dirs = ['posts', 'templates', 'static']
    existing_dirs = [d for d in watch_dirs if Path(d).exists()]
    
    if not existing_dirs:
        print("❌ No directories to watch found!")
        return
    
    watcher = SimpleFileWatcher(existing_dirs)
    
    for directory in existing_dirs:
        print(f"👁️  Watching {directory}/")
    
    print(f"⏱️  Checking for changes every 2 seconds...")
    
    try:
        while True:
            if watcher.check_changes():
                watcher.rebuild_site()
            time.sleep(2)  # Check every 2 seconds
    except KeyboardInterrupt:
        print("\n🛑 Stopping live preview...")

if __name__ == '__main__':
    main() 