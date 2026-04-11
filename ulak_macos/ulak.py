#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULAK - Yerel Ağ Dosya Paylaşım Uygulaması
macOS Versiyonu - Tek Dosya
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
                          QKeySequence, QPainter, QColor, QImage)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QListWidget, QLabel,
                             QFileDialog, QMessageBox, QProgressBar,
                             QListWidgetItem, QTabWidget, QFrame, QLineEdit,
                             QDialog, QDialogButtonBox, QCheckBox, QScrollArea,
                             QSystemTrayIcon, QMenu, QShortcut, QTextEdit,
                             QAction, QMenuBar)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

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
    except Exception:
        raise ValueError("Şifre çözme hatası - Parolalar eşleşmiyor")


# ============================================================================
# ANNOUNCEMENT MANAGER
# ============================================================================

TARGET_URL = "https://algsoft.net.tr/uygulama-duyurulari/"
ELEMENT_ID = "ulak_macos_web"


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
                display_text = (raw_text.replace('&', '&amp;')
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
body {{ background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%);
    min-height: 100vh; display: flex; justify-content: center;
    align-items: center; font-family: -apple-system, 'SF Pro Display',
    'Helvetica Neue', Arial, sans-serif; padding: 20px; }}
.container {{ background: rgba(44,44,46,0.95); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px; padding: 40px; max-width: 700px; width: 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }}
h1 {{ color: #007AFF; text-align: center; font-size: 1.8em; margin-bottom: 6px;
    font-weight: 700; }}
