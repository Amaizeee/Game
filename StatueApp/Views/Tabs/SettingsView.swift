import SwiftUI

struct SettingsView: View {
    let viewModel: StatueViewModel

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: StatueTheme.sectionSpacing) {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Moi")
                            .font(.statueBrand(34))
                            .brandLetterSpacing()
                        Text("Paramètres sobres pour garder le profil, l'abonnement et les notifications à jour.")
                            .font(.statueBody(15))
                            .foregroundStyle(StatueTheme.mutedInk)
                    }

                    SettingsSection(title: "Profil") {
                        SettingsRow(title: "Modifier profil", detail: "Photo, bio, ville")
                        SettingsRow(title: "Carte membre", detail: viewModel.currentMember.memberNumberDisplay)
                    }

                    SettingsSection(title: "Abonnement") {
                        SettingsRow(title: "Gérer abonnement", detail: viewModel.currentMember.tier.monthlyPrice)
                        SettingsRow(title: "Upgrade ou downgrade", detail: "Bronze, Gold, Diamond")
                    }

                    SettingsSection(title: "Compte") {
                        SettingsRow(title: "Notifications", detail: "Fil, chat, events")
                        SettingsRow(title: "Déconnexion", detail: "Sortir de Statue")
                    }
                }
                .padding(24)
            }
            .background(StatueTheme.background.ignoresSafeArea())
            .toolbar(.hidden, for: .navigationBar)
        }
    }
}

private struct SettingsSection<Content: View>: View {
    let title: String
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionHeader(title: title)
            VStack(spacing: 0) {
                content
            }
            .background(StatueTheme.surface)
            .clipShape(RoundedRectangle(cornerRadius: StatueTheme.cardRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: StatueTheme.cardRadius, style: .continuous)
                    .stroke(StatueTheme.tertiaryBorder, lineWidth: 0.5)
            )
        }
    }
}

private struct SettingsRow: View {
    let title: String
    let detail: String

    var body: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.statueBody(15, weight: .medium))
                    .foregroundStyle(StatueTheme.ink)
                Text(detail)
                    .font(.statueBody(12))
                    .foregroundStyle(StatueTheme.mutedInk)
            }
            Spacer()
            Image(systemName: "chevron.right")
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(StatueTheme.mutedInk)
        }
        .padding(16)
        .overlay(alignment: .bottom) {
            Rectangle()
                .fill(StatueTheme.tertiaryBorder)
                .frame(height: 0.5)
                .padding(.leading, 16)
        }
    }
}

#Preview {
    SettingsView(viewModel: StatueViewModel())
}
