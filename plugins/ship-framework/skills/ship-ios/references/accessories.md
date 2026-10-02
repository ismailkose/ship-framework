<!-- ship-reference
id: ios-accessories
kind: mixed
sources: iPhoneOS27.0.sdk CoreBluetooth / AccessorySetupKit (headers) / CoreNFC / HomeKit / MatterSupport interfaces; iPhoneOS27.0.sdk (device) DockKit interface (Xcode 27.0 27A266a — examples type-check via scripts/checks/ios.sh; the DockKit example against the device SDK; the heart-rate parser runs on the host via scripts/checks/ios_runtime); https://developer.apple.com/documentation/corebluetooth ; https://developer.apple.com/documentation/corebluetooth/cbcentralmanager ; https://developer.apple.com/documentation/accessorysetupkit ; https://developer.apple.com/documentation/corenfc ; https://developer.apple.com/documentation/homekit ; https://developer.apple.com/documentation/mattersupport ; https://developer.apple.com/documentation/dockkit ; https://developer.apple.com/documentation/wifiaware ; Bluetooth SIG GATT Specification Supplement, Heart Rate Measurement (https://www.bluetooth.com/specifications/specs/) (all checked 2026-09-25). Written for Ship from Apple's docs, the SDK, and the Bluetooth spec; no third-party text.
reviewed: 2026-09-25
-->
# Accessories — Bluetooth, AccessorySetupKit, NFC, Home, DockKit

**When to read:** "connect our accessory / heart-rate strap / sensor", "pair a device", reading data
from Bluetooth LE, NFC tags, smart-home control, camera stands. **Everything here needs the real
hardware to verify** — the simulator has no Bluetooth, NFC, or DockKit. **Apple** = platform
requirement; **Ship** = default.

## 1. Pick the path

| You're connecting… | Use | Prerequisites |
|---|---|---|
| **Your own** Bluetooth/Wi-Fi accessory | **AccessorySetupKit** (iOS 18) to pair, then Core Bluetooth to talk | Info.plist `NSAccessorySetupSupports` + the accessory's service UUIDs / name in `NSAccessorySetupBluetoothServices` (see Apple's setup doc) |
| Any standard BLE device (heart-rate strap, sensor) | Core Bluetooth | `NSBluetoothAlwaysUsageDescription`; Background Modes › Uses Bluetooth LE accessories to receive data in the background |
| NFC tags (NDEF) | Core NFC `NFCNDEFReaderSession` | Near Field Communication Tag Reading capability, `NFCReaderUsageDescription`; iPhone only |
| Smart-home accessories | HomeKit (control) / MatterSupport (add a Matter device) | HomeKit capability, `NSHomeKitUsageDescription` |
| Subject-tracking camera stands | DockKit (iOS 17) | A DockKit-compatible stand; device SDK only |
| Peer-to-peer Wi-Fi between devices | Wi-Fi Aware (iOS 26) | Entitlements and paired devices per Apple's docs — read them before planning |

**Ship:** for your own accessory, AccessorySetupKit first: the person picks the device in a system
sheet, and the app never asks for blanket Bluetooth permission. Custom pairing UI needs a reason.

## 2. Core Bluetooth — from scan to data

**The lifecycle** (each step waits for the previous delegate callback):
1. Create one `CBCentralManager`; wait for `.poweredOn` in `centralManagerDidUpdateState`.
   `.unauthorized` / `.poweredOff` / `.unsupported` → explain in the UI and stop.
2. `scanForPeripherals(withServices: [yourService])` — never `nil` services in production (slow,
   battery, and background scans require a service list). Stop scanning once you have the device.
3. `connect` and **keep a strong reference** to the `CBPeripheral` (a dropped reference cancels the
   connection).
4. In `didConnect`: set `peripheral.delegate`, `discoverServices([yourService])`.
5. `didDiscoverServices` → `discoverCharacteristics([yourCharacteristic], for:)`.
6. `didDiscoverCharacteristicsFor` → `setNotifyValue(true, for:)` for streams, `readValue(for:)` for
   one-off values, `writeValue(_:for:type:)` with the type the characteristic supports
   (`.withResponse` when you need confirmation).
7. `didUpdateValueFor` → parse the bytes (below). Check `error` on every callback.
8. **Disconnects:** `didDisconnectPeripheral` / `didFailToConnect` → show "reconnecting…" and call
   `connect` again — a pending `connect` doesn't time out, so the system reconnects when the device
   comes back into range. Stop reconnecting when the person chooses to forget the device.
   **Stop has to stick:** a later `.poweredOn`, a late `didDiscover`/`didConnect`, or a callback
   from a manager you replaced can all arrive after the person pressed Stop — only scan or connect
   while they still want a connection, and ignore callbacks from a manager or peripheral you've let go.
