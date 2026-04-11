import SwiftUI

@main
struct UlakWatchApp: App {
    @StateObject private var connectivity = WatchConnectivityManager.shared
    
    var body: some Scene {
        WindowGroup {
            WatchMainView()
                .environmentObject(connectivity)
                .onAppear {
                    // iPhone'dan durum bilgisi al
                    connectivity.requestStatus()
                }
        }
    }
}
