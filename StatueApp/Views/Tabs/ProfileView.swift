import SwiftUI

struct ProfileView: View {
    let viewModel: StatueViewModel

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: StatueTheme.sectionSpacing) {
                profileHeader

                SectionHeader(title: "Accès", subtitle: "Votre abonnement déverrouille les salons et privilèges associés.")

                VStack(spacing: 12) {
                    ForEach(MembershipTier.allCases) { tier in
                        TierPlanRow(
                            tier: tier,
                            isSelected: viewModel.currentMember.tier == tier,
                            onSelect: { viewModel.updateTier(tier) }
                        )
                    }
                }
            }
            .padding(24)
        }
        .background(StatueTheme.background.ignoresSafeArea())
    }

    private var profileHeader: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack(alignment: .center, spacing: 16) {
                ZStack {
                    Circle()
                        .fill(viewModel.currentMember.tier.cardBackground)
                    Text(String(viewModel.currentMember.fullName.prefix(1)))
                        .font(.statueBrand(34))
                        .foregroundStyle(viewModel.currentMember.tier.foreground)
                }
                .frame(width: 82, height: 82)
                .overlay(
                    Circle()
                        .stroke(viewModel.currentMember.tier == .gold ? Color(hex: "#d4af37") : viewModel.currentMember.tier.border, lineWidth: 1)
                )

                VStack(alignment: .leading, spacing: 8) {
                    Text(viewModel.currentMember.fullName)
                        .font(.statueBrand(24))
                    Text("@\(viewModel.currentMember.username)")
                        .font(.statueBody(14))
                        .foregroundStyle(StatueTheme.mutedInk)
                    TierBadge(tier: viewModel.currentMember.tier)
                }
            }

            Text(viewModel.currentMember.bio)
                .font(.statueBody(15))
                .lineSpacing(4)
                .foregroundStyle(StatueTheme.mutedInk)

            Text(viewModel.currentMember.city.uppercased())
                .font(.statueBody(10, weight: .semibold))
                .badgeLetterSpacing()
                .foregroundStyle(StatueTheme.ink)
        }
        .statueCard()
    }
}

private struct TierPlanRow: View {
    let tier: MembershipTier
    let isSelected: Bool
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    VStack(alignment: .leading, spacing: 5) {
                        Text(tier.displayName)
                            .font(.statueBrand(22))
                            .foregroundStyle(StatueTheme.ink)
                        Text(tier.monthlyPrice)
                            .font(.statueBody(13, weight: .medium))
                            .foregroundStyle(StatueTheme.mutedInk)
                    }
                    Spacer()
                    if isSelected {
                        Text("ACTIF")
                            .font(.statueBody(10, weight: .semibold))
                            .badgeLetterSpacing()
                            .foregroundStyle(tier.foreground)
                    }
                }

                VStack(alignment: .leading, spacing: 8) {
                    ForEach(tier.includedFeatures, id: \.self) { feature in
                        Text(feature)
                            .font(.statueBody(13))
                            .foregroundStyle(StatueTheme.mutedInk)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(18)
            .background(StatueTheme.surface)
            .clipShape(RoundedRectangle(cornerRadius: StatueTheme.cardRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: StatueTheme.cardRadius, style: .continuous)
                    .stroke(isSelected ? tier.foreground : StatueTheme.tertiaryBorder, lineWidth: isSelected ? 1 : 0.5)
            )
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    ProfileView(viewModel: StatueViewModel())
}
