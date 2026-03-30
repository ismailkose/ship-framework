# Core Bluetooth — iOS Reference

> **When to read:** Dev reads this when building features with Bluetooth: scanning, connecting, reading/writing characteristics, or background bluetooth modes.

---

## Triage
- **Implement new feature** → Read Core API + Code Examples
- **Fix a bug** → Check Common Mistakes first
- **Review code** → Use Review Checklist

---

## Core API

| Type | Purpose |
|------|---------|
| `CBCentralManager` | Client-side BLE; scan/connect to peripherals |
| `CBPeripheralManager` | Server-side BLE; advertise services/characteristics |
| `CBPeripheral` | Discovered device; handles connection, service discovery |
| `CBCentralManagerDelegate` | Callbacks: discovered peripherals, connection state changes |
| `CBPeripheralDelegate` | Callbacks: service discovery, characteristic reads/writes, notifications |
| `CBService` | Service container; UUID + characteristics |
| `CBCharacteristic` | Data endpoint; UUID + value + properties (read, write, notify) |
| `CBDescriptor` | Metadata about characteristic; CCCD for notifications |
| `CBUUID` | Bluetooth UUID (16-bit standard or 128-bit custom) |
| `CBManagerState` | `.unknown`, `.resetting`, `.unsupported`, `.unauthorized`, `.poweredOff`, `.poweredOn` |
| `CBConnectOptions` | Connection params: notify power, auto-connect |

---

## Code Examples

### Example 1: Scan and connect to BLE peripheral with RSSI filtering
```swift
import CoreBluetooth

class BLEManager: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var centralManager: CBCentralManager!
    var connectedPeripheral: CBPeripheral?
    private let rssiThreshold: Int = -70  // Ignore weaker signals

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: .main)
    }

    func startScanning() {
        guard centralManager.state == .poweredOn else {
            print("Bluetooth not available")
            return
        }

        let serviceUUIDs = [CBUUID(string: "180A")] // Device Info Service (example)
        centralManager.scanForPeripherals(withServices: serviceUUIDs, options: nil)
        print("Scanning...")
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        // Filter by RSSI to avoid weak/distant signals
        guard RSSI.intValue > rssiThreshold else {
            return  // Ignore weak signals
        }

        print("Discovered: \(peripheral.name ?? "Unknown") at \(RSSI) dBm")

        // IMPORTANT: Retain the peripheral — Core Bluetooth does not keep a reference
        if connectedPeripheral == nil {
            connectedPeripheral = peripheral
            connectedPeripheral?.delegate = self
            centralManager.connect(peripheral, options: nil)
            centralManager.stopScan()
        }
    }

    // MARK: - CBCentralManagerDelegate
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn:
            print("Bluetooth powered on; ready to scan")
        case .poweredOff, .resetting:
            print("Bluetooth off or resetting")
        case .unauthorized:
            print("Bluetooth access not authorized")
        case .unsupported:
            print("Bluetooth not supported")
        default:
            print("Unknown state")
        }
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String : Any],
        rssi RSSI: NSNumber
    ) {
        print("Discovered: \(peripheral.name ?? "Unknown") at \(RSSI) dBm")

        // Connect to first discovered peripheral
        if connectedPeripheral == nil {
            connectedPeripheral = peripheral
            connectedPeripheral?.delegate = self
            centralManager.connect(peripheral, options: nil)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("Connected to \(peripheral.name ?? "device")")
        peripheral.discoverServices(nil) // Discover all services
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("Failed to connect: \(error?.localizedDescription ?? "unknown")")
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        print("Disconnected: \(error?.localizedDescription ?? "user initiated")")
        connectedPeripheral = nil
    }

    // MARK: - CBPeripheralDelegate
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = peripheral.services else { return }

        services.forEach { service in
            print("Service: \(service.uuid)")
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard let characteristics = service.characteristics else { return }

        characteristics.forEach { characteristic in
            print("  Characteristic: \(characteristic.uuid)")

            // Always check properties before attempting operations
            if characteristic.properties.contains(.read) {
                peripheral.readValue(for: characteristic)
            }

            if characteristic.properties.contains(.notify) {
                peripheral.setNotifyValue(true, for: characteristic)
            }

            // Check write capability before writing
            if characteristic.properties.contains(.write) ||
               characteristic.properties.contains(.writeWithoutResponse) {
                print("    Characteristic supports write")
            }
        }
    }

    func writeValue(_ data: Data, to characteristic: CBCharacteristic, on peripheral: CBPeripheral) {
        // Always check before writing
        if characteristic.properties.contains(.writeWithoutResponse) {
            peripheral.writeValue(data, for: characteristic, type: .withoutResponse)
        } else if characteristic.properties.contains(.write) {
            peripheral.writeValue(data, for: characteristic, type: .withResponse)
        } else {
            print("Characteristic does not support write")
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard let value = characteristic.value else { return }
        print("Read: \(characteristic.uuid) = \(value.hexString)")
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
        print("Notification enabled: \(characteristic.uuid)")
    }
}
```

