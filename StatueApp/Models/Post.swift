import SwiftUI

struct StatuePost: Identifiable, Equatable {
    let id: UUID
    var author: Member
    var title: String
    var body: String
    var tier: MembershipTier
    var dateLabel: String
    var accentColor: Color

    static let samples: [StatuePost] = [
        StatuePost(
            id: UUID(),
            author: .preview,
            title: "Private dinner notes",
            body: "Trois introductions utiles autour de la santé préventive, à conserver pour le prochain salon.",
            tier: .bronze,
            dateLabel: "Aujourd'hui",
            accentColor: Color(hex: "#b87333")
        ),
        StatuePost(
            id: UUID(),
            author: .preview,
            title: "Gold room signal",
            body: "Un opérateur fintech cherche deux profils growth senior pour une expansion discrète en Europe.",
            tier: .gold,
            dateLabel: "Hier",
            accentColor: Color(hex: "#d4af37")
        ),
        StatuePost(
            id: UUID(),
            author: Member.preview.withTier(.diamond),
            title: "Diamond briefing",
            body: "Allocation limitée pour un événement IRL autour des family offices nouvelle génération.",
            tier: .diamond,
            dateLabel: "Vendredi",
            accentColor: Color(hex: "#1a1a1a")
        )
    ]
}

extension Member {
    func withTier(_ tier: MembershipTier) -> Member {
        var copy = self
        copy.tier = tier
        return copy
    }
}
