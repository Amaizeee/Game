import CoreImage.CIFilterBuiltins
import SwiftUI

struct QRImage: View {
    let url: URL
    let tint: Color

    private let context = CIContext()
    private let filter = CIFilter.qrCodeGenerator()

    var body: some View {
        generatedImage
            .interpolation(.none)
            .resizable()
            .scaledToFit()
            .padding(14)
            .background(Color.white)
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(tint.opacity(0.24), lineWidth: 0.5)
            )
            .accessibilityLabel("QR code du profil public")
    }

    private var generatedImage: Image {
        filter.message = Data(url.absoluteString.utf8)
        filter.correctionLevel = "M"

        guard let outputImage = filter.outputImage else {
            return Image(systemName: "qrcode")
        }

        let transformed = outputImage.transformed(by: CGAffineTransform(scaleX: 12, y: 12))
        guard let cgImage = context.createCGImage(transformed, from: transformed.extent) else {
            return Image(systemName: "qrcode")
        }

        return Image(decorative: cgImage, scale: 1)
    }
}
