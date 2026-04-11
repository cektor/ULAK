import SwiftUI

struct AboutView: View {
    @Environment(\.dismiss) var dismiss

var body: some View {
        NavigationStack {
            ZStack {
                UlakTheme.backgroundGradient.ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 20) {
                        VStack(spacing: 12) {
                            Image("logo")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 110, height: 110)
                                .clipShape(RoundedRectangle(cornerRadius: 24))
                                .shadow(color: UlakTheme.neonBlue.opacity(0.8), radius: 15)

                            Text("ULAK")
                                .font(.system(size: 36, weight: .bold))
                                .foregroundColor(UlakTheme.neonBlue)
                                .shadow(color: UlakTheme.neonBlue.opacity(0.8), radius: 10)

                            Text("Güvenli Dosya Paylaşımı")
                                .font(.system(size: 16))
                                .foregroundColor(UlakTheme.textSecondary)

                            Text("Versiyon 1.0.5 - IOS")
                                .font(.caption)
                                .foregroundColor(UlakTheme.neonPurple)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background(Capsule().fill(UlakTheme.neonPurple.opacity(0.2)))
                        }
                        .padding(.top, 20)

                        VStack(alignment: .leading, spacing: 12) {
                            Text("Hakkında")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(UlakTheme.neonBlue)

                            Text("ULAK, yerel ağ üzerinden güvenli ve hızlı dosya paylaşımı yapmanızı sağlayan Türk yapımı açık kaynaklı bir uygulamadır. İnternet bağlantısı gerektirmeden, aynı Wi-Fi ağındaki cihazlar arasında anlık dosya ve metin transferi yapabilirsiniz.")
                                .font(.system(size: 13))
                                .foregroundColor(UlakTheme.textPrimary)
                                .lineSpacing(4)
                        }
                        .padding(16)
                        .neonCard()

                        // Yerli ve Milli kart
                        HStack(spacing: 14) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.red.opacity(0.15))
                                    .frame(width: 52, height: 52)
                                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.red.opacity(0.7), lineWidth: 1.5))
                                Text("🇹🇷")
                                    .font(.system(size: 26))
                            }
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Yerli ve Milli Proje")
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(UlakTheme.neonCyan)
                                Text("TÜRK Yazılımcılar Tarafından Geliştirilmiştir.")
                                    .font(.system(size: 13, weight: .semibold))
                                    .foregroundColor(UlakTheme.neonCyan)
                            }
                            Spacer()
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 14)
                        .frame(maxWidth: .infinity)
                        .background(RoundedRectangle(cornerRadius: 14).fill(UlakTheme.cardBackground))
                        .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.red.opacity(0.8), lineWidth: 1.5))

                        VStack(spacing: 12) {
                            Text("Geliştirici")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(UlakTheme.neonBlue)

                            Text("Fatih ÖNDER (CekToR)")
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(UlakTheme.textPrimary)

                            Text("ALGSoft Inc. © 2026")
                                .font(.caption)
                                .foregroundColor(UlakTheme.textSecondary)

                            Text("MIT Lisansı")
                                .font(.caption)
                                .foregroundColor(UlakTheme.neonGreen)

                            HStack(spacing: 20) {
                                Link(destination: URL(string: "https://github.com/cektor/ulak")!) {
                                    Label("GitHub", systemImage: "link")
                                        .font(.caption)
                                        .foregroundColor(UlakTheme.neonBlue)
                                }
                                Link(destination: URL(string: "https://ulak.algsoft.net.tr/")!) {
                                    Label("Web Sitesi", systemImage: "globe")
                                        .font(.caption)
                                        .foregroundColor(UlakTheme.neonBlue)
                                }
                            }
                        }
                        .padding(20)
                        .frame(maxWidth: .infinity)
                        .neonCard()

                        Spacer(minLength: 40)
                    }
                    .padding(.horizontal, 16)
                }
            }
            .navigationTitle("Hakkında")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarColorScheme(.dark)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Kapat") { dismiss() }
                        .foregroundColor(UlakTheme.neonBlue)
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}
