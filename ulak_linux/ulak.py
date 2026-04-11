#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULAK - Yerel Ağ Dosya Paylaşım Uygulaması
Linux Versiyonu - Tek Dosya
© 2026 ALGSoft Inc.
Geliştirici: Fatih ÖNDER (CekToR)
"""

import sys
import os

import socket
import json
import threading
import time
import zipfile
import tempfile
import hashlib
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QIcon, QPixmap, QKeySequence, QPainter, QColor, QImage
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QListWidget, QLabel,
                             QFileDialog, QMessageBox, QProgressBar, QListWidgetItem,
                             QTabWidget, QFrame, QLineEdit, QDialog, QDialogButtonBox,
                             QCheckBox, QScrollArea, QSystemTrayIcon, QMenu, QShortcut,
                             QDesktopWidget, QTextEdit)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

if "WAYLAND_DISPLAY" in os.environ or os.environ.get("XDG_SESSION_TYPE") == "wayland":
    os.environ["QT_QPA_PLATFORM"] = "wayland"
else:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

# Duyuru yönetimi için
try:
    import requests
    from bs4 import BeautifulSoup
    _DEPS_AVAILABLE = True
except ImportError:
    _DEPS_AVAILABLE = False

# ============================================================================
# CRYPTO MODULE
# ============================================================================

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """AES-256 ile veriyi şifreler"""
    iv = bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """AES-256 ile veriyi çözer"""
    try:
        iv = bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data
    except Exception as e:
        raise ValueError("Şifre çözme hatası - Parolalar eşleşmiyor")

# ============================================================================
# ANNOUNCEMENT MANAGER
# ============================================================================

TARGET_URL = "https://algsoft.net.tr/uygulama-duyurulari/"
ELEMENT_ID = "ulak_linux_web"

class AnnouncementManager(QObject):
    announcement_fetched = pyqtSignal(str)
    fetch_failed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def fetch_async(self):
        t = threading.Thread(target=self._fetch, daemon=True)
        t.start()

    def _fetch(self):
        if not _DEPS_AVAILABLE:
            self.fetch_failed.emit()
            return
        try:
            response = requests.get(TARGET_URL, timeout=8)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.find(id=ELEMENT_ID)
            if element:
                text = element.get_text(separator=' ', strip=True)
                if text:
                    self.announcement_fetched.emit(text)
                    return
            self.fetch_failed.emit()
        except Exception:
            self.fetch_failed.emit()

# ============================================================================
# WEB SERVER
# ============================================================================

class ULAKWebServer:
    def __init__(self, port=53319):
        self.port = port
        self.shared_contents = {}
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
        token = uuid.uuid4().hex[:8]
        self.shared_contents.clear()
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
                pass

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
                    self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
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
                display_text = (raw_text.replace('&', '&amp;').replace('<', '&lt;')
                               .replace('>', '&gt;').replace('\n', '<br>'))
                js_text = json.dumps(raw_text)
                return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ULAK - Metin</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%); min-height: 100vh;
    display: flex; justify-content: center; align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }}
.container {{ background: rgba(20, 27, 64, 0.97); border: 2px solid #00d4ff;
    border-radius: 20px; padding: 40px; max-width: 700px; width: 100%;
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.3); }}
h1 {{ color: #00d4ff; text-align: center; font-size: 1.8em; margin-bottom: 6px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5); }}
.sender {{ color: #b24bf3; text-align: center; font-size: 0.9em; margin-bottom: 24px; }}
.text-box {{ background: rgba(10, 14, 39, 0.8); border: 1px solid #2d3462;
    border-radius: 12px; padding: 20px; color: #e8eaf6; font-size: 1em;
    line-height: 1.7; max-height: 420px; overflow-y: auto; word-break: break-word;
    white-space: pre-wrap; }}
.copy-btn {{ display: block; width: 100%; padding: 15px;
    background: linear-gradient(135deg, #00d4ff, #b24bf3); color: #fff;
    border: none; border-radius: 12px; font-size: 1.1em; font-weight: bold;
    cursor: pointer; margin-top: 20px; transition: opacity 0.2s;
    box-shadow: 0 0 18px rgba(0, 212, 255, 0.3); }}
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
body {{ background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    min-height: 100vh; display: flex; justify-content: center; align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }}
.container {{ background: rgba(20, 27, 64, 0.97); border: 2px solid #00d4ff;
    border-radius: 20px; padding: 40px; max-width: 480px; width: 100%;
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.3); text-align: center; }}
h1 {{ color: #00d4ff; font-size: 1.8em; margin-bottom: 6px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5); }}
.icon {{ font-size: 4em; margin: 20px 0; }}
.filename {{ color: #e8eaf6; font-size: 1.1em; font-weight: bold;
    margin: 10px 0; word-break: break-all; }}
.meta {{ color: #8b949e; font-size: 0.9em; margin: 5px 0; }}
.sender {{ color: #b24bf3; font-size: 0.9em; margin: 16px 0; }}
.download-btn {{ display: block; width: 100%; padding: 18px;
    background: linear-gradient(135deg, #00d4ff, #b24bf3); color: #fff;
    border: none; border-radius: 14px; font-size: 1.2em; font-weight: bold;
    cursor: pointer; text-decoration: none; margin-top: 24px;
    box-shadow: 0 0 24px rgba(0, 212, 255, 0.4); transition: opacity 0.2s; }}
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
body {{ background: linear-gradient(135deg, #0a0e27, #1a1f3a); min-height: 100vh;
    display: flex; justify-content: center; align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif; color: #e8eaf6; }}
.container {{ background: rgba(20, 27, 64, 0.97); border: 2px solid #ff2e97;
    border-radius: 20px; padding: 40px; max-width: 400px; width: 90%;
    text-align: center; box-shadow: 0 0 40px rgba(255, 46, 151, 0.3); }}
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


# ============================================================================
# NETWORK MANAGER
# ============================================================================

            try:
                message = json.dumps({
                    'type': 'announce',
                    'name': self.device_name,
                    'ip': self.get_local_ip()
                }).encode('utf-8')
                sock.sendto(message, ('<broadcast>', self.broadcast_port))
                sock.sendto(message, ('255.255.255.255', self.broadcast_port))
                local_ip = self.get_local_ip()
                if local_ip != '127.0.0.1':
                    parts = local_ip.split('.')
                    broadcast_addr = f"{parts[0]}.{parts[1]}.{parts[2]}.255"
                    try:
                        sock.sendto(message, (broadcast_addr, self.broadcast_port))
                    except:
                        pass
                print(f"Broadcasting: {self.device_name} - {self.get_local_ip()}")
            except Exception as e:
                print(f"Broadcast error: {e}")
            time.sleep(2)
        sock.close()
    
    def _listen_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        
        try:
            sock.bind(('', self.broadcast_port))
            print(f"Listening for broadcasts on 0.0.0.0:{self.broadcast_port}")
        except Exception as e:
            print(f"Bind error: {e}")
            try:
                sock.bind(('0.0.0.0', self.broadcast_port))
            except:
                return
        
        sock.settimeout(1)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))
                print(f"Received broadcast from {addr}: {msg}")
                
                if msg['type'] == 'announce':
                    sender_ip = msg['ip']
                    my_ip = self.get_local_ip()
                    
                    if sender_ip != my_ip and sender_ip != '127.0.0.1':
                        device_id = sender_ip
                        self.last_seen[device_id] = time.time()
                        
                        if device_id not in self.discovered_devices:
                            print(f"Found NEW device: {msg['name']} - {sender_ip}")
                            self.discovered_devices[device_id] = msg
                            self.device_found.emit({'name': msg['name'], 'ip': sender_ip})
                        else:
                            self.discovered_devices[device_id] = msg
                    else:
                        print(f"Ignoring own broadcast: {sender_ip} vs {my_ip}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")
        sock.close()
    
    def _cleanup_devices(self):
        while self.running:
            time.sleep(3)
            current_time = time.time()
            to_remove = []
            
            for device_id, last_time in list(self.last_seen.items()):
                if current_time - last_time > 7:
                    to_remove.append(device_id)
            
            for device_id in to_remove:
                if device_id in self.discovered_devices:
                    del self.discovered_devices[device_id]
                if device_id in self.last_seen:
                    del self.last_seen[device_id]
                print(f"Device lost: {device_id}")
                self.device_lost.emit(device_id)
    
    def _listen_files(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        
        sock.bind(('0.0.0.0', self.port))
        sock.listen(5)
        sock.settimeout(1)
        print(f"Listening for files on port {self.port}")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=self._handle_file_transfer, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Accept error: {e}")
        sock.close()
    
    def _handle_file_transfer(self, conn):
        try:
            conn.settimeout(120)
            print("[DEBUG] Starting file transfer handler")
            
            header_size_data = conn.recv(4)
            if len(header_size_data) < 4:
                print("[ERROR] Failed to read header size")
                return
                
            header_size = int.from_bytes(header_size_data, 'big')
            print(f"[DEBUG] Header size: {header_size}")
            
            header_data = b''
            while len(header_data) < header_size:
                chunk = conn.recv(header_size - len(header_data))
                if not chunk:
                    return
                header_data += chunk
            
            header = json.loads(header_data.decode('utf-8'))
            print(f"[DEBUG] Received header: {header}")
            
            if header.get('type') == 'text':
                is_encrypted = header.get('encrypted', False)
                text_content = header.get('content', '')
                sender = header.get('sender', 'Unknown')
                
                if is_encrypted:
                    try:
                        import base64
                        encrypted_bytes = base64.b64decode(text_content)
                        decrypted_bytes = decrypt_data(encrypted_bytes, self.encryption_key)
                        text_content = decrypted_bytes.decode('utf-8')
                    except Exception as e:
                        print(f"[ERROR] Text decryption failed: {e}")
                        try:
                            conn.sendall(b'DECRYPT_FAIL')
                        except:
                            pass
                        self.decryption_failed.emit('Metin Mesajı', sender)
                        conn.close()
                        return
                          base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(downloads, f"{base}_{counter}{ext}")
                counter += 1
            
            print(f"[DEBUG] Saving to: {save_path} (encrypted={file_info['encrypted']})")
            
            received = 0
            filesize = file_info['filesize']
            is_encrypted = file_info['encrypted']
            start_time = time.time()
            last_update = start_time
            
            with open(save_path, 'wb') as f:
                while received < filesize:
                    if is_encrypted:
                        chunk_size_data = conn.recv(4)
                        if len(chunk_size_data) < 4:
                            break
                        chunk_size = int.from_bytes(chunk_size_data, 'big')
                        
                        encrypted_chunk = b''
                        while len(encrypted_chunk) < chunk_size:
                            part = conn.recv(chunk_size - len(encrypted_chunk))
                            if not part:
                                break
                            encrypted_chunk += part
                        
                        if len(encrypted_chunk) < chunk_size:
                            break
                        
                        try:
                            chunk = decrypt_data(encrypted_chunk, self.encryption_key)
                        except ValueError as e:
                            print(f"[ERROR] Decryption failed: {e}")
                            try:
                                conn.sendall(b'DECRYPT_FAIL')
                            except:
                                pass
                            self.decryption_failed.emit(file_info['filename'], file_info['sender'])
                            conn.close()
                            if os.path.exists(save_path):
                                os.remove(save_path)
                            return
                        
                        f.write(chunk)
                        received += len(chunk)
                    else:
                        chunk = conn.recv(min(65536, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                    
                    current_time = time.time()
                    if current_time - last_update >= 0.5:
                        elapsed = current_time - start_time
                        speed = received / elapsed if elapsed > 0 else 0
                        self.transfer_speed.emit(speed, received, filesize)
                        last_update = current_time
                    
                    if filesize > 0:
                        progress = int((received / filesize) * 100)
                        self.progress_updated.emit(progress)
            
            print(f"[DEBUG] Received {received}/{filesize} bytes")
            
            if received == filesize:
                final_name = filename
                is_clipboard_image = file_info.get('is_clipboard_image', False)
                
                if file_info['is_folder']:
                    print(f"[DEBUG] This is a folder, extracting ZIP: {save_path}")
                    extract_path = save_path[:-4] if save_path.endswith('.zip') else save_path
                    print(f"[DEBUG] Extract path: {extract_path}")
                    
                    try:
                        with zipfile.ZipFile(save_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_path)
                        print(f"[DEBUG] Extracted to: {extract_path}")
                        
                        os.remove(save_path)
                        print(f"[DEBUG] Removed ZIP: {save_path}")
                        
                        final_name = os.path.basename(extract_path)
                        print(f"[DEBUG] Final folder name: {final_name}")
                    except Exception as e:
                        print(f"[ERROR] Extract error: {e}")
                        import traceback
                        traceback.print_exc()
                elif is_clipboard_image:
                    print(f"[DEBUG] This is a clipboard image: {filename}")
                    self.clipboard_image_received.emit(save_path, file_info['sender'])
                    print(f"[DEBUG] Clipboard image signal emitted")
                    return
                else:
                    print(f"[DEBUG] This is a regular file: {filename}")
                
                print(f"[DEBUG] Emitting file_received signal with name: {final_name}, sender: {file_info['sender']}")
                self.file_received.emit(final_name, file_info['sender'])
                print(f"[DEBUG] Signal emitted successfully")
            else:
                print(f"[ERROR] Incomplete transfer: {received}/{filesize}")
                if os.path.exists(save_path):
                    os.remove(save_path)
                
        except Exception as e:
            print(f"[ERROR] Error receiving file: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()
            print("[DEBUG] Connection closed")
    
    def send_file(self, filepath, target_ip, is_clipboard_image=False):
        temp_file = None
        try:
            print(f"[DEBUG] Sending {filepath} to {target_ip}")
            
            is_folder = os.path.isdir(filepath)
            print(f"[DEBUG] is_folder: {is_folder}")
            
            if is_folder:
                file_count = sum([len(files) for _, _, files in os.walk(filepath)])
                folder_count = sum([len(dirs) for _, dirs, _ in os.walk(filepath)])
                
                print(f"[DEBUG] Creating ZIP for folder: {filepath}")
                print(f"[DEBUG] Contents: {file_count} files, {folder_count} folders")
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip').name
                with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(filepath):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                arcname = os.path.relpath(file_path, os.path.dirname(filepath))
                                zipf.write(file_path, arcname)
                                print(f"[DEBUG] Added to ZIP: {arcname}")
                            except Exception as e:
                                print(f"[ERROR] Skipping file {file_path}: {e}")
                
                print(f"[DEBUG] ZIP created: {temp_file}")
                actual_file = temp_file
                filename = os.path.basename(filepath) + '.zip'
                print(f"[DEBUG] Filename to send: {filename}")
            else:
                actual_file = filepath
                filename = os.path.basename(filepath)
                file_count = 0
                folder_count = 0
                print(f"[DEBUG] Regular file: {filename}")
            
            filesize = os.path.getsize(actual_file)
            print(f"[DEBUG] File size: {filesize} bytes")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((target_ip, self.port))
            print("[DEBUG] Connected")
            
            header = json.dumps({
                'filename': filename,
                'filesize': filesize,
                'sender': self.device_name,
                'is_folder': is_folder,
                'file_count': file_count,
                'folder_count': folder_count,
                'encrypted': self.use_encryption,
                'is_clipboard_image': is_clipboard_image
            }).encode('utf-8')
            
            sock.sendall(len(header).to_bytes(4, 'big'))
            sock.sendall(header)
            print(f"[DEBUG] Header sent (encrypted={self.use_encryption}, is_folder={is_folder}), waiting for acceptance...")
            
            sock.settimeout(65)
            try:
                response = sock.recv(8)
                print(f"[DEBUG] Received response: {response}")
                if response == b'REJECTED':
                    print("[DEBUG] Transfer rejected by receiver")
                    sock.close()
                    if temp_file and os.path.exists(temp_file):
                        os.remove(temp_file)
                    self.transfer_rejected.emit(os.path.basename(filepath), 'Receiver rejected')
                    return False
                elif response == b'TIMEOUT__':
                    print("[DEBUG] Transfer timeout by receiver")
                    sock.close()
                    if temp_file and os.path.exists(temp_file):
                        os.remove(temp_file)
                    return False
            except socket.timeout:
                print("[ERROR] No response from receiver")
                sock.close()
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
                return False
            except Exception as e:
                print(f"[ERROR] Error waiting for response: {e}")
                sock.close()
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
                return False
            
            sock.settimeout(120)
            print("[DEBUG] Starting file transfer")
            
            sent = 0
            start_time = time.time()
            last_update = start_time
            
            with open(actual_file, 'rb') as f:
                while sent < filesize:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    
                    try:
                        if self.use_encryption:
                            encrypted_chunk = encrypt_data(chunk, self.encryption_key)
                            chunk_size = len(encrypted_chunk)
                            sock.sendall(chunk_size.to_bytes(4, 'big'))
                            sock.sendall(encrypted_chunk)
                        else:
                            sock.sendall(chunk)
                    except Exception as e:
                        print(f"[ERROR] Send error: {e}")
                        sock.close()
                        if temp_file and os.path.exists(temp_file):
                            os.remove(temp_file)
                        return False
                    
                    sent += len(chunk)
                    
                    sock.settimeout(0.01)
                    try:
                        error_msg = sock.recv(12, socket.MSG_DONTWAIT)
                        if error_msg == b'DECRYPT_FAIL':
                            print("[ERROR] Receiver reported decryption failure")
                            sock.close()
                            if temp_file and os.path.exists(temp_file):
                                os.remove(temp_file)
                            self.transfer_rejected.emit(os.path.basename(filepath), 'Decryption failed')
                            return False
                    except:
                        pass
                    sock.settimeout(120)
                    
                    current_time = time.time()
                    if current_time - last_update >= 0.5:
                        elapsed = current_time - start_time
                        speed = sent / elapsed if elapsed > 0 else 0
                        self.transfer_speed.emit(speed, sent, filesize)
                        last_update = current_time
                    
                    if filesize > 0:
                        progress = int((sent / filesize) * 100)
                        self.progress_updated.emit(progress)
            
            print(f"[DEBUG] Sent {sent}/{filesize} bytes")
            sock.close()
            
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"[DEBUG] Removed temp ZIP: {temp_file}")
            
            success = sent == filesize
            print(f"[DEBUG] Transfer {'successful' if success else 'failed'}")
            return success
            
        except Exception as e:
            print(f"[ERROR] Error sending file: {e}")
            import traceback
            traceback.print_exc()
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def send_text(self, text, target_ip):
        try:
            print(f"[DEBUG] Sending text to {target_ip}: {text[:50]}...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target_ip, self.port))
            
            content = text
            if self.use_encryption:
                try:
                    import base64
                    encrypted_bytes = encrypt_data(text.encode('utf-8'), self.encryption_key)
                    content = base64.b64encode(encrypted_bytes).decode('ascii')
                except Exception as e:
                    print(f"[ERROR] Encryption failed: {e}")
                    return False
            
            header = json.dumps({
                'type': 'text',
                'content': content,
                'sender': self.device_name,
                'encrypted': self.use_encryption
            }).encode('utf-8')
            
            sock.sendall(len(header).to_bytes(4, 'big'))
            sock.sendall(header)
            
            if self.use_encryption:
                sock.settimeout(2)
                try:
                    error_msg = sock.recv(12)
                    if error_msg == b'DECRYPT_FAIL':
                        print("[ERROR] Receiver reported text decryption failure")
                        sock.close()
                        self.transfer_rejected.emit('Metin Mesajı', 'Decryption failed')
                        return False
                except socket.timeout:
                    pass
            
            sock.close()
            
            print(f"[DEBUG] Text sent successfully (encrypted={self.use_encryption})")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error sending text: {e}")
            return False


# ============================================================================
# STYLES
# ============================================================================


}

QPushButton#sendActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00fff9, stop:1 #00b8e6);
}

QPushButton#sendActionBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0099bb, stop:1 #007aa3);
}

QPushButton#linkBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4ff, stop:1 #0099cc);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#linkBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00fff9, stop:1 #00b8e6);
}

QListWidget {
    background-color: #141b40;
    border: 2px solid #00d4ff;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    background-color: #1e234a;
    border-radius: 8px;
    padding: 16px;
    margin: 4px;
    color: #e8eaf6;
    border: 1px solid #2d3462;
}

QListWidget::item:hover {
    background-color: #252d5c;
    border: 1px solid #00d4ff;
}

QListWidget::item:selected {
    background-color: rgba(0, 212, 255, 0.15);
    color: #00d4ff;
    border: 1px solid #00d4ff;
}

QLabel {
    color: #e8eaf6;
    background: transparent;
}

QProgressBar {
    border: 2px solid #00d4ff;
    border-radius: 8px;
    text-align: center;
    background-color: #141b40;
    color: #e8eaf6;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4ff, stop:1 #b24bf3);
    border-radius: 6px;
}

QScrollBar:vertical {
    background: #141b40;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #00d4ff;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #00fff9;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #141b40;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #00d4ff;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTabWidget::pane {
    border: 2px solid #2d3462;
    border-radius: 0px;
    background-color: #0a0e27;
}

QTabBar::tab {
    background-color: #141b40;
    color: #8b949e;
    padding: 8px 12px;
    border: 1px solid #2d3462;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: bold;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #1e234a;
    color: #00d4ff;
    border-color: #00d4ff;
    border-bottom: 2px solid #00d4ff;
}

QTabBar::tab:hover:!selected {
    background-color: #1e234a;
    color: #e8eaf6;
}

QLineEdit {
    background-color: #141b40;
    border: 1px solid #2d3462;
    border-radius: 8px;
    color: #e8eaf6;
    padding: 8px 12px;
    selection-background-color: rgba(0, 212, 255, 0.3);
}

QLineEdit:focus {
    border: 1px solid #00d4ff;
    background-color: #1e234a;
}

QCheckBox {
    color: #e8eaf6;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #2d3462;
    background: #141b40;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00d4ff, stop:1 #b24bf3);
    border-color: #00d4ff;
}

QCheckBox::indicator:hover {
    border-color: #00d4ff;
}

QMessageBox {
    background-color: #141b40;
}

QMessageBox QLabel {
    color: #e8eaf6;
    background: transparent;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QFrame {
    background-color: #0a0e27;
}

QMenu {
    background-color: #141b40;
    border: 1px solid #00d4ff;
    border-radius: 8px;
    color: #e8eaf6;
}

QMenu::item:selected {
    background-color: rgba(0, 212, 255, 0.2);
    color: #00d4ff;
}

QTextEdit {
    background-color: #141b40;
    border: 1px solid #2d3462;
    border-radius: 8px;
    color: #e8eaf6;
    padding: 8px;
    selection-background-color: rgba(0, 212, 255, 0.3);
}

QTextEdit:focus {
    border-color: #00d4ff;
}

QDialog {
    background-color: #141b40;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
    min-height: 32px;
}
"""

