# ULAK - Yerel Ağ Dosya Paylaşımı

<div align="center">

![ULAK Logo](img/logo.png)

**Yerel Ağınızda Hızlı, Güvenli ve Kolay Dosya Paylaşımı**

[![Lisans: MIT](https://img.shields.io/badge/Lisans-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Android-blue)](https://github.com/cektor/ULAK)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://www.python.org/)

[English](README.md) | [Türkçe](README-tr.md)

</div>

---

## 🌟 ULAK Nedir?

**ULAK**, yerel ağınızdaki cihazlar arasında dosya, metin ve pano içeriği paylaşmanızı sağlayan modern, çapraz platform bir uygulamadır - **internet bağlantısı gerekmez**. Tüm platformlar için AirDrop gibi düşünün!

### Neden ULAK?

- 🚀 **Yıldırım Hızı** - Yerel ağ üzerinden doğrudan cihazdan cihaza transfer
- 🔒 **Güvenli** - Hassas dosyalar için isteğe bağlı AES-256 şifreleme
- 🎯 **Basit** - Yapılandırma gerekmez, sadece kurun ve paylaşın
- 🌐 **Çapraz Platform** - Windows, Linux ve Android'de çalışır
- 📱 **Otomatik Keşif** - Ağınızdaki cihazları otomatik bulur
- 💯 **Ücretsiz ve Açık Kaynak** - Reklam yok, takip yok, abonelik yok

---

## ✨ Temel Özellikler

### 📁 Dosya ve Klasör Paylaşımı
- Tek veya çoklu dosya gönderimi
- Tüm içeriğiyle klasör paylaşımı
- Sürükle & bırak desteği
- Gerçek zamanlı transfer ilerlemesi
- Çoklu cihaza eşzamanlı transfer

### 💬 Metin ve Pano Paylaşımı
- Cihazlar arası metin mesajı gönderimi
- Pano içeriği paylaşımı (metin ve resim)
- Alınan içeriği otomatik panoya kopyalama
- Hızlı notlar ve linkler için mükemmel

### 📸 Ekran Görüntüsü Paylaşımı
- Ekran görüntüsü al ve anında paylaş
- Hızlı kısayol: `Ctrl+Shift+S`
- Hazırlık için 3 saniyelik geri sayım
- Seçili cihazlara doğrudan gönderim

### 🔐 Güvenlik Özellikleri
- **AES-256 Şifreleme** - Dosyalarınız için askeri düzey şifreleme
- **Parola Koruması** - Özel şifreleme parolaları belirleyin
- **Sadece Yerel Ağ** - Verileriniz ağınızdan çıkmaz
- **Bulut Depolama Yok** - Doğrudan eşler arası transfer

### 🎨 Kullanıcı Deneyimi
- **Modern Karanlık Tema** - Gözleri yormaz
- **Sezgisel Arayüz** - Öğrenme eğrisi yok
- **Sistem Tepsisi Desteği** - Arka planda çalışır
- **Bildirimler** - Dosyalar geldiğinde haberdar olun
- **Transfer Geçmişi** - Alınan dosyaları takip edin

---

## 📱 Platform Desteği

### 🪟 Windows
- **Sürüm**: Windows 10/11
- **Kurulum**: Taşınabilir çalıştırılabilir dosya veya yükleyici
- **Özellikler**: Yerel Windows entegrasyonu ile tam özellik seti

### 🐧 Linux
- **Dağıtımlar**: Ubuntu, Debian, Fedora, Arch ve daha fazlası
- **Kurulum**: Sistem paketi veya bağımsız Python scripti
- **Özellikler**: Masaüstü entegrasyonu ile tam özellik seti
- **İkon**: Sistem teması ile düzgün entegre

### 🤖 Android
- **Sürüm**: Android 6.0+
- **Kurulum**: APK indirme
- **Özellikler**: Tüm temel özelliklerle mobil optimize arayüz
- **İzinler**: Sadece ağ erişimi

---

## 🚀 Hızlı Başlangıç

### Yeni Başlayanlar İçin

1. **ULAK'ı İndirin** platformunuz için:
   - Windows: [Releases](https://github.com/cektor/ULAK/releases) sayfasından `.exe` indirin
   - Linux: `install.sh` dosyasını indirin ve çalıştırın
   - Android: `.apk` dosyasını indirin ve kurun

2. **Uygulamayı kurun** dosya paylaşmak istediğiniz tüm cihazlara

3. **ULAK'ı açın** her cihazda - birbirlerini otomatik keşfedecekler

4. **Paylaşmaya Başlayın**:
   - Listeden bir cihaz seçin
   - "Dosya Gönder"e tıklayın veya dosyaları sürükleyip bırakın
   - Alıcı kabul etmek için bildirim alacak
   - Tamamlandı! Dosyalar transfer edildi

### İleri Düzey Kullanıcılar İçin

#### Linux Kurulumu
```bash
# Repository'yi klonlayın
git clone https://github.com/cektor/ULAK.git
cd ULAK/localsend_app/ulak_linux

# Bağımlılıkları yükleyin
pip3 install -r requirements.txt

# Sistem geneline kurun
sudo bash install.sh

# Çalıştırın
ulak
```

#### Windows Kurulumu
```bash
# Repository'yi klonlayın
git clone https://github.com/cektor/ULAK.git
cd ULAK/localsend_app

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Çalıştırın
python main.py
```

---

## 📖 Nasıl Kullanılır

### Dosya Gönderme

1. **ULAK'ı açın** hem gönderici hem alıcı cihazlarda
2. **Bekleyin** cihazların "Yakındaki Cihazlar" listesinde görünmesi için (2-3 saniye)
3. **Seçin** hedef cihaz(lar)ı - birden fazla seçebilirsiniz!
4. **Dosyaları seçin**:
   - Dosyalar için "📄 Dosya Gönder"e tıklayın
   - Klasörler için "📁 Klasör Gönder"e tıklayın
   - Veya basitçe dosyaları pencereye **sürükleyip bırakın**
5. **"📤 Gönder" butonuna tıklayın**
6. **Alıcı transferi kabul eder**
7. **Tamamlandı!** Dosyalar İndirilenler klasörüne kaydedildi

### Metin Gönderme

1. Hedef cihazı seçin
2. "💬 Metin Gönder"e tıklayın
3. Mesajınızı yazın veya yapıştırın
4. "📨 Gönder"e tıklayın
5. Alıcı mesajla birlikte bir popup alır

### Pano Gönderme

1. Metni veya resmi panoya kopyalayın
2. Hedef cihazı seçin
3. "📋 Panoyu Gönder"e tıklayın
4. Alıcı otomatik olarak panosuna alır

### Ekran Görüntüsü Alma ve Paylaşma

1. Hedef cihazı seçin
2. "📸 Ekran Görüntüsü"ne tıklayın veya `Ctrl+Shift+S` tuşlayın
3. 3 saniyelik geri sayımı bekleyin
4. Ekran görüntüsü alınır ve otomatik gönderilir

---

## 🔧 Yapılandırma

### Ayarlar Paneli

"⚙️ Ayarlar" sekmesinden ayarlara erişin:

#### Cihaz Ayarları
- **Cihaz Adı**: Cihazınızın diğerlerine nasıl göründüğünü değiştirin
- **Port**: Varsayılan 53317 (gerekirse değiştirin)
- **Broadcast Port**: Varsayılan 53318 (cihaz keşfi için)

#### Güvenlik Ayarları
- **🔒 AES-256 Şifrelemeyi Etkinleştir**: Şifrelemeyi aç/kapat
- **Şifreleme Parolası**: Özel parola belirleyin (tüm cihazlarda aynı)
- **Not**: Cihazlar iletişim kurmak için aynı parolayı kullanmalı

#### Bildirim Ayarları
- **🔔 Bildirimleri Göster**: Dosyalar geldiğinde bildirim alın
- **🔊 Ses Çal**: Transfer tamamlandığında sesli bildirim
- **📥 Sistem Tepsisinde Çalıştır**: Kapatmak yerine tepsiye küçült

#### Pano Ayarları
- **📋 Panoyu Otomatik Kopyala**: Alınan metin/resimleri otomatik panoya kopyala

#### İndirme Ayarları
- **📁 İndirme Klasörü**: Alınan dosyaların nereye kaydedileceğini seçin

---

## 🔐 Güvenlik ve Gizlilik

### ULAK Neler Yapar
- ✅ Dosyaları yerel ağdaki cihazlar arasında doğrudan transfer eder
- ✅ İsteğe bağlı olarak dosyaları AES-256 ile şifreler
- ✅ Ayarları cihazınızda yerel olarak saklar
- ✅ UDP broadcast kullanarak cihazları otomatik keşfeder

### ULAK Neler YAPMAZ
- ❌ İnternete bağlanmaz
- ❌ Dosyaları herhangi bir sunucuya yüklemez
- ❌ Kişisel veri toplamaz
- ❌ Kullanımınızı takip etmez
- ❌ Hesap veya giriş gerektirmez

### Şifreleme Detayları
- **Algoritma**: AES-256-CBC
- **Anahtar Türetme**: Parolanın SHA-256 hash'i
- **Varsayılan Anahtar**: Parola belirlenmezse kullanılır
- **Uyumluluk**: Tüm platformlarda çalışır

---

## 🌐 Ağ Gereksinimleri

### İhtiyacınız Olanlar
- Tüm cihazlar **aynı yerel ağda** olmalı (aynı WiFi/router)
- **53317 ve 53318 portları** açık olmalı (genellikle otomatik)
- İnternet bağlantısı gerekmez

### Güvenlik Duvarı Yapılandırması
Cihazlar birbirini görmüyorsa:

**Windows**:
```
ULAK'ı Windows Güvenlik Duvarından izin verin
```

**Linux**:
```bash
sudo ufw allow 53317/tcp
sudo ufw allow 53318/udp
```

**Android**:
```
Genellikle yapılandırma gerekmez
```

---

## 📦 Kurulum Detayları

### Windows
- **Taşınabilir**: Sadece `.exe` dosyasını çalıştırın
- **Yükleyici**: Yakında
- **Gereksinimler**: Windows 10/11, ek yazılım gerekmez

### Linux
- **Sistem Kurulumu**: `/usr/share/ulak/` konumuna kurulur
- **İkon**: `/usr/share/pixmaps/ulaklo.png` konumuna yerleştirilir
- **Desktop Entry**: Uygulama menüsüne eklenir
- **Yapılandırma**: `~/.config/ulak/` içinde saklanır
- **Gereksinimler**: Python 3.8+, PyQt5, cryptography

### Android
- **APK Kurulumu**: Ayarlardan "Bilinmeyen Kaynaklar"ı etkinleştirin
- **İzinler**: Sadece ağ erişimi
- **Depolama**: İndirilenler klasörü
- **Gereksinimler**: Android 6.0+

---

## 🛠️ Teknik Detaylar

### Mimari
- **Protokol**: Dosya transferi için TCP/IP, cihaz keşfi için UDP
- **Port**: 53317 (transfer), 53318 (keşif)
- **Buffer Boyutu**: 8192 byte
- **Şifreleme**: PKCS7 padding ile AES-256-CBC
- **UI Framework**: PyQt5 (Masaüstü), Android SDK (Mobil)

### Dosya Transfer Süreci
1. Gönderici UDP 53318 portunda varlığını yayınlar
2. Alıcı gönderiyi keşfeder ve cihaz listesine ekler
3. Kullanıcı dosya ve hedef cihazı seçer
4. Gönderici dosya meta verilerini gönderir (ad, boyut, şifreleme durumu)
5. Alıcı kabul/reddet dialogu gösterir
6. Kabul edilirse, dosya TCP 53317 portu üzerinden transfer edilir
7. İlerleme gerçek zamanlı gösterilir
8. Alıcı dosyayı İndirilenler klasörüne kaydeder

### Klasör Transferi
- Klasörler transfer öncesi otomatik ziplenır
- Alıcı tarafta otomatik çıkartılır
- Klasör yapısı korunur
- Transfer öncesi dosya/klasör sayısı gösterilir

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Nasıl yardımcı olabilirsiniz:

### Hata Bildirme
- [GitHub Issues](https://github.com/cektor/ULAK/issues) üzerinden issue açın
- İşletim sisteminizi, ULAK sürümünüzü ve hatayı tekrarlama adımlarını ekleyin

### Özellik İstekleri
- "enhancement" etiketi ile issue açın
- Özelliği ve neden yararlı olacağını açıklayın

### Kod Katkıları
1. Repository'yi fork edin
2. Özellik branch'i oluşturun
3. Değişikliklerinizi yapın
4. Kapsamlı test edin
5. Pull request gönderin

### Çeviri
- ULAK'ı dilinize çevirmeye yardım edin
- `/locales/` içindeki dil dosyalarını düzenleyin

---

## 📝 Değişiklik Günlüğü

### Sürüm 1.0.0 (Güncel)
- ✨ İlk sürüm
- 📁 Dosya ve klasör paylaşımı
- 💬 Metin mesajlaşma
- 📋 Pano paylaşımı
- 📸 Ekran görüntüsü paylaşımı
- 🔒 AES-256 şifreleme
- 🌐 Çapraz platform desteği (Windows, Linux, Android)
- 🎨 Modern karanlık tema arayüz
- 📊 Gerçek zamanlı transfer ilerlemesi
- 🔔 Bildirimler ve sesler

---

## 🆘 Sorun Giderme

### Cihazlar Görünmüyor
1. Tüm cihazların aynı ağda olduğundan emin olun
2. Güvenlik duvarı ayarlarını kontrol edin
3. Her iki cihazda da ULAK'ı yeniden başlatmayı deneyin
4. 53317 ve 53318 portlarının engellenm ediğini doğrulayın

### Transfer Başarısız Oluyor
1. Her iki cihazda şifreleme ayarlarının eşleştiğini kontrol edin
2. Alıcıda yeterli disk alanı olduğundan emin olun
3. Şifrelemeyi geçici olarak devre dışı bırakmayı deneyin
4. Ağ kararlılığını kontrol edin

### Şifreleme Parolası Sorunları
1. Her iki cihaz da tamamen aynı parolayı kullanmalı
2. Parola büyük/küçük harf duyarlıdır
3. Varsayılan şifrelemeyi kullanmak için boş bırakın
4. Parolayı değiştirin: Ayarlar → Kaydet → ULAK'ı yeniden başlat

### Linux'ta İkon Görünmüyor
1. Çalıştırın: `sudo gtk-update-icon-cache -f -t /usr/share/pixmaps`
2. Oturumu kapatıp açın
3. İkonun var olduğunu kontrol edin: `ls /usr/share/pixmaps/ulaklo.png`

---

## 📞 Destek ve İletişim

### Yardım Alın
- 📧 E-posta: info@algyazilim.com
- 🌐 Web Sitesi: https://algyazilim.com
- 🐱 GitHub: https://github.com/cektor/ULAK
- 📖 Dokümantasyon: [Wiki](https://github.com/cektor/ULAK/wiki)

### Topluluk
- Hata bildirin: [GitHub Issues](https://github.com/cektor/ULAK/issues)
- Özellik isteyin: [GitHub Discussions](https://github.com/cektor/ULAK/discussions)
- Güncellemeleri takip edin: [GitHub Releases](https://github.com/cektor/ULAK/releases)

---

## 👨💻 Katkıda Bulunanlar

### Geliştirici
**Fatih ÖNDER (CekToR)**
- GitHub: [@cektor](https://github.com/cektor)
- E-posta: fatih@algyazilim.com

### Şirket
**ALG Yazılım & Elektronik Inc.**
- Web Sitesi: https://algyazilim.com
- E-posta: info@algyazilim.com

### Özel Teşekkürler
- Mükemmel UI framework'ü için PyQt5 ekibine
- Cryptography kütüphanesi katkıda bulunanlarına
- Tüm beta test kullanıcılarına ve erken kullanıcılara

---

## 📄 Lisans

ULAK, **MIT Lisansı** altında lisanslanmıştır.

```
MIT Lisansı

Telif Hakkı (c) 2025 ALG Yazılım & Elektronik Inc.

İşbu belge ile, bu yazılımın ve ilgili dokümantasyon dosyalarının ("Yazılım")
bir kopyasını alan herhangi bir kişiye, Yazılım'ı kullanma, kopyalama, değiştirme,
birleştirme, yayınlama, dağıtma, alt lisanslama ve/veya satma hakları da dahil
olmak üzere, Yazılım'da herhangi bir kısıtlama olmaksızın işlem yapma izni
ücretsiz olarak verilir.

Yukarıdaki telif hakkı bildirimi ve bu izin bildirimi, Yazılım'ın tüm
kopyalarına veya önemli bölümlerine dahil edilecektir.

YAZILIM "OLDUĞU GİBİ" SAĞLANIR, TİCARİ ELVERİŞLİLİK, BELİRLİ BİR AMACA
UYGUNLUK VE İHLAL ETMEME GARANTİLERİ DAHİL ANCAK BUNLARLA SINIRLI OLMAMAK
ÜZERE, AÇIK VEYA ZIMNİ HİÇBİR GARANTİ OLMAKSIZIN. HİÇBİR DURUMDA YAZARLAR
VEYA TELİF HAKKI SAHİPLERİ, YAZILIM'DAN VEYA YAZILIM'IN KULLANIMI VEYA
DİĞER İŞLEMLERİNDEN KAYNAKLANAN HERHANGİ BİR İDDİA, HASAR VEYA DİĞER
YÜKÜMLÜLÜKLERDEN SORUMLU TUTULAMAZ.
```

---

## 🌟 Yıldız Geçmişi

ULAK'ı yararlı buluyorsanız, lütfen GitHub'da yıldız vermeyi düşünün! ⭐

---

<div align="center">

**ALG Yazılım tarafından ❤️ ile yapıldı**

[İndir](https://github.com/cektor/ULAK/releases) • [Dokümantasyon](https://github.com/cektor/ULAK/wiki) • [Hata Bildir](https://github.com/cektor/ULAK/issues) • [Özellik İste](https://github.com/cektor/ULAK/discussions)

</div>
