import SwiftUI
import UserNotifications
import WatchConnectivity

@main
struct ulakApp: App {
    @StateObject private var networkManager = NetworkManager.shared
    @StateObject private var appSettings = AppSettings.shared
    @Environment(\.scenePhase) private var scenePhase

    init() {
        // Bildirim iznini arka planda iste, init'i bloke etme
        DispatchQueue.main.async {
            UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
        }
        
        // Watch Connectivity'yi başlat
        if WCSession.isSupported() {
            let session = WCSession.default
            session.delegate = WatchSessionDelegate.shared
            session.activate()
        }
        
        // ULAK'i otomatik başlat
        DispatchQueue.main.async {
            NetworkManager.shared.start()
            print("🚀 ULAK uygulama başlatıldığında otomatik başlatıldı")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(networkManager)
                .environmentObject(appSettings)
                .preferredColorScheme(.dark)
                .onAppear {
                    setupWatchCallbacks()
                    // ULAK'in çalıştığından emin ol
                    if !networkManager.isRunning {
                        networkManager.start()
                        print("🚀 ULAK ContentView'da başlatıldı")
                    }
                }
        }
        .onChange(of: scenePhase) { newPhase in
            switch newPhase {
            case .active:
                // Uygulama öne geldiğinde ULAK'ı başlat
                if !networkManager.isRunning {
                    networkManager.start()
                    print("🚀 ULAK uygulama aktif olduğunda başlatıldı")
                }
                WatchSessionDelegate.shared.sendStatusUpdate()
            case .background:
                // Arka plana geçtiğinde çalışmaya devam et
                print("🔵 ULAK arka planda çalışıyor")
            case .inactive:
                print("🟡 ULAK inactive")
            @unknown default:
                break
            }
        }
    }
    
    private func setupWatchCallbacks() {
        // Network değişikliklerinde Watch'a bildir
        networkManager.onNewItemReceived = {
            WatchSessionDelegate.shared.sendStatusUpdate()
        }
        
        networkManager.onFileReceived = { item in
            WatchSessionDelegate.shared.sendItemReceived(item)
        }
        
        networkManager.onTextReceived = { item in
            WatchSessionDelegate.shared.sendItemReceived(item)
        }
        
        networkManager.onTransferProgress = { fileName, progress in
            WatchSessionDelegate.shared.sendTransferProgress(
                fileName: fileName,
                progress: progress,
                isTransferring: networkManager.isTransferring
            )
        }
    }
}

// Watch Connectivity Delegate
class WatchSessionDelegate: NSObject, WCSessionDelegate {
    static let shared = WatchSessionDelegate()
    private var pendingTransfers: [String: TransferRequest] = [:]
    
