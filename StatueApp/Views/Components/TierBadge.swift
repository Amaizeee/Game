import SwiftUI

struct TierBadge: View {
    let tier: MembershipTier

    var body: some View {
        Text(tier.displayName.uppercased())
            .font(.statueBody(10, weight: .semibold))
            .badgeLetterSpacing()
            .foregroundStyle(tier.foreground)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(tier.cardBackground)
            .clipShape(Capsule())
            .overlay(
                Capsule()
                    .stroke(tier.border, lineWidth: 0.5)
            )
    }
}

#Preview {
    HStack {
        ForEach(MembershipTier.allCases) { tier in
            TierBadge(tier: tier)
        }
    }
    .padding()
}
