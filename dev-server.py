#!/usr/bin/env python3
"""
Development server with auto-reload functionality
"""

import os
import time
import json
import subprocess
import threading
import http.server
import socketserver
from pathlib import Path
from urllib.parse import urlparse

# Global variable to track last build time
last_build_time = time.time()

class DevServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="docs", **kwargs)
    
    def end_headers(self):
        # Add CORS headers for dev server
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Handle the build status endpoint
        if self.path == '/__dev_status__':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'last_build_time': last_build_time,
                'status': 'ok'
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Handle HTML files - inject auto-reload script
        if self.path.endswith('.html') or self.path == '/' or self.path.endswith('/'):
            # Determine the actual file path
            if self.path == '/' or self.path.endswith('/'):
                file_path = Path("docs") / "index.html"
            else:
                file_path = Path("docs") / self.path.lstrip('/')
            
            if file_path.exists() and file_path.suffix == '.html':
                # Read the HTML file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Inject auto-reload script before closing </head> tag
                auto_reload_script = '''
<script>
(function() {
    let lastBuildTime = null;
    
    function checkForUpdates() {
        fetch('/__dev_status__')
            .then(response => response.json())
            .then(data => {
                if (lastBuildTime === null) {
                    lastBuildTime = data.last_build_time;
                    return;
                }
                
                if (data.last_build_time > lastBuildTime) {
                    console.log('🔄 Site updated, reloading...');
                    location.reload();
                }
            })
            .catch(error => {
                console.log('Dev server connection lost:', error);
            });
    }
    
    // Check every 1 second
    setInterval(checkForUpdates, 1000);
    
    // Initial check
    checkForUpdates();
    
    console.log('🚀 Auto-reload active - changes will automatically refresh the page');
})();
</script>
'''
                
                # Insert script before </head> or before </body> if no </head>
                if '</head>' in content:
                    content = content.replace('</head>', auto_reload_script + '\n</head>')
                elif '</body>' in content:
                    content = content.replace('</body>', auto_reload_script + '\n</body>')
                else:
                    content = content + auto_reload_script
                
                # Send the modified content
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
        
        # For all other files, use default behavior
        super().do_GET()

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
        global last_build_time
        
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
                last_build_time = time.time()
                print("✅ Build complete! Browser will auto-reload.")
            else:
                print(f"❌ Build failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Build error: {e}")

def start_dev_server(port=8000):
    """Start the development server"""
    handler = DevServerHandler
    
    # Try ports starting from the requested port
    for attempt_port in range(port, port + 10):
        try:
            with socketserver.TCPServer(("", attempt_port), handler) as httpd:
                print(f"🌐 Development server running at http://localhost:{attempt_port}")
                if attempt_port != port:
                    print(f"   (Port {port} was busy, using {attempt_port} instead)")
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping development server...")
                break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                continue
            else:
                raise
    else:
        print(f"❌ Could not find an available port between {port} and {port + 9}")
        print("   Try killing existing servers: pkill -f 'python.*server'")

def main():
    print("🚀 Starting development server with auto-reload...")
    print("📁 Watching: posts/, templates/, static/")
    print("🔄 Auto-reload enabled - no need to refresh browser!")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Initial build
    print("🔄 Initial build...")
    subprocess.run(['python', 'build.py'])
    
    # Start dev server in background thread
    server_thread = threading.Thread(target=start_dev_server, daemon=True)
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
    print(f"✨ Browser will automatically reload when files change!\n")
    
    try:
        while True:
            if watcher.check_changes():
                watcher.rebuild_site()
            time.sleep(2)  # Check every 2 seconds
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")

if __name__ == '__main__':
    main() 