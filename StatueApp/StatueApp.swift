import SwiftUI

@main
struct StatueApp: App {
    var body: some Scene {
        WindowGroup {
            RootTabView(viewModel: StatueViewModel())
        }
    }
}
