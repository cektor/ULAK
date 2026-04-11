import Foundation
import WatchConnectivity

class PhoneConnectivityManager: NSObject, ObservableObject {
    static let shared = PhoneConnectivityManager()
    
    private override init() {
        super.init()
        if WCSession.isSupported() {
            let session = WCSession.default
            session.delegate = self
            session.activate()
        }
    }
    
    // Watch'a durum bilgisi gönder
    func sendStatusUpdate() {
        guard WCSession.default.isReachable else { return }
        
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
        
        let message: [String: Any] = [
            "type": "statusUpdate",
            "isRunning": networkManager.isRunning,
            "localIP": networkManager.localIP,
            "deviceName": settings.deviceName,
            "useEncryption": settings.useEncryption,
            "autoAccept": settings.autoAccept,
            "devices": devices,
            "receivedItems": items
        ]
        
        WCSession.default.sendMessage(message, replyHandler: nil) { error in
            print("Status gönderme hatası: \(error.localizedDescription)")
        }
    }
    
    // Watch'a cihaz güncellemesi gönder
    func sendDeviceUpdate() {
        guard WCSession.default.isReachable else { return }
        
        let devices = NetworkManager.shared.discoveredDevices.map { device in
            ["name": device.name, "ip": device.ip]
        }
        
        let message: [String: Any] = [
            "type": "deviceUpdate",
            "devices": devices
        ]
        
        WCSession.default.sendMessage(message, replyHandler: nil)
    }
    
    // Watch'a yeni öğe bilgisi gönder
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
    
    // Watch'a transfer progress gönder
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
}

extension PhoneConnectivityManager: WCSessionDelegate {
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        if activationState == .activated {
            DispatchQueue.main.async {
                self.sendStatusUpdate()
            }
        }
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {}
    
    func sessionDidDeactivate(_ session: WCSession) {
        session.activate()
    }
    
    func sessionReachabilityDidChange(_ session: WCSession) {
        if session.isReachable {
            DispatchQueue.main.async {
                self.sendStatusUpdate()
            }
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any], replyHandler: @escaping ([String : Any]) -> Void) {
        DispatchQueue.main.async {
            guard let action = message["action"] as? String else {
                replyHandler(["error": "No action specified"])
                return
            }
            
            let networkManager = NetworkManager.shared
            let settings = AppSettings.shared
            
            switch action {
            case "getStatus":
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
                
                replyHandler([
                    "isRunning": networkManager.isRunning,
                    "localIP": networkManager.localIP,
                    "deviceName": settings.deviceName,
                    "useEncryption": settings.useEncryption,
                    "autoAccept": settings.autoAccept,
                    "devices": devices,
                    "receivedItems": items
                ])
                
            case "sendText":
                guard let text = message["text"] as? String,
                      let deviceIPs = message["devices"] as? [String] else {
                    replyHandler(["error": "Invalid parameters"])
                    return
                }
                
                let devices = networkManager.discoveredDevices.filter { deviceIPs.contains($0.ip) }
                networkManager.sendText(text, to: devices)
                replyHandler(["success": true])
                
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
                replyHandler(["success": true])
                
            case "clearHistory":
                networkManager.clearReceivedItems()
                replyHandler(["success": true])
                
            default:
                replyHandler(["error": "Unknown action"])
            }
        }
    }
}
