import SwiftUI

struct RootTabView: View {
    @State var viewModel: StatueViewModel

    var body: some View {
        TabView {
            FeedView(viewModel: viewModel)
                .tabItem { Label("Fil", systemImage: "square.stack") }

            MemberCardView(member: viewModel.currentMember)
                .tabItem { Label("Carte", systemImage: "creditcard") }

            ProfileView(viewModel: viewModel)
                .tabItem { Label("Profil", systemImage: "person.crop.square") }

            SettingsView(viewModel: viewModel)
                .tabItem { Label("Moi", systemImage: "gearshape") }
        }
        .tint(StatueTheme.ink)
    }
}

#Preview {
    RootTabView(viewModel: StatueViewModel())
}