### Example 2: Write characteristic
```swift
func writeCharacteristic(data: Data) {
    guard let peripheral = connectedPeripheral,
          let service = peripheral.services?.first,
          let characteristic = service.characteristics?.first(where: { $0.properties.contains(.write) }) else {
        return
    }

    let writeType: CBCharacteristicWriteType = characteristic.properties.contains(.writeWithoutResponse) ? .withoutResponse : .withResponse
    peripheral.writeValue(data, for: characteristic, type: writeType)
    print("Write initiated")
}
```

### Example 3: Peripheral server (advertise service)
```swift
import CoreBluetooth

class BLEPeripheralManager: NSObject, CBPeripheralManagerDelegate {
    var peripheralManager: CBPeripheralManager!

    override init() {
        super.init()
        peripheralManager = CBPeripheralManager(delegate: self, queue: .main)
    }

    func startAdvertising() {
        let serviceUUID = CBUUID(string: "180A")
        let characteristicUUID = CBUUID(string: "2A29")

        let characteristic = CBMutableCharacteristic(
            type: characteristicUUID,
            properties: [.read, .notify],
            value: nil,
            permissions: [.readable]
        )

        let service = CBMutableService(type: serviceUUID, primary: true)
        service.characteristics = [characteristic]

        peripheralManager.add(service)

        let advertisementData: [String: Any] = [
            CBAdvertisementDataLocalNameKey: "MyBLEDevice",
            CBAdvertisementDataServiceUUIDsKey: [serviceUUID]
        ]

        peripheralManager.startAdvertising(advertisementData)
        print("Advertising started")
    }

    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        switch peripheral.state {
        case .poweredOn:
            print("Peripheral ready to advertise")
            startAdvertising()
        default:
            print("Peripheral state: \(peripheral.state)")
        }
    }

    func peripheralManager(_ peripheral: CBPeripheralManager, didAdd service: CBService, error: Error?) {
        if let error = error {
            print("Add service error: \(error)")
        } else {
            print("Service added")
        }
    }

    func peripheralManager(_ peripheral: CBPeripheralManager, central: CBCentral, didSubscribeTo characteristic: CBCharacteristic) {
        print("Central subscribed to \(characteristic.uuid)")
    }
}
```

### Example 4: Background modes and state restoration
```swift
// In Info.plist, add NSBluetoothPeripheralUsageDescription and NSBluetoothCentralUsageDescription

// Enable background modes in Capabilities
// Add: Background Modes → Bluetooth Central & Peripheral

class BLEManager {
    func setupStateRestoration() {
        // Restore previous scan/connection on app launch
        let options: [String: Any] = [
            CBCentralManagerOptionRestoreIdentifierKey: "MyBLECentralManager",
            CBCentralManagerOptionShowPowerAlertKey: true
        ]

        let centralManager = CBCentralManager(delegate: self, queue: .main, options: options)
    }

    func centralManager(_ central: CBCentralManager, willRestoreState dict: [String : Any]) {
        if let peripherals = dict[CBCentralManagerRestoredStatePeripheralsKey] as? [CBPeripheral] {
            peripherals.forEach { peripheral in
                print("Restoring connection to \(peripheral.name ?? "device")")
                peripheral.delegate = self  // Re-assign delegate
                central.connect(peripheral, options: nil)
            }
        }
    }
}
```

### State Restoration Details

When the system relaunches your app for a BLE event (background central or
peripheral mode), the `willRestoreState` delegate callback fires **immediately**,
before `centralManagerDidUpdateState` or `peripheralManagerDidUpdateState`.

**For central manager state restoration:**
- Restore prior peripheral references from
  `CBCentralManagerRestoredStatePeripheralsKey`
- Restore scan services from `CBCentralManagerRestoredStateScanServicesKey` if
  scanning was active
- Re-assign delegates and retain peripherals in `willRestoreState`

