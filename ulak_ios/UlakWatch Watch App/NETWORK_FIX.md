# 🔧 Apple Watch Network Keşfi Sorunu Çözümü

## Sorun
- ❌ Apple Watch'ta "Hiçbir cihaz bulunamadı" görünüyor
- ❌ Diğer cihazlar Apple Watch'ı görmüyor

## Çözüm

### 1️⃣ Info.plist Ayarları (ÖNEMLİ!)

Xcode'da:
1. Target → **UlakWatch Watch App** seçin
2. **Info** tab'ına gidin
3. **Custom watchOS Target Properties** altında "+" butonuna tıklayın

Aşağıdaki ayarları ekleyin:

#### A) Local Network İzni
```
Key: Privacy - Local Network Usage Description
Type: String
Value: ULAK yerel ağdaki cihazları keşfetmek için ağ erişimi gerektirir.
```

#### B) Bonjour Services
```
Key: Bonjour services
Type: Array
  Item 0 (String): _ulak._tcp
  Item 1 (String): _ulak._udp
```

#### C) Local Network Bonjour Services (Kritik!)
```
Key: NSLocalNetworkUsageDescription
Type: String
Value: ULAK yerel ağdaki cihazları keşfetmek için ağ erişimi gerektirir.
```

#### D) Bonjour Services (Alternatif Key)
```
Key: NSBonjourServices
Type: Array
  Item 0 (String): _ulak._tcp
  Item 1 (String): _ulak._udp
```

### 2️⃣ Capabilities

Target → **UlakWatch Watch App** → **Signing & Capabilities**:

1. "+ Capability" tıklayın
2. **Background Modes** ekleyin
3. ✅ **Network** seçeneğini işaretleyin

### 3️⃣ Entitlements (Gerekirse)

Eğer hala çalışmıyorsa:

1. Target → UlakWatch Watch App → Signing & Capabilities
2. "+ Capability" → **Multipath**
3. "+ Capability" → **Network Extensions** (opsiyonel)

### 4️⃣ Build Settings

Target → UlakWatch Watch App → Build Settings:

**Search: "Other Linker Flags"**
```
-framework Network
-framework Combine
```

### 5️⃣ Simulator vs Gerçek Cihaz

⚠️ **ÖNEMLİ:** Simulator'da network keşfi çalışmayabilir!

**Gerçek Apple Watch'ta test edin:**
1. Apple Watch'u iPhone'a bağlayın (paired)
2. iPhone ve Watch aynı WiFi'da olmalı
3. Xcode → Window → Devices and Simulators
4. Apple Watch'u seçin
5. Scheme: UlakWatch Watch App
6. Destination: Gerçek Apple Watch
7. ⌘R → Run

### 6️⃣ Network İzinleri Kontrolü

Watch uygulaması ilk çalıştığında:
- ✅ "Local Network" izni istemelidir
- ✅ İzni verin

Eğer izin istenmiyorsa:
1. iPhone'da Settings → Privacy & Security → Local Network
2. ULAK uygulamasını bulun
3. ✅ İzni açın

### 7️⃣ Firewall Kontrolü

**iPhone'da:**
- Settings → General → VPN & Device Management
- Firewall kapalı olmalı veya ULAK'a izin verilmeli

**Mac'te:**
- System Settings → Network → Firewall
- ULAK'a izin verilmeli

### 8️⃣ WiFi Kontrolü

Tüm cihazlar:
- ✅ Aynı WiFi ağında
- ✅ 2.4GHz veya 5GHz (ikisi de çalışır)
- ❌ VPN kapalı
- ❌ Hotspot değil

### 9️⃣ Debug

Watch uygulamasında debug için:

```swift
// WatchReceiveView.swift içinde
var body: some View {
    VStack {
        Text("IP: \(networkManager.localIP)")
            .font(.caption2)
        Text("Running: \(networkManager.isRunning ? "Yes" : "No")")
            .font(.caption2)
        Text("Devices: \(networkManager.discoveredDevices.count)")
            .font(.caption2)
        // ... rest of code
    }
}
```

### 🔟 Manuel Test

Terminal'den test edin:

**Mac'te (UDP broadcast gönder):**
```bash
echo '{"type":"announce","name":"Test Mac","ip":"192.168.1.100"}' | nc -u -b 255.255.255.255 53318
```

**Watch'ta görmeli:**
- "Test Mac" cihazı listede görünmeli

## Hızlı Kontrol Listesi

- [ ] Info tab → NSLocalNetworkUsageDescription eklendi
- [ ] Info tab → NSBonjourServices array eklendi
- [ ] Capabilities → Background Modes → Network aktif
- [ ] Gerçek Apple Watch'ta test ediliyor (simulator değil)
- [ ] iPhone ve Watch aynı WiFi'da
- [ ] Local Network izni verildi
- [ ] VPN kapalı
- [ ] Firewall ULAK'a izin veriyor
- [ ] networkManager.start() çağrıldı
- [ ] Clean build yapıldı (⌘⇧K)

## Sorun Devam Ediyorsa

1. **Xcode Console'u kontrol edin:**
   ```
   View → Debug Area → Activate Console (⌘⇧Y)
   ```
   
2. **Network hatalarını arayın:**
   - "Permission denied"
   - "Network unreachable"
   - "Address already in use"

3. **Port çakışması:**
   ```bash
   # Mac'te kontrol et
   lsof -i :53318
   lsof -i :53317
   ```

4. **Watch'ı yeniden başlat:**
   - Yan düğmeye basılı tut
   - Power Off
   - Tekrar aç

5. **iPhone'u yeniden başlat**

6. **Uygulamayı sil ve yeniden yükle**

## Test Senaryosu

1. **Mac ULAK'ı çalıştır**
2. **iPhone ULAK'ı çalıştır**
3. **Watch ULAK'ı çalıştır**
4. **Watch'ta "Al" sayfasına git**
5. **"Cihazlar" bölümünde Mac ve iPhone görünmeli**
6. **Mac'te Watch görünmeli**
7. **iPhone'da Watch görünmeli**

## Başarı Kriterleri

✅ Watch'ta IP adresi görünüyor (0.0.0.0 değil)
✅ Watch "Aktif" durumda
✅ Watch en az 1 cihaz görüyor
✅ Diğer cihazlar Watch'ı görüyor
✅ Metin gönderme/alma çalışıyor

---

**Not:** Simulator'da network keşfi çalışmaz. Mutlaka gerçek Apple Watch'ta test edin!