    // Transfer'i kaydet
    func registerTransfer(id: String, request: TransferRequest) {
        pendingTransfers[id] = request
        print("📋 Transfer kaydedildi: \(id) - \(request.name)")
    }
    
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        if activationState == .activated {
            print("✅ Watch session activated")
            
            // ULAK'i otomatik başlat
            DispatchQueue.main.async {
                let networkManager = NetworkManager.shared
                if !networkManager.isRunning {
                    print("🚀 ULAK otomatik başlatılıyor (Watch bağlandı)...")
                    networkManager.start()
                }
                
                // Watch'a bildir
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                    self.sendStatusUpdate()
                }
            }
        }
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) {
        session.activate()
    }
    
    func sessionReachabilityDidChange(_ session: WCSession) {
        print("🔄 Watch reachability changed: \(session.isReachable)")
        
        if session.isReachable {
            print("✅ Watch reachable")
            
            // ULAK'i otomatik başlat
            DispatchQueue.main.async {
                let networkManager = NetworkManager.shared
                if !networkManager.isRunning {
                    print("🚀 ULAK otomatik başlatılıyor (Watch erişilebilir)...")
                    networkManager.start()
                }
                
                // Watch'a bildir
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    self.sendStatusUpdate()
                }
            }
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any], replyHandler: @escaping ([String : Any]) -> Void) {
        DispatchQueue.main.async {
            guard let action = message["action"] as? String else {
                replyHandler(["error": "No action"])
                return
            }
            
            let networkManager = NetworkManager.shared
            let settings = AppSettings.shared
            
            switch action {
            case "getStatus":
                replyHandler(self.getStatusDict())
                
            case "sendText":
                guard let text = message["text"] as? String,
                      let deviceIPs = message["devices"] as? [String] else {
                    print("❌ sendText: Invalid parameters")
                    replyHandler(["error": "Invalid parameters"])
                    return
                }
                
                print("📤 iPhone: Metin gönderiliyor: \(text) → \(deviceIPs)")
                
                let devices = networkManager.discoveredDevices.filter { deviceIPs.contains($0.ip) }
                
                if devices.isEmpty {
                    print("❌ Cihaz bulunamadı: \(deviceIPs)")
                    replyHandler(["error": "No devices found"])
                    return
                }
                
                print("✅ \(devices.count) cihaza gönderiliyor...")
                networkManager.sendText(text, to: devices)
                
                replyHandler(["success": true, "deviceCount": devices.count])
                
            case "toggleService":
                if networkManager.isRunning {
                    networkManager.stop()
                } else {
                    networkManager.start()
                }
                replyHandler(["isRunning": networkManager.isRunning])
                
            case "updateSettings":
                if let deviceName = message["deviceName"] as? String {
                    settings.deviceName = deviceName
                }
                if let useEncryption = message["useEncryption"] as? Bool {
                    settings.useEncryption = useEncryption
                }
                if let encryptionPassword = message["encryptionPassword"] as? String {
                    settings.encryptionPassword = encryptionPassword
                }
                if let autoAccept = message["autoAccept"] as? Bool {
                    settings.autoAccept = autoAccept
                }
                if let useNotifications = message["useNotifications"] as? Bool {
                    settings.useNotifications = useNotifications
                }
                replyHandler(["success": true])
                
            case "clearHistory":
                networkManager.clearReceivedItems()
                replyHandler(["success": true])

            case "deleteItem":
                guard let itemId = message["itemId"] as? String else {
                    replyHandler(["error": "Invalid parameters"])
                    return
                }
                networkManager.deleteReceivedItem(id: itemId)
                replyHandler(["success": true])

            case "rescanDevices":
                networkManager.rescanDevices()
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
                    replyHandler(self.getStatusDict())
                }

            case "acceptTransfer":
                guard let transferId = message["transferId"] as? String,
                      let transfer = self.pendingTransfers[transferId] else {
                    replyHandler(["error": "Transfer not found"])
                    return
                }
                print("✅ Watch transfer'i kabul etti: \(transferId)")
                transfer.accept?()
                self.pendingTransfers.removeValue(forKey: transferId)
                replyHandler(["success": true])
                
            case "rejectTransfer":
                guard let transferId = message["transferId"] as? String,
                      let transfer = self.pendingTransfers[transferId] else {
                    replyHandler(["error": "Transfer not found"])
                    return
                }
                print("❌ Watch transfer'i reddetti: \(transferId)")
                transfer.reject?()
                self.pendingTransfers.removeValue(forKey: transferId)
                replyHandler(["success": true])
                
            default:
                replyHandler(["error": "Unknown action"])
            }
        }
    }
    
    func sendStatusUpdate() {
        guard WCSession.default.isReachable else { return }
        let message: [String: Any] = [
            "type": "statusUpdate"
        ].merging(getStatusDict()) { $1 }
        WCSession.default.sendMessage(message, replyHandler: nil)
    }
    
    func sendItemReceived(_ item: ReceivedItem) {
        guard WCSession.default.isReachable else { return }
        var itemDict: [String: Any] = [
            "id": item.id,
            "type": item.type == .text ? "text" : "file",
            "name": item.name,
            "sender": item.sender,
            "timestamp": item.timestamp.timeIntervalSince1970 * 1000
        ]
        if let text = item.textContent {
            itemDict["textContent"] = text
        }
        let message: [String: Any] = [
            "type": "itemReceived",
            "item": itemDict
        ]
        WCSession.default.sendMessage(message, replyHandler: nil)
    }
    
    func sendTransferProgress(fileName: String, progress: Double, isTransferring: Bool) {
        guard WCSession.default.isReachable else { return }
        let message: [String: Any] = [
            "type": "transferProgress",
            "fileName": fileName,
            "progress": progress,
            "isTransferring": isTransferring
        ]
        WCSession.default.sendMessage(message, replyHandler: nil)
    }
    
    private func getStatusDict() -> [String: Any] {
        let networkManager = NetworkManager.shared
        let settings = AppSettings.shared
        
        let devices = networkManager.discoveredDevices.map { device in
            ["name": device.name, "ip": device.ip]
        }
        
        let items = networkManager.receivedItems.prefix(20).map { item -> [String: Any] in
            var dict: [String: Any] = [
                "id": item.id,
                "type": item.type == .text ? "text" : "file",
                "name": item.name,
                "sender": item.sender,
                "timestamp": item.timestamp.timeIntervalSince1970 * 1000
            ]
            if let text = item.textContent {
                dict["textContent"] = text
            }
            return dict
        }
        
        return [
            "isRunning": networkManager.isRunning,
            "localIP": networkManager.localIP,
            "deviceName": settings.deviceName,
            "useEncryption": settings.useEncryption,
            "autoAccept": settings.autoAccept,
            "useNotifications": settings.useNotifications,
            "devices": devices,
            "receivedItems": items
        ]
    }
}
