import threading
from PyQt5.QtCore import QObject, pyqtSignal

# ── Easily updatable parameters ───────────────────────────────────────────────
TARGET_URL = "https://algsoft.net.tr/uygulama-duyurulari/"
ELEMENT_ID = "ulak_windows_web"
# ─────────────────────────────────────────────────────────────────────────────

try:
    import requests
    from bs4 import BeautifulSoup
    _DEPS_AVAILABLE = True
except ImportError:
    _DEPS_AVAILABLE = False


class AnnouncementManager(QObject):
    """Arka planda TARGET_URL'den ELEMENT_ID'li öğeyi çeker ve sinyal fırlatır."""
    announcement_fetched = pyqtSignal(str)   # başarı — metin
    fetch_failed = pyqtSignal()              # hata / boş içerik

    def __init__(self):
        super().__init__()

    def fetch_async(self):
        """Arka plan thread'inde duyuruyu çek."""
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
