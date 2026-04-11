import SwiftUI

struct WatchReceiveView: View {
    @EnvironmentObject var connectivity: WatchConnectivityManager
    @State private var refreshTimer: Timer?
    @State private var isScanning = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 10) {
                    Text("Durum")
                        .font(.headline)

                    // iPhone bağlantı + ULAK durumu
                    HStack(spacing: 8) {
                        VStack(spacing: 2) {
                            Image(systemName: connectivity.isReachable ? "iphone" : "iphone.slash")
                                .foregroundColor(connectivity.isReachable ? .green : .red)
                                .font(.title3)
                            Text(connectivity.isReachable ? "Bağlı" : "Bağlı Değil")
                                .font(.system(size: 9))
                                .foregroundColor(.secondary)
                        }

                        Divider().frame(height: 30)

                        VStack(spacing: 2) {
                            Circle()
                                .fill(connectivity.isRunning ? Color.green : Color.red)
                                .frame(width: 12, height: 12)
                            Text(connectivity.isRunning ? "Aktif" : "Pasif")
                                .font(.system(size: 9))
                                .foregroundColor(.secondary)
                        }

                        if connectivity.isReachable && !connectivity.localIP.isEmpty && connectivity.localIP != "0.0.0.0" {
                            Divider().frame(height: 30)
                            VStack(spacing: 2) {
                                Image(systemName: "network")
                                    .foregroundColor(.blue)
                                    .font(.caption)
                                Text(connectivity.localIP)
                                    .font(.system(size: 8))
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                    .padding(8)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)

                    // Transfer durumu
                    if connectivity.isTransferring {
                        VStack(spacing: 4) {
                            Text(connectivity.transferFileName)
                                .font(.caption2)
                                .lineLimit(1)
                            ProgressView(value: connectivity.transferProgress)
                            Text("\(Int(connectivity.transferProgress * 100))%")
                                .font(.caption2)
                        }
                        .padding(8)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                    }

                    // Başlat/Durdur
                    if connectivity.isReachable {
                        Button {
                            connectivity.toggleService()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                                connectivity.requestStatus()
                            }
                        } label: {
                            Label(
                                connectivity.isRunning ? "Durdur" : "Başlat",
                                systemImage: connectivity.isRunning ? "stop.circle.fill" : "play.circle.fill"
                            )
                            .font(.caption)
                            .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(connectivity.isRunning ? .red : .green)

                        Divider()

                        // Cihazlar başlık + Tara
                        HStack {
                            Text("Cihazlar (\(connectivity.discoveredDevices.count))")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Spacer()
                            Button {
                                isScanning = true
                                connectivity.rescanDevices()
                                DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                                    isScanning = false
                                }
                            } label: {
                                if isScanning {
                                    ProgressView()
                                        .scaleEffect(0.7)
                                } else {
                                    Image(systemName: "arrow.clockwise")
                                        .font(.caption2)
                                }
                            }
                            .buttonStyle(.bordered)
                            .disabled(isScanning)
                        }

                        if connectivity.discoveredDevices.isEmpty {
                            Text("Cihaz bulunamadı")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                                .padding(.vertical, 4)
                        } else {
                            VStack(spacing: 4) {
                                ForEach(connectivity.discoveredDevices) { device in
                                    HStack(spacing: 6) {
                                        Image(systemName: "laptopcomputer")
                                            .font(.caption2)
                                            .foregroundColor(.green)
                                        VStack(alignment: .leading, spacing: 1) {
                                            Text(device.name)
                                                .font(.caption2)
                                                .lineLimit(1)
                                            Text(device.ip)
                                                .font(.system(size: 8))
                                                .foregroundColor(.secondary)
                                        }
                                        Spacer()
                                        Circle()
                                            .fill(Color.green)
                                            .frame(width: 6, height: 6)
                                    }
                                    .padding(.vertical, 4)
                                    .padding(.horizontal, 6)
                                    .background(Color.green.opacity(0.08))
                                    .cornerRadius(6)
                                }
                            }
                        }

                        // Alınan öğe sayısı
                        if !connectivity.receivedItems.isEmpty {
                            Divider()
                            HStack {
                                Image(systemName: "tray.fill")
                                    .font(.caption2)
                                    .foregroundColor(.orange)
                                Text("\(connectivity.receivedItems.count) öğe alındı")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                            }
                        }
                    } else {
                        VStack(spacing: 8) {
                            Image(systemName: "iphone.slash")
                                .font(.largeTitle)
                                .foregroundColor(.secondary)
                            Text("iPhone'u açın")
                                .font(.caption)
                            Text("ULAK uygulamasını çalıştırın")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                        .padding()
                    }
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 8)
            }
            .onAppear {
                startRefreshTimer()
            }
            .onDisappear {
                stopRefreshTimer()
            }
        }
    }

    private func startRefreshTimer() {
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { _ in
            if connectivity.isReachable {
                connectivity.requestStatus()
            }
        }
    }

    private func stopRefreshTimer() {
        refreshTimer?.invalidate()
        refreshTimer = nil
    }
}
