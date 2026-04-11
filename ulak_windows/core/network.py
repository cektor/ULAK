import socket
import json
import threading
import os
import time
import zipfile
import tempfile
from PyQt5.QtCore import QObject, pyqtSignal
import hashlib
from core.crypto import encrypt_data, decrypt_data

class NetworkManager(QObject):
    device_found = pyqtSignal(dict)
    device_lost = pyqtSignal(str)
    file_received = pyqtSignal(str, str)
    text_received = pyqtSignal(str, str)  # text, sender
    clipboard_image_received = pyqtSignal(str, str)  # image_path, sender
    progress_updated = pyqtSignal(int)
    transfer_speed = pyqtSignal(float, int, int)  # speed (bytes/s), transferred, total
    transfer_request = pyqtSignal(dict, object)
    transfer_rejected = pyqtSignal(str, str)
    decryption_failed = pyqtSignal(str, str)  # filename, sender
    
    def __init__(self):
        super().__init__()
        self.port = 53317
        self.broadcast_port = 53318
        self.device_name = socket.gethostname()
        self.running = False
        self.discovered_devices = {}
        self.last_seen = {}
        self.use_encryption = False
        import hashlib
        self.encryption_key = hashlib.sha256(b'ulak_default_key').digest()  # Default key
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
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
                message = json.dumps({
                    'type': 'announce',
                    'name': self.device_name,
                    'ip': self.get_local_ip()
                }).encode('utf-8')
                
                # Broadcast'i birden fazla adrese gönder
                sock.sendto(message, ('<broadcast>', self.broadcast_port))
                sock.sendto(message, ('255.255.255.255', self.broadcast_port))
                
                # Yerel ağ broadcast adresi
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
        
        # Tüm arayüzlerden dinle
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
                    
                    # Kendi mesajımızı filtrele
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
            
            # Read header size
            header_size_data = conn.recv(4)
            if len(header_size_data) < 4:
                print("[ERROR] Failed to read header size")
                return
                
            header_size = int.from_bytes(header_size_data, 'big')
            print(f"[DEBUG] Header size: {header_size}")
            
            # Read header
            header_data = b''
            while len(header_data) < header_size:
                chunk = conn.recv(header_size - len(header_data))
                if not chunk:
                    return
                header_data += chunk
            
            header = json.loads(header_data.decode('utf-8'))
            print(f"[DEBUG] Received header: {header}")
            
            # Check if this is a text message
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
                
                print(f"[DEBUG] Received text message from {sender}: {text_content[:50]}...")
                self.text_received.emit(text_content, sender)
                conn.close()
                return
            
            file_info = {
                'filename': header['filename'],
                'filesize': header['filesize'],
                'sender': header['sender'],
                'is_folder': header.get('is_folder', False),
                'file_count': header.get('file_count', 0),
                'folder_count': header.get('folder_count', 0),
                'encrypted': header.get('encrypted', False),
                'is_clipboard_image': header.get('is_clipboard_image', False)
            }
            
            print(f"[DEBUG] File info - is_folder: {file_info['is_folder']}, filename: {file_info['filename']}")
            
            # Request approval
            transfer_event = threading.Event()
            transfer_result = {'accepted': False}
            
            def callback(accepted):
                transfer_result['accepted'] = accepted
                transfer_event.set()
                print(f"[DEBUG] Transfer {'accepted' if accepted else 'rejected'}")
            
            self.transfer_request.emit(file_info, callback)
            
            # Wait for approval
            if not transfer_event.wait(timeout=60):
                print("[ERROR] Transfer timeout")
                try:
                    conn.sendall(b'TIMEOUT__')
                except:
                    pass
                conn.close()
                return
            
            if not transfer_result['accepted']:
                print("[DEBUG] Transfer rejected by user")
                try:
                    conn.sendall(b'REJECTED')
                    print("[DEBUG] Sent REJECTED to sender")
                except Exception as e:
                    print(f"[ERROR] Failed to send rejection: {e}")
                conn.close()
                return
            
            print("[DEBUG] Transfer accepted, starting file receive")
            
            # Send acceptance response to sender
            try:
                conn.sendall(b'ACCEPTED')
                print("[DEBUG] Sent ACCEPTED to sender")
            except Exception as e:
                print(f"[ERROR] Failed to send acceptance: {e}")
                conn.close()
                return
            
            # Receive file
            downloads = self.download_folder
            os.makedirs(downloads, exist_ok=True)
            
            filename = file_info['filename']
            save_path = os.path.join(downloads, filename)
            
            # Handle duplicate names
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
            
            # Connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((target_ip, self.port))
            print("[DEBUG] Connected")
            
            # Send header
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
            
            # Wait for acceptance/rejection response (before sending file)
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
            
            # Dosya gönderimi için timeout'u artır
            sock.settimeout(120)
            print("[DEBUG] Starting file transfer")
            
            # Send file
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
                    
                    # Check for decryption failure from receiver
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
            
            # Check for decryption failure
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
