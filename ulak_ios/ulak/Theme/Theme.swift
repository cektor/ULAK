import SwiftUI

struct UlakTheme {
    static let backgroundDark = Color(hex: "0a0e27")
    static let backgroundGradientStart = Color(hex: "0f1729")
    static let backgroundGradientEnd = Color(hex: "1a1f3a")
    static let cardBackground = Color(hex: "1a1f3a")

    static let neonBlue = Color(hex: "00d4ff")
    static let neonCyan = Color(hex: "00fff9")
    static let neonPurple = Color(hex: "b24bf3")
    static let neonPink = Color(hex: "ff2e97")
    static let neonGreen = Color(hex: "39ff14")

    static let textPrimary = Color(hex: "e8f1ff")
    static let textSecondary = Color(hex: "8b9dc3")

    static let buttonGradient = LinearGradient(
        colors: [neonBlue, Color(hex: "7c3aed"), neonPurple],
        startPoint: .leading,
        endPoint: .trailing
    )

    static let blueButtonGradient = LinearGradient(
        colors: [neonBlue, Color(hex: "003580")],
        startPoint: .leading,
        endPoint: .trailing
    )

    static let redButtonGradient = LinearGradient(
        colors: [neonPink, Color(hex: "cc0000")],
        startPoint: .leading,
        endPoint: .trailing
    )

    static let greenButtonGradient = LinearGradient(
        colors: [neonGreen, Color(hex: "006400")],
        startPoint: .leading,
        endPoint: .trailing
    )

    static let backgroundGradient = LinearGradient(
        colors: [backgroundGradientStart, backgroundDark, backgroundGradientEnd],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )

    static let cardGradient = LinearGradient(
        colors: [cardBackground, Color(hex: "0f1729")],
        startPoint: .top,
        endPoint: .bottom
    )
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3:
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6:
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8:
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(.sRGB, red: Double(r) / 255, green: Double(g) / 255, blue: Double(b) / 255, opacity: Double(a) / 255)
    }
}

// MARK: - Reusable View Modifiers

struct NeonCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(UlakTheme.cardBackground)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(UlakTheme.neonBlue.opacity(0.4), lineWidth: 1)
                    )
                    .shadow(color: UlakTheme.neonBlue.opacity(0.2), radius: 8, x: 0, y: 0)
            )
    }
}

struct GradientButtonStyle: ButtonStyle {
    let gradient: LinearGradient

    init(gradient: LinearGradient = UlakTheme.buttonGradient) {
        self.gradient = gradient
    }

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 15, weight: .semibold))
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(gradient)
            )
            .opacity(configuration.isPressed ? 0.8 : 1.0)
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
    }
}

extension View {
    func neonCard() -> some View {
        modifier(NeonCardModifier())
    }
}

// MARK: - iPad-safe UIActivityViewController presenter

func presentActivityVC(_ vc: UIActivityViewController, sourceView: UIView? = nil) {
    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
          let root = scene.windows.first?.rootViewController else { return }

    if let popover = vc.popoverPresentationController {
        let view = sourceView ?? root.view!
        popover.sourceView = view
        popover.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.midY, width: 0, height: 0)
        popover.permittedArrowDirections = []
    }
    root.present(vc, animated: true)
}