.sender {{ color: #BF5AF2; text-align: center; font-size: 0.9em; margin-bottom: 24px; }}
.text-box {{ background: rgba(28,28,30,0.8); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 20px; color: #e8eaf6; font-size: 1em;
    line-height: 1.7; max-height: 420px; overflow-y: auto;
    word-break: break-word; white-space: pre-wrap; }}
.copy-btn {{ display: block; width: 100%; padding: 15px;
    background: #007AFF; color: #fff; border: none; border-radius: 12px;
    font-size: 1.1em; font-weight: 600; cursor: pointer; margin-top: 20px;
    transition: opacity 0.2s; }}
.copy-btn:hover {{ opacity: 0.85; }}
.footer {{ text-align: center; color: #636366; font-size: 0.75em; margin-top: 20px; }}
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
                    filesize = (os.path.getsize(filepath)
                                if os.path.exists(filepath) else 0)
                except Exception:
                    filesize = 0
                ext = os.path.splitext(filename)[1].lower()
                if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp',
                           '.bmp', '.svg', '.heic'):
                    icon = '🖼️'
                elif ext in ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'):
                    icon = '🎥'
                elif ext in ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'):
                    icon = '🎵'
                elif ext in ('.pdf',):
                    icon = '📕'
                elif ext in ('.zip', '.rar', '.7z', '.tar', '.gz'):
                    icon = '📦'
                elif ext in ('.doc', '.docx', '.odt', '.pages'):
                    icon = '📝'
                elif ext in ('.xls', '.xlsx', '.ods', '.numbers'):
                    icon = '📊'
                elif ext in ('.ppt', '.pptx', '.odp', '.key'):
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
bod                for unit in ('B', 'KB', 'MB', 'GB'):
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
body {{ background: linear-gradient(135deg, #1c1c1e, #2c2c2e);
    min-height: 100vh; display: flex; justify-content: center;
    align-items: center; font-family: -apple-system, 'Helvetica Neue',
    Arial, sans-serif; color: #e8eaf6; }}
.container {{ background: rgba(44,44,46,0.95);
    border: 1px solid rgba(255,69,58,0.4);
    border-radius: 20px; padding: 40px; max-width: 400px; width: 90%;
    text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }}
h1 {{ color: #FF453A; margin-bottom: 16px; }}
p {{ color: #8e8e93; }}
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

class NetworkManager(QObject):
    device_found = pyqtSignal(dict)
    device_lost = pyqtSignal(str)
    file_received = pyqtSignal(str, str, str)
    text_received = pyqtSignal(str, str)
    clipboard_image_received = pyqtSignal(str, str)
    progress_updated = pyqtSignal(int)
    transfer_speed = pyqtSignal(float, int, int)
    transfer_request = pyqtSignal(dict, object)
    transfer_rejected = pyqtSignal(str, str)
    decryption_failed = pyqtSignal(str, str)
    receive_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.port = 53317
        self.broadcast_port = 53318
        self.device_name = socket.gethostname()
        self.running = False
        self.discovered_devices = {}
        self.last_seen = {}
        self.use_encryption = False
        self.encryption_key = hashlib.sha256(b'ulak_default_key').digest()
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'

    def start_discovery(self):
        self.running = True
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._listen_broadcast, daemon=True).start()
        threading.Thread(target=self._listen_files, daemon=True).start()
        threading.Thread(target=self._cleanup_devices, daemon=True).start()

    def stop_discovery(self):
        self.running = False

    def _broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass

        while self.running:
            try:
                local_ip = self.get_local_ip()
                message = json.dumps({
                    'type': 'announce',
                    'name': self.device_name,
                    'ip': local_ip
                }).encode('utf-8')
                sock.sendto(message, ('<broadcast>', self.broadcast_port))
                sock.sendto(message, ('255.255.255.255', self.broadcast_port))
                if local_ip != '127.0.0.1':
                    parts = local_ip.split('.')
                    broadcast_addr = f"{parts[0]}.{parts[1]}.{parts[2]}.255"
                    try:
                        sock.sendto(message, (broadcast_addr, self.broadcast_port))
                    except Exception:
                        pass
            except Exception as e:
                print(f"Broadcast error: {e}")
            time.sleep(2)
        sock.close()
                    if sender_ip != my_ip and sender_ip != '127.0.0.1':
                        device_id = sender_ip
                        self.last_seen[device_id] = time.time()

                        if device_id not in self.discovered_devices:
                            self.discovered_devices[device_id] = msg
                            self.device_found.emit(
                                {'name': msg['name'], 'ip': sender_ip})
                        else:
                            self.discovered_devices[device_id] = msg
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

        while self.running:
            try:
                conn, addr = sock.accept()
                threading.Thread(
                    target=self._handle_file_transfer,
                    args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Accept error: {e}")
        sock.close()

    def _handle_file_transfer(self, conn):
        file_info = {}
        try:
            conn.settimeout(30)

            header_size_data = conn.recv(4)
            if len(header_size_data) < 4:
                return

            header_size = int.from_bytes(header_size_data, 'big')

            header_data = b''
            while len(header_data) < header_size:
                chunk = conn.recv(header_size - len(header_data))
                if not chunk:
                    return
                header_data += chunk

            header = json.loads(header_data.decode('utf-8'))

            if header.get('type') == 'text':
                is_encrypted = header.get('encrypted', False)
                text_content = header.get('content', '')
                sender = header.get('sender', 'Unknown')

                if is_encrypted:
                    try:
                        import base64
                        encrypted_bytes = base64.b64decode(text_content)
                        decrypted_bytes = decrypt_data(
                            encrypted_bytes, self.encryption_key)
                        text_content = decrypted_bytes.decode('utf-8')
                    except Exception as e:
                        print(f"[ERROR] Text decryption failed: {e}")
                        try:
                            conn.sendall(b'DECRYPT_FAIL')
                        except Exception:
                            pass
                        self.decryption_failed.emit('Metin Mesajı', sender)
                        conn.close()
                        return

                self.text_received.emit(text_content, sender)
                conn.close()
                return

            file_info = {
                'filename': header.get('filename') or header.get('name', 'dosya'),
                'filesize': header.get('filesize') or header.get('size', 0),
                'sender': header.get('sender', 'Unknown'),
                'is_folder': header.get('is_folder', False),
                'file_count': header.get('file_count', 0),
                'folder_count': header.get('folder_count', 0),
                'encrypted': header.get('encrypted', False),
                'is_clipboard_image': header.get('is_clipboard_image', False)
            }

            transfer_event = threading.Event()
            transfer_result = {'accepted': False}

            def callback(accepted):
                transfer_result['accepted'] = accepted
                transfer_event.set()

            self.transfer_request.emit(file_info, callback)

            if not transfer_event.wait(timeout=60):
                try:
                    conn.sendall(b'TIMEOUT__')
                except Exception:
                    pass
                conn.close()
                return

            if not transfer_result['accepted']:
                try:
                    conn.sendall(b'REJECTED')
                except Exception as e:
                    print(f"[ERROR] Failed to send rejection: {e}")
                conn.close()
                return

            try:
                conn.sendall(b'ACCEPTED')
            except Exception as e:
                print(f"[ERROR] Failed to send acceptance: {e}")
                conn.close()
                return

            # Veri transferi için daha uzun timeout
            conn.settimeout(60)

            downloads = self.download_folder
            os.makedirs(downloads, exist_ok=True)

            filename = file_info['filename']
            save_path = os.path.join(downloads, filename)

            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(downloads, f"{base}_{counter}{ext}")
                counter += 1

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
                            chunk = decrypt_data(
                                encrypted_chunk, self.encryption_key)
                        except ValueError as e:
                            print(f"[ERROR] Decryption failed: {e}")
                            try:
                                conn.sendall(b'DECRYPT_FAIL')
                            except Exception:
                                pass
                            self.decryption_failed.emit(
                                file_info['filename'], file_info['sender'])
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

            if received == filesize:
                final_name = filename
                is_clipboard_image = file_info.get('is_clipboard_image', False)

                final_path = save_path
                if file_info['is_folder']:
                    extract_path = (save_path[:-4]
                                    if save_path.endswith('.zip')
                                    else save_path)
                    try:
                        with zipfile.ZipFile(save_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_path)
                        os.remove(save_path)
                        final_name = os.path.basename(extract_path)
                        final_path = extract_path
                    except Exception as e:
                        print(f"[ERROR] Extract error: {e}")
                elif is_clipboard_image:
                    self.clipboard_image_received.emit(
                        save_path, file_info['sender'])
                    return

                self.file_received.emit(final_name, file_info['sender'], final_path)
            else:
                print(f"[ERROR] Incomplete transfer: {received}/{filesize}")
                if os.path.exists(save_path):
                    os.remove(save_path)
                self.receive_failed.emit(file_info.get('sender', ''))

        except Exception as e:
            print(f"[ERROR] Error receiving file: {e}")
            try:
                self.receive_failed.emit(file_info.get('sender', ''))
            except Exception:
                pass
        finally:
            conn.close()

    def send_file(self, filepath, target_ip, is_clipboard_image=False):
        temp_file = None
        try:
            is_folder = os.path.isdir(filepath)

            if is_folder:
                file_count = sum(
                    [len(files) for _, _, files in os.walk(filepath)])
                folder_count = sum(
                    [len(dirs) for _, dirs, _ in os.walk(filepath)])

                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.zip').name
                with zipfile.ZipFile(
                        temp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(filepath):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                arcname = os.path.relpath(
                                    file_path, os.path.dirname(filepath))
                                zipf.write(file_path, arcname)
                            except Exception as e:
                                print(f"[ERROR] Skipping file {file_path}: {e}")

                actual_file = temp_file
                filename = os.path.basename(filepath) + '.zip'
            else:
                actual_file = filepath
                filename = os.path.basename(filepath)
                file_count = 0
                folder_count = 0

            filesize = os.path.getsize(actual_file)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((target_ip, self.port))

            header = json.dumps({
                'type': 'file',
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

            sock.settimeout(65)
            try:
                response = sock.recv(8)
                if response == b'REJECTED':
                    sock.close()
                    if temp_file and os.path.exists(temp_file):
                        os.remove(temp_file)
                    self.transfer_rejected.emit(
                        os.path.basename(filepath), 'Receiver rejected')
                    return False
                elif response == b'TIMEOUT__':
                    sock.close()
                    if temp_file and os.path.exists(temp_file):
                        os.remove(temp_file)
                    return False
            except socket.timeout:
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
                            encrypted_chunk = encrypt_data(
                                chunk, self.encryption_key)
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
                            sock.close()
                            if temp_file and os.path.exists(temp_file):
                                os.remove(temp_file)
                            self.transfer_rejected.emit(
                                os.path.basename(filepath), 'Decryption failed')
             
            return sent == filesize

        except Exception as e:
            print(f"[ERROR] Error sending file: {e}")
            import traceback
            traceback.print_exc()
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            return False

    def send_text(self, text, target_ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target_ip, self.port))

            content = text
            if self.use_encryption:
                try:
                    import base64
                    encrypted_bytes = encrypt_data(
                        text.encode('utf-8'), self.encryption_key)
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
                        sock.close()
                        self.transfer_rejected.emit(
                            'Metin Mesajı', 'Decryption failed')
                        return False
                except socket.timeout:
                    pass

            sock.close()
            return True

        except Exception as e:
            print(f"[ERROR] Error sending text: {e}")
            return False


# ============================================================================
# STYLES — Modern macOS Dark Theme
# ============================================================================

MACOS_DARK_THEME = """
QMainWindow {
    background-color: #1c1c1e;
}

QWidget {
    background-color: #1c1c1e;
    color: #ffffff;
    font-size: 13px;
}

QPushButton {
    background-color: #0a84ff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #409cff;
}

QPushButton:pressed {
    background-color: #0060df;
}

QPushButton:disabled {
    background-color: #3a3a3c;
    color: #636366;
}

QPushButton#secondaryBtn {
    background-color: #2c2c2e;
    color: #0a84ff;
    border: 1px solid rgba(255,255,255,0.12);
}

QPushButton#secondaryBtn:hover {
    background-color: #3a3a3c;
    color: #409cff;
}

QPushButton#linkBtn {
    background-color: #0a84ff;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#linkBtn:hover {
    background-color: #409cff;
}

QPushButton#linkBtn:pressed {
    background-color: #0060df;
}

QListWidget {
    background-color: #2c2c2e;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 10px;
    padding: 6px;
    outline: none;
}

QListWidget::item {
    background-color: #3a3a3c;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 3px;
    color: #ffffff;
    border: 1px solid transparent;
}

QListWidget::item:hover {
    background-color: #48484a;
    border: 1px solid rgba(255,255,255,0.12);
}

QListWidget::item:selected {
    background-color: rgba(10, 132, 255, 0.25);
    color: #ffffff;
    border: 1px solid rgba(10, 132, 255, 0.6);
}

QLabel {
    color: #ffffff;
    background: transparent;
}

QProgressBar {
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 6px;
    text-align: center;
    background-color: #2c2c2e;
    color: #ffffff;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #0a84ff;
    border-radius: 5px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.25);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255,255,255,0.40);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: rgba(255,255,255,0.25);
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTabWidget {
    border: none;
    background-color: #1c1c1e;
}

QTabWidget::pane {
    border: 1px solid rgba(255,255,255,0.10);
    border-top: none;
    background-color: #1c1c1e;
    border-radius: 0px 0px 8px 8px;
}

QTabWidget::tab-bar {
    alignment: left;
}

QTabBar::tab {
    background-color: #2c2c2e;
    color: #8e8e93;
    padding: 10px 20px;
    border: 1px solid rgba(255,255,255,0.08);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 12px;
    min-width: 100px;
    text-align: center;
}

QTabBar::tab:selected {
    background-color: #3a3a3c;
    color: #0a84ff;
    border-color: rgba(10,132,255,0.4);
}

QTabBar::tab:hover:!selected {
    background-color: #333335;
    color: #ebebf5;
}

QLineEdit {
    background-color: #2c2c2e;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    color: #ffffff;
    padding: 8px 12px;
    selection-background-color: rgba(10, 132, 255, 0.4);
}

QLineEdit:focus {
    border: 1px solid #0a84ff;
    background-color: #3a3a3c;
}

QCheckBox {
    color: #ffffff;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid rgba(255,255,255,0.25);
    background: #2c2c2e;
}

QCheckBox::indicator:checked {
    background-color: #0a84ff;
    border-color: #0a84ff;
}

QCheckBox::indicator:hover {
    border-color: #0a84ff;
}

QMessageBox {
    background-color: #2c2c2e;
}

QMessageBox QLabel {
    color: #ffffff;
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
    background-color: #1c1c1e;
}

QMenu {
    background-color: #2c2c2e;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    color: #ffffff;
    padding: 4px;
}

QMenu::item {
    padding: 6px 20px;
    border-radius: 6px;
    margin: 1px 4px;
}

QMenu::item:selected {
    background-color: #0a84ff;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: rgba(255,255,255,0.10);
    margin: 4px 8px;
}

QTextEdit {
    background-color: #2c2c2e;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    color: #ffffff;
    padding: 8px;
    selection-background-color: rgba(10, 132, 255, 0.4);
}

QTextEdit:focus {
    border-color: #0a84ff;
}

QDialog {
    background-color: #2c2c2e;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
    min-height: 30px;
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
        self.setMinimumHeight(90)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed rgba(255,255,255,0.20);
                border-radius: 12px;
                background-color: #2c2c2e;
            }
            QFrame:hover {
                border: 2px dashed #0a84ff;
                background-color: rgba(10,132,255,0.08);
            }
        """)

        layout = QVBoxLayout(self)
        icon = QLabel("📁")
        icon_font = QFont()
        icon_font.setFamily('Apple Color Emoji')
        if not icon_font.exactMatch():
            icon_font.setFamily('Segoe UI Emoji')
        if not icon_font.exactMatch():
            icon_font.setFamily('Noto Color Emoji')
        icon_font.setPointSize(28)
        icon.setFont(icon_font)
        icon.setAlignment(Qt.AlignCenter)

        text = QLabel("Dosya/Klasör sürükleyin\nveya tıklayarak seçin")
        text_font = QFont()
        text_font.setPointSize(10)
        text.setFont(text_font)
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("color: #8e8e93;")

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
        self.setStyleSheet(MACOS_DARK_THEME)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"💬 {sender} bir mesaj gönderdi")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #0a84ff;")
        layout.addWidget(title)

        self.text_display = QTextEdit()
        self.text_display.setPlainText(text)
        self.text_display.setReadOnly(True)
        self.text_display.setMinimumHeight(150)
        layout.addWidget(self.text_display)

        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Kopyala")
        copy_btn.setMinimumHeight(34)
        copy_btn_font = QFont()
        copy_btn.setFont(copy_btn_font)
        copy_btn.clicked.connect(self.copy_text)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton("✅ Tamam")
        close_btn.setMinimumHeight(34)
        close_btn_font = QFont()
        close_btn.setFont(close_btn_font)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def copy_text(self):
        QApplication.clipboard().setText(self.text_display.toPlainText())
        copy_btn = self.sender()
        if copy_btn:
            copy_btn.setText("✅ Kopyalandı")
            import weakref
            ref = weakref.ref(copy_btn)
            QTimer.singleShot(1000, lambda: ref() and ref().setText("📋 Kopyala"))


class AnnouncementCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        self.setObjectName("announcementCard")
        self.setStyleSheet("""
            QFrame#announcementCard {
                background-color: rgba(191,90,242,0.12);
                border: 1px solid rgba(191,90,242,0.35);
                border-radius: 10px;
                margin: 4px 10px 0px 10px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 10, 10)
        layout.setSpacing(5)

        header = QHBoxLayout()
        header.setSpacing(6)

        title_lbl = QLabel("📢 Duyurular")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(
            "color: #bf5af2; background: transparent; border: none;")
        header.addWidget(title_lbl)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setToolTip("Kapat")
        close_btn_font = QFont()
        close_btn.setFont(close_btn_font)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(191,90,242,0.18);
                color: #bf5af2;
                border: 1px solid rgba(191,90,242,0.35);
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(191,90,242,0.40);
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self._on_close)
        header.addWidget(close_btn)
        layout.addLayout(header)

        self._text_lbl = QLabel()
        text_font = QFont()
        text_font.setPointSize(10)
        self._text_lbl.setFont(text_font)
        self._text_lbl.setStyleSheet(
            "color: #ebebf5; background: transparent; border: none;")
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


class TextSendDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Metin Gönder")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setMinimumHeight(280)
        self.setStyleSheet(MACOS_DARK_THEME)
        self.parent_app = parent

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("💬 Metin Mesajı Gönder")
        title.setFont(QFont('Helvetica Neue', 15, QFont.Bold))
        title.setStyleSheet("color: #0a84ff;")
        layout.addWidget(title)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Mesajınızı buraya yazın...")
        self.text_input.setMinimumHeight(140)
        layout.addWidget(self.text_input)

        btn_layout = QHBoxLayout()

        paste_btn = QPushButton("📋 Yapıştır")
        paste_btn.setObjectName("secondaryBtn")
        paste_btn.setMinimumHeight(34)
        paste_btn.clicked.connect(self.paste_text)
        btn_layout.addWidget(paste_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("İptal")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setMinimumHeight(34)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        send_btn = QPushButton("📨 Gönder")
        send_btn.setMinimumHeight(34)
        send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(send_btn)

        layout.addLayout(btn_layout)

    def paste_text(self):
        clipboard_text = QApplication.clipboard().text()
        if clipboard_text:
            self.text_input.setPlainText(clipboard_text)

    def send_message(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, 'Hata', 'Lütfen bir metin girin!')
            return
        if self.parent_app:
            self.parent_app.send_text_from_dialog(text)
        self.accept()


class CountdownDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ekran Görüntüsü")
        self.setModal(True)
        self.setMinimumWidth(280)
        self.setMinimumHeight(180)
        self.setStyleSheet(MACOS_DARK_THEME)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        self.countdown_label = QLabel("3")
        self.countdown_label.setFont(
            QFont('Helvetica Neue', 64, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: #0a84ff;")
        layout.addWidget(self.countdown_label)

        info_label = QLabel("Ekran görüntüsü alınıyor...")
        info_label.setFont(QFont('Helvetica Neue', 12))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #8e8e93;")
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
        self.setMinimumWidth(520)
        self.setMinimumHeight(380)
        self.setStyleSheet(MACOS_DARK_THEME)
        self.callbacks = []
        self.files_info = files_info
        self.checkboxes = []

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        sender = files_info[0]['sender'] if files_info else 'Bilinmeyen'
        title = QLabel(f"📥 {sender} {len(files_info)} dosya gönderiyor")
        title.setFont(QFont('Helvetica Neue', 15, QFont.Bold))
        title.setStyleSheet("color: #0a84ff;")
        layout.addWidget(title)

        total_size = sum(f['filesize'] for f in files_info)
        summary = QLabel(f"Toplam Boyut: {self.format_size(total_size)}")
        summary.setFont(QFont('Helvetica Neue', 11))
        summary.setStyleSheet("color: #8e8e93; padding: 4px;")
        layout.addWidget(summary)

        select_layout = QHBoxLayout()
        files_label = QLabel("Dosya Listesi:")
        files_label.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        select_layout.addWidget(files_label)
        select_layout.addStretch()

        select_all_btn = QPushButton("✅ Tümünü Seç")
        select_all_btn.setObjectName("secondaryBtn")
        select_all_btn.setMaximumWidth(120)
        select_all_btn.clicked.connect(self.select_all)
        select_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Tümünü Kaldır")
        deselect_all_btn.setObjectName("secondaryBtn")
        deselect_all_btn.setMaximumWidth(120)
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_layout.addWidget(deselect_all_btn)

        layout.addLayout(select_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(180)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for idx, file_info in enumerate(files_info):
            file_frame = QFrame()
            file_frame.setStyleSheet(
                "background-color: #2c2c2e; border-radius: 8px; padding: 10px;"
                "border: 1px solid rgba(255,255,255,0.10); margin: 3px;")
            file_layout = QHBoxLayout(file_frame)

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            file_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

            info_layout = QVBoxLayout()
            icon = "📁" if file_info['is_folder'] else "📄"
            name_label = QLabel(f"{icon} {file_info['filename']}")
            name_label.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
            info_layout.addWidget(name_label)

            details_layout = QHBoxLayout()
            size_label = QLabel(f"Boyut: {self.format_size(file_info['filesize'])}")
            size_label.setStyleSheet("color: #8e8e93; font-size: 10px;")
            details_layout.addWidget(size_label)

            if file_info.get('encrypted', False):
                enc_label = QLabel("🔒 Şifreli")
                enc_label.setStyleSheet("color: #30d158; font-size: 10px;")
                details_layout.addWidget(enc_label)

            details_layout.addStretch()
            info_layout.addLayout(details_layout)

            file_layout.addLayout(info_layout)
            scroll_layout.addWidget(file_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.progress = QProgressBar()
        self.progress.setMinimumHeight(20)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel(
            "Almak istediğiniz dosyaları seçin ve onaylayın")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8e8e93; padding: 6px;")
        layout.addWidget(self.status_label)

        buttons = QDialogButtonBox()
        self.accept_btn = buttons.addButton(
            "✅ Seçilenleri Kabul Et", QDialogButtonBox.AcceptRole)
        self.reject_btn = buttons.addButton(
            "❌ Tümünü Reddet", QDialogButtonBox.RejectRole)
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
        for idx, (callback, checkbox) in enumerate(
                zip(self.callbacks, self.checkboxes)):
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
        self.setWindowTitle("Dosya Alımı")
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setStyleSheet(MACOS_DARK_THEME)
        self.callback = None

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"📥 {file_info['sender']} dosya gönderiyor")
        title.setFont(QFont('Helvetica Neue', 15, QFont.Bold))
        title.setStyleSheet("color: #0a84ff;")
        layout.addWidget(title)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #2c2c2e; border-radius: 10px; padding: 14px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        info_layout = QVBoxLayout(info_frame)

        if file_info['is_folder']:
            icon_label = QLabel(f"📁 {file_info['filename']}")
        else:
            icon_label = QLabel(f"📄 {file_info['filename']}")
        icon_label.setFont(QFont('Helvetica Neue', 13, QFont.Bold))
        info_layout.addWidget(icon_label)

        size_label = QLabel(f"Boyut: {self.format_size(file_info['filesize'])}")
        size_label.setStyleSheet("color: #8e8e93;")
        info_layout.addWidget(size_label)

        if file_info.get('encrypted', False):
            enc_label = QLabel("🔒 AES-256 Şifreli Gönderim")
            enc_label.setStyleSheet(
                "color: #30d158; font-weight: bold; padding-top: 4px;")
            info_layout.addWidget(enc_label)

        if file_info['is_folder']:
            content_label = QLabel(
                f"İçerik: {file_info.get('file_count', 0)} dosya, "
                f"{file_info.get('folder_count', 0)} klasör")
            content_label.setStyleSheet("color: #8e8e93;")
            info_layout.addWidget(content_label)

            note_label = QLabel(
                "Not: Tüm klasör içeriği tek seferde alınacaktır")
            note_label.setStyleSheet(
                "color: #ffd60a; font-style: italic; padding-top: 8px;")
            info_layout.addWidget(note_label)

        from datetime import datetime
        time_label = QLabel(
            f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        time_label.setStyleSheet("color: #8e8e93;")
        info_layout.addWidget(time_label)

        layout.addWidget(info_frame)

        self.progress = QProgressBar()
        self.progress.setMinimumHeight(20)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Kabul etmek için onaylayın")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #8e8e93; padding: 6px;")
        layout.addWidget(self.status_label)

        buttons = QDialogButtonBox()
        self.accept_btn = buttons.addButton(
            "✅ Kabul Et", QDialogButtonBox.AcceptRole)
        self.reject_btn = buttons.addButton(
            "❌ Reddet", QDialogButtonBox.RejectRole)
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


        layout.addWidget(desc)

        link_frame = QFrame()
        link_frame.setStyleSheet(
            "background-color: #2c2c2e;"
            "border: 1px solid rgba(10,132,255,0.5);"
            "border-radius: 10px; padding: 14px;")
        link_layout = QVBoxLayout(link_frame)

        self.link_label = QLabel(link)
        self.link_label.setFont(QFont('Helvetica Neue', 13, QFont.Bold))
        self.link_label.setStyleSheet("color: #0a84ff;")
        self.link_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.link_label.setAlignment(Qt.AlignCenter)
        self.link_label.setWordWrap(True)
        link_layout.addWidget(self.link_label)

        layout.addWidget(link_frame)

        info = QLabel(
            "⚠️ Bu pencere açık olduğu sürece link erişilebilir.\n"
            "Pencereyi kapattığınızda link sıfırlanır."
        )
        info.setStyleSheet(
            "color: #ffd60a; font-size: 11px; font-style: italic;")
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Linki Kopyala")
        copy_btn.setMinimumHeight(38)
        copy_btn.clicked.connect(self.copy_link)
        btn_layout.addWidget(copy_btn)

        close_btn = QPushButton("Kapat")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setMinimumHeight(38)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def copy_link(self):
        QApplication.clipboard().setText(self.link_label.text())
        copy_btn = self.sender()
        if copy_btn:
            copy_btn.setText("✅ Kopyalandı!")
            import weakref
            ref = weakref.ref(copy_btn)
            QTimer.singleShot(
                2000, lambda: ref() and ref().setText("📋 Linki Kopyala"))

    def closeEvent(self, event):
        if self.parent_app and hasattr(self.parent_app, 'web_server'):
            self.parent_app.web_server.clear_content()
        super().closeEvent(event)

    def reject(self):
        if self.parent_app and hasattr(self.parent_app, 'web_server'):
            self.parent_app.web_server.clear_content()
        super().reject()


# ============================================================================
# KEYBOARD SHORTCUTS DIALOG
# ============================================================================

class KeyboardShortcutsDialog(QDialog):
    """macOS klavye kısayolları açıklama penceresi."""

    SHORTCUTS = [
        ("Dosya İşlemleri", [
            ("⌘O",    "Dosya Seç"),
            ("⌘⇧O",  "Klasör Seç"),
            ("⌘↩",   "Seçili Dosyaları Gönder"),
            ("⌘L",   "Link Üzerinden Gönder"),
            ("⌘⇧D",  "İndirilenler Klasörünü Aç"),
            ("⌘W",   "Pencereyi Kapat"),
        ]),
        ("İletişim", [
            ("⌘T",   "Metin Mesajı Gönder"),
            ("⌘B",   "Pano İçeriğini Gönder"),
            ("⌘⇧S",  "Ekran Görüntüsü Al ve Gönder"),
        ]),
        ("Sekmeler", [
            ("⌘1",   "↑ Gönder Sekmesi"),
            ("⌘2",   "↓ Alınanlar Sekmesi"),
            ("⌘3",   "⚙ Ayarlar Sekmesi"),
            ("⌘4",   "ⓘ Hakkında Sekmesi"),
        ]),
        ("Uygulama", [
            ("⌘,",   "Tercihler / Ayarlar"),
            ("⌘Q",   "Uygulamadan Çık"),
            ("⌘⇧K",  "Bu Pencereyi Göster"),
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Klavye Kısayolları")
        self.setModal(True)
        self.setMinimumWidth(740)
        self.setStyleSheet(MACOS_DARK_THEME)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(22, 20, 22, 18)

        # ── Başlık ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("⌨️ Klavye Kısayolları")
        title.setFont(QFont('Helvetica Neue', 15, QFont.Bold))
        title.setStyleSheet("color: #0a84ff;")
        header.addWidget(title)
        header.addStretch()
        note = QLabel("⌘ Command   ⇧ Shift   ⌥ Option   ↩ Return")
        note.setFont(QFont('Helvetica Neue', 10))
        note.setStyleSheet("color: #636366; font-style: italic;")
        header.addWidget(note)
        layout.addLayout(header)

        # ── 2 sütunlu ızgara ─────────────────────────────────────────────────
        # Sol: SHORTCUTS[0] + SHORTCUTS[1]   Sağ: SHORTCUTS[2] + SHORTCUTS[3]
        cols = QHBoxLayout()
        cols.setSpacing(12)

        left_col  = QVBoxLayout()
        left_col.setSpacing(8)
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        for col_layout, sections in (
                (left_col,  self.SHORTCUTS[:2]),
                (right_col, self.SHORTCUTS[2:])):

            for section_title, items in sections:
                sec_lbl = QLabel(section_title.upper())
                sec_lbl.setFont(QFont('Helvetica Neue', 9, QFont.Bold))
                sec_lbl.setStyleSheet(
                    "color: #636366; letter-spacing: 1px; padding-top: 2px;")
                col_layout.addWidget(sec_lbl)

                frame = QFrame()
                frame.setStyleSheet(
                    "QFrame { background-color: #2c2c2e; border-radius: 10px;"
                    " border: 1px solid rgba(255,255,255,0.10); }")
                frame_layout = QVBoxLayout(frame)
                frame_layout.setSpacing(0)
                frame_layout.setContentsMargins(0, 2, 0, 2)

                for i, (key, desc) in enumerate(items):
                    row_w = QWidget()
                    row_w.setStyleSheet(
                        "background: transparent; border: none;")
                    row = QHBoxLayout(row_w)
       
                            " border: none; max-height: 1px; }")
                        frame_layout.addWidget(sep)

                col_layout.addWidget(frame)

            col_layout.addStretch()

        cols.addLayout(left_col, 1)
        cols.addLayout(right_col, 1)
        layout.addLayout(cols)

        # ── Kapat butonu ──────────────────────────────────────────────────────
        close_btn = QPushButton("Kapat")
        close_btn.setObjectName("secondaryBtn")
        close_btn.setMinimumHeight(34)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ============================================================================
# RECEIVED ITEM DETAIL DIALOG
# ============================================================================

class ReceivedItemDetailDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet(MACOS_DARK_THEME)
        self._build_ui()

    def _build_ui(self):
        item_type = self.item_data.get('type', 'unknown')
        sender = self.item_data.get('sender', 'Bilinmiyor')
        timestamp = self.item_data.get('timestamp', '')

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        if item_type == 'text':
            self.setWindowTitle("Metin Detayı")
            self.setMinimumHeight(360)

            title = QLabel("💬 Metin Mesajı")
            title.setFont(QFont('Helvetica Neue', 15, QFont.Bold))
            title.setStyleSheet("color: #0a84ff;")
            layout.addWidget(title)

            meta_label = QLabel(f"Gönderen: {sender}   |   {timestamp}")
            meta_label.setStyleSheet("color: #8e8e93; font-size: 11px;")
            layout.addWidget(meta_label)

            self._text_display = QTextEdit()
            self._text_display.setPlainText(self.item_data.get('full_text', ''))
            self._text_display.setReadOnly(True)
            self._text_display.setMinimumHeight(200)
            layout.addWidget(self._text_display)

            btn_layout = QHBoxLayout()
            copy_btn = QPushButton("📋 Kopyala")
            copy_btn.setMinimumHeight(36)
            copy_btn.clicked.connect(self._copy_text)
            btn_layout.addWidget(copy_btn)

            close_btn = QPushButton("Kapat")
            close_btn.setObjectName("secondaryBtn")
            close_btn.setMinimumHeight(36)
            close_btn.clicked.connect(self.accept)
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)

        elif item_type in ('file', 'clipboard_image'):
            path = self.item_data.get('path', '')
            name = self.item_data.get('name', 'Dosya')
            is_image = (item_type == 'clipboard_image'
                        or self._is_image_file(name))

            if item_type == 'clipboard_image':
                self.setWindowTitle("Pano Resmi Detayı")
                title_text = "🖼️ Pano Resmi"
            else:
                self.setWindowTitle("Dosya Detayı")
                title_text = f"📄 {name}"

            title = QLabel(title_text)
            title.setFont(QFont('Helvetica Neue', 15, QFont.Bold))
            title.setStyleSheet("color: #0a84ff;")
            title.setWordWrap(True)
            layout.addWidget(title)

            meta_label = QLabel(f"Gönderen: {sender}   |   {timestamp}")
            meta_label.setStyleSheet("color: #8e8e93; font-size: 11px;")
            layout.addWidget(meta_label)

            info_frame = QFrame()
            info_frame.setStyleSheet(
             
                if not pixmap.isNull():
                    self.setMinimumHeight(520)
                    preview_label = QLabel()
                    scaled = pixmap.scaled(
                        480, 300, Qt.KeepAspectRatio,
                        Qt.SmoothTransformation)
                    preview_label.setPixmap(scaled)
                    preview_label.setAlignment(Qt.AlignCenter)
                    preview_label.setStyleSheet(
                        "background-color: #2c2c2e; border-radius: 8px;"
                        "padding: 10px; border: 1px solid rgba(255,255,255,0.08);")
                    layout.addWidget(preview_label)

            btn_layout = QHBoxLayout()
            if path and os.path.exists(path):
                open_btn = QPushButton("📂 Finder'da Göster")
                open_btn.setMinimumHeight(36)
                open_btn.clicked.connect(lambda: self._open_in_finder(path))
                btn_layout.addWidget(open_btn)

                if is_image:
                    copy_img_btn = QPushButton("📋 Panoya Kopyala")
                    copy_img_btn.setMinimumHeight(36)
                    copy_img_btn.clicked.connect(
                        lambda: self._copy_image(path))
                    btn_layout.addWidget(copy_img_btn)

            close_btn = QPushButton("Kapat")
            close_btn.setObjectName("secondaryBtn")
            close_btn.setMinimumHeight(36)
            close_btn.clicked.connect(self.accept)
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)
        else:
            self.setWindowTitle("Detay")
            close_btn = QPushButton("Kapat")
            close_btn.setMinimumHeight(36)
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)

    def _is_image_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp',
                       '.bmp', '.heic', '.svg')

    def _fmt_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def _copy_text(self):
        QApplication.clipboard().setText(self._text_display.toPlainText())
        btn = self.sender()
        if btn:
            btn.setText("✅ Kopyalandı!")
            import weakref
            ref = weakref.ref(btn)
            QTimer.singleShot(1500,
                              lambda: ref() and ref().setText("📋 Kopyala"))

    def _open_in_finder(self, path):
        try:
            subprocess.Popen(['open', '-R', path])
        except Exception as e:
            print(f"[ERROR] Failed to open in Finder: {e}")

    def _copy_image(self, path):
        try:
            image = QImage(path)
            if not image.isNull():
                QApplication.clipboard().setImage(image)
                btn = self.sender()
                if btn:
                    btn.setText("✅ Kopyalandı!")
                    import weakref
                    ref = weakref.ref(btn)
                    QTimer.singleShot(
                        1500,
                        lambda: ref() and ref().setText("📋 Panoya Kopyala"))
        except Exception as e:
            print(f"[ERROR] Failed to copy image: {e}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class LocalSendApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # macOS: Application Support dizini
        self.config_dir = os.path.expanduser(
            '~/Library/Application Support/ULAK')
        os.makedirs(self.config_dir, exist_ok=True)
        self.settings = QSettings(
            os.path.join(self.config_dir, 'ulak.conf'), QSettings.IniFormat)

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
        self.setup_menu_bar()
        self._load_history()
        self.load_settings()
        self.setup_connections()
        self.setup_tray_icon()
        self.setup_shortcuts()
        self.check_port_conflict()
        self.web_server.start()
        self.network.start_discovery()
        self.announcement_manager.fetch_async()

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
        # macOS .app bundle desteği
        try:
            base_path = sys._MEIPASS  # PyInstaller bundle
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, *paths)

    def init_ui(self):
        self.setWindowTitle('ULAK')
        self.setMinimumSize(780, 620)
        self.setStyleSheet(MACOS_DARK_THEME)
        
        # Sistem default fontu - emoji desteği için özellikle ayarlanmıyor
        font = QFont()
        font.setPointSize(13)
        self.setFont(font)

        icon_path = self.get_resource_path('ulaklo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # macOS tarzı başlık çubuğu
        header_bar = QWidget()
        header_bar.setStyleSheet(
            "background: #2c2c2e;"
            "border-bottom: 1px solid rgba(255,255,255,0.10);")
        header_bar.setFixedHeight(52)
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(16, 0, 16, 0)

        self.logo_label = QLabel()
        logo_path = self.get_resource_path('ulaklo.png')
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(
                logo_pixmap.scaled(
                    28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(self.logo_label)

        title = QLabel("ULAK")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #0a84ff;")
        header_layout.addWidget(title)

        subtitle = QLabel("Yerel Ağ Dosya Paylaşımı")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #636366; padding-left: 6px;")
        header_layout.addWidget(subtitle)

        header_layout.addStretch()

        self.status_indicator = QLabel("🟢")
        status_font = QFont()
        status_font.setPointSize(13)
        self.status_indicator.setFont(status_font)
        self.status_indicator.setToolTip("Bağlı")
        header_layout.addWidget(self.status_indicator)

        main_layout.addWidget(header_bar)

        self.announcement_card = AnnouncementCard()
        main_layout.addWidget(self.announcement_card)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(False)
        self.tabs.setDocumentMode(False)
        self.tabs.setMovable(False)
        self.tabs.setUsesScrollButtons(False)
        # Tab bar fontu - sistem default fontu emoji desteği için özellikle ayarlanmıyor
        tab_font = QFont()
        tab_font.setPointSize(12)
        tab_font.setWeight(QFont.Bold)
        self.tabs.tabBar().setFont(tab_font)
        self.tabs.setElideMode(Qt.ElideNone)
        main_layout.addWidget(self.tabs)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setFormat("%p%")
        main_layout.addWidget(self.progress_bar)

        self.transfer_info_label = QLabel("")
        self.transfer_info_label.setStyleSheet(
            "background-color: #2c2c2e; padding: 6px 16px;"
            "color: #0a84ff; font-size: 11px;")
        self.transfer_info_label.setAlignment(Qt.AlignCenter)
        self.transfer_info_label.setVisible(False)
        main_layout.addWidget(self.transfer_info_label)

        # Tab isimlerini Unicode desteği ile yeniden ayarla
        QTimer.singleShot(10, self._fix_tab_names)
        QTimer.singleShot(100, self._fix_tab_names)
        QTimer.singleShot(250, self._fix_tab_names)
        QTimer.singleShot(500, self._fix_tab_names)
        QTimer.singleShot(1000, self._fix_tab_names)
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_device_list)
        self.refresh_timer.start(2000)
        
    def _fix_tab_names(self):
        """Tab isimlerini Unicode karakterlerle düzgün ayarlar"""
        try:
            # Tab isimlerini tekrar ayarla (variation selector olmadan)
            tab_names = [
                "\u2191 G\u00f6nder",
                "\u2193 Al\u0131nanlar",
                "\u2699 Ayarlar",
                "\u24d8 Hakk\u0131nda"
            ]
            
            for i, name in enumerate(tab_names):
                self.tabs.setTabText(i, name)
                self.tabs.setTabToolTip(i, name)
                # Her tab için ayrı ayrı yenile
                self.tabs.tabBar().setTabText(i, name)
            
            # Tab bar fontunu yeniden ayarla - sistem default fontu emoji desteği için
            tab_font = QFont()
            tab_font.setPointSize(12)
            tab_font.setWeight(QFont.Bold)
            self.tabs.tabBar().setFont(tab_font)
            
            # Tab bar'ı zorla yenile
            self.tabs.tabBar().repaint()
            self.tabs.repaint()
            
            print("[DEBUG] Tab names fixed")
        except Exception as e:
            print(f"[ERROR] Tab name fix error: {e}")

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
        self.encryption_info_label.setFont(
            QFont('Helvetica Neue', 10, QFont.Bold))
        self.encryption_info_label.setStyleSheet(
            "color: #ffffff; background-color: #30d158;"
            "padding: 8px; border-radius: 8px; cursor: pointer;")
        self.encryption_info_label.setAlignment(Qt.AlignCenter)
        self.encryption_info_label.setVisible(False)
        self.encryption_info_label.setToolTip(
            "Şifreleme ayarlarına gitmek için tıklayın")
        self.encryption_info_label.clicked.connect(
            self._go_to_encryption_settings)
        send_layout.addWidget(self.encryption_info_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.file_send_btn = QPushButton("📄 Dosya")
        self.file_send_btn.setMinimumHeight(46)
        self.file_send_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.file_send_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.file_send_btn)

        self.folder_send_btn = QPushButton("📁 Klasör")
        self.folder_send_btn.setMinimumHeight(46)
        self.folder_send_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.folder_send_btn.clicked.connect(self.select_folder)
        buttons_layout.addWidget(self.folder_send_btn)

        self.text_send_btn = QPushButton("💬 Metin")
        self.text_send_btn.setMinimumHeight(46)
        self.text_send_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.text_send_btn.clicked.connect(self.open_text_send_dialog)
        buttons_layout.addWidget(self.text_send_btn)

        self.clipboard_send_btn = QPushButton("📋 Pano")
        self.clipboard_send_btn.setMinimumHeight(46)
        self.clipboard_send_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.clipboard_send_btn.clicked.connect(self.send_clipboard)
        buttons_layout.addWidget(self.clipboard_send_btn)

        self.screenshot_btn = QPushButton("📸 Ekran")
        self.screenshot_btn.setMinimumHeight(46)
        self.screenshot_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.screenshot_btn.clicked.connect(self.open_screenshot_dialog)
        buttons_layout.addWidget(self.screenshot_btn)

        send_layout.addLayout(buttons_layout)

        self.link_send_btn = QPushButton(
            "🔗 Link Üzerinden Gönder (Cihaz Seçmeden)")
        self.link_send_btn.setObjectName("linkBtn")
        self.link_send_btn.setMinimumHeight(42)
        self.link_send_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.link_send_btn.clicked.connect(self.show_link_send_options)
        send_layout.addWidget(self.link_send_btn)

        hint_label = QLabel(
            "✨ İpucu: Dosya/klasörü buraya sürükleyip bırakabilirsiniz")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet(
            "color: #636366; font-style: italic; padding: 4px;")
        send_layout.addWidget(hint_label)

        files_label = QLabel("Seçili Dosyalar")
        files_label.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        send_layout.addWidget(files_label)

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(110)
        send_layout.addWidget(self.files_list)

        devices_label = QLabel("Yakındaki Cihazlar")
        devices_label.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        send_layout.addWidget(devices_label)

        self.devices_list = QListWidget()
        self.devices_list.setSelectionMode(QListWidget.MultiSelection)
        self.devices_list.setWordWrap(True)
        self.devices_list.setTextElideMode(Qt.ElideNone)
        send_layout.addWidget(self.devices_list)

        btn_layout = QHBoxLayout()

        self.clear_btn = QPushButton("🗑️ Temizle")
        self.clear_btn.setObjectName("secondaryBtn")
        self.clear_btn.setMinimumHeight(34)
        self.clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.clear_btn)

        self.send_btn = QPushButton("📤 Gönder")
        self.send_btn.setMinimumHeight(34)
        self.send_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        self.send_btn.clicked.connect(self.send_files)
        self.send_btn.setEnabled(False)
        btn_layout.addWidget(self.send_btn, 2)

        send_layout.addLayout(btn_layout)

        self.tabs.addTab(send_tab, "")
        # Tab ismi sonra UTF-8 ile ayarlanacak

    def _build_receive_tab(self):
        receive_tab = QWidget()
        receive_layout = QVBoxLayout(receive_tab)
        receive_layout.setContentsMargins(20, 20, 20, 20)
        receive_layout.setSpacing(14)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #2c2c2e; border-radius: 10px; padding: 14px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        info_layout = QVBoxLayout(info_frame)

        device_label = QLabel(f"🖥️ Cihaz Adı: {self.network.device_name}")
        device_label.setFont(QFont('Helvetica Neue', 12))
        info_layout.addWidget(device_label)

        ip_label = QLabel(f"🌐 IP Adresi: {self.network.get_local_ip()}")
        ip_label.setFont(QFont('Helvetica Neue', 12))
        info_layout.addWidget(ip_label)

        self.port_label = QLabel(f"🔌 Port: {self.network.port}")
        self.port_label.setFont(QFont('Helvetica Neue', 12))
        info_layout.addWidget(self.port_label)

        receive_layout.addWidget(info_frame)

        history_label = QLabel("📥 Alınanlar")
        history_label.setFont(QFont('Helvetica Neue', 13, QFont.Bold))
        receive_layout.addWidget(history_label)

        self.history_list = QListWidget()
        receive_layout.addWidget(self.history_list)

        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.setSpacing(8)

        open_folder_btn = QPushButton("📁 İndirilenler Klasörünü Aç (Finder)")
        open_folder_btn.setObjectName("secondaryBtn")
        open_folder_btn.setMinimumHeight(40)
        open_folder_btn.clicked.connect(self.open_downloads)
        bottom_btn_layout.addWidget(open_folder_btn, 2)

        clear_history_btn = QPushButton("🗑️ Listeyi Temizle")
        clear_history_btn.setObjectName("secondaryBtn")
        clear_history_btn.setMinimumHeight(40)
        clear_history_btn.clicked.connect(self._clear_history)
        bottom_btn_layout.addWidget(clear_history_btn)

        receive_layout.addLayout(bottom_btn_layout)

        self.tabs.addTab(receive_tab, "")
        # Tab ismi sonra UTF-8 ile ayarlanacak

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
        settings_layout.setSpacing(14)

        settings_label = QLabel("⚙️ Ayarlar")
        settings_label.setFont(QFont('Helvetica Neue', 16, QFont.Bold))
        settings_label.setStyleSheet("color: #0a84ff;")
        settings_layout.addWidget(settings_label)

        name_layout = QHBoxLayout()
        name_label = QLabel("Cihaz Adı:")
        name_label.setMinimumWidth(130)
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit(self.network.device_name)
        name_layout.addWidget(self.name_input)
        settings_layout.addLayout(name_layout)

        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_label.setMinimumWidth(130)
        port_layout.addWidget(port_label)
        self.port_input = QLineEdit(str(self.network.port))
        self.port_input.setPlaceholderText("Varsayılan: 53317")
        port_layout.addWidget(self.port_input)
        settings_layout.addLayout(port_layout)

        broadcast_port_layout = QHBoxLayout()
        broadcast_label = QLabel("Broadcast Port:")
        broadcast_label.setMinimumWidth(130)
        broadcast_port_layout.addWidget(broadcast_label)
        self.broadcast_port_input = QLineEdit(str(self.network.broadcast_port))
        self.broadcast_port_input.setPlaceholderText("Varsayılan: 53318")
        broadcast_port_layout.addWidget(self.broadcast_port_input)
        settings_layout.addLayout(broadcast_port_layout)

        options_frame = QFrame()
        options_frame.setStyleSheet(
            "background-color: #2c2c2e; border-radius: 10px; padding: 4px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(2)

        self.encryption_checkbox = QCheckBox("🔒 AES-256 Şifreleme Kullan")
        self.encryption_checkbox.setFont(QFont('Helvetica Neue', 11))
        self.encryption_checkbox.setStyleSheet("padding: 10px;")
        self.encryption_checkbox.stateChanged.connect(self.on_encryption_changed)
        options_layout.addWidget(self.encryption_checkbox)

        self.notification_checkbox = QCheckBox(
            "🔔 Dosya Alındığında Bildirim Göster")
        self.notification_checkbox.setFont(QFont('Helvetica Neue', 11))
        self.notification_checkbox.setStyleSheet("padding: 10px;")
        options_layout.addWidget(self.notification_checkbox)

        self.sound_checkbox = QCheckBox(
            "🔊 Transfer Tamamlandığında Ses Çal")
        self.sound_checkbox.setFont(QFont('Helvetica Neue', 11))
        self.sound_checkbox.setStyleSheet("padding: 10px;")
        options_layout.addWidget(self.sound_checkbox)

        self.tray_checkbox = QCheckBox("📥 Menü Çubuğunda Çalıştır")
        self.tray_checkbox.setFont(QFont('Helvetica Neue', 11))
        self.tray_checkbox.setStyleSheet("padding: 10px;")
        self.tray_checkbox.stateChanged.connect(self.on_tray_changed)
        options_layout.addWidget(self.tray_checkbox)

        self.auto_copy_clipboard_checkbox = QCheckBox(
            "📋 Pano İçeriğini Otomatik Kopyala")
        self.auto_copy_clipboard_checkbox.setFont(QFont('Helvetica Neue', 11))
        self.auto_copy_clipboard_checkbox.setStyleSheet("padding: 10px;")
 

        download_folder_label = QLabel("📁 İndirme Klasörü:")
        download_folder_label.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        settings_layout.addWidget(download_folder_label)

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

        settings_layout.addLayout(download_path_layout)

        password_label = QLabel(
            "Şifreleme Parolası (Boş bırakılırsa varsayılan kullanılır):")
        password_label.setFont(QFont('Helvetica Neue', 10))
        password_label.setStyleSheet("color: #8e8e93; padding-top: 8px;")
        password_label.setWordWrap(True)
        settings_layout.addWidget(password_label)

        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "Özel şifreleme parolası girin...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(34)
        password_input_layout.addWidget(self.password_input)

        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setObjectName("secondaryBtn")
        self.show_password_btn.setFixedSize(40, 34)
        self.show_password_btn.setToolTip("Parolayı göster/gizle")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.show_password_btn)
        settings_layout.addLayout(password_input_layout)

        password_note = QLabel(
            "⚠️ Not: Aynı parolayı kullanan cihazlar arası "
            "transfer yapılabilir")
        password_note.setFont(QFont('Helvetica Neue', 9))
        password_note.setStyleSheet("color: #ffd60a; font-style: italic;")
        password_note.setWordWrap(True)
        settings_layout.addWidget(password_note)

        save_btn = QPushButton("💾 Kaydet")
        save_btn.setMinimumHeight(38)
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)

        settings_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        settings_main_layout.addWidget(scroll_area)

        self.tabs.addTab(settings_tab, "")
        # Tab ismi sonra UTF-8 ile ayarlanacak

    def _build_about_tab(self):
        about_tab = QWidget()
        about_scroll = QScrollArea()
        about_scroll.setWidgetResizable(True)
        about_scroll.setFrameShape(QFrame.NoFrame)

        about_content = QWidget()
        about_layout = QVBoxLayout(about_content)
        about_layout.setContentsMargins(24, 24, 24, 24)
        about_layout.setSpacing(18)

        logo_label = QLabel()
        logo_path = self.get_resource_path('ulaklo.png')
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(
                    100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(logo_label)

        about_title = QLabel("ULAK")
        about_title.setFont(QFont('Helvetica Neue', 24, QFont.Bold))
        about_title.setAlignment(Qt.AlignCenter)
        about_title.setStyleSheet("color: #0a84ff;")
        about_layout.addWidget(about_title)

        version_label = QLabel("Versiyon 1.0.5 — macOS")
        version_label.setFont(QFont('Helvetica Neue', 13))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #8e8e93; padding-bottom: 10px;")
        about_layout.addWidget(version_label)

        desc_frame = QFrame()
        desc_frame.setStyleSheet(
            "background-color: #2c2c2e; border-radius: 12px; padding: 18px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        desc_layout = QVBoxLayout(desc_frame)

        desc_title = QLabel("📝 Açıklama")
        desc_title.setFont(QFont('Helvetica Neue', 14, QFont.Bold))
        desc_title.setStyleSheet("color: #0a84ff;")
        desc_layout.addWidget(desc_title)

        desc_text = QLabel(
            "Yerel ağ üzerinden hızlı ve güvenli dosya paylaşımı")
        desc_text.setFont(QFont('Helvetica Neue', 13))
        desc_text.setStyleSheet("color: #ebebf5; padding-top: 6px;")
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)

        about_layout.addWidget(desc_frame)

        national_frame = QFrame()
        national_frame.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "stop:0 #1a1a3e, stop:1 #2d1b3d);"
            "border-radius: 12px; padding: 18px;"
            "border: 2px solid #e30a17;")
        national_layout = QHBoxLayout(national_frame)

        flag_label = QLabel("🇹🇷")
        flag_label.setFont(QFont('Helvetica Neue', 40))
        flag_label.setAlignment(Qt.AlignCenter)
        national_layout.addWidget(flag_label)

        text_label = QLabel(
            "Yerli ve Milli Proje\n"
            "TÜRK Yazılımcılar Tarafından Geliştirilmiştir.")
        text_label.setFont(QFont('Helvetica Neue', 14, QFont.Bold))
        text_label.setStyleSheet("color: #87ceeb; padding: 8px;")
        text_label.setWordWrap(True)
        national_layout.addWidget(text_label, 1)

        about_layout.addWidget(national_frame)

        platform_frame = QFrame()
        platform_frame.setStyleSheet(
            "background-color: #2c2c2e; border-radius: 12px; padding: 18px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        platform_layout = QVBoxLayout(platform_frame)

        platform_title = QLabel("💻 Platform Desteği")
        platform_title.setFont(QFont('Helvetica Neue', 14, QFont.Bold))
        platform_title.setStyleSheet("color: #0a84ff;")
        platform_layout.addWidget(platform_title)

        download_btn = QPushButton(
            "🪟 Windows  🐧 Linux  🍎 macOS  🤖 Android İçin İndir")
        download_btn.setMinimumHeight(44)
        download_btn.setFont(QFont('Helvetica Neue', 11, QFont.Bold))
        download_btn.clicked.connect(
            lambda: self.open_url("https://ulak.algsoft.net.tr/"))
        platform_layout.addWidget(download_btn)

        about_layout.addWidget(platform_frame)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #2c2c2e; border-radius: 12px; padding: 18px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("ℹ️ Bilgi")
        info_title.setFont(QFont('Helvetica Neue', 14, QFont.Bold))
        info_title.setStyleSheet("color: #0a84ff;")
        info_layout.addWidget(info_title)

        for text, color in [
            ("👨‍💻 Geliştirici: Fatih ÖNDER (CekToR)", "#ebebf5"),
            ("© 2026 ALGSoft Inc.", "#ebebf5"),
            ("🌐 https://algsoft.net.tr", "#ebebf5"),
            ("📧 info@algsoft.net.tr", "#ebebf5"),
            ("📜 Lisans: MIT", "#ebebf5"),
            ("🐱 GitHub: github.com/cektor/ulak", "#0a84ff"),
        ]:
            lbl = QLabel(text)
            lbl.setFont(QFont('Helvetica Neue', 12))
            lbl.setStyleSheet(f"color: {color}; padding-top: 3px;")
            info_layout.addWidget(lbl)

        about_layout.addWidget(info_frame)
        about_layout.addStretch()

        about_scroll.setWidget(about_content)
        about_tab_layout = QVBoxLayout(about_tab)
        about_tab_layout.setContentsMargins(0, 0, 0, 0)
        about_tab_layout.addWidget(about_scroll)

        self.tabs.addTab(about_tab, "")
        # Tab ismi sonra UTF-8 ile ayarlanacak

    def _go_to_encryption_settings(self):
        self.tabs.setCurrentIndex(2)
        self.encryption_checkbox.setFocus()

    def show_link_send_options(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("🔗 Link Üzerinden Gönder")
        dialog.setModal(True)

        clipboard_btn.clicked.connect(
            lambda: (dialog.accept(), self._link_send_clipboard()))
        layout.addWidget(clipboard_btn)

        cancel_btn = QPushButton("İptal")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setMinimumHeight(36)
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

        QMessageBox.warning(
            self, 'Hata', 'Panoda paylaşılabilir içerik bulunamadı!')

    def _show_link_dialog(self, link):
        dialog = LinkShareDialog(link, self)
        dialog.exec_()

    def setup_menu_bar(self):
        """Tam macOS native menü barı — Cmd tuşu ile çalışır."""
        mb = self.menuBar()

        # ── ULAK (App menu) ──────────────────────────────────────────────────
        app_menu = mb.addMenu("ULAK")

        about_act = QAction("ULAK Hakkında", self)
        about_act.setMenuRole(QAction.AboutRole)
        about_act.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        app_menu.addAction(about_act)

        prefs_act = QAction("Tercihler...", self)
        prefs_act.setMenuRole(QAction.PreferencesRole)
        prefs_act.setShortcut(QKeySequence("Ctrl+,"))
        prefs_act.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        app_menu.addAction(prefs_act)

        quit_act = QAction("ULAK'tan Çık", self)
        quit_act.setMenuRole(QAction.QuitRole)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(QApplication.quit)
        app_menu.addAction(quit_act)

        # ── Dosya ─────────────────────────────────────────────────────────────
        file_menu = mb.addMenu("Dosya")

        open_file_act = QAction("Dosya Seç...", self)
        open_file_act.setShortcut(QKeySequence("Ctrl+O"))
        open_file_act.triggered.connect(self.select_files)
        file_menu.addAction(open_file_act)

        open_folder_act = QAction("Klasör Seç...", self)
        open_folder_act.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_act.triggered.connect(self.select_folder)
        file_menu.addAction(open_folder_act)

        file_menu.addSeparator()

        send_act = QAction("Gönder", self)
        send_act.setShortcut(QKeySequence("Ctrl+Return"))
        send_act.triggered.connect(self.send_files)
        file_menu.addAction(send_act)

        link_act = QAction("Link Üzerinden Gönder...", self)
        link_act.setShortcut(QKeySequence("Ctrl+L"))
        link_act.triggered.connect(self.show_link_send_options)
        file_menu.addAction(link_act)

        file_menu.addSeparator()

        downloads_act = QAction("İndirilenler Klasörünü Aç", self)
        downloads_act.setShortcut(QKeySequence("Ctrl+Shift+D"))
        downloads_act.triggered.connect(self.open_downloads)
        file_menu.addAction(downloads_act)

        file_menu.addSeparator()

        close_act = QAction("Pencereyi Kapat", self)
        close_act.setShortcut(QKeySequence("Ctrl+W"))
        close_act.triggered.connect(self.close)
        file_menu.addAction(close_act)

        # ── Düzenle ───────────────────────────────────────────────────────────
        edit_menu = mb.addMenu("Düzenle")

        text_act = QAction("Metin Mesajı Gönder...", self)
        text_act.setShortcut(QKeySequence("Ctrl+T"))
        text_act.triggered.connect(self.open_text_send_dialog)
        edit_menu.addAction(text_act)

        clipboard_act = QAction("Pano İçeriğini Gönder", self)
        clipboard_act.setShortcut(QKeySequence("Ctrl+B"))
        clipboard_act.triggered.connect(self.send_clipboard)
        edit_menu.addAction(clipboard_act)

        screenshot_act = QAction("Ekran Görüntüsü Al ve Gönder", self)
        screenshot_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        screenshot_act.triggered.connect(self.open_screenshot_dialog)
        edit_menu.addAction(screenshot_act)

        # ── Görünüm ───────────────────────────────────────────────────────────
        view_menu = mb.addMenu("Görünüm")

        for idx, label in enumerate(
                ["↑ Gönder", "↓ Alınanlar", "⚙ Ayarlar", "ⓘ Hakkında"]):
            tab_act = QAction(label, self)
            tab_act.setShortcut(QKeySequence(f"Ctrl+{idx + 1}"))
            tab_act.triggered.connect(
                lambda checked, i=idx: self.tabs.setCurrentIndex(i))
            view_menu.addAction(tab_act)

        # ── Yardım ────────────────────────────────────────────────────────────
        help_menu = mb.addMenu("Yardım")

        shortcuts_act = QAction("Klavye Kısayolları...", self)
        shortcuts_act.setShortcut(QKeySequence("Ctrl+Shift+K"))
        shortcuts_act.triggered.connect(self.show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_act)

    def show_keyboard_shortcuts(self):
        KeyboardShortcutsDialog(self).exec_()

    def setup_shortcuts(self):
        # Tüm kısayollar setup_menu_bar() içindeki QAction'lar ile yönetiliyor.
        # macOS'ta Ctrl = Cmd tuşuna eşlenir (Qt davranışı).
        pass

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
            self.tray_icon.setIcon(self._create_tray_icon())

        tray_menu = QMenu()
        show_action = tray_menu.addAction("💻 ULAK'ı Göster")
        show_action.triggered.connect(self._show_window)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Çıkış")
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        if self.settings.value('use_tray', False, type=bool):
            self.tray_icon.show()

    def _show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _create_tray_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(10, 132, 255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        return QIcon(pixmap)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self._show_window()

    def on_tray_changed(self):
        if hasattr(self, 'tray_icon'):
            if self.tray_checkbox.isChecked():
                self.tray_icon.show()
            else:
                self.tray_icon.hide()

    def show_notification(self, title, message):
        if not self.settings.value('use_notifications', True, type=bool):
            return
        # macOS'ta önce QSystemTrayIcon ile dene
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title, message, QSystemTrayIcon.Information, 3000)
            return
        # osascript ile macOS native bildirim
        try:
            safe_title = title.replace('"', '\\"')
            safe_msg = (message.replace('"', '\\"')
                        .replace('\n', ' ')
                        .replace("'", "\\'"))
            subprocess.Popen(
                ['osascript', '-e',
                 f'display notification "{safe_msg}" '
                 f'with title "{safe_title}"'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[INFO] Notification error: {e}")

    def play_sound(self):
        if not self.settings.value('use_sound', False, type=bool):
            return
        # macOS: afplay ile sistem sesi çal
        sounds = [
            '/System/Library/Sounds/Glass.aiff',
            '/System/Library/Sounds/Ping.aiff',
            '/System/Library/Sounds/Pop.aiff',
        ]
        for sound in sounds:
            if os.path.exists(sound):
                try:
                    subprocess.Popen(
                        ['afplay', sound],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
                except Exception:
                    pass
                return

    def get_device_icon(self, device_name):
        name_lower = device_name.lower()
        if any(x in name_lower for x in ['iphone', 'android', 'mobile']):
            return "📱"
        elif any(x in name_lower for x in ['ipad', 'tablet']):
            return "📱"
        elif any(x in name_lower for x in ['mac', 'macbook', 'imac']):
            return "🍎"
        elif any(x in name_lower for x in ['windows', 'pc', 'win']):
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
        self.network.clipboard_image_received.connect(
            self.on_clipboard_image_received)
        self.network.transfer_request.connect(self.on_transfer_request)
        self.network.receive_failed.connect(self.on_receive_failed)
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
        self.history_list.itemDoubleClicked.connect(self._show_item_detail)
        self.history_list.itemClicked.connect(self._show_item_brief)


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

    def on_device_lost(self, device_ip):
        if device_ip in self.devices:
            del self.devices[device_ip]
            self.update_device_list()

    def update_device_list(self):
        selected_ips = []
        for item in self.devices_list.selectedItems():
            selected_ips.append(item.data(Qt.UserRole))

        self.devices_list.clear()
        for device_id, device in self.devices.items():
            icon = self.get_device_icon(device['name'])
            item = QListWidgetItem(
                f"{icon} {device['name']}\n    {device['ip']}")
            item.setData(Qt.UserRole, device_id)
            item.setSizeHint(QSize(0, 48))
            self.devices_list.addItem(item)
            if device_id in selected_ips:
                item.setSelected(True)

        if len(self.devices) == 0:
            self.status_bar.setText("Yakında cihaz bulunamadı")
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
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.png')
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
                                    temp_path, device_ip,
                                    is_clipboard_image=True):
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

        QMessageBox.warning(
            self, 'Hata', 'Panoda metin veya resim bulunamadı!')

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
            # macOS'ta pencereyi gizleyerek ekran yakala
            self.hide()
            QTimer.singleShot(400, self._capture_screen)

        except Exception as e:
            self.show()
            self._show_window()
            print(f"[ERROR] Screenshot failed: {e}")

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
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
                QTimer.singleShot(
                    0,
                    lambda: self._screenshot_send_complete(
                        success_count, len(target_devices)))

            threading.Thread(
                target=send_screenshot_image, daemon=True).start()

    def _screenshot_send_complete(self, success, total):
        if success == total:
            self.status_bar.setText(
                '✅ Ekran görüntüsü başarıyla gönderildi!')
        else:
            self.status_bar.setText(f'⚠️ {success}/{total} cihaza gönderildi')
        QTimer.singleShot(3000, lambda: self.status_bar.setText(''))


    def _text_send_complete(self, success, total):
        if success == total:
            self.status_bar.setText('✅ Metin başarıyla gönderildi!')
        else:
            self.status_bar.setText(
                f'⚠️ {success}/{total} cihaza gönderildi')
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

        with ThreadPoolExecutor(
                max_workers=min(len(target_devices), 4)) as executor:
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
                progress = int(
                    (completed_transfers / total_transfers) * 100)
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
            self.status_bar.setText(
                f'✅ {success} transfer başarıyla tamamlandı!')
            self.play_sound()
        else:
            self.status_bar.setText(
                f'⚠️ {success}/{total} transfer tamamlandı')
        self.send_btn.setEnabled(True)
        self.send_btn.setText("📤 Gönder")
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_file_received(self, filename, sender, path=''):
        self.tabs.setCurrentIndex(1)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.transfer_info_label.setVisible(False)
        if self.current_dialog:
            try:
                if hasattr(self.current_dialog, 'status_label'):
                    self.current_dialog.status_label.setText(
                        "✅ Transfer tamamlandı!")
                if hasattr(self.current_dialog, 'progress'):
                    self.current_dialog.progress.setValue(100)
                if isinstance(self.current_dialog, TransferDialog):
                    self.current_dialog.accept()
                    self.current_dialog.close()
                    self.current_dialog.deleteLater()
                    self.current_dialog = None
            except Exception as e:
                print(f"[ERROR] Error closing dialog: {e}")
        from datetime import datetime
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        data = {
            'type': 'file',
            'name': filename,
            'sender': sender,
            'path': path,
            'timestamp': timestamp,
        }
        item = QListWidgetItem(
            f"✅ {filename}\n    {sender}  •  {timestamp}")
        item.setData(Qt.UserRole, data)
        self.history_list.insertItem(0, item)
        self._save_history()
        self.status_bar.setText(f'✅ {sender} cihazından dosya alındı!')
        self.show_notification('ULAK - Dosya Alındı',
                               f'{filename}\n{sender} cihazından alındı')
        self.play_sound()
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_receive_failed(self, sender):
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.transfer_info_label.setVisible(False)
        if self.current_dialog:
            try:
                if hasattr(self.current_dialog, 'status_label'):
                    self.current_dialog.status_label.setText(
                        "❌ Transfer başarısız!")
                if isinstance(self.current_dialog, (TransferDialog, BatchTransferDialog)):
                    self.current_dialog.close()
                    self.current_dialog.deleteLater()
                    self.current_dialog = None
            except Exception:
                self.current_dialog = None
        msg = f'❌ Transfer başarısız: {sender}' if sender else '❌ Transfer başarısız'
        self.status_bar.setText(msg)
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def on_text_received(self, text, sender):
        self.tabs.setCurrentIndex(1)
        if self.settings.value('auto_copy_clipboard', True, type=bool):
            QApplication.clipboard().setText(text)
        dialog = TextMessageDialog(text, sender, self)
        dialog.exec_()
        from datetime import datetime
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        data = {
            'type': 'text',
            'full_text': text,
            'sender': sender,
            'timestamp': timestamp,
        }
        preview = text[:50] + ('...' if len(text) > 50 else '')
        item = QListWidgetItem(
            f"💬 {preview}\n    {sender}  •  {timestamp}")
        item.setData(Qt.UserRole, data)
        self.history_list.insertItem(0, item)
        self._save_history()
        self.show_notification('ULAK - Metin Mesajı',
                               f'{sender}: {text[:100]}')
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
        from datetime import datetime
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        data = {
            'type': 'clipboard_image',
            'name': os.path.basename(image_path),
            'sender': sender,
            'path': image_path,
            'timestamp': timestamp,
        }
        item = QListWidgetItem(
            f"🖼️ Pano Resmi\n    {sender}  •  {timestamp}")
        item.setData(Qt.UserRole, data)
        self.history_list.insertItem(0, item)
        self._save_history()
        self.show_notification('ULAK - Pano Resmi',
                               f'{sender} bir resim gönderdi')
        self.play_sound()

    def on_transfer_request(self, file_info, callback):
        self.pending_transfers.append({'info': file_info, 'callback': callback})

        if self.batch_timer:
            self.batch_timer.stop()

        self.batch_timer = QTimer()
        self.batch_timer.setSingleShot(True)
        self.batch_timer.timeout.connect(self._show_batch_dialog)
        self.batch_timer.start(500)

    def _show_batch_dialog(self):
        if not self.pending_transfers:
            return

        self.tabs.setCurrentIndex(1)

        if len(self.pending_transfers) == 1:
            transfer = self.pending_transfers[0]
            self.current_dialog = TransferDialog(transfer['info'], self)
            self.current_dialog.callback = transfer['callback']
            self.current_dialog.finished.connect(
                lambda: self._cleanup_dialog())
            self.current_dialog.show()
        else:
            files_info = [t['info'] for t in self.pending_transfers]
            self.current_dialog = BatchTransferDialog(files_info, self)
            self.current_dialog.callbacks = [
                t['callback'] for t in self.pending_transfers]
            self.current_dialog.finished.connect(
                lambda: self._cleanup_dialog())
            self.current_dialog.show()

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
                f'Her iki cihazda da aynı şifreleme parolasını '
                f'kullandığınızdan emin olun.')
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
            eta_str = (f"{eta_seconds//3600}h "
                       f"{(eta_seconds%3600)//60}m")

        info_text = (f"⚡ {speed_str}  |  {trans_str} / {total_str}"
                     f"  |  ⏱️ Kalan: {eta_str}")
        self.transfer_info_label.setText(info_text)
        self.progress_bar.setFormat(f"%p% - {speed_str}")
        if self.current_dialog and hasattr(
                self.current_dialog, 'status_label'):
            self.current_dialog.status_label.setText(
                f"📥 {speed_str} - {trans_str} / {total_str}")

    def _history_file_path(self):
        return os.path.join(self.config_dir, 'history.json')

    def _save_history(self):
        history_data = []
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            data = item.data(Qt.UserRole)
            if data:
                history_data.append(data)
        try:
            with open(self._history_file_path(), 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save history: {e}")

    def _load_history(self):
        history_file = self._history_file_path()
        if not os.path.exists(history_file):
            return
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            for data in history_data:
                item = self._create_history_item(data)
                self.history_list.addItem(item)
        except Exception as e:
            print(f"[ERROR] Failed to load history: {e}")

    def _create_history_item(self, data):
        item_type = data.get('type', 'unknown')
        sender = data.get('sender', 'Bilinmiyor')
        timestamp = data.get('timestamp', '')
        suffix = f"  •  {timestamp}" if timestamp else ''
        if item_type == 'text':
            text = data.get('full_text', '')
            preview = text[:50] + ('...' if len(text) > 50 else '')
            display = f"💬 {preview}\n    {sender}{suffix}"
        elif item_type == 'clipboard_image':
            display = f"🖼️ Pano Resmi\n    {sender}{suffix}"
        else:
            name = data.get('name', 'Dosya')
            display = f"✅ {name}\n    {sender}{suffix}"
        item = QListWidgetItem(display)
        item.setData(Qt.UserRole, data)
        return item

    def _show_item_detail(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return
        dialog = ReceivedItemDetailDialog(data, self)
        dialog.exec_()

    def _show_item_brief(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return
        item_type = data.get('type', 'unknown')
        sender = data.get('sender', 'Bilinmiyor')
        timestamp = data.get('timestamp', '')
        if item_type == 'text':
            preview = data.get('full_text', '')[:80]
            self.status_bar.setText(f"💬 {sender}: {preview}")
        elif item_type == 'clipboard_image':
            path = data.get('path', '')
            exists = '✅' if path and os.path.exists(path) else '⚠️'
            self.status_bar.setText(
                f"{exists} Pano Resmi — {sender}  •  {timestamp} "
                f"— Çift tıkla: detay")
        else:
            name = data.get('name', 'Dosya')
            path = data.get('path', '')
            exists = '✅' if path and os.path.exists(path) else '⚠️'
            self.status_bar.setText(
                f"{exists} {name} — {sender}  •  {timestamp} "
                f"— Çift tıkla: detay")
        QTimer.singleShot(5000, lambda: self.status_bar.setText(''))

    def _clear_history(self):
        if self.history_list.count() == 0:
            return
        reply = QMessageBox.question(
            self, 'Listeyi Temizle',
            'Tüm alınan dosya geçmişi silinecek.\nEmin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_list.clear()
            self._save_history()


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

    def load_settings(self):
        saved_name = self.settings.value('device_name', '')
        if saved_name:
            self.network.device_name = saved_name
            self.name_input.setText(saved_name)

        saved_port = self.settings.value('port', 53317, type=int)
        self.network.port = saved_port

        saved_broadcast_port = self.settings.value(
            'broadcast_port', 53318, type=int)
        self.network.broadcast_port = saved_broadcast_port

        use_encryption = self.settings.value(
            'use_encryption', False, type=bool)
        self.network.use_encryption = use_encryption
        self.encryption_checkbox.setChecked(use_encryption)
        self.encryption_info_label.setVisible(use_encryption)

        saved_password = self.settings.value('encryption_password', '')
        if saved_password:
            self.password_input.setText(saved_password)
            self.network.encryption_key = hashlib.sha256(
                saved_password.encode()).digest()

        self.notification_checkbox.setChecked(
            self.settings.value('use_notifications', True, type=bool))
        self.sound_checkbox.setChecked(
            self.settings.value('use_sound', False, type=bool))
        self.tray_checkbox.setChecked(
            self.settings.value('use_tray', False, type=bool))
        self.auto_copy_clipboard_checkbox.setChecked(
            self.settings.value('auto_copy_clipboard', True, type=bool))

        saved_download_path = self.settings.value('download_folder', '')
        if saved_download_path and os.path.exists(saved_download_path):
            self.network.download_folder = saved_download_path
            self.download_path_input.setText(saved_download_path)
        else:
            default_path = os.path.join(
                os.path.expanduser('~'), 'Downloads')
            self.network.download_folder = default_path
            self.download_path_input.setText(default_path)

    def save_settings(self):
        new_name = self.name_input.text().strip()
        if new_name:
            self.network.device_name = new_name
            self.settings.setValue('device_name', new_name)
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
            QMessageBox.warning(
                self, 'Hata', 'Geçerli bir port numarası girin!')
            return

        try:
            new_broadcast_port = int(self.broadcast_port_input.text())
            if 1024 <= new_broadcast_port <= 65535:
                self.network.broadcast_port = new_broadcast_port
                self.settings.setValue(
                    'broadcast_port', new_broadcast_port)
            else:
                QMessageBox.warning(
                    self, 'Hata',
                    'Broadcast port 1024-65535 arasında olmalıdır!')
                return
        except ValueError:
            QMessageBox.warning(
                self, 'Hata',
                'Geçerli bir broadcast port numarası girin!')
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



    def closeEvent(self, event):
        if self.tray_checkbox.isChecked() and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                'ULAK',
                'Uygulama menü çubuğunda çalışmaya devam ediyor',
                QSystemTrayIcon.Information, 2000)
        else:
            self.network.stop_discovery()
            self.web_server.stop()
            event.accept()

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)


# ============================================================================
# MAIN
# ============================================================================

def main():
    # macOS: Yüksek DPI desteği
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
       # Tab isimlerinin düzgün görünmesi için birden fazla deneme
    def fix_tabs_repeatedly():
        for delay in [50, 150, 300, 500, 800, 1200]:
            QTimer.singleShot(delay, window._fix_tab_names)
    
    QTimer.singleShot(0, fix_tabs_repeatedly)
 

if __name__ == '__main__':
    main()
