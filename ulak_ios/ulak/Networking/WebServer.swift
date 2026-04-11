import Foundation
import Network
import UIKit

// MARK: - Shared Content

struct SharedContent {
    let token: String
    let isFile: Bool
    let fileName: String?
    let fileData: Data?
    let text: String?
    let mimeType: String
}

// MARK: - WebServer

class WebServer: ObservableObject {
    static let shared = WebServer()

    let port: UInt16 = 53319
    private var listener: NWListener?
    private var currentContent: SharedContent?
    @Published var shareURL: String?
    @Published var isRunning = false

    private init() {}

    func start() {
        guard listener == nil else { return }
        do {
            listener = try NWListener(using: .tcp, on: NWEndpoint.Port(rawValue: port)!)
            listener?.stateUpdateHandler = { [weak self] state in
                switch state {
                case .ready:
                    DispatchQueue.main.async { self?.isRunning = true }
                case .failed:
                    DispatchQueue.main.async { self?.isRunning = false }
                default: break
                }
            }
            listener?.newConnectionHandler = { [weak self] connection in
                self?.handleConnection(connection)
            }
            listener?.start(queue: .global(qos: .utility))
        } catch {
            print("WebServer start error: \(error)")
        }
    }

    func stop() {
        listener?.cancel()
        listener = nil
        isRunning = false
        shareURL = nil
        currentContent = nil
    }

    func shareText(_ text: String) -> String {
        let token = generateToken()
        currentContent = SharedContent(
            token: token, isFile: false,
            fileName: nil, fileData: nil,
            text: text, mimeType: "text/plain"
        )
        let url = "http://\(localIP):\(port)/\(token)"
        DispatchQueue.main.async { self.shareURL = url }
        return url
    }

    func shareFile(url: URL) -> String {
        // Security-scoped URL erişimi (fileImporter URL'leri için zorunlu)
        let accessed = url.startAccessingSecurityScopedResource()
        defer { if accessed { url.stopAccessingSecurityScopedResource() } }
        let data = try? Data(contentsOf: url)
        let token = generateToken()
        currentContent = SharedContent(
            token: token, isFile: true,
            fileName: url.lastPathComponent,
            fileData: data,
            text: nil,
            mimeType: mimeType(for: url.pathExtension)
        )
        let shareUrl = "http://\(localIP):\(port)/\(token)"
        DispatchQueue.main.async { self.shareURL = shareUrl }
        return shareUrl
    }

    func shareData(_ data: Data, fileName: String, fileMimeType: String) -> String {
        let token = generateToken()
        currentContent = SharedContent(
            token: token, isFile: true,
            fileName: fileName,
            fileData: data,
            text: nil,
            mimeType: fileMimeType
        )
        let shareUrl = "http://\(localIP):\(port)/\(token)"
        DispatchQueue.main.async { self.shareURL = shareUrl }
        return shareUrl
    }

    private func handleConnection(_ connection: NWConnection) {
        connection.start(queue: .global(qos: .utility))
        connection.receive(minimumIncompleteLength: 1, maximumLength: 8192) { [weak self] data, _, _, error in
            guard let self = self, let data = data, error == nil else {
                connection.cancel()
                return
            }

            let request = String(data: data, encoding: .utf8) ?? ""
            let firstLine = request.components(separatedBy: "\r\n").first ?? ""
            let parts = firstLine.components(separatedBy: " ")
            guard parts.count >= 2 else {
                connection.cancel()
                return
            }

            let path = parts[1]
            self.handleRequest(path: path, connection: connection)
        }
    }

    private func handleRequest(path: String, connection: NWConnection) {
        guard let content = currentContent else {
            sendNotFound(connection: connection)
            return
        }

        let pathWithoutQuery = path.components(separatedBy: "?").first ?? path
        let isDownload = path.contains("download=1")
        let token = pathWithoutQuery.trimmingCharacters(in: CharacterSet(charactersIn: "/"))

        if token.isEmpty || token == content.token {
            if content.isFile {
                if isDownload, let fileData = content.fileData {
                    sendFile(data: fileData, name: content.fileName ?? "file", mimeType: content.mimeType, connection: connection)
                } else {
                    sendFilePage(content: content, connection: connection)
                }
            } else {
                sendTextPage(content: content, connection: connection)
            }
        } else {
            sendNotFound(connection: connection)
        }
    }