9. **Next launch:** remember `peripheral.identifier` and use `retrievePeripherals(withIdentifiers:)`
   before scanning again.
10. **Background and relaunch:** with the background mode and
    `CBCentralManagerOptionRestoreIdentifierKey`, the system can relaunch the app for Bluetooth
    events; handle `willRestoreState` — take back the restored peripherals and set their delegates
    before anything else.

**Parsing is where apps go wrong.** Read the characteristic's spec for byte layout, endianness, and
flags. The Heart Rate Measurement (`0x2A37`) sends a flags byte first; bit 0 says whether the rate is
one byte or two (little-endian); other bits add sensor contact, energy, and RR-intervals. The parser
below runs in Ship's host tests with sample payloads.

```swift
import CoreBluetooth

/// Heart Rate Measurement (Bluetooth SIG 0x2A37) → beats per minute and sensor contact.
nonisolated func parseHeartRate(_ data: Data) -> (bpm: Int, contact: Bool?)? {
    let bytes = [UInt8](data)
    guard let flags = bytes.first else { return nil }
    let wide = flags & 0x01 != 0                                 // bit 0: UInt16 rate
    let contactSupported = flags & 0x04 != 0                     // bit 2: contact status supported
    let contact: Bool? = contactSupported ? (flags & 0x02 != 0) : nil
    if wide {
        guard bytes.count >= 3 else { return nil }
        return (Int(UInt16(bytes[1]) | UInt16(bytes[2]) << 8), contact)
    }
    guard bytes.count >= 2 else { return nil }
    return (Int(bytes[1]), contact)
}

/// Every scan/connect decision as a pure function of (state, callback), so the rules — nothing
/// resumes after Stop, callbacks from a replaced manager are ignored — are testable without a radio.
nonisolated struct HeartRateLink: Sendable {
    enum Status: Equatable, Sendable { case off, starting, unauthorized, unavailable, searching, connecting, live(Int), noContact, reconnecting }
    enum Event: Sendable { case poweredOn, poweredOff, unauthorized, foundKnownDevice, discovered, connected, disconnected, measured(bpm: Int, contact: Bool?) }
    enum Command: Equatable, Sendable { case scan, stopScan, connect, cancelConnection, discoverServices }

    private(set) var status: Status = .off
    private(set) var generation = 0            // bumps on every start and stop; older callbacks are stale
    private(set) var wanted = false
    private var hasDevice = false
    private var poweredOn = false

    mutating func start() { generation += 1; wanted = true; hasDevice = false; poweredOn = false; status = .starting }

    mutating func stop() -> [Command] {
        let was = wanted
        generation += 1; wanted = false; status = .off
        return was ? [.stopScan, .cancelConnection] : []
    }

    mutating func handle(_ event: Event, from sender: Int) -> [Command] {
        guard wanted, sender == generation else { return [] }       // stopped, or a stale manager
        switch event {
        case .foundKnownDevice: hasDevice = true; return []
        case .poweredOn:
            poweredOn = true
            status = hasDevice ? .connecting : .searching
            return hasDevice ? [.connect] : [.scan]
        case .poweredOff: poweredOn = false; status = .unavailable; return []
        case .unauthorized: poweredOn = false; status = .unauthorized; return []
        case .discovered:
            guard poweredOn, !hasDevice else { return [] }          // duplicate or too early
            hasDevice = true; status = .connecting
            return [.stopScan, .connect]
        case .connected: return [.discoverServices]
        case .disconnected:
            guard poweredOn else { return [] }                      // power-on reconnects instead
            status = .reconnecting
            return [.connect]                                       // pending; completes when back in range
        case .measured(let bpm, let contact):
            status = contact == false ? .noContact : .live(bpm)
            return []
        }
    }
}

@MainActor @Observable
final class HeartRateMonitor: NSObject {
    static let service = CBUUID(string: "180D")
    static let measurement = CBUUID(string: "2A37")

    private(set) var link = HeartRateLink()
    private var central: CBCentralManager?
    private var strap: CBPeripheral?                               // strong reference

    func start(knownDevice: UUID?) {
        if central != nil { stop() }                               // never two live managers
        link.start()
        let manager = CBCentralManager(delegate: self, queue: nil,
                                       options: [CBCentralManagerOptionRestoreIdentifierKey: "heart-rate"])
        central = manager
        if let id = knownDevice, let known = manager.retrievePeripherals(withIdentifiers: [id]).first {
            keep(known)
        }
    }

    func stop() {                                                  // the person turned it off
        run(link.stop())
        strap?.delegate = nil; central?.delegate = nil             // let both go: late callbacks are dropped
        strap = nil; central = nil
    }

    private func keep(_ peripheral: CBPeripheral) {
        strap = peripheral
        peripheral.delegate = self
        _ = link.handle(.foundKnownDevice, from: link.generation)
    }

    /// The generation a callback belongs to: the current one only if it comes from the objects we hold.
    private func sender(_ manager: CBCentralManager, _ peripheral: CBPeripheral? = nil) -> Int {
        manager === central && (peripheral == nil || peripheral === strap) ? link.generation : -1
    }

    private func run(_ commands: [HeartRateLink.Command]) {
        for command in commands {
            switch command {
            case .scan: central?.scanForPeripherals(withServices: [Self.service])
            case .stopScan: central?.stopScan()
            case .connect: if let strap { central?.connect(strap) }
            case .cancelConnection: if let strap { central?.cancelPeripheralConnection(strap) }
            case .discoverServices: strap?.discoverServices([Self.service])
            }
        }
    }
}

extension HeartRateMonitor: @preconcurrency CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ manager: CBCentralManager) {
        let event: HeartRateLink.Event = switch manager.state {
            case .poweredOn: .poweredOn
            case .unauthorized: .unauthorized
            default: .poweredOff
        }
        run(link.handle(event, from: sender(manager)))
    }

    func centralManager(_ manager: CBCentralManager, willRestoreState dict: [String: Any]) {
        // May arrive while `start` is still creating the manager, so it isn't matched by identity.
        guard link.wanted, let restored = (dict[CBCentralManagerRestoredStatePeripheralsKey] as? [CBPeripheral])?.first else { return }
        keep(restored)                                             // delegate set before any other callback
    }

    func centralManager(_ manager: CBCentralManager, didDiscover peripheral: CBPeripheral,
                        advertisementData: [String: Any], rssi RSSI: NSNumber) {
        let commands = link.handle(.discovered, from: sender(manager))
        guard !commands.isEmpty else { return }
        strap = peripheral                                         // persist peripheral.identifier in the app
        peripheral.delegate = self
        run(commands)
    }

    func centralManager(_ manager: CBCentralManager, didConnect peripheral: CBPeripheral) {
        run(link.handle(.connected, from: sender(manager, peripheral)))
    }

    func centralManager(_ manager: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral,
                        error: (any Error)?) {
        run(link.handle(.disconnected, from: sender(manager, peripheral)))
    }

    func centralManager(_ manager: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: (any Error)?) {
        run(link.handle(.disconnected, from: sender(manager, peripheral)))
    }
}

extension HeartRateMonitor: @preconcurrency CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: (any Error)?) {
        guard link.wanted, peripheral === strap, error == nil,
              let service = peripheral.services?.first(where: { $0.uuid == Self.service }) else { return }
        peripheral.discoverCharacteristics([Self.measurement], for: service)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: (any Error)?) {
        guard link.wanted, peripheral === strap, error == nil,
              let rate = service.characteristics?.first(where: { $0.uuid == Self.measurement }) else { return }
        peripheral.setNotifyValue(true, for: rate)                 // stream of measurements
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: (any Error)?) {
        guard error == nil, let data = characteristic.value, let reading = parseHeartRate(data),
              let central else { return }
        _ = link.handle(.measured(bpm: reading.bpm, contact: reading.contact), from: sender(central, peripheral))
    }
}
```

