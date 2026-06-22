import AppKit
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let imageDir = root.appendingPathComponent("images")
let outputDir = root.appendingPathComponent("contact_sheets")
try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

let files = try FileManager.default.contentsOfDirectory(at: imageDir, includingPropertiesForKeys: nil)
    .filter { $0.lastPathComponent.hasPrefix("bini_body_") && $0.pathExtension.lowercased() == "png" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

let oldSheets = try FileManager.default.contentsOfDirectory(at: outputDir, includingPropertiesForKeys: nil)
    .filter { $0.lastPathComponent.hasPrefix("contact_sheet_") && $0.pathExtension.lowercased() == "jpg" }
for sheet in oldSheets {
    try FileManager.default.removeItem(at: sheet)
}

let thumbW: CGFloat = 220
let thumbH: CGFloat = 330
let labelH: CGFloat = 28
let gap: CGFloat = 18
let margin: CGFloat = 24
let cols = 5
let rows = 5
let sheetW = margin * 2 + CGFloat(cols) * thumbW + CGFloat(cols - 1) * gap
let sheetH = margin * 2 + CGFloat(rows) * (thumbH + labelH) + CGFloat(rows - 1) * gap

let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .center
paragraph.lineBreakMode = .byTruncatingMiddle
let labelAttrs: [NSAttributedString.Key: Any] = [
    .font: NSFont.monospacedSystemFont(ofSize: 13, weight: .regular),
    .foregroundColor: NSColor(calibratedWhite: 0.82, alpha: 1),
    .paragraphStyle: paragraph
]

func drawAspectFit(_ image: NSImage, in rect: NSRect) {
    let size = image.size
    guard size.width > 0 && size.height > 0 else { return }
    let scale = min(rect.width / size.width, rect.height / size.height)
    let drawSize = NSSize(width: size.width * scale, height: size.height * scale)
    let drawRect = NSRect(
        x: rect.midX - drawSize.width / 2,
        y: rect.midY - drawSize.height / 2,
        width: drawSize.width,
        height: drawSize.height
    )
    image.draw(in: drawRect, from: .zero, operation: .sourceOver, fraction: 1)
}

func saveJPEG(_ image: NSImage, to url: URL) throws {
    guard let tiff = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiff),
          let jpeg = bitmap.representation(using: .jpeg, properties: [.compressionFactor: 0.9]) else {
        throw NSError(domain: "ContactSheet", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unable to encode JPEG"])
    }
    try jpeg.write(to: url)
}

let imagesPerSheet = cols * rows
let sheetCount = Int(ceil(Double(files.count) / Double(imagesPerSheet)))

for sheetIndex in 0..<sheetCount {
    let start = sheetIndex * imagesPerSheet
    let slice = Array(files[start..<min(start + imagesPerSheet, files.count)])
    let canvas = NSImage(size: NSSize(width: sheetW, height: sheetH))
    canvas.lockFocus()
    NSColor(calibratedRed: 0.05, green: 0.06, blue: 0.07, alpha: 1).setFill()
    NSRect(x: 0, y: 0, width: sheetW, height: sheetH).fill()

    for (i, file) in slice.enumerated() {
        guard let image = NSImage(contentsOf: file) else { continue }
        let col = i % cols
        let row = i / cols
        let x = margin + CGFloat(col) * (thumbW + gap)
        let y = sheetH - margin - CGFloat(row + 1) * (thumbH + labelH) - CGFloat(row) * gap
        let frame = NSRect(x: x, y: y + labelH, width: thumbW, height: thumbH)
        NSColor(calibratedRed: 0.09, green: 0.10, blue: 0.12, alpha: 1).setFill()
        frame.fill()
        drawAspectFit(image, in: frame)
        let labelRect = NSRect(x: x, y: y, width: thumbW, height: labelH)
        file.lastPathComponent.draw(in: labelRect.insetBy(dx: 4, dy: 6), withAttributes: labelAttrs)
    }

    canvas.unlockFocus()
    let output = outputDir.appendingPathComponent(String(format: "contact_sheet_%03d.jpg", sheetIndex + 1))
    try saveJPEG(canvas, to: output)
    print("Wrote \(output.path)")
}
