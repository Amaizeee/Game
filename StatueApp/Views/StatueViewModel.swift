import Observation
import SwiftUI

@Observable
final class StatueViewModel {
    var currentMember: Member
    var selectedTier: MembershipTier
    var posts: [StatuePost]

    init(
        currentMember: Member = .preview,
        posts: [StatuePost] = StatuePost.samples
    ) {
        self.currentMember = currentMember
        self.selectedTier = currentMember.tier
        self.posts = posts
    }

    func updateTier(_ tier: MembershipTier) {
        selectedTier = tier
        currentMember.tier = tier
    }
}
