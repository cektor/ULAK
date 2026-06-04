# Privacy Policy — ULAK for Windows

**Effective Date:** June 4, 2026  
**Last Updated:** June 4, 2026  
**Developer:** Fatih ÖNDER (CekToR) — ALGSoft Inc.  
**Contact:** info@algsoft.net.tr  
**Website:** [algsoft.net.tr](https://algsoft.net.tr)

---

## 1. Introduction

ULAK ("the Application", "we", "our") is a local area network (LAN) file-sharing application developed by ALGSoft Inc. and distributed through the Microsoft Store. This Privacy Policy explains what information the Application accesses, how it is used, and your rights regarding that information.

By installing or using ULAK, you agree to the practices described in this Privacy Policy. If you do not agree, please uninstall the Application.

---

## 2. Summary at a Glance

| Category | Details |
|---|---|
| **Personal data collected** | Device hostname, local IP address |
| **Sent to the internet?** | Only to fetch in-app announcements (no user data transmitted) |
| **Files uploaded to any server?** | Never — all transfers are local network only |
| **Third-party data sharing?** | None |
| **Children under 13** | Application does not knowingly collect data from children |
| **Data sold?** | Never |

---

## 3. Information the Application Accesses

### 3.1 Device Hostname
- **What:** Your computer's network name (e.g., `DESKTOP-ABC123`), retrieved via the operating system API.
- **Why:** Broadcast over your local network so nearby devices running ULAK can identify your device by name.
- **Scope:** Stays within your local network. Never transmitted to any server on the internet.

### 3.2 Local IP Address
- **What:** Your device's private IPv4 address on the local network (e.g., `192.168.1.x`).
- **Why:** Required to establish peer-to-peer connections between devices on the same network for file and text transfer.
- **Scope:** Shared only with other devices on your local network via UDP broadcast. Never transmitted to any server on the internet.

### 3.3 Files and Text Selected by the User
- **What:** Files or text that you explicitly choose to send through the Application.
- **Why:** Transferred directly to the recipient device you select.
- **Scope:** Transferred over your local network only, using AES-256 encrypted channels when encryption is enabled. ALGSoft Inc. never receives, stores, or processes your files.

### 3.4 Application Preferences
- **What:** User interface settings such as device icons and platform assignments.
- **Why:** To remember your customizations between sessions.
- **Where stored:** Locally on your device via Windows Registry under the key `HKCU\Software\ULAK\ULAK`. Never synchronized or transmitted externally.

### 3.5 In-App Announcement Content
- **What:** The Application makes a single outbound HTTP GET request to `https://algsoft.net.tr/uygulama-duyurulari/` to display developer announcements (e.g., new version notices).
- **User data sent:** None. This is a read-only request. No device identifiers, IP addresses, or any personal information are included in the request beyond what is contained in a standard HTTP request header (User-Agent, etc.).
- **Frequency:** Once per application launch.

---

## 4. Information the Application Does NOT Collect

The Application does **not** collect, store, or transmit:

- Your name, email address, phone number, or any contact information
- Passwords or encryption keys (keys are generated locally and never leave your device)
- Location data (GPS or otherwise)
- Browsing history, clipboard content (beyond explicit send actions), or keystrokes
- Usage analytics, crash reports, or telemetry
- Advertising identifiers or tracking tokens
- Any biometric data

---

## 5. How Information Is Used

| Information | Purpose | Shared Externally? |
|---|---|---|
| Device hostname | Device discovery on LAN | No |
| Local IP address | Peer-to-peer LAN connections | No |
| User-selected files/text | File transfer to chosen device | No |
| App preferences | UI personalization | No |
| HTTP request to announcement URL | Display developer announcements | No (read-only GET) |

---

## 6. Local Network Communication

ULAK operates exclusively over your local area network (LAN / Wi-Fi). It uses the following network ports:

| Port | Protocol | Purpose |
|---|---|---|
| `53317` | TCP | File and text transfer between devices |
| `53318` | UDP | Device discovery broadcasts |

All peer-to-peer transfers are initiated only upon your explicit action (selecting a device and choosing to send). No data is relayed through any ALGSoft server.

---

## 7. Encryption

When the encryption option is enabled, file transfers are protected using **AES-256-CBC** symmetric encryption. The encryption key is derived locally on your device. ALGSoft Inc. does not have access to your encryption keys and cannot decrypt your transfers.

---

## 8. Data Sharing and Third Parties

We do **not** sell, rent, lease, or share your personal information with any third party for any purpose.

The Application does not integrate any third-party analytics SDKs, advertising networks, or tracking libraries.

---

## 9. Data Storage and Retention

- **Files received:** Saved to your `Downloads` folder (or a folder you specify). These files are under your full control. ULAK does not retain copies.
- **App preferences:** Stored in the Windows Registry on your device. Removed when you uninstall the Application via Windows Settings or the Microsoft Store.
- **No cloud storage:** ULAK does not use any cloud storage service.

---

## 10. Children's Privacy

ULAK is not directed at children under the age of 13. The Application does not knowingly collect personal information from children. If you believe a child has provided personal information through the Application, please contact us at info@algsoft.net.tr and we will take appropriate action.

This Application complies with the **Children's Online Privacy Protection Act (COPPA)**.

---

## 11. Microsoft Store Compliance

This Application is distributed through the Microsoft Store and complies with:

- [Microsoft Store Policies](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies) — including Policy 10.5 (Personal Information)
- The Application requests only the permissions necessary for its core functionality (local network access).
- No capability declarations beyond local network communication are used.

---

## 12. Your Rights and Choices

Depending on your jurisdiction, you may have the following rights regarding your personal information:

- **Access:** Request information about what data the Application stores about you.
- **Deletion:** Uninstall the Application to remove all locally stored preferences. No data is held externally by ALGSoft Inc.
- **Opt-out:** You may disable network discovery at any time from the Application's Settings tab, which stops all broadcast activity.

To exercise any of these rights, contact us at **info@algsoft.net.tr**.

---

## 13. Security

We implement reasonable technical measures to protect data in transit:

- AES-256 encryption for file transfers (when enabled)
- All communication is confined to your local private network
- No data is transmitted to external servers beyond the single announcement fetch described in Section 3.5

However, no method of transmission over a local network is 100% secure. We encourage you to use the encryption feature when transferring sensitive files.

---

## 14. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. When we do, we will update the **Last Updated** date at the top of this document and notify users through the in-app announcement system. Continued use of the Application after changes are posted constitutes acceptance of the updated policy.

---

## 15. Contact Us

If you have questions or concerns about this Privacy Policy or the Application's data practices, please contact us:

- **Email:** info@algsoft.net.tr
- **Website:** [algsoft.net.tr](https://algsoft.net.tr)
- **GitHub:** [github.com/cektor/ulak](https://github.com/cektor/ulak)

---

## 16. Governing Law

This Privacy Policy is governed by the laws of the Republic of Turkey. Any disputes arising under this policy shall be subject to the exclusive jurisdiction of Turkish courts.

---

*© 2026 ALGSoft Inc. All rights reserved.*  
*ULAK is open-source software licensed under the [MIT License](https://opensource.org/licenses/MIT).*