**For peripheral manager state restoration:**
- Restore services from `CBPeripheralManagerRestoredStateServicesKey`
- Restore advertising state from `CBPeripheralManagerRestoredStateAdvertisementDataKey`
- Resume advertising or service setup after state restoration

The system only restores state if the app was backgrounded (not force-quit) and
the appropriate background mode is enabled in Info.plist.

---

## Common Mistakes

### ❌ Not checking Bluetooth state before scanning
```swift
// Bad: Crashes if Bluetooth off
centralManager.scanForPeripherals(withServices: nil, options: nil)
```
✅ **Fix:** Check powered-on state first
```swift
if centralManager.state == .poweredOn {
    centralManager.scanForPeripherals(withServices: nil, options: nil)
} else {
    print("Bluetooth not available")
}
```

### ❌ Losing the peripheral reference
```swift
// Bad: Peripheral is deallocated immediately after discovery
func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, ...) {
    central.connect(peripheral, options: nil)  // peripheral is not retained
}
```
✅ **Fix:** Hold a strong reference to the peripheral
```swift
class BLEManager {
    var discoveredPeripheral: CBPeripheral?  // Strong reference

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, ...) {
        discoveredPeripheral = peripheral  // Retain the peripheral
        peripheral.delegate = self
        central.connect(peripheral, options: nil)
    }
}
```
Core Bluetooth does not retain discovered peripherals. Without a strong reference,
the peripheral is deallocated and the connection fails silently.

### ❌ Forgetting to set delegate before discovery
```swift
// Bad: Callbacks never received
let peripheral = discoveredPeripheral
centralManager.connect(peripheral, options: nil)
// No delegate set yet
```
✅ **Fix:** Set delegate before discovery/connection
```swift
let peripheral = discoveredPeripheral
peripheral.delegate = self
centralManager.connect(peripheral, options: nil)
```

### ❌ Reading all characteristics indiscriminately
```swift
// Bad: Excessive power/latency
service.characteristics?.forEach { characteristic in
    peripheral.readValue(for: characteristic)
}
```
✅ **Fix:** Only read readable characteristics; use notifications
```swift
service.characteristics?.forEach { characteristic in
    if characteristic.properties.contains(.read) {
        peripheral.readValue(for: characteristic)
    }
    if characteristic.properties.contains(.notify) {
        peripheral.setNotifyValue(true, for: characteristic)
    }
}
```

### ❌ Not checking characteristic write type
```swift
// Bad: Write may fail silently
peripheral.writeValue(data, for: characteristic, type: .withResponse)
// But characteristic doesn't support write with response
```
✅ **Fix:** Check properties first
```swift
let writeType: CBCharacteristicWriteType =
    characteristic.properties.contains(.writeWithoutResponse) ? .withoutResponse : .withResponse
peripheral.writeValue(data, for: characteristic, type: writeType)
```

### ❌ Not requesting Bluetooth permissions
```swift
// Bad: App crashes on iOS 13+
// No NSBluetoothPeripheralUsageDescription in Info.plist
```
✅ **Fix:** Add usage descriptions
```
Info.plist:
- NSBluetoothPeripheralUsageDescription: "Describe why..."
- NSBluetoothCentralUsageDescription: "Describe why..."
```

### ❌ Scanning without service filter
```swift
// Bad: High battery drain; discovers all nearby devices
centralManager.scanForPeripherals(withServices: nil, options: nil)
```
✅ **Fix:** Filter by service UUIDs
```swift
let serviceUUIDs = [CBUUID(string: "180A")] // Only device info services
centralManager.scanForPeripherals(withServices: serviceUUIDs, options: nil)
```

---

## Review Checklist

- [ ] Bluetooth state checked (`.poweredOn`) before any operation
- [ ] `CBCentralManagerDelegate` and `CBPeripheralDelegate` set before discovery/connection
- [ ] Scanning filters by service UUID (reduces power/latency)
- [ ] Characteristics checked for read/write properties before accessing
- [ ] Write type matches characteristic properties (withResponse vs withoutResponse)
- [ ] Notifications enabled for characteristics that support `.notify`
- [ ] NSBluetoothCentralUsageDescription / NSBluetoothPeripheralUsageDescription in Info.plist
- [ ] Background modes enabled if scanning/advertising in background
- [ ] State restoration implemented for background operation
- [ ] Peripheral disconnected cleanly in deinit or app background
- [ ] Error handling covers Bluetooth unavailable, device unreachable, permission denied
- [ ] Tests mock CBCentralManager/CBPeripheralManager for unit testing

---
_Source: Apple Developer Documentation · Condensed for Ship Framework agent reference_
