import XCTest
@testable import ulak

final class ulakTests: XCTestCase {
    func testEncryptDecryptText() throws {
        let original = "Merhaba ULAK!"
        let password = "test_password"

        guard let encrypted = EncryptionManager.shared.encryptText(original, password: password) else {
            XCTFail("Encryption failed")
            return
              )

        let stored = item.storageString
        let restored = ReceivedItem.from(storageString: stored)

        XCTAssertNotNil(restored)
        XCTAssertEqual(restored?.name, item.name)
        XCTAssertEqual(restored?.sender, item.sender)
    }
}
