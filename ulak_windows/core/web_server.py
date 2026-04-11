import threading
import socket
import os
import json
import mimetypes
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler


class ULAKWebServer:
    def __init__(self, port=53319):
        self.port = port
        self.shared_contents = {}  # token -> content dict
        self.server = None
        self.thread = None

    def start(self):
        try:
            handler = self._make_handler()
            self.server = HTTPServer(('0.0.0.0', self.port), handler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            print(f"[WebServer] Started on port {self.port}")
        except Exception as e:
            print(f"[WebServer] Failed to start: {e}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server = None

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'

    def share_content(self, content_type, data, sender_name):
        """
        content_type: 'file', 'text', 'clipboard_text'
        data: file path (str) for file, or text (str) for text/clipboard
        Returns the link string: http://IP:PORT
        """
        token = uuid.uuid4().hex[:8]
        self.shared_contents.clear()  # Keep only the latest
        self.shared_contents[token] = {
            'type': content_type,
            'data': data,
            'sender': sender_name,
            'token': token,
        }
        ip = self.get_local_ip()
        return f"http://{ip}:{self.port}"

    def clear_content(self):
        self.shared_contents.clear()

    def _make_handler(self):
        server_instance = self

        class ULAKHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress HTTP log spam

            def do_GET(self):
                path = self.path

                if path == '/' or path == '':
                    self._serve_main_page()
                elif '?' in path:
                    raw_path, query = path.split('?', 1)
                    token = raw_path.lstrip('/')
                    if 'download=1' in query:
                        self._serve_download(token)
                    else:
                        self._serve_content_page(token)
                else:
                    token = path.lstrip('/')
                    if token:
                        self._serve_content_page(token)
                    else:
                        self._serve_main_page()

            def _get_first_content(self):
                if server_instance.shared_contents:
                    token = list(server_instance.shared_contents.keys())[0]
                    return token, server_instance.shared_contents[token]
                return None, None

            def _serve_main_page(self):
                token, content = self._get_first_content()
                if not content:
                    self._send_error_page("İçerik bulunamadı veya süresi doldu.")
                    return
                content_type = content['type']
                if content_type in ('text', 'clipboard_text'):
                    html = self._build_text_page(content)
                else:
                    html = self._build_file_page(token, content)
                self._send_html(html)

            def _serve_content_page(self, token):
                content = server_instance.shared_contents.get(token)
                if not content:
                    self._send_error_page("İçerik bulunamadı veya süresi doldu.")
                    return
                content_type = content['type']
                if content_type in ('text', 'clipboard_text'):
                    html = self._build_text_page(content)
                else:
                    html = self._build_file_page(token, content)
                self._send_html(html)

            def _serve_download(self, token):
                content = server_instance.shared_contents.get(token)
                if not content:
                    self._send_error_page("Dosya bulunamadı veya süresi doldu.")
                    return
                if content['type'] not in ('file',):
                    self._send_error_page("Bu içerik indirilebilir değil.")
                    return
                filepath = content['data']
                if not os.path.exists(filepath):
                    self._send_error_page("Dosya artık mevcut değil.")
                    return
                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)
                mime_type, _ = mimetypes.guess_type(filepath)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                try:
                    self.send_response(200)
                    self.send_header('Content-Type', mime_type)
                    self.send_header('Content-Disposition',
                                     f'attachment; filename="{filename}"')
                    self.send_header('Content-Length', str(filesize))
                    self.end_headers()
                    with open(filepath, 'rb') as f:
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            try:
                                self.wfile.write(chunk)
                            except Exception:
                                break
                except Exception as e:
                    print(f"[WebServer] Download error: {e}")

            def _build_text_page(self, content):
                raw_text = content['data']
                sender = content.get('sender', 'Bilinmiyor')
                display_text = (raw_text
                                .replace('&', '&amp;')
                                .replace('<', '&lt;')
                                .replace('>', '&gt;')
                                .replace('\n', '<br>'))
                js_text = json.dumps(raw_text)
                return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ULAK - Metin</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 20px;
}}
.container {{
    background: rgba(20, 27, 64, 0.97);
    border: 2px solid #00d4ff;
    border-radius: 20px;
    padding: 40px;
    max-width: 700px;
    width: 100%;
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.3);
}}
h1 {{
    color: #00d4ff;
    text-align: center;
    font-size: 1.8em;
    margin-bottom: 6px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}}