# ============================================================================
# UI HELPER CLASSES
# ============================================================================

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class DropZone(QFrame):
    filesDropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #2d3462;
                border-radius: 10px;
                background-color: #141b40;
            }
            QFrame:hover {
                border: 2px dashed #00d4ff;
                background-color: #1e234a;
            }
        """)

        layout = QVBoxLayout(self)
        icon = QLabel("📁")
        icon.setFont(QFont('Segoe UI', 32))
        icon.setAlignment(Qt.AlignCenter)

        text = QLabel("Dosya/Klasör sürükleyin\nveya tıklayarak seçin")
        text.setFont(QFont('Segoe UI', 10))
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("color: #5a6080;")

        layout.addWidget(icon)
        layout.addWidget(text)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.filesDropped.emit(files)


class TextMessageDialog(QDialog):
    def __init__(self, text, sender, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Metin Mesajı Alındı")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setStyleSheet(DARK_THEME)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel(f"💬 {sender} bir mesaj gönderdi")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)

        self.text_display = QTextEdit()
        self.text_display.setPlainText(text)
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(150)
        layout.addWidget(self.text_display)

        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Kopyala")
        copy_btn.setMinimumHeight(36)
        copy_btn.clicked.connect(self.copy_text)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton("✅ Tamam")
        close_btn.setMinimumHeight(36)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def copy_text(self):
        QApplication.clipboard().setText(self.text_display.toPlainText())
        copy_btn = self.sender()
        if copy_btn:
            copy_btn.setText("✅ Kopyalandı")
            def _restore():
                try:
                    copy_btn.setText("📋 Kopyala")
                except RuntimeError:
                    pass
            QTimer.singleShot(1000, _restore)


class AnnouncementCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        self.setObjectName("announcementCard")
        self.setStyleSheet("""
            QFrame#announcementCard {
                background-color: #1a0d38;
                border: 1px solid #b24bf3;
                border-radius: 8px;
                margin: 4px 8px 0px 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 10, 10)
        layout.setSpacing(5)

        header = QHBoxLayout()
        header.setSpacing(6)

        title_lbl = QLabel("📢 Duyurular")
        title_lbl.setFont(QFont('Segoe UI', 10, QFont.Bold))
        title_lbl.setStyleSheet("color: #b24bf3; background: transparent; border: none;")
        header.addWidget(title_lbl)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setToolTip("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(178,75,243,0.18);
                color: #b24bf3;
                border: 1px solid #b24bf3;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(178,75,243,0.40);
                color: #ffffff;
                border-color: #d090ff;
            }
        """)
        close_btn.clicked.connect(self._on_close)
        header.addWidget(close_btn)
        layout.addLayout(header)

        self._text_lbl = QLabel()
        self._text_lbl.setFont(QFont('Segoe UI', 10))
        self._text_lbl.setStyleSheet("color: #e8eaf6; background: transparent; border: none;")
        self._text_lbl.setWordWrap(True)
        layout.addWidget(self._text_lbl)

    def show_announcement(self, text):
        if not text or not text.strip():
            self.setVisible(False)
            return
        self._text_lbl.setText(text.strip())
        if not self.isVisible():
            self.setVisible(True)
            QTimer.singleShot(10, self._animate_show)

    def _animate_show(self):
        self.setMaximumHeight(16777215)
        target = max(self.sizeHint().height(), 60)
        self.setMaximumHeight(0)

        anim = QPropertyAnimation(self, b"maximumHeight", self)
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: self.setMaximumHeight(16777215))
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def _on_close(self):
        current = self.height()
        anim = QPropertyAnimation(self, b"maximumHeight", self)
        anim.setDuration(200)
        anim.setStartValue(current)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(lambda: self.setVisible(False))
        anim.start(QPropertyAnimation.DeleteWhenStopped)



        self.countdown_label = QLabel("3")
        self.countdown_label.setFont(QFont('Segoe UI', 72, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: #00d4ff;")
        layout.addWidget(self.countdown_label)

        info_label = QLabel("Ekran görüntüsü alınıyor...")
        info_label.setFont(QFont('Segoe UI', 12))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #8b949e;")
        layout.addWidget(info_label)

        self.counter = 3
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.counter -= 1
        if self.counter > 0:
            self.countdown_label.setText(str(self.counter))
        else:
            self.timer.stop()
            self.accept()



class BatchTransferDialog(QDialog):
    def __init__(self, files_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Toplu Dosya Alımı")
        self.setModal(True)
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)
        self.setStyleSheet(DARK_THEME)
        self.callbacks = []
        self.files_info = files_info
        self.checkboxes = []

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        sender = files_info[0]['sender'] if files_info else 'Bilinmeyen'
        title = QLabel(f"📥 {sender} {len(files_info)} dosya gönderiyor")

            details_layout.addStretch()
            info_layout.addLayout(details_layout)
            
            file_layout.addLayout(info_layout)
            scroll_layout.addWidget(file_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.progress = QProgressBar()
        self.progress.setMinimumHeight(24)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Almak istediğiniz dosyaları seçin ve onaylayın")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8b949e; padding: 8px;")
        layout.addWidget(self.status_label)

        buttons = QDialogButtonBox()
        self.accept_btn = buttons.addButton("✅ Seçilenleri Kabul Et", QDialogButtonBox.AcceptRole)
        self.reject_btn = buttons.addButton("❌ Tümünü Reddet", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept_selected)
        buttons.rejected.connect(self.reject_all)
        layout.addWidget(buttons)

    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.setChecked(False)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def accept_selected(self):
        selected_count = 0
        for idx, (callback, checkbox) in enumerate(zip(self.callbacks, self.checkboxes)):
            if checkbox.isChecked():
                callback(True)
                selected_count += 1
            else:
                callback(False)
        
        if selected_count == 0:
            QMessageBox.warning(self, 'Uyarı', 'Hiçbir dosya seçilmedi!')
            return
        
        self.progress.setVisible(True)
        self.status_label.setText(f"✅ {selected_count} dosya alınıyor...")
        self.accept_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)
        self.reject_btn.setVisible(False)

    def reject_all(self):
        for callback in self.callbacks:
            callback(False)
        self.close()


class TransferDialog(QDialog):
    def __init__(self, file_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dosya Alınıyor")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setStyleSheet(DARK_THEME)
        self.callback = None

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel(f"📥 {file_info['sender']} dosya gönderiyor")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #141b40; border-radius: 12px; padding: 16px;"
            "border: 1px solid #2d3462;")
        info_layout = QVBoxLayout(info_frame)

        if file_info['is_folder']:
            icon_label = QLabel(f"📁 {file_info['filename']}")
        else:
            icon_label = QLabel(f"📄 {file_info['filename']}")
        icon_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        info_layout.addWidget(icon_label)

        size_label = QLabel(f"Boyut: {self.format_size(file_info['filesize'])}")
        size_label.setStyleSheet("color: #8b949e;")
        info_layout.addWidget(size_label)

        if file_info.get('encrypted', False):
            enc_label = QLabel("🔒 AES-256 Şifreli Gönderim")
            enc_label.setStyleSheet("color: #39ff14; font-weight: bold; padding-top: 4px;")
            info_layout.addWidget(enc_label)

        if file_info['is_folder']:
            content_label = QLabel(
                f"İçerik: {file_info.get('file_count', 0)} dosya, "
                f"{file_info.get('folder_count', 0)} klasör")
            content_label.setStyleSheet("color: #8b949e;")
            info_layout.addWidget(content_label)

            note_label = QLabel("Not: Tüm klasör içeriği tek seferde alınacaktır")
            note_label.setStyleSheet(
                "color: #f9e2af; font-style: italic; padding-top: 8px;")
            info_layout.addWidget(note_label)

        from datetime import datetime
        time_label = QLabel(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        time_label.setStyleSheet("color: #8b949e;")
        info_layout.addWidget(time_label)

        layout.addWidget(info_frame)

        self.progress = QProgressBar()
        self.progress.setMinimumHeight(24)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Kabul etmek için onaylayın")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8b949e; padding: 8px;")
        layout.addWidget(self.status_label)

        buttons = QDialogButtonBox()
        self.accept_btn = buttons.addButton("✅ Kabul Et", QDialogButtonBox.AcceptRole)
        self.reject_btn = buttons.addButton("❌ Reddet", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept_transfer)
        buttons.rejected.connect(self.reject_transfer)
        layout.addWidget(buttons)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def accept_transfer(self):
        if self.callback:
            self.callback(True)
        self.progress.setVisible(True)
        self.status_label.setText("Dosya alınıyor...")
        self.accept_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)
        self.reject_btn.setVisible(False)

    def reject_transfer(self):
        if self.callback:
            self.callback(False)
        self.close()


class LinkShareDialog(QDialog):
    def __init__(self, link, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔗 Link Üzerinden Gönder")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet(DARK_THEME)
        self.parent_app = parent

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("🔗 Link Oluşturuldu")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "Aşağıdaki linki karşı cihazda tarayıcıda açın.\n"
            "Hedef cihazın aynı ağda olması yeterli — ULAK yüklü olmak zorunda değil."
        )
        desc.setStyleSheet("color: #8b949e; font-size: 12px;")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        link_frame = QFrame()
        link_frame.setStyleSheet(
            "background-color: #141b40; border: 2px solid #00d4ff; "
            "border-radius: 12px; padding: 16px;")
        link_layout = QVBoxLayout(link_frame)

        self.link_label = QLabel(link)
        self.link_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.link_label.setStyleSheet("color: #00fff9;")
        self.link_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.link_label.setAlignment(Qt.AlignCenter)
        self.link_label.setWordWrap(True)
        link_layout.addWidget(self.link_label)

        layout.addWidget(link_frame)

        info = QLabel(
            "⚠️ Bu pencere açık olduğu sürece link erişilebilir.\n"
            "Pencereyi kapattığınızda link sıfırlanır."
        )
        info.setStyleSheet("color: #f9e2af; font-size: 11px; font-style: italic;")
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Linki Kopyala")
        copy_btn.setMinimumHeight(40)
        copy_btn.clicked.connect(self.copy_link)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton("✖ Kapat")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def copy_link(self):
        QApplication.clipboard().setText(self.link_label.text())
        copy_btn = self.sender()
        if copy_btn:
            copy_btn.setText("✅ Kopyalandı!")
            QTimer.singleShot(2000, lambda: copy_btn.setText("📋 Linki Kopyala"))

    def closeEvent(self, event):
        if self.parent_app and hasattr(self.parent_app, 'web_server'):
            self.parent_app.web_server.clear_content()
        super().closeEvent(event)

    def reject(self):
        if self.parent_app and hasattr(self.parent_app, 'web_server'):
            self.parent_app.web_server.clear_content()
        super().reject()



# ============================================================================
# MAIN APPLICATION
# ============================================================================

class LocalSendApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # QSettings'i özel dizine yönlendir
        config_dir = os.path.expanduser('~/.config/ULAK')
        os.makedirs(config_dir, exist_ok=True)
        self.settings = QSettings(os.path.join(config_dir, 'ulak.conf'), QSettings.IniFormat)
        self.network = NetworkManager()
        self.web_server = ULAKWebServer(port=53319)
        self.announcement_manager = AnnouncementManager()
        self.devices = {}
        self.current_dialog = None
        self.pending_transfers = []
        self.batch_timer = None

        saved_name = self.settings.value('device_name', '')
        if saved_name:
            self.network.device_name = saved_name

        self.init_ui()
        self.load_settings()
        self.setup_connections()
        self.setup_tray_icon()
        self.setup_shortcuts()
        self.check_port_conflict()
        self.web_server.start()
        self.network.start_discovery()
        self.announcement_manager.fetch_async()
        print(f"App started: {self.network.device_name} - {self.network.get_local_ip()}")

    def check_port_conflict(self):
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_sock.bind(('0.0.0.0', self.network.port))
            test_sock.close()
        except OSError:
            QMessageBox.warning(
                self, 'Port Uyarısı',
                f'⚠️ Port {self.network.port} başka bir uygulama tarafından '
                f'kullanılıyor!\n\nULAK düzgün çalışmayabilir.\n'
                f'Ayarlardan farklı bir port seçmeyi deneyin.'
            )

    def get_resource_path(self, *paths):
        if paths and paths[0] == 'ulaklo.png':
            system_icon = '/usr/share/pixmaps/ulaklo.png'
            if os.path.exists(system_icon):
                return system_icon
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, *paths)

    def init_ui(self):
        self.setWindowTitle('ULAK')
        self.setMinimumSize(750, 600)
        self.setStyleSheet(DARK_THEME)

        icon_path = self.get_resource_path('ulaklo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_bar = QWidget()
        header_bar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #0a0e27, stop:1 #141b40);"
            " padding: 12px;"
            " border-bottom: 2px solid #00d4ff;")
        header_layout = QHBoxLayout(header_bar)

        self.logo_label = QLabel()
        logo_path = self.get_resource_path('ulaklo.png')
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(
                logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(self.logo_label)

        title = QLabel("ULAK")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #00d4ff; text-shadow: 0 0 10px rgba(0,212,255,0.5);")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.status_indicator = QLabel("🟢")
        self.status_indicator.setFont(QFont('Segoe UI', 14))
        header_layout.addWidget(self.status_indicator)

        main_layout.addWidget(header_bar)

        self.announcement_card = AnnouncementCard()
        main_layout.addWidget(self.announcement_card)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(False)
        main_layout.addWidget(self.tabs)

        self._build_send_tab()
        self._build_receive_tab()
        self._build_settings_tab()
        self._build_about_tab()

        self.status_bar = QLabel("")
        self.status_bar.setStyleSheet(
            "background-color: #141b40; padding: 10px; color: #8b949e;"
            " border-top: 1px solid #2d3462;")
        self.status_bar.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(24)
        self.progress_bar.setMaximumHeight(24)
        self.progress_bar.setFormat("%p%")
        main_layout.addWidget(self.progress_bar)

        self.transfer_info_label = QLabel("")
        self.transfer_info_label.setStyleSheet(
            "background-color: #141b40; padding: 8px; color: #00d4ff; font-size: 10px;")
        self.transfer_info_label.setAlignment(Qt.AlignCenter)
        self.transfer_info_label.setVisible(False)
        main_layout.addWidget(self.transfer_info_label)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_device_list)
        self.refresh_timer.start(2000)

    def _build_send_tab(self):
        send_tab = QWidget()
        send_tab.setAcceptDrops(True)
        send_tab.dragEnterEvent = self.send_tab_drag_enter
        send_tab.dropEvent = self.send_tab_drop

        send_layout = QVBoxLayout(send_tab)
        send_layout.setContentsMargins(16, 16, 16, 16)
        send_layout.setSpacing(12)

        self.encryption_info_label = ClickableLabel(
            "🔒 AES-256 Şifrelenmiş Biçimde Gönderiyorsunuz")
        self.encryption_info_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.encryption_info_label.setStyleSheet(
            "color: #0a0e27; background: #39ff14;"
            " padding: 8px; border-radius: 8px; cursor: pointer;")
        self.encryption_info_label.setAlignment(Qt.AlignCenter)
        self.encryption_info_label.setVisible(False)
        self.encryption_info_label.setToolTip(
            "Şifreleme ayarlarına gitmek için tıklayın")
        self.encryption_info_label.clicked.connect(self._go_to_encryption_settings)
        send_layout.addWidget(self.encryption_info_label)

        buttons_layout = QHBoxLayout()

        self.file_send_btn = QPushButton("📄 Dosya Gönder")
        self.file_send_btn.setObjectName("sendActionBtn")
        self.file_send_btn.setMinimumHeight(50)
        self.file_send_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.file_send_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.file_send_btn)

        self.folder_send_btn = QPushButton("📁 Klasör Gönder")
        self.folder_send_btn.setObjectName("sendActionBtn")
        self.folder_send_btn.setMinimumHeight(50)
        self.folder_send_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.folder_send_btn.clicked.connect(self.select_folder)
        buttons_layout.addWidget(self.folder_send_btn)

        self.text_send_btn = QPushButton("💬 Metin Gönder")
        self.text_send_btn.setObjectName("sendActionBtn")
        self.text_send_btn.setMinimumHeight(50)
        self.text_send_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.text_send_btn.clicked.connect(self.open_text_send_dialog)
        buttons_layout.addWidget(self.text_send_btn)

        self.clipboard_send_btn = QPushButton("📋 Panoyu Gönder")
        self.clipboard_send_btn.setObjectName("sendActionBtn")
        self.clipboard_send_btn.setMinimumHeight(50)
        self.clipboard_send_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.clipboard_send_btn.clicked.connect(self.send_clipboard)
        buttons_layout.addWidget(self.clipboard_send_btn)

        self.screenshot_btn = QPushButton("📸 Ekran Görüntüsü")
        self.screenshot_btn.setObjectName("sendActionBtn")
        self.screenshot_btn.setMinimumHeight(50)
        self.screenshot_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.screenshot_btn.clicked.connect(self.open_screenshot_dialog)
        buttons_layout.addWidget(self.screenshot_btn)

        send_layout.addLayout(buttons_layout)

        self.link_send_btn = QPushButton("🔗 Link Üzerinden Gönder (Cihaz Seçmeden)")
        self.link_send_btn.setObjectName("linkBtn")
        self.link_send_btn.setMinimumHeight(46)
        self.link_send_btn.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.link_send_btn.clicked.connect(self.show_link_send_options)
        send_layout.addWidget(self.link_send_btn)

        hint_label = QLabel(


    def _build_receive_tab(self):
        receive_tab = QWidget()
        receive_layout = QVBoxLayout(receive_tab)
        receive_layout.setContentsMargins(20, 20, 20, 20)
        receive_layout.setSpacing(16)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #141b40; border-radius: 12px; padding: 16px;"
            " border: 1px solid #2d3462;")
        info_layout = QVBoxLayout(info_frame)

        device_label = QLabel(f"🖥️ Cihaz Adı: {self.network.device_name}")
        device_label.setFont(QFont('Segoe UI', 12))
        info_layout.addWidget(device_label)

        ip_label = QLabel(f"🌐 IP Adresi: {self.network.get_local_ip()}")
        ip_label.setFont(QFont('Segoe UI', 12))
        info_layout.addWidget(ip_label)

        self.port_label = QLabel(f"🔌 Port: {self.network.port}")
        self.port_label.setFont(QFont('Segoe UI', 12))
        info_layout.addWidget(self.port_label)

        receive_layout.addWidget(info_frame)

        history_label = QLabel("📥 Alınan")
        history_label.setFont(QFont('Segoe UI', 13, QFont.Bold))
        receive_layout.addWidget(history_label)

        self.history_list = QListWidget()
        receive_layout.addWidget(self.history_list)

        bottom_btn_layout = QHBoxLayout()

        open_folder_btn = QPushButton("📁 İndirilenler Klasörünü Aç")
        open_folder_btn.setObjectName("secondaryBtn")
        open_folder_btn.setMinimumHeight(44)
        open_folder_btn.clicked.connect(self.open_downloads)
        bottom_btn_layout.addWidget(open_folder_btn)

        clear_history_btn = QPushButton("🗑️ Listeyi Temizle")
        clear_history_btn.setObjectName("secondaryBtn")
        clear_history_btn.setMinimumHeight(44)
        clear_history_btn.clicked.connect(self.clear_history)
        bottom_btn_layout.addWidget(clear_history_btn)

        receive_layout.addLayout(bottom_btn_layout)

        self.tabs.addTab(receive_tab, "📥 Alınanlar")


    def _build_settings_tab(self):
        settings_tab = QWidget()
        settings_main_layout = QVBoxLayout(settings_tab)
        settings_main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        settings_layout = QVBoxLayout(scroll_content)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(16)

        settings_label = QLabel("⚙️ Ayarlar")
        settings_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        settings_label.setStyleSheet("color: #00d4ff;")
        settings_layout.addWidget(settings_label)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Cihaz Adı:"))
        self.name_input = QLineEdit(self.network.device_name)
        name_layout.addWidget(self.name_input)
        settings_layout.addLayout(name_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit(str(self.network.port))
        self.port_input.setPlaceholderText("Varsayılan: 53317")
        port_layout.addWidget(self.port_input)
        settings_layout.addLayout(port_layout)

        broadcast_port_layout = QHBoxLayout()
        broadcast_port_layout.addWidget(QLabel("Broadcast Port:"))
        self.broadcast_port_input = QLineEdit(str(self.network.broadcast_port))
        self.broadcast_port_input.setPlaceholderText("Varsayılan: 53318")
        broadcast_port_layout.addWidget(self.broadcast_port_input)
        settings_layout.addLayout(broadcast_port_layout)

        self.encryption_checkbox = QCheckBox("🔒 AES-256 Şifreleme Kullan")
        self.encryption_checkbox.setFont(QFont('Segoe UI', 11))
        self.encryption_checkbox.setStyleSheet("padding: 8px;")
        self.encryption_checkbox.stateChanged.connect(self.on_encryption_changed)
        settings_layout.addWidget(self.encryption_checkbox)

        self.notification_checkbox = QCheckBox("🔔 Dosya Alındığında Bildirim Göster")
        self.notification_checkbox.setFont(QFont('Segoe UI', 11))
        self.notification_checkbox.setStyleSheet("padding: 8px;")
        settings_layout.addWidget(self.notification_checkbox)

        self.sound_checkbox = QCheckBox("🔊 Transfer Tamamlandığında Ses Çal")
        self.sound_checkbox.setFont(QFont('Segoe UI', 11))
        self.sound_checkbox.setStyleSheet("padding: 8px;")
        settings_layout.addWidget(self.sound_checkbox)

        self.tray_checkbox = QCheckBox("📥 Sistem Tepsisinde Çalıştır")
        self.tray_checkbox.setFont(QFont('Segoe UI', 11))
        self.tray_checkbox.setStyleSheet("padding: 8px;")
        self.tray_checkbox.stateChanged.connect(self.on_tray_changed)
        settings_layout.addWidget(self.tray_checkbox)

        self.auto_copy_clipboard_checkbox = QCheckBox("📋 Pano İçeriğini Otomatik Kopyala")
        self.auto_copy_clipboard_checkbox.setFont(QFont('Segoe UI', 11))
        self.auto_copy_clipboard_checkbox.setStyleSheet("padding: 8px;")
        settings_layout.addWidget(self.auto_copy_clipboard_checkbox)

        clipboard_note = QLabel(
            "ℹ️ Not: Pano içeriği (metin/resim) alındığında otomatik panoya kopyalanır")
        clipboard_note.setFont(QFont('Segoe UI', 9))
        clipboard_note.setStyleSheet(
            "color: #8b949e; font-style: italic; padding: 4px 8px;")
        clipboard_note.setWordWrap(True)
        settings_layout.addWidget(clipboard_note)

        shortcut_label = QLabel("⌨️ Kısayol Tuşları")
        shortcut_label.setFont(QFont('Segoe UI', 11, QFont.Bold))
        shortcut_label.setStyleSheet("padding-top: 8px; color: #00d4ff;")
        settings_layout.addWidget(shortcut_label)

        shortcut_info = QLabel(
            "📸 Hızlı Ekran Görüntüsü: Ctrl+Shift+S\n(3 saniye geri sayım ile tam ekran)")
        shortcut_info.setFont(QFont('Segoe UI', 10))
        shortcut_info.setStyleSheet("color: #8b949e; padding: 4px 8px;")
        settings_layout.addWidget(shortcut_info)

        download_folder_layout = QVBoxLayout()
        download_folder_label = QLabel("📁 İndirme Klasörü:")
        download_folder_label.setFont(QFont('Segoe UI', 11, QFont.Bold))
        download_folder_layout.addWidget(download_folder_label)

        download_path_layout = QHBoxLayout()
        self.download_path_input = QLineEdit()
        self.download_path_input.setReadOnly(True)
        self.download_path_input.setPlaceholderText(
            "Varsayılan: Downloads klasörü")
        download_path_layout.addWidget(self.download_path_input)

        browse_btn = QPushButton("📂 Gözat")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setMinimumHeight(32)
        browse_btn.clicked.connect(self.browse_download_folder)
        download_path_layout.addWidget(browse_btn)

        download_folder_layout.addLayout(download_path_layout)
        settings_layout.addLayout(download_folder_layout)

        password_layout = QVBoxLayout()
        password_label = QLabel(
            "Şifreleme Parolası (Boş bırakılırsa varsayılan kullanılır):")
        password_label.setFont(QFont('Segoe UI', 10))
        password_label.setStyleSheet("color: #8b949e; padding-top: 8px;")
        password_label.setWordWrap(True)
        password_layout.addWidget(password_label)

        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Özel şifreleme parolası girin...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(36)
        password_input_layout.addWidget(self.password_input)

        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setObjectName("secondaryBtn")
        self.show_password_btn.setFixedSize(44, 36)
        self.show_password_btn.setToolTip("Parolayı göster/gizle")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.show_password_btn)
        password_layout.addLayout(password_input_layout)

        password_note = QLabel(
            "⚠️ Not: Aynı parolayı kullanan cihazlar arası transfer yapılabilir")
        password_note.setFont(QFont('Segoe UI', 9))
        password_note.setStyleSheet("color: #f9e2af; font-style: italic;")
        password_note.setWordWrap(True)
        password_note.setContentsMargins(0, 6, 0, 6)
        password_note.setMinimumHeight(40)
        password_layout.addWidget(password_note)

        settings_layout.addLayout(password_layout)

        save_btn = QPushButton("💾 Kaydet")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)

        settings_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        settings_main_layout.addWidget(scroll_area)

        self.tabs.addTab(settings_tab, "⚙️ Ayarlar")

    def _build_about_tab(self):
        about_tab = QWidget()
        about_scroll = QScrollArea()
        about_scroll.setWidgetResizable(True)
        about_scroll.setFrameShape(QFrame.NoFrame)

        about_content = QWidget()
        about_layout = QVBoxLayout(about_content)
        about_layout.setContentsMargins(24, 24, 24, 24)
        about_layout.setSpacing(20)

        logo_label = QLabel()
        logo_path = self.get_resource_path('ulaklo.png')
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio,
                                   Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(logo_label)

        about_title = QLabel("ULAK")
        about_title.setFont(QFont('Segoe UI', 24, QFont.Bold))
        about_title.setAlignment(Qt.AlignCenter)
        about_title.setStyleSheet(
            "color: #00d4ff; text-shadow: 0 0 20px rgba(0,212,255,0.5);")
        about_layout.addWidget(about_title)

        version_label = QLabel("Versiyon 1.0.5 - Linux")
        version_label.setFont(QFont('Segoe UI', 14))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #8b949e; padding-bottom: 16px;")
        about_layout.addWidget(version_label)

        desc_frame = QFrame()
        desc_frame.setStyleSheet(
            "background-color: #141b40; border-radius: 12px; padding: 20px;"
            " border: 1px solid #2d3462;")
        desc_layout = QVBoxLayout(desc_frame)

        desc_title = QLabel("📝 Açıklama")
        desc_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        desc_title.setStyleSheet("color: #00d4ff;")
        desc_layout.addWidget(desc_title)

        desc_text = QLabel("Yerel ağ üzerinden hızlı ve güvenli dosya paylaşımı")
        desc_text.setFont(QFont('Segoe UI', 14))
        desc_text.setStyleSheet("color: #e8eaf6; padding-top: 8px;")
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)

        about_layout.addWidget(desc_frame)

        national_frame = QFrame()
        national_frame.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #1a1a3e, stop:1 #2d1b3d);"
            " border-radius: 12px; padding: 20px;"
            " border: 2px solid #e30a17;")
        national_layout = QHBoxLayout(national_frame)

        flag_label = QLabel("🇹🇷")
        flag_label.setFont(QFont('Segoe UI', 48))
        flag_label.setAlignment(Qt.AlignCenter)
        national_layout.addWidget(flag_label)

        text_label = QLabel("Yerli ve Milli Proje, TÜRK Yazılımcılar Tarafından Geliştirilmiştir.")
        text_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        text_label.setStyleSheet("color: #87ceeb; padding: 10px;")
        text_label.setWordWrap(True)
        national_layout.addWidget(text_label, 1)

        about_layout.addWidget(national_frame)

        platform_frame = QFrame()
        platform_frame.setStyleSheet(
            "background-color: #141b40; border-radius: 12px; padding: 20px;"
            " border: 1px solid #2d3462;")
        platform_layout = QVBoxLayout(platform_frame)

        platform_title = QLabel("💻 Platform Desteği")
        platform_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        platform_title.setStyleSheet("color: #00d4ff;")
        platform_layout.addWidget(platform_title)

        download_btn = QPushButton("🪟 Windows  🐧 Linux  🤖 Android  🍎 macOS İçin İndir")
        download_btn.setMinimumHeight(50)
        download_btn.setFont(QFont('Segoe UI', 12, QFont.Bold))
        download_btn.clicked.connect(
            lambda: self.open_url("https://ulak.algsoft.net.tr/"))
        platform_layout.addWidget(download_btn)

        about_layout.addWidget(platform_frame)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #141b40; border-radius: 12px; padding: 20px;"
            " border: 1px solid #2d3462;")
        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("ℹ️ Bilgi")
        info_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        info_title.setStyleSheet("color: #00d4ff;")
        info_layout.addWidget(info_title)

        for text, color in [
            ("👨💻 Geliştirici: Fatih ÖNDER (CekToR)", "#e8eaf6"),
            ("© 2026 ALGSoft Inc.", "#e8eaf6"),
            ("🌐 https://algsoft.net.tr", "#e8eaf6"),
            ("📧 info@algsoft.net.tr", "#e8eaf6"),
            ("📜 Lisans: MIT", "#e8eaf6"),
            ("🐱 GitHub: github.com/cektor/ulak", "#00d4ff"),
        ]:
            lbl = QLabel(text)
            lbl.setFont(QFont('Segoe UI', 14))
            lbl.setStyleSheet(f"color: {color}; padding-top: 4px;")
            info_layout.addWidget(lbl)

        about_layout.addWidget(info_frame)
        about_layout.addStretch()

        about_scroll.setWidget(about_content)
        about_tab_layout = QVBoxLayout(about_tab)
        about_tab_layout.setContentsMargins(0, 0, 0, 0)
        about_tab_layout.addWidget(about_scroll)

        self.tabs.addTab(about_tab, "ℹ️ Hakkında")

    def _go_to_encryption_settings(self):
        self.tabs.setCurrentIndex(2)
        self.encryption_checkbox.setFocus()


    def show_link_send_options(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("🔗 Link Üzerinden Gönder")
        dialog.setModal(True)
        dialog.setMinimumWidth(380)
        dialog.setStyleSheet(DARK_THEME)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        title = QLabel("Ne göndermek istiyorsunuz?")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        file_btn = QPushButton("📄 Dosya Gönder")
        file_btn.setMinimumHeight(46)
        file_btn.clicked.connect(lambda: (dialog.accept(), self._link_select_file()))
        layout.addWidget(file_btn)

        text_btn = QPushButton("💬 Metin Gönder")
        text_btn.setMinimumHeight(46)
        text_btn.clicked.connect(lambda: (dialog.accept(), self._link_send_text()))
        layout.addWidget(text_btn)

        clipboard_btn = QPushButton("📋 Pano Gönder")
        clipboard_btn.setMinimumHeight(46)
        clipboard_btn.clicked.connect(
            lambda: (dialog.accept(), self._link_send_clipboard()))
        layout.addWidget(clipboard_btn)

        cancel_btn = QPushButton("❌ İptal")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.exec_()

    def _link_select_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Link İçin Dosya Seç')
        if not files:
            return
        filepath = files[0]
        link = self.web_server.share_content(
            'file', filepath, self.network.device_name)
        self._show_link_dialog(link)

    def _link_send_text(self):
        dialog = TextSendDialog(self)
        def send_as_link():
            text = dialog.text_input.toPlainText().strip()
            if not text:
                QMessageBox.warning(dialog, 'Hata', 'Lütfen bir metin girin!')
                return
            dialog.accept()
            link = self.web_server.share_content(
                'text', text, self.network.device_name)
            self._show_link_dialog(link)

        for btn in dialog.findChildren(QPushButton):
            if "Gönder" in btn.text() and "İptal" not in btn.text():
                btn.clicked.disconnect()
                btn.clicked.connect(send_as_link)
                break
        dialog.exec_()

    def _link_send_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.png')
                temp_path = temp_file.name
                temp_file.close()
                if image.save(temp_path, 'PNG'):
                    link = self.web_server.share_content(
                        'file', temp_path, self.network.device_name)
                    self._show_link_dialog(link)
                    return

        if mime_data.hasText():
            text = clipboard.text().strip()
            if text:
                link = self.web_server.share_content(
                    'clipboard_text', text, self.network.device_name)
                self._show_link_dialog(link)
                return

        QMessageBox.warning(self, 'Hata', 'Panoda paylaşılabilir içerik bulunamadı!')

    def _show_link_dialog(self, link):
        dialog = LinkShareDialog(link, self)
        dialog.exec_()

    def setup_shortcuts(self):
        self.screenshot_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.screenshot_shortcut.activated.connect(self.quick_screenshot)

    def quick_screenshot(self):
        selected = self.devices_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Hata', 'Lütfen önce bir cihaz seçin!')
            return
        self.open_screenshot_dialog()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        icon_path = self.get_resource_path('ulaklo.png')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.create_tray_icon())

        tray_menu = QMenu()
        show_action = tray_menu.addAction("💻 Göster")
        show_action.triggered.connect(self.show)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("❌ Çıkış")
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        if self.settings.value('use_tray', False, type=bool):
            self.tray_icon.show()

    def create_tray_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(0, 212, 255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()
        return QIcon(pixmap)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def on_tray_changed(self):
        if hasattr(self, 'tray_icon'):
            if self.tray_checkbox.isChecked():
                self.tray_icon.show()
            else:
                self.tray_icon.hide()

    def show_notification(self, title, message):
        if self.settings.value('use_notifications', True, type=bool):
            if self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    title, message, QSystemTrayIcon.Information, 3000)

    def play_sound(self):
        if self.settings.value('use_sound', False, type=bool):
            try:
                os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null &')
            except Exception as e:
                print(f"[ERROR] Sound error: {e}")

    def get_device_icon(self, device_name):
        name_lower = device_name.lower()
        if 'android' in name_lower or 'iphone' in name_lower or 'mobile' in name_lower:
            return "📱"
        elif 'ipad' in name_lower or 'tablet' in name_lower:
            return "📱"
        elif 'mac' in name_lower or 'macbook' in name_lower:
            return "💻"
        elif 'windows' in name_lower or 'pc' in name_lower:
            return "🖥️"
        elif 'linux' in name_lower:
            return "🐧"
        else:
            return "💻"

    def setup_connections(self):
        self.network.device_found.connect(self.on_device_found)
        self.network.device_lost.connect(self.on_device_lost)
        self.network.file_received.connect(self.on_file_received)
        self.network.text_received.connect(self.on_text_received)
        self.network.clipboard_image_received.connect(self.on_clipboard_image_received)
        self.network.transfer_request.connect(self.on_transfer_request)
        self.announcement_manager.announcement_fetched.connect(
            self.announcement_card.show_announcement)
        self.announcement_manager.fetch_failed.connect(
            lambda: self.announcement_card.setVisible(False))
        self.network.transfer_rejected.connect(self.on_transfer_rejected)
        self.network.progress_updated.connect(self.on_progress_updated)
        self.network.transfer_speed.connect(self.on_transfer_speed)
        self.network.decryption_failed.connect(self.on_decryption_failed)
        self.devices_list.itemSelectionChanged.connect(self.update_send_button)
        self.files_list.itemSelectionChanged.connect(self.update_send_button)
        self.history_list.itemDoubleClicked.connect(self.on_history_double_click)

    def send_tab_drag_enter(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def send_tab_drop(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.on_files_dropped(files)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Dosya Seç')
        if files:
            self.on_files_dropped(files)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Klasör Seç')
        if folder:
            self.on_files_dropped([folder])

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def on_files_dropped(self, files):
        if not self.files_list.count():
            self.clear_files()
        for file in files:
            duplicate = False
            for i in range(self.files_list.count()):
                if self.files_list.item(i).data(Qt.UserRole) == file:
                    duplicate = True
                    break
            if not duplicate:
                if os.path.isfile(file):
                    item = QListWidgetItem(f"📄 {os.path.basename(file)}")
                    item.setData(Qt.UserRole, file)
                    self.files_list.addItem(item)
                elif os.path.isdir(file):
                    item = QListWidgetItem(f"📁 {os.path.basename(file)}")
                    item.setData(Qt.UserRole, file)
                    self.files_list.addItem(item)
        self.update_send_button()

    def clear_files(self):
        self.files_list.clear()
        self.update_send_button()

    def update_send_button(self):
        has_files = self.files_list.count() > 0
        has_device = len(self.devices_list.selectedItems()) > 0
        self.send_btn.setEnabled(has_files and has_device)
        selected_count = len(self.devices_list.selectedItems())
        if selected_count > 1:
            self.send_btn.setText(f"📤 {selected_count} Cihaza Gönder")
        else:
            self.send_btn.setText("📤 Gönder")

    def on_device_found(self, device):
        device_id = device['ip']
        self.devices[device_id] = device
        print(f"Device found in UI: {device}")

    def on_device_lost(self, device_ip):
        if device_ip in self.devices:
            del self.devices[device_ip]
            self.update_device_list()

    def update_device_list(self):
        selected_ips = []
        selected_items = self.devices_list.selectedItems()
        for item in selected_items:
            selected_ips.append(item.data(Qt.UserRole))

        self.devices_list.clear()
        for device_id, device in self.devices.items():
            icon = self.get_device_icon(device['name'])
            item = QListWidgetItem(f"{icon} {device['name']}\n    {device['ip']}")
            item.setData(Qt.UserRole, device_id)
            from PyQt5.QtCore import QSize
            item.setSizeHint(QSize(0, 50))
            self.devices_list.addItem(item)
            if device_id in selected_ips:
                item.setSelected(True)

        if len(self.devices) == 0:
            self.status_bar.setText("Cihaz bulunamadı")
        else:
            self.status_bar.setText(f"{len(self.devices)} cihaz bulundu")

    def send_clipboard(self):
        selected = self.devices_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Hata', 'Lütfen önce bir cihaz seçin!')
            return

        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_path = temp_file.name
                temp_file.close()
                if image.save(temp_path, 'PNG'):
                    target_devices = []
                    for item in selected:
                        device_id = item.data(Qt.UserRole)
                        device = self.devices[device_id]
                        target_devices.append((device['name'], device['ip']))
                    self.status_bar.setText('Pano resmi gönderiliyor...')

                    def send_clipboard_image():
                        success_count = 0
                        for device_name, device_ip in target_devices:
                            if self.network.send_file(
                                    temp_path, device_ip, is_clipboard_image=True):
                                success_count += 1
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass
                        QTimer.singleShot(
                            0,
                            lambda: self._clipboard_send_complete(
                                success_count, len(target_devices)))

                    threading.Thread(
                        target=send_clipboard_image, daemon=True).start()
                    return

        if mime_data.hasText():
            text = clipboard.text().strip()
            if text:
                target_devices = []
                for item in selected:
                    device_id = item.data(Qt.UserRole)
                    device = self.devices[device_id]
                    target_devices.append((device['name'], device['ip']))
                self.status_bar.setText('Pano içeriği gönderiliyor...')
                threading.Thread(
                    target=self._send_text_thread,
                    args=(text, target_devices), daemon=True).start()
                return

        QMessageBox.warning(self, 'Hata', 'Panoda metin veya resim bulunamadı!')

    def _clipboard_send_complete(self, success, total):
        if success == total:
            self.status_bar.setText('✅ Pano içeriği başarıyla gönderildi!')
        else:
            self.status_bar.setText(f'⚠️ {success}/{total} cihaza gönderildi')
        QTimer.singleShot(3000, lambda: self.status_bar.setText(''))

    def open_screenshot_dialog(self):
        selected = self.devices_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, 'Hata', 'Lütfen önce bir cihaz seçin!')
            return
        dialog = CountdownDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            QTimer.singleShot(100, self._capture_screen)

    def _capture_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            pixmap = screen.grabWindow(QApplication.desktop().winId())
            if not pixmap.isNull():
                self.send_screenshot(pixmap)

    def send_screenshot(self, pixmap):
        if pixmap.isNull():
            return
        selected = self.devices_list.selectedItems()
        if not selected:
            return
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_path = temp_file.name
        temp_file.close()
        if pixmap.save(temp_path, 'PNG'):
            target_devices = []
            for item in selected:
                device_id = item.data(Qt.UserRole)
                device = self.devices[device_id]
                target_devices.append((device['name'], device['ip']))
            self.status_bar.setText('Ekran görüntüsü gönderiliyor...')

            def send_screenshot_image():
                success_count = 0
                for device_name, device_ip in target_devices:
                    if self.network.send_file(
                            temp_path, device_ip, is_clipboard_image=True):
                        success_count += 1

        if not selected:
            return
        target_devices = []
        for item in selected:
            device_id = item.data(Qt.UserRole)
            device = self.devices[device_id]
            target_devices.append((device['name'], device['ip']))
        self.status_bar.setText('Metin gönderiliyor...')
        threading.Thread(
            target=self._send_text_thread,
            args=(text, target_devices), daemon=True).start()

    def _send_text_thread(self, text, target_devices):
        success_count = 0
        for device_name, device_ip in target_devices:
            if self.network.send_text(text, device_ip):
                success_count += 1
        QTimer.singleShot(
            0,
            lambda: self._text_send_complete(success_count, len(target_devices)))

    def _text_send_complete(self, success, total):
        if success == total:
            self.status_bar.setText('✅ Metin başarıyla gönderildi!')
        else:
            self.status_bar.setText(f'⚠️ {success}/{total} cihaza gönderildi')
        QTimer.singleShot(3000, lambda: self.status_bar.setText(''))


    def send_files(self):
        selected = self.devices_list.selectedItems()
        if not selected or self.files_list.count() == 0:
            return
        files = []
        for i in range(self.files_list.count()):
            files.append(self.files_list.item(i).data(Qt.UserRole))
        target_devices = []
        for item in selected:
            device_id = item.data(Qt.UserRole)
            device = self.devices[device_id]
            target_devices.append((device['name'], device['ip']))
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.transfer_info_label.setVisible(True)
        if len(target_devices) > 1:
            device_names = ', '.join([d[0] for d in target_devices])
            self.status_bar.setText(
                f'{len(target_devices)} cihaza gönderiliyor: {device_names}')
        else:
            self.status_bar.setText(
                f'{target_devices[0][0]} cihazına gönderiliyor...')
        self.send_btn.setEnabled(False)
        threading.Thread(
            target=self._send_files_multi_thread,
            args=(files, target_devices), daemon=True).start()

    def _send_files_multi_thread(self, files, target_devices):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        total_transfers = len(files) * len(target_devices)
        completed_transfers = 0
        success_count = 0

        def send_to_device(device_name, device_ip, filepath):
            return self.network.send_file(filepath, device_ip)

        with ThreadPoolExecutor(max_workers=min(len(target_devices), 4)) as executor:
            futures = []
            for device_name, device_ip in target_devices:
                for filepath in files:
                    future = executor.submit(
                        send_to_device, device_name, device_ip, filepath)
                    futures.append(future)
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
                completed_transfers += 1
                progress = int((completed_transfers / total_transfers) * 100)
                QTimer.singleShot(
                    0, lambda p=progress: self.progress_bar.setValue(p))

        QTimer.singleShot(
            0, lambda: self._send_complete(success_count, total_transfers))

    def _send_complete(self, success, total):
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.transfer_info_label.setVisible(False)
        self.clear_files()
        if success == total:
            self.status_bar.setText(f'✅ {success} transfer başarıyla tamamlandı!')
            self.play_sound()
        else:
            self.status_bar.setText(f'⚠️ {success}/{total} transfer tamamlandı')
        self.send_btn.setEnabled(True)
        self.send_btn.setText("📤 Gönder")
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_file_received(self, filename, sender):
        self.tabs.setCurrentIndex(1)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.transfer_info_label.setVisible(False)
        if self.current_dialog:
            try:
                if hasattr(self.current_dialog, 'status_label'):
                    self.current_dialog.status_label.setText("✅ Transfer tamamlandı!")
                if hasattr(self.current_dialog, 'progress'):
                    self.current_dialog.progress.setValue(100)
                if isinstance(self.current_dialog, TransferDialog):
                    self.current_dialog.accept()
                    self.current_dialog.close()
                    self.current_dialog.deleteLater()
                    self.current_dialog = None
            except Exception as e:
                print(f"[ERROR] Error closing dialog: {e}")
        filepath = os.path.join(self.network.download_folder, filename)
        is_folder = os.path.isdir(filepath)
        icon = "📁" if is_folder else "✅"
        ftype = "folder" if is_folder else "file"
        item = QListWidgetItem(f"{icon} {filename}\n    {sender}")
        item.setData(Qt.UserRole, {"type": ftype, "filename": filename, "sender": sender, "path": filepath})
        self.history_list.insertItem(0, item)
        self._save_history()
        self.status_bar.setText(f'✅ {sender} cihazından dosya alındı!')
        self.show_notification('ULAK - Dosya Alındı',
                               f'{filename}\n{sender} cihazından alındı')
        self.play_sound()
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_text_received(self, text, sender):
        self.tabs.setCurrentIndex(1)
        if self.settings.value('auto_copy_clipboard', True, type=bool):
            QApplication.clipboard().setText(text)
        dialog = TextMessageDialog(text, sender, self)
        dialog.exec_()
        item = QListWidgetItem(
            f"💬 {text[:50]}{'...' if len(text) > 50 else ''}\n    {sender}")
        item.setData(Qt.UserRole, {"type": "text", "text": text, "sender": sender})
        self.history_list.insertItem(0, item)
        self._save_history()
        self.show_notification('ULAK - Metin Mesajı', f'{sender}: {text[:100]}')
        self.play_sound()

    def on_clipboard_image_received(self, image_path, sender):
        self.tabs.setCurrentIndex(1)
        if self.settings.value('auto_copy_clipboard', True, type=bool):
            try:
                image = QImage(image_path)
                if not image.isNull():
                    QApplication.clipboard().setImage(image)
            except Exception as e:
                print(f"[ERROR] Failed to copy image to clipboard: {e}")
        item = QListWidgetItem(f"🖼️ Pano Resmi\n    {sender}")
        item.setData(Qt.UserRole, {"type": "image", "path": image_path, "sender": sender})
        self.history_list.insertItem(0, item)
        self._save_history()
        self.show_notification('ULAK - Pano Resmi', f'{sender} bir resim gönderdi')
        self.play_sound()

    def on_transfer_request(self, file_info, callback):
        self.pending_transfers.append({'info': file_info, 'callback': callback})
        
        if self.batch_timer:
            self.batch_timer.stop()
        
        self.batch_timer = QTimer()
        self.batch_timer.setSingleShot(True)
        self.batch_timer.timeout.connect(self._show_batch_dialog)
        self.batch_timer.start(500)

         self.pending_transfers = []

    def _cleanup_dialog(self):
        if self.current_dialog and not self.current_dialog.isVisible():
            self.current_dialog = None

    def on_transfer_rejected(self, filename, reason):
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.transfer_info_label.setVisible(False)
        if reason == 'Decryption failed':
            QMessageBox.critical(
                self, 'Şifre Hatası',
                f'❌ {filename} gönderilemedi!\n\n'
                f'⚠️ Alıcı şifreyi çözemedi.\n\n'
                f'Sebep: Şifreleme parolaları eşleşmiyor.\n\n'
                f'Her iki cihazda da aynı şifreleme parolasını kullandığınızdan '
                f'emin olun.')
            self.status_bar.setText(f'❌ Şifre hatası: {filename}')
        else:
            QMessageBox.warning(
                self, 'Transfer Reddedildi',
                f'{filename} alıcı tarafından reddedildi.')
            self.status_bar.setText(f'❌ Transfer reddedildi: {filename}')
        self.send_btn.setEnabled(True)
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_decryption_failed(self, filename, sender):
        if self.current_dialog:
            try:
                self.current_dialog.close()
                self.current_dialog.deleteLater()
            except Exception:
                pass
            self.current_dialog = None
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.transfer_info_label.setVisible(False)
        QMessageBox.critical(
            self, 'Şifre Çözme Hatası',
            f'❌ {filename} dosyası şifresi çözülemedi!\n\n'
            f'Gönderen: {sender}\n\n'
            f'⚠️ Sebep: Şifreleme parolaları eşleşmiyor.\n\n'
            f'Her iki cihazda da aynı şifreleme parolasını kullandığınızdan '
            f'emin olun.')
        self.status_bar.setText(f'❌ Şifre hatası: {filename}')
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_progress_updated(self, progress):
        self.progress_bar.setValue(progress)
        if self.current_dialog and hasattr(self.current_dialog, 'progress'):
            self.current_dialog.progress.setValue(progress)
            if progress >= 100:
                QTimer.singleShot(500, self._auto_close_dialog)

    def _auto_close_dialog(self):
        if self.current_dialog:
            try:
                self.current_dialog.close()
                self.current_dialog.deleteLater()
            except Exception:
                pass
            self.current_dialog = None

    def on_transfer_speed(self, speed, transferred, total):
        def fmt_speed(s):
            if s < 1024:
                return f"{s:.1f} B/s"
            elif s < 1024 * 1024:
                return f"{s/1024:.1f} KB/s"
            else:
                return f"{s/(1024*1024):.2f} MB/s"

        def fmt_size(v):
            if v < 1024:
                return f"{v} B"
            elif v < 1024 * 1024:
                return f"{v/1024:.1f} KB"
            elif v < 1024 * 1024 * 1024:
                return f"{v/(1024*1024):.1f} MB"
            else:
                return f"{v/(1024*1024*1024):.2f} GB"

        speed_str = fmt_speed(speed)
        trans_str = fmt_size(transferred)
        total_str = fmt_size(total)
        remaining = total - transferred
        eta_seconds = int(remaining / speed) if speed > 0 else 0
        if eta_seconds < 60:
            eta_str = f"{eta_seconds}s"
        elif eta_seconds < 3600:
            eta_str = f"{eta_seconds//60}m {eta_seconds%60}s"
        else:
            eta_str = f"{eta_seconds//3600}h {(eta_seconds%3600)//60}m"

        info_text = (f"⚡ {speed_str}  |  {trans_str} / {total_str}"
                     f"  |  ⏱️ Kalan: {eta_str}")
        self.transfer_info_label.setText(info_text)
        self.progress_bar.setFormat(f"%p% - {speed_str}")
        if self.current_dialog and hasattr(self.current_dialog, 'status_label'):
            self.current_dialog.status_label.setText(
                f"📥 {speed_str} - {trans_str} / {total_str}")

    def open_downloads(self):
        download_folder = self.network.download_folder
        os.makedirs(download_folder, exist_ok=True)
        try:
            import subprocess
            for cmd in ['xdg-open', 'nautilus', 'dolphin', 'thunar', 'pcmanfm']:
                try:
                    subprocess.Popen([cmd, download_folder])
                    break
                except FileNotFoundError:
                    continue
        except Exception as e:
            print(f"[ERROR] Failed to open downloads folder: {e}")
            QMessageBox.information(
                self, 'İndirilenler',
                f'İndirilenler klasörü:\n{download_folder}')

    def browse_download_folder(self):
        current_path = (self.download_path_input.text()
                        or os.path.join(os.path.expanduser('~'), 'Downloads'))
        folder = QFileDialog.getExistingDirectory(
            self, 'İndirme Klasörü Seç', current_path)
        if folder:
            self.download_path_input.setText(folder)
            self.network.download_folder = folder

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈")
            self.show_password_btn.setToolTip("Parolayı gizle")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁")
            self.show_password_btn.setToolTip("Parolayı göster")

    def on_encryption_changed(self):
        is_checked = self.encryption_checkbox.isChecked()
        self.network.use_encryption = is_checked
        self.encryption_info_label.setVisible(is_checked)


        self._load_history()

        saved_download_path = self.settings.value('download_folder', '')
        if saved_download_path and os.path.exists(saved_download_path):
            self.network.download_folder = saved_download_path
            self.download_path_input.setText(saved_download_path)
        else:
            default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            self.network.download_folder = default_path
            self.download_path_input.setText(default_path)

    def save_settings(self):
        new_name = self.name_input.text().strip()
        if new_name:
            self.network.device_name = new_name
            self.settings.setValue('device_name', new_name)
            self.settings.sync()
        else:
            QMessageBox.warning(self, 'Hata', 'Cihaz adı boş olamaz!')
            return

        try:
            new_port = int(self.port_input.text())
            if 1024 <= new_port <= 65535:
                self.network.port = new_port
                self.settings.setValue('port', new_port)
                self.port_label.setText(f"🔌 Port: {new_port}")
            else:
                QMessageBox.warning(
                    self, 'Hata', 'Port 1024-65535 arasında olmalıdır!')
                return
        except ValueError:
            QMessageBox.warning(self, 'Hata', 'Geçerli bir port numarası girin!')
            return

        try:
            new_broadcast_port = int(self.broadcast_port_input.text())
            if 1024 <= new_broadcast_port <= 65535:
                self.network.broadcast_port = new_broadcast_port
                self.settings.setValue('broadcast_port', new_broadcast_port)
            else:
                QMessageBox.warning(
                    self, 'Hata', 'Broadcast port 1024-65535 arasında olmalıdır!')
                return
        except ValueError:
            QMessageBox.warning(
                self, 'Hata', 'Geçerli bir broadcast port numarası girin!')
            return

        use_encryption = self.encryption_checkbox.isChecked()
        self.network.use_encryption = use_encryption
        self.settings.setValue('use_encryption', use_encryption)
        self.encryption_info_label.setVisible(use_encryption)

        password = self.password_input.text().strip()
        if password:
            self.settings.setValue('encryption_password', password)
            self.network.encryption_key = hashlib.sha256(
                password.encode()).digest()
        else:
            self.settings.setValue('encryption_password', '')
            self.network.encryption_key = hashlib.sha256(
                b'ulak_default_key').digest()
        self.settings.sync()

        self.settings.setValue(
            'use_notifications', self.notification_checkbox.isChecked())
        self.settings.setValue('use_sound', self.sound_checkbox.isChecked())
        self.settings.setValue('use_tray', self.tray_checkbox.isChecked())
        self.settings.setValue(
            'auto_copy_clipboard',
            self.auto_copy_clipboard_checkbox.isChecked())

        download_path = self.download_path_input.text().strip()
        if download_path and os.path.exists(download_path):
            self.network.download_folder = download_path
            self.settings.setValue('download_folder', download_path)

        self.settings.sync()
        self.status_bar.setText(
            '✅ Ayarlar kaydedildi - '
            'Değişikliklerin tam etkili olması için uygulamayı yeniden başlatın')
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def closeEvent(self, event):
        if self.tray_checkbox.isChecked() and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                'ULAK', 'Uygulama arka planda çalışmaya devam ediyor',
                QSystemTrayIcon.Information, 2000)
        else:
            self.network.stop_discovery()
            self.web_server.stop()
            event.accept()

    def _save_history(self):
        import json as _j
        entries = []
        for i in range(self.history_list.count()):
            it = self.history_list.item(i)
            d = it.data(Qt.UserRole) or {}
            entries.append({'text': it.text(), 'data': d})
        self.settings.setValue('receive_history', _j.dumps(entries, ensure_ascii=False))
        self.settings.sync()

    def _load_history(self):
        import json as _j
        raw = self.settings.value('receive_history', '[]')
        try:
            if isinstance(raw, list):
                for text in raw:
                    self.history_list.addItem(QListWidgetItem(text))
                return
            entries = _j.loads(raw)
            for entry in entries:
                it = QListWidgetItem(entry.get('text', ''))
                it.setData(Qt.UserRole, entry.get('data', {}))
                self.history_list.addItem(it)
        except Exception:
            pass

    def clear_history(self):
        self.history_list.clear()
        self.settings.remove('receive_history')
        self.settings.sync()

    def on_history_double_click(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return
        t = data.get('type', '')
        if t == 'text':
            self._show_text_detail(data.get('text', ''), data.get('sender', ''))
        elif t == 'image':
            self._show_image_detail(data.get('path', ''), data.get('sender', ''))
        elif t in ('file', 'folder'):
            self._show_file_detail(data.get('filename', ''), data.get('path', ''), data.get('sender', ''), t == 'folder')

    def _show_text_detail(self, text, sender):
        dialog = TextMessageDialog(text, sender, self)
        dialog.exec_()

    def _show_image_detail(self, image_path, sender):
        from datetime import datetime
        dialog = QDialog(self)
        dialog.setWindowTitle("🖼️ Resim / Ekran Görüntüsü")
        dialog.setModal(True)
        dialog.setMinimumWidth(560)
        dialog.setStyleSheet(DARK_THEME)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        title = QLabel(f"🖼️ Gönderen: {sender}")
        title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)

        exists = os.path.exists(image_path)
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setMinimumHeight(300)
        if exists:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                img_label.setPixmap(pixmap.scaled(520, 340, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img_label.setText("Resim yüklenemedi")
                img_label.setStyleSheet("color: #ff2e97;")
        else:
            img_label.setText("❌ Dosya artık mevcut değil")
            img_label.setStyleSheet("color: #ff2e97; font-size: 14px;")
        layout.addWidget(img_label)

        if exists:
            info_frame = QFrame()
            info_frame.setStyleSheet("background-color: #141b40; border-radius: 8px; padding: 10px; border: 1px solid #2d3462;")
            info_layout = QVBoxLayout(info_frame)
            size = os.path.getsize(image_path)
            info_layout.addWidget(QLabel(f"📦 Boyut: {self.format_size(size)}"))
            info_layout.addWidget(QLabel(f"📁 Konum: {image_path}"))
            layout.addWidget(info_frame)

        btn_layout = QHBoxLayout()
        if exists:
            copy_btn = QPushButton("📋 Resmi Panoya Kopyala")
            copy_btn.setMinimumHeight(38)
            def do_copy_img():
                img = QImage(image_path)
                if not img.isNull():
                    QApplication.clipboard().setImage(img)
                    copy_btn.setText("✅ Kopyalandı!")
                    def restore():
                        try:
                            copy_btn.setText("📋 Resmi Panoya Kopyala")
                        except RuntimeError:
                            pass
                    QTimer.singleShot(2000, restore)
            copy_btn.clicked.connect(do_copy_img)
            btn_layout.addWidget(copy_btn)

            open_btn = QPushButton("🔍 Tam Ekran Aç")
            open_btn.setObjectName("secondaryBtn")
            open_btn.setMinimumHeight(38)
            open_btn.clicked.connect(lambda: self._open_file(image_path))
            btn_layout.addWidget(open_btn)

        close_btn = QPushButton("✖ Kapat")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setMinimumHeight(38)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        dialog.exec_()

    def _show_file_detail(self, filename, filepath, sender, is_folder=False):
        dialog = QDialog(self)
        icon = "📁" if is_folder else "📄"
        dialog.setWindowTitle(f"{icon} {'Klasör' if is_folder else 'Dosya'} Bilgisi")
        dialog.setModal(True)
        dialog.setMinimumWidth(460)
        dialog.setStyleSheet(DARK_THEME)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        title = QLabel(f"{icon} {filename}")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        title.setWordWrap(True)
        layout.addWidget(title)

        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #141b40; border-radius: 10px; padding: 14px; border: 1px solid #2d3462;")
        info_layout = QVBoxLayout(info_frame)

        def lbl(text, color="#e8eaf6"):
            l = QLabel(text)
            l.setStyleSheet(f"color: {color}; padding: 2px 0;")
            l.setWordWrap(True)
            return l

        info_layout.addWidget(lbl(f"👤 Gönderen: {sender}"))
        exists = os.path.exists(filepath)
        info_layout.addWidget(lbl("✅ Mevcut" if exists else "❌ Dosya artık mevcut değil",
                                  "#39ff14" if exists else "#ff2e97"))
        if exists:
            if is_folder:
                fc = sum(len(files) for _, _, files in os.walk(filepath))
                dc = sum(len(dirs) for _, dirs, _ in os.walk(filepath))
                info_layout.addWidget(lbl(f"📊 İçerik: {fc} dosya, {dc} klasör"))
            else:
                info_layout.addWidget(lbl(f"📦 Boyut: {self.format_size(os.path.getsize(filepath))}"))
                ext = os.path.splitext(filename)[1]
                info_layout.addWidget(lbl(f"🔖 Tür: {ext if ext else 'Bilinmiyor'}"))
        info_layout.addWidget(lbl(f"📁 Konum: {filepath}", "#8b949e"))
        layout.addWidget(info_frame)

        # Resim ise önizleme göster
        ext_lower = os.path.splitext(filename)[1].lower()
        if exists and not is_folder and ext_lower in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'):
            prev_label = QLabel()
            prev_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                prev_label.setPixmap(pixmap.scaled(420, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                layout.addWidget(prev_label)

        btn_layout = QHBoxLayout()
        if exists:
            open_btn = QPushButton(f"{'📂 Klasörü Aç' if is_folder else '📂 Dosyayı Aç'}")
            open_btn.setMinimumHeight(38)
            open_btn.clicked.connect(lambda: self._open_file(filepath))
            btn_layout.addWidget(open_btn)

            folder_btn = QPushButton("📁 Klasörde Göster")
            folder_btn.setObjectName("secondaryBtn")
            folder_btn.setMinimumHeight(38)
            folder_btn.clicked.connect(lambda: self._open_file(os.path.dirname(filepath)))
            btn_layout.addWidget(folder_btn)

            if not is_folder:
                copy_path_btn = QPushButton("📋 Yolu Kopyala")
                copy_path_btn.setObjectName("secondaryBtn")
                copy_path_btn.setMinimumHeight(38)
                def do_copy_path():
                    QApplication.clipboard().setText(filepath)
                    copy_path_btn.setText("✅ Kopyalandı!")
                    def restore():
                        try:
                            copy_path_btn.setText("📋 Yolu Kopyala")
                        except RuntimeError:
                            pass
                    QTimer.singleShot(2000, restore)
                copy_path_btn.clicked.connect(do_copy_path)
                btn_layout.addWidget(copy_path_btn)

        close_btn = QPushButton("✖ Kapat")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setMinimumHeight(38)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        dialog.exec_()

    def _open_file(self, path):
        try:
            import subprocess
            subprocess.Popen(['xdg-open', path])
        except Exception as e:
            print(f"[ERROR] Cannot open: {e}")

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)


# ============================================================================
# MAIN
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = LocalSendApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
