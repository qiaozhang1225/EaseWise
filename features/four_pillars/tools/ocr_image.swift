import Foundation
import Vision
import AppKit

struct OcrResult: Encodable {
    let path: String
    let status: String
    let text: String
    let error: String?
}

func recognizeText(path: String) -> OcrResult {
    let url = URL(fileURLWithPath: path)
    guard let image = NSImage(contentsOf: url) else {
        return OcrResult(path: path, status: "failed", text: "", error: "image_open_failed")
    }
    guard let tiffData = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let cgImage = bitmap.cgImage else {
        return OcrResult(path: path, status: "failed", text: "", error: "image_decode_failed")
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
        let lines = (request.results ?? [])
            .compactMap { $0.topCandidates(1).first?.string.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        return OcrResult(path: path, status: "ok", text: lines.joined(separator: "\n"), error: nil)
    } catch {
        return OcrResult(path: path, status: "failed", text: "", error: "vision_request_failed")
    }
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.withoutEscapingSlashes]

for path in CommandLine.arguments.dropFirst() {
    let result = recognizeText(path: path)
    if let data = try? encoder.encode(result), let line = String(data: data, encoding: .utf8) {
        print(line)
    }
}
