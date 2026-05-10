// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Statue",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .executable(name: "Statue", targets: ["StatueApp"])
    ],
    targets: [
        .executableTarget(
            name: "StatueApp",
            path: "StatueApp"
        )
    ]
)
