import AppKit
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let selectedDir = root.appendingPathComponent("selected")
let reviewsDir = root.appendingPathComponent("reviews")
let contactSheetsDir = root.appendingPathComponent("contact_sheets")
try FileManager.default.createDirectory(at: reviewsDir, withIntermediateDirectories: true)
try FileManager.default.createDirectory(at: contactSheetsDir, withIntermediateDirectories: true)

let keep = [
    "026", "027", "028", "029", "030",
    "031", "032", "033", "034", "035",
    "037", "038", "039", "040",
    "042", "043", "044", "045", "046", "047", "049", "050",
    "051", "052", "053", "054", "055", "056", "057", "058", "059", "060",
    "061", "062", "063", "064", "065", "066", "067", "068", "069", "070",
    "071", "072", "073", "074", "075", "076", "077", "078", "079", "080",
]

let files = keep.map { selectedDir.appendingPathComponent("bini_body_\($0).png") }
    .filter { FileManager.default.fileExists(atPath: $0.path) }

let thumbW: CGFloat = 180
let thumbH: CGFloat = 270
let labelH: CGFloat = 24
let gap: CGFloat = 12
let margin: CGFloat = 20
let cols = 4
let rows = Int(ceil(Double(files.count) / Double(cols)))
let sheetW = margin * 2 + CGFloat(cols) * thumbW + CGFloat(cols - 1) * gap
let sheetH = margin * 2 + CGFloat(rows) * (thumbH + labelH) + CGFloat(max(rows - 1, 0)) * gap

let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .center
paragraph.lineBreakMode = .byTruncatingMiddle
let labelAttrs: [NSAttributedString.Key: Any] = [
    .font: NSFont.monospacedSystemFont(ofSize: 12, weight: .regular),
    .foregroundColor: NSColor(calibratedWhite: 0.84, alpha: 1),
    .paragraphStyle: paragraph,
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
          let jpeg = bitmap.representation(using: .jpeg, properties: [.compressionFactor: 0.88]) else {
        throw NSError(domain: "SelectedContactSheet", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unable to encode JPEG"])
    }
    try jpeg.write(to: url)
}

let canvas = NSImage(size: NSSize(width: sheetW, height: sheetH))
canvas.lockFocus()
NSColor(calibratedRed: 0.05, green: 0.06, blue: 0.07, alpha: 1).setFill()
NSRect(x: 0, y: 0, width: sheetW, height: sheetH).fill()

for (i, file) in files.enumerated() {
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
    file.lastPathComponent.draw(in: labelRect.insetBy(dx: 4, dy: 5), withAttributes: labelAttrs)
}

canvas.unlockFocus()

let reviewsOutput = reviewsDir.appendingPathComponent("selected_contact_sheet.jpg")
let contactSheetsOutput = contactSheetsDir.appendingPathComponent("selected_contact_sheet.jpg")
if FileManager.default.fileExists(atPath: reviewsOutput.path) {
    try FileManager.default.removeItem(at: reviewsOutput)
}
if FileManager.default.fileExists(atPath: contactSheetsOutput.path) {
    try FileManager.default.removeItem(at: contactSheetsOutput)
}
try saveJPEG(canvas, to: reviewsOutput)
try FileManager.default.copyItem(at: reviewsOutput, to: contactSheetsOutput)
print("Wrote \(reviewsOutput.path)")
print("Wrote \(contactSheetsOutput.path)")
print("Selected images: \(files.count)")