.sender {{
    color: #b24bf3;
    text-align: center;
    font-size: 0.9em;
    margin-bottom: 24px;
}}
.text-box {{
    background: rgba(10, 14, 39, 0.8);
    border: 1px solid #2d3462;
    border-radius: 12px;
    padding: 20px;
    color: #e8eaf6;
    font-size: 1em;
    line-height: 1.7;
    max-height: 420px;
    overflow-y: auto;
    word-break: break-word;
    white-space: pre-wrap;
}}
.copy-btn {{
    display: block;
    width: 100%;
    padding: 15px;
    background: linear-gradient(135deg, #00d4ff, #b24bf3);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    margin-top: 20px;
    transition: opacity 0.2s;
    box-shadow: 0 0 18px rgba(0, 212, 255, 0.3);
}}
.copy-btn:hover {{ opacity: 0.85; }}
.footer {{ text-align: center; color: #5a6080; font-size: 0.75em; margin-top: 20px; }}
</style>
</head>
<body>
<div class="container">
  <h1>📨 ULAK</h1>
  <p class="sender">Gönderen: {sender}</p>
  <div class="text-box">{display_text}</div>
  <button class="copy-btn" onclick="copyText()">📋 Kopyala</button>
  <p class="footer">© 2026 ALGSoft Inc.</p>
</div>
<script>
function copyText() {{
  var text = {js_text};
  if (navigator.clipboard) {{
    navigator.clipboard.writeText(text).then(function() {{
      var btn = document.querySelector('.copy-btn');
      btn.textContent = '✅ Kopyalandı!';
      setTimeout(function() {{ btn.textContent = '📋 Kopyala'; }}, 2000);
    }});
  }} else {{
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    var btn = document.querySelector('.copy-btn');
    btn.textContent = '✅ Kopyalandı!';
    setTimeout(function() {{ btn.textContent = '📋 Kopyala'; }}, 2000);
  }}
}}
</script>
</body>
</html>"""

            def _build_file_page(self, token, content):
                filepath = content['data']
                sender = content.get('sender', 'Bilinmiyor')
                filename = os.path.basename(filepath) if filepath else 'dosya'
                try:
                    filesize = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                except Exception:
                    filesize = 0
                ext = os.path.splitext(filename)[1].lower()
                if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'):
                    icon = '🖼️'
                elif ext in ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'):
                    icon = '🎥'
                elif ext in ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'):
                    icon = '🎵'
                elif ext in ('.pdf',):
                    icon = '📕'
                elif ext in ('.zip', '.rar', '.7z', '.tar', '.gz'):
                    icon = '📦'
                elif ext in ('.doc', '.docx', '.odt'):
                    icon = '📝'
                elif ext in ('.xls', '.xlsx', '.ods'):
                    icon = '📊'
                elif ext in ('.ppt', '.pptx', '.odp'):
                    icon = '📋'
                else:
                    icon = '📄'
                size_str = self._format_size(filesize)
                download_url = f"/{token}?download=1"
                return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ULAK - {filename}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 20px;
}}
.container {{
    background: rgba(20, 27, 64, 0.97);
    border: 2px solid #00d4ff;
    border-radius: 20px;
    padding: 40px;
    max-width: 480px;
    width: 100%;
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.3);
    text-align: center;
}}
h1 {{
    color: #00d4ff;
    font-size: 1.8em;
    margin-bottom: 6px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}}
.icon {{ font-size: 4em; margin: 20px 0; }}
.filename {{
    color: #e8eaf6;
    font-size: 1.1em;
    font-weight: bold;
    margin: 10px 0;
    word-break: break-all;
}}
.meta {{ color: #8b949e; font-size: 0.9em; margin: 5px 0; }}
.sender {{ color: #b24bf3; font-size: 0.9em; margin: 16px 0; }}
.download-btn {{
    display: block;
    width: 100%;
    padding: 18px;
    background: linear-gradient(135deg, #00d4ff, #b24bf3);
    color: #fff;
    border: none;
    border-radius: 14px;
    font-size: 1.2em;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    margin-top: 24px;
    box-shadow: 0 0 24px rgba(0, 212, 255, 0.4);
    transition: opacity 0.2s;
}}
.download-btn:hover {{ opacity: 0.85; }}
.footer {{ color: #5a6080; font-size: 0.75em; margin-top: 20px; }}
</style>
</head>
<body>
<div class="container">
  <h1>📡 ULAK</h1>
  <div class="icon">{icon}</div>
  <div class="filename">{filename}</div>
  <div class="meta">Boyut: {size_str}</div>
  <div class="meta">Tür: {ext if ext else 'Bilinmiyor'}</div>
  <div class="sender">Gönderen: {sender}</div>
  <a class="download-btn" href="{download_url}">⬇️ İndir</a>
  <p class="footer">© 2026 ALGSoft Inc.</p>
</div>
</body>
</html>"""

            def _format_size(self, size):
                for unit in ('B', 'KB', 'MB', 'GB'):
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"

            def _send_html(self, html):
                encoded = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def _send_error_page(self, message):
                html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ULAK - Hata</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: linear-gradient(135deg, #0a0e27, #1a1f3a);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #e8eaf6;
}}
.container {{
    background: rgba(20, 27, 64, 0.97);
    border: 2px solid #ff2e97;
    border-radius: 20px;
    padding: 40px;
    max-width: 400px;
    width: 90%;
    text-align: center;
    box-shadow: 0 0 40px rgba(255, 46, 151, 0.3);
}}
h1 {{ color: #ff2e97; margin-bottom: 16px; }}
p {{ color: #8b949e; }}
</style>
</head>
<body>
<div class="container">
  <h1>⚠️ Hata</h1>
  <p>{message}</p>
</div>
</body>
</html>"""
                encoded = html.encode('utf-8')
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        return ULAKHandler