**Not shown:** persisting the device's `identifier`, a "forget device" flow, write-with-response
error handling, and background-mode configuration. `HeartRateLink`'s rules run in Ship's host tests
(`ios_runtime/heart_rate_link`: Stop then power-on, late discovery/connection/data, a replaced
manager's callbacks, reconnects); the monitor that feeds it real callbacks compiles but has **not**
been run against a radio or a strap — that's a hardware check (§7).

## 3. AccessorySetupKit (iOS 18) — pairing your own accessory

1. Declare the accessory in Info.plist (supported types and its Bluetooth service UUIDs / Wi-Fi
   SSID prefix) — without it the picker shows nothing.
2. Create one `ASAccessorySession` and `activate(on:eventHandler:)`; the first event lists
   accessories the person already gave your app.
3. `showPicker(for: [ASPickerDisplayItem(name:productImage:descriptor:)])` — the system finds,
   shows, and pairs the device. Events: `.accessoryAdded` (keep `accessory.bluetoothIdentifier`),
   `.accessoryChanged`, `.accessoryRemoved` (the person removed it in Settings — forget it),
   `.pickerDidDismiss`.
4. Talk to it with Core Bluetooth: `retrievePeripherals(withIdentifiers: [bluetoothIdentifier])`,
   then §2 from step 3. No `NSBluetoothAlwaysUsageDescription` prompt for that device.
5. **Test:** device + the accessory; also remove it in Settings › Privacy › Accessories and relaunch.

## 4. NFC tags

- Check `NFCNDEFReaderSession.readingAvailable` (false on iPad, simulator, older iPhones) — hide the
  button when false.
- One session per scan: `begin()` shows the system sheet; set `alertMessage` to say what to scan.
  `didDetectNDEFs` gives the messages; `didInvalidateWithError` always ends it —
  `.readerSessionInvalidationErrorUserCanceled` and the first-read invalidation are normal, show
  nothing; other errors show a retry.
- Writing or non-NDEF tags: `NFCTagReaderSession` / `NFCNDEFReaderSession` with `connect(to:)`, and the
  Info.plist entries for the tag types you read.
- **Test:** a real tag on an iPhone.

## 5. Home: HomeKit and Matter

- Controlling the person's home: one `HMHomeManager`; wait for `homeManagerDidUpdateHomes` before
  reading `homes` (it's empty until then); handle authorization changes
  (`homeManagerDidUpdate(_:authorizationStatus:)`).
- Adding a Matter device to the person's home from your app: `MatterAddDeviceRequest(…).perform()`
  (MatterSupport) runs Apple's setup flow; your app's own ecosystem support needs the Matter
  extension described in Apple's MatterSupport docs.
- **Test:** real accessories (or Apple's HomeKit Accessory Simulator for HomeKit logic on a Mac).

## 6. DockKit — camera stands (iOS 17, device SDK)

- **Default:** do nothing — with system tracking on, the stand follows people in any camera app.
  Take over only for a custom experience (track a whiteboard, an object, or a chosen subject).
- Observe `DockAccessoryManager.shared.accessoryStateChanges` (docked/undocked); when docked, either
  keep system tracking, or turn it off (`setSystemTrackingEnabled(false)`) and drive tracking
  yourself with `track(_:cameraInformation:)` from your Vision/metadata observations,
  `setFramingMode`, `selectSubject(at:)`, or `setRegionOfInterest`.
- **Always restore system tracking** when your camera screen goes away or the app backgrounds —
  otherwise the stand stops following in other apps. Every call `throws`; an undock mid-session is
  normal, not an error to show.
- **Test:** a DockKit stand with a device; undock during tracking; background the app mid-session.

```swift
// device-sdk — DockKit isn't in the simulator SDK; this block type-checks against iPhoneOS.
import DockKit

@MainActor
final class StandCoordinator {
    private var watch: Task<Void, Never>?

    /// Custom framing while this screen is up; the system's tracking comes back when it ends.
    func begin() {
        watch = Task {
            do {
                for await change in try DockAccessoryManager.shared.accessoryStateChanges {
                    guard change.state == .docked, let stand = change.accessory else { continue }
                    try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
                    try await stand.setFramingMode(.center)
                }
            } catch {
                // an undock or an unsupported stand: nothing to show; system tracking is restored in end()
            }
        }
    }

    func end() async {
        watch?.cancel()
        try? await DockAccessoryManager.shared.setSystemTrackingEnabled(true)
    }
}
```

## 7. Verify (all hardware)

| What | How | Level |
|---|---|---|
| Heart-rate parsing | Host test with 8-bit, 16-bit, contact, and truncated payloads | CI (`ios_runtime/heart_rate`) |
| Scan → connect → notify → bpm on screen | A real strap; watch values update | **Manual, device + accessory** |
| Disconnect and reconnect | Walk out of range and back; power-cycle the strap | **Manual** |
| Stop/start rules (`HeartRateLink`) | Host test: Stop then power-on, late callbacks, replaced manager | CI (`ios_runtime/heart_rate_link`) — pure logic only |
| Stop sticks on hardware | Stop while Bluetooth is off, then turn it on; Stop mid-connect; Stop, walk out of range and back — nothing reconnects | **Manual, device + accessory** |
| Relaunch and restoration | Kill the app while connected, trigger a Bluetooth event; restart after Stop (`willRestoreState` isn't matched by manager identity — check it doesn't resume a stopped monitor) | **Manual** |
| AccessorySetupKit pairing, removal in Settings | Real accessory | **Manual** |
| NFC read + cancel | Real tag; cancel the sheet | **Manual, iPhone** |
| DockKit takeover and restore | Stand; undock mid-session; background | **Manual** |

Apple: [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth) ·
[AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit) ·
[Core NFC](https://developer.apple.com/documentation/corenfc) ·
[HomeKit](https://developer.apple.com/documentation/homekit) ·
[DockKit](https://developer.apple.com/documentation/dockkit) · Bluetooth SIG specs:
[bluetooth.com](https://www.bluetooth.com/specifications/specs/).
