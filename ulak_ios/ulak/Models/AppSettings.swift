import Foundation
import Combine

#if os(iOS)
import UIKit
#elseif os(watchOS)
import WatchKit
#endif

class AppSettings: ObservableObject {
    static let shared = AppSettings()

    private let defaults = UserDefaults.standard
    private let suiteDefaults = UserDefaults(suiteName: "ulak_prefs") ?? UserDefaults.standard

    @Published var deviceName: String {
        didSet { suiteDefaults.set(deviceName, forKey: "device_name") }
    }

    @Published var useEncryption: Bool {
        didSet { suiteDefaults.set(useEncryption, forKey: "use_encryption") }
    }

    @Published var encryptionPassword: String {
        didSet { suiteDefaults.set(encryptionPassword, forKey: "encryption_password") }
    }
    
    var effectiveEncryptionPassword: String {
        encryptionPassword.isEmpty ? "ulak_default_key" : encryptionPassword
    }

    @Published var useNotifications: Bool {
        didSet { suiteDefaults.set(useNotifications, forKey: "use_notifications") }
    }

    @Published var autoAccept: Bool {
        didSet { suiteDefaults.set(autoAccept, forKey: "auto_accept") }
    }

    private init() {
        #if os(iOS)
        let defaultName = UIDevice.current.name
        #elseif os(watchOS)
        let defaultName = WKInterfaceDevice.current().name
        #else
        let defaultName = "ULAK Device"
        #endif
        
        deviceName = suiteDefaults.string(forKey: "device_name") ?? defaultName
        useEncryption = suiteDefaults.bool(forKey: "use_encryption")
        encryptionPassword = suiteDefaults.string(forKey: "encryption_password") ?? "ulak_default_key"
        useNotifications = suiteDefaults.object(forKey: "use_notifications") as? Bool ?? true
        autoAccept = suiteDefaults.bool(forKey: "auto_accept")
    }
}
