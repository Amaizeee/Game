import SwiftUI

struct FeedView: View {
    let viewModel: StatueViewModel

    private var visiblePosts: [StatuePost] {
        viewModel.posts.filter { post in
            switch viewModel.currentMember.tier {
            case .bronze:
                return post.tier == .bronze
            case .gold:
                return post.tier == .bronze || post.tier == .gold
            case .diamond:
                return true
            }
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: StatueTheme.sectionSpacing) {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Statue")
                            .font(.statueBrand(34))
                            .brandLetterSpacing()
                        Text("Un réseau fermé pour signaux rares, liens qualifiés et conversations calmes.")
                            .font(.statueBody(15))
                            .foregroundStyle(StatueTheme.mutedInk)
                    }

                    SectionHeader(
                        title: "Fil membre",
                        subtitle: "Votre rang ouvre les salons \(viewModel.currentMember.tier.displayName)."
                    )

                    VStack(spacing: 14) {
                        ForEach(visiblePosts) { post in
                            PostCard(post: post)
                        }
                    }
                }
                .padding(24)
            }
            .background(StatueTheme.background.ignoresSafeArea())
            .navigationTitle("")
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}

private struct PostCard: View {
    let post: StatuePost

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .center) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(post.author.username)
                        .font(.statueBody(14, weight: .semibold))
                    Text(post.dateLabel)
                        .font(.statueBody(12))
                        .foregroundStyle(StatueTheme.mutedInk)
                }
                Spacer()
                TierBadge(tier: post.tier)
            }

            Rectangle()
                .fill(StatueTheme.tertiaryBorder)
                .frame(height: 0.5)

            VStack(alignment: .leading, spacing: 8) {
                Text(post.title)
                    .font(.statueBrand(20))
                    .foregroundStyle(StatueTheme.ink)
                Text(post.body)
                    .font(.statueBody(15))
                    .lineSpacing(4)
                    .foregroundStyle(StatueTheme.mutedInk)
            }
        }
        .statueCard()
    }
}

#Preview {
    FeedView(viewModel: StatueViewModel())
}
