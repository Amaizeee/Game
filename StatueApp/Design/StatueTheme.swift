import SwiftUI

enum StatueTheme {
    static let background = Color(hex: "#f7f4ee")
    static let surface = Color(hex: "#fffdf8")
    static let ink = Color(hex: "#171412")
    static let mutedInk = Color(hex: "#756d64")
    static let tertiaryBorder = Color.black.opacity(0.14)
    static let cardRadius: CGFloat = 14
    static let sectionSpacing: CGFloat = 28
}

extension Font {
    static func statueBrand(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .custom("Georgia", size: size).weight(weight)
    }

    static func statueBody(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .default)
    }
}

extension View {
    func statueCard() -> some View {
        padding(18)
            .background(StatueTheme.surface)
            .clipShape(RoundedRectangle(cornerRadius: StatueTheme.cardRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: StatueTheme.cardRadius, style: .continuous)
                    .stroke(StatueTheme.tertiaryBorder, lineWidth: 0.5)
            )
    }

    func brandLetterSpacing() -> some View {
        tracking(2)
    }

    func badgeLetterSpacing() -> some View {
        tracking(1)
    }
}

extension Color {
    init(hex: String) {
        let cleaned = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: cleaned).scanHexInt64(&int)

        let red: UInt64
        let green: UInt64
        let blue: UInt64
        switch cleaned.count {
        case 3:
            red = (int >> 8) * 17
            green = ((int >> 4) & 0xF) * 17
            blue = (int & 0xF) * 17
        case 6:
            red = int >> 16
            green = (int >> 8) & 0xFF
            blue = int & 0xFF
        default:
            red = 0
            green = 0
            blue = 0
        }

        self.init(
            .sRGB,
            red: Double(red) / 255,
            green: Double(green) / 255,
            blue: Double(blue) / 255,
            opacity: 1
        )
    }
}