    private func sendTextPage(content: SharedContent, connection: NWConnection) {
        let text = content.text ?? ""
        let escaped = text
            .replacingOccurrences(of: "&", with: "&amp;")
            .replacingOccurrences(of: "<", with: "&lt;")
            .replacingOccurrences(of: ">", with: "&gt;")

        let html = """
        <!DOCTYPE html><html lang="tr"><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ULAK - Metin Paylaşımı</title>
        <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0e27; color:#e8f1ff; font-family:-apple-system,sans-serif; min-height:100vh; padding:20px; }
        .container { max-width:800px; margin:0 auto; }
        h1 { text-align:center; color:#00d4ff; font-size:2em; margin:30px 0; text-shadow:0 0 20px #00d4ff; }
        .card { background:#1a1f3a; border:1px solid #00d4ff44; border-radius:12px; padding:24px; margin:20px 0; box-shadow:0 0 20px #00d4ff22; }
        pre { white-space:pre-wrap; word-break:break-all; font-size:14px; line-height:1.6; }
        .btn { display:inline-block; padding:12px 28px; background:linear-gradient(45deg,#00d4ff,#7c3aed,#b24bf3); color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:15px; font-weight:600; margin-top:16px; }
        .logo { text-align:center; font-size:2.5em; margin:10px 0; }
        </style></head><body>
        <div class="container">
        <div class="logo">📡</div>
        <h1>ULAK</h1>
        <div class="card">
        <h3 style="color:#00d4ff;margin-bottom:12px;">📝 Metin İçeriği</h3>
        <pre>\(escaped)</pre>
        <button class="btn" onclick="navigator.clipboard.writeText(document.querySelector('pre').textContent).then(()=>this.textContent='✅ Kopyalandı!')">📋 Kopyala</button>
        </div>
        </div></body></html>
        """

        let body = html.data(using: .utf8) ?? Data()
        let response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: \(body.count)\r\nConnection: close\r\n\r\n"
        var responseData = response.data(using: .utf8)!
        responseData.append(body)
        connection.send(content: responseData, completion: .contentProcessed { _ in connection.cancel() })
    }

    private func sendFilePage(content: SharedContent, connection: NWConnection) {
        let name = content.fileName ?? "file"
        let icon = fileIcon(for: name)
        let size = content.fileData?.count ?? 0
        let sizeStr = ByteCountFormatter.string(fromByteCount: Int64(size), countStyle: .file)

        let html = """
        <!DOCTYPE html><html lang="tr"><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ULAK - \(name)</title>
        <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0e27; color:#e8f1ff; font-family:-apple-system,sans-serif; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
        .card { background:#1a1f3a; border:1px solid #00d4ff44; border-radius:16px; padding:40px; text-align:center; max-width:480px; box-shadow:0 0 30px #00d4ff22; }
        .icon { font-size:5em; margin-bottom:20px; }
        h1 { color:#00d4ff; margin-bottom:8px; text-shadow:0 0 20px #00d4ff; }
        h2 { font-size:1.1em; color:#e8f1ff; word-break:break-all; margin-bottom:16px; }
        .size { color:#8b9dc3; margin-bottom:30px; }
        .btn { display:inline-block; padding:14px 36px; background:linear-gradient(45deg,#00d4ff,#7c3aed,#b24bf3); color:#fff; border:none; border-radius:10px; cursor:pointer; font-size:16px; font-weight:700; text-decoration:none; }
        </style></head><body>
        <div class="card">
        <div class="icon">\(icon)</div>
        <h1>ULAK</h1>
        <h2>\(name)</h2>
        <div class="size">\(sizeStr)</div>
        <a class="btn" href="/\(content.token)?download=1">⬇️ İndir</a>
        </div></body></html>
        """

        let body = html.data(using: .utf8) ?? Data()
        let response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: \(body.count)\r\nConnection: close\r\n\r\n"
        var responseData = response.data(using: .utf8)!
        responseData.append(body)
        connection.send(content: responseData, completion: .contentProcessed { _ in connection.cancel() })
    }

    private func sendFile(data: Data, name: String, mimeType: String, connection: NWConnection) {
        let encodedName = name.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? name
        let response = "HTTP/1.1 200 OK\r\nContent-Type: \(mimeType)\r\nContent-Disposition: attachment; filename*=UTF-8''\(encodedName)\r\nContent-Length: \(data.count)\r\nConnection: close\r\n\r\n"
        var responseData = response.data(using: .utf8)!
        responseData.append(data)
        connection.send(content: responseData, completion: .contentProcessed { _ in connection.cancel() })
    }

    private func sendNotFound(connection: NWConnection) {
        let body = "Not Found".data(using: .utf8)!
        let response = "HTTP/1.1 404 Not Found\r\nContent-Length: \(body.count)\r\nConnection: close\r\n\r\n"
        var responseData = response.data(using: .utf8)!
        responseData.append(body)
        connection.send(content: responseData, completion: .contentProcessed { _ in connection.cancel() })
    }

    private func generateToken() -> String {
        let chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return String((0..<8).map { _ in chars.randomElement()! })
    }

    private var localIP: String { NetworkManager.shared.localIP }

    private func mimeType(for ext: String) -> String {
        switch ext.lowercased() {
        case "jpg", "jpeg": return "image/jpeg"
        case "png": return "image/png"
        case "gif": return "image/gif"
        case "mp4": return "video/mp4"
        case "mp3": return "audio/mpeg"
        case "pdf": return "application/pdf"
        case "zip": return "application/zip"
        case "txt": return "text/plain"
        default: return "application/octet-stream"
        }
    }

    private func fileIcon(for name: String) -> String {
        let ext = (name as NSString).pathExtension.lowercased()
        switch ext {
        case "jpg", "jpeg", "png", "gif", "heic": return "🖼️"
        case "mp4", "mov", "avi", "mkv": return "🎥"
        case "mp3", "wav", "aac": return "🎵"
        case "pdf": return "📄"
        case "zip", "rar", "7z": return "🗄️"
        default: return "📁"
        }
    }
}
