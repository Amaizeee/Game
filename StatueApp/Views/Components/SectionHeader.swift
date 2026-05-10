import SwiftUI

struct SectionHeader: View {
    let title: String
    var subtitle: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(.statueBrand(13))
                .brandLetterSpacing()
                .foregroundStyle(StatueTheme.ink)

            if let subtitle {
                Text(subtitle)
                    .font(.statueBody(13))
                    .foregroundStyle(StatueTheme.mutedInk)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
