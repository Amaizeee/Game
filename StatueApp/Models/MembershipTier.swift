import SwiftUI

enum MembershipTier: String, CaseIterable, Identifiable {
    case bronze
    case gold
    case diamond

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .bronze: return "Bronze"
        case .gold: return "Gold"
        case .diamond: return "Diamond"
        }
    }

    var monthlyPrice: String {
        switch self {
        case .bronze: return "5 €/mois"
        case .gold: return "50 €/mois"
        case .diamond: return "100 €/mois"
        }
    }

    var cardBackground: Color {
        switch self {
        case .bronze: return Color(hex: "#2a1f17")
        case .gold: return Color(hex: "#1a1407")
        case .diamond: return Color(hex: "#f5f5f5")
        }
    }

    var foreground: Color {
        switch self {
        case .bronze: return Color(hex: "#b87333")
        case .gold: return Color(hex: "#d4af37")
        case .diamond: return Color(hex: "#1a1a1a")
        }
    }

    var border: Color {
        switch self {
        case .bronze: return Color(hex: "#3a2a1d")
        case .gold: return Color(hex: "#2a2008")
        case .diamond: return Color(hex: "#c0c0c0")
        }
    }

    var includedFeatures: [String] {
        switch self {
        case .bronze:
            return ["Carte membre et QR", "Fil Bronze", "Chat Bronze", "1 post par jour"]
        case .gold:
            return ["Tout Bronze", "Fil Gold", "Chat Gold", "Archives", "Cadre doré profil"]
        case .diamond:
            return ["Tout Gold", "Fil Diamond", "DM ouverts", "Events IRL", "Salon privé"]
        }
    }
}
