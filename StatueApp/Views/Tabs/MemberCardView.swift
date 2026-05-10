import SwiftUI

struct MemberCardView: View {
    let member: Member

    var body: some View {
        ScrollView {
            VStack(spacing: StatueTheme.sectionSpacing) {
                LuxuryMemberCard(member: member)
                    .padding(.top, 20)

                HStack(spacing: 12) {
                    StatBlock(value: "\(member.postsCount)", label: "Posts")
                    StatBlock(value: "\(member.linksCount)", label: "Liens")
                }

                SectionHeader(title: "Archives", subtitle: "Grille des posts passés")

                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 10), count: 3), spacing: 10) {
                    ForEach(0..<9, id: \.self) { index in
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(index.isMultiple(of: 2) ? member.tier.cardBackground : StatueTheme.surface)
                            .aspectRatio(1, contentMode: .fit)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12, style: .continuous)
                                    .stroke(member.tier.border.opacity(0.6), lineWidth: 0.5)
                            )
                    }
                }
            }
            .padding(24)
        }
        .background(StatueTheme.background.ignoresSafeArea())
    }
}

private struct LuxuryMemberCard: View {
    let member: Member

    var body: some View {
        VStack(alignment: .leading, spacing: 26) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("STATUE")
                        .font(.statueBrand(18))
                        .brandLetterSpacing()
                    Text("MEMBER")
                        .font(.statueBrand(11))
                        .brandLetterSpacing()
                }
                Spacer()
                TierBadge(tier: member.tier)
            }

            Spacer(minLength: 18)

            QRImage(url: member.publicProfileURL, tint: member.tier.foreground)
                .frame(width: 132, height: 132)

            Spacer(minLength: 18)

            VStack(alignment: .leading, spacing: 10) {
                Text(member.username)
                    .font(.statueBrand(26))
                    .brandLetterSpacing()
                Text(member.memberNumberDisplay)
                    .font(.statueBrand(13))
                    .brandLetterSpacing()
                Text(member.publicProfileURL.absoluteString)
                    .font(.statueBody(12))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
        }
        .foregroundStyle(member.tier.foreground)
        .frame(maxWidth: .infinity, minHeight: 430, alignment: .leading)
        .padding(26)
        .background(member.tier.cardBackground)
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(member.tier.border, lineWidth: 0.7)
        )
    }
}

private struct StatBlock: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 8) {
            Text(value)
                .font(.statueBrand(30))
                .brandLetterSpacing()
            Text(label.uppercased())
                .font(.statueBody(10, weight: .semibold))
                .badgeLetterSpacing()
                .foregroundStyle(StatueTheme.mutedInk)
        }
        .frame(maxWidth: .infinity)
        .statueCard()
    }
}

#Preview {
    MemberCardView(member: .preview)
}
