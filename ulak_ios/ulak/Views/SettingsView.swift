import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appSettings: AppSettings
    @State private var showAbout = false

    var body: some View {
        NavigationStack {
            ZStack {
                UlakTheme.backgroundGradient.ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 16) {
                        deviceCard
                        securityCard
                        transferCard
                        notificationCard
                        aboutCard
                        footerCard
                        downloadCard
                        Spacer(minLength: 40)
                    }
                    .padding(16)
                }
            }
            .navigationTitle("Ayarlar")
            .navigationBarTitleDisplayMode(.large)
            .toolbarColorScheme(.dark)
        }
        .sheet(isPresented: $showAbout) {
            AboutView()
        }
    }

    // MARK: - Device Card

    private var deviceCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label("Cihaz Ayarları", systemImage: "iphone.badge.play")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(UlakTheme.neonBlue)

            VStack(alignment: .leading, spacing: 6) {
                Text("Cihaz Adı")
                    .font(.caption)
                    .foregroundColor(UlakTheme.textSecondary)
                TextField("Cihaz adını girin", text: $appSettings.deviceName)
                    .textFieldStyle(UlakTextFieldStyle())
            }
        }
        .padding(16)
        .neonCard()
    }

    // MARK: - Security Card

    private var securityCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label("Güvenlik", systemImage: "lock.shield.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(UlakTheme.neonBlue)

            Toggle(isOn: $appSettings.useEncryption) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("AES-256 Şifreleme")
                        .font(.system(size: 14))
                        .foregroundColor(UlakTheme.textPrimary)
                    Text("Dosya ve metinleri şifrele")
                        .font(.caption)
                        .foregroundColor(UlakTheme.textSecondary)
                }
            }
            .tint(UlakTheme.neonBlue)

            if appSettings.useEncryption {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Şifreleme Parolası")
                        .font(.caption)
                        .foregroundColor(UlakTheme.textSecondary)
                    SecureField("Parola girin (boş = varsayılan)", text: $appSettings.encryptionPassword)
                        .textFieldStyle(UlakTextFieldStyle())
                    Text("⚠️ Aynı parolayı tüm cihazlarda kullanın")
                        .font(.caption2)
                        .foregroundColor(UlakTheme.neonPink)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(16)
        .neonCard()
        .animation(.easeInOut(duration: 0.3), value: appSettings.useEncryption)
    }

    // MARK: - Transfer Card

    private var transferCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label("Transfer Ayarları", systemImage: "arrow.up.arrow.down.circle.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(UlakTheme.neonBlue)

            Toggle(isOn: $appSettings.autoAccept) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Otomatik Kabul")
                        .font(.system(size: 14))
                        .foregroundColor(UlakTheme.textPrimary)
                    Text("Dosyaları onay istemeden al")
                        .font(.caption)
                        .foregroundColor(UlakTheme.textSecondary)
                }
            }
            .tint(UlakTheme.neonBlue)
        }
        .padding(16)
        .neonCard()
    }

    // MARK: - Notification Card

    private var notificationCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label("Bildirimler", systemImage: "bell.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(UlakTheme.neonBlue)

            Toggle(isOn: $appSettings.useNotifications) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Bildirimler")
                        .font(.system(size: 14))
                        .foregroundColor(UlakTheme.textPrimary)
                    Text("Dosya alındığında bildirim gönder")
                        .font(.caption)
                        .foregroundColor(UlakTheme.textSecondary)
                }
            }
            .tint(UlakTheme.neonBlue)
        }
        .padding(16)
        .neonCard()
    }

    // MARK: - About Card

    private var aboutCard: some View {
        VStack(spacing: 12) {
            Button(action: { showAbout = true }) {
                HStack {
                    Label("Hakkında", systemImage: "info.circle.fill")
                        .foregroundColor(UlakTheme.textPrimary)
                    Spacer()
                    Image(systemName: "chevron.right")
                        .foregroundColor(UlakTheme.textSecondary)
                }
                .font(.system(size: 14))
            }
            .buttonStyle(PlainButtonStyle())

            Divider().background(UlakTheme.neonBlue.opacity(0.3))

            Link(destination: URL(string: "https://ulak.algsoft.net.tr/")!) {
                HStack {
                    Label("Web Sitesi", systemImage: "globe")
                        .foregroundColor(UlakTheme.textPrimary)
                    Spacer()
                    Image(systemName: "arrow.up.right")
                        .foregroundColor(UlakTheme.textSecondary)
                }
                .font(.system(size: 14))
            }
        }
        .padding(16)
        .neonCard()
    }

    // MARK: - Download Card

    private var downloadCard: some View {
        VStack(spacing: 12) {
            Label("Diğer Platformlar", systemImage: "arrow.down.circle.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(UlakTheme.neonBlue)

            Text("Windows · MacOS · Linux · Android")
                .font(.caption)
                .foregroundColor(UlakTheme.textSecondary)

            Link(destination: URL(string: "https://ulak.algsoft.net.tr")!) {
                HStack {
                    Image(systemName: "arrow.down.to.line")
                    Text("İndir")
                        .font(.system(size: 14, weight: .semibold))
                }
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(UlakTheme.neonBlue)
                .clipShape(RoundedRectangle(cornerRadius: 10))
            }
        }
        .padding(16)
        .neonCard()
    }

    // MARK: - Footer Card

    private var footerCard: some View {
        VStack(spacing: 8) {
            Image("logo")
                .resizable()
                .scaledToFit()
                .frame(width: 56, height: 56)
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .shadow(color: UlakTheme.neonBlue.opacity(0.6), radius: 8)
            Text("ULAK")
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(UlakTheme.neonBlue)
            Text("Fatih ÖNDER (CekToR) / ALGSoft Inc.")
                .font(.caption)
                .foregroundColor(UlakTheme.textSecondary)
            Text("Türkiye'nin güvenli dosya paylaşım uygulaması")
                .font(.caption2)
                .foregroundColor(UlakTheme.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(20)
        .neonCard()
    }
}

// MARK: - Custom TextField Style

struct UlakTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(RoundedRectangle(cornerRadius: 8).fill(UlakTheme.backgroundDark.opacity(0.6)))
            .overlay(RoundedRectangle(cornerRadius: 8).stroke(UlakTheme.neonBlue.opacity(0.4), lineWidth: 1))
            .foregroundColor(UlakTheme.textPrimary)
            .font(.system(size: 14))
    }
}
