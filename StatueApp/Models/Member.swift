import Foundation

struct Member: Identifiable, Equatable {
    let id: UUID
    var username: String
    var fullName: String
    var bio: String
    var city: String
    var tier: MembershipTier
    let memberNumber: Int
    var postsCount: Int
    var linksCount: Int

    var memberNumberDisplay: String {
        "N° " + String(format: "%04d", memberNumber)
    }

    var publicProfileURL: URL {
        URL(string: "https://statue.app/member/\(username)")!
    }

    static let preview = Member(
        id: UUID(),
        username: "claire.martin",
        fullName: "Claire Martin",
        bio: "VC associate. Art contemporain, SaaS vertical et tables calmes.",
        city: "Paris",
        tier: .gold,
        memberNumber: 247,
        postsCount: 38,
        linksCount: 126
    )
}
