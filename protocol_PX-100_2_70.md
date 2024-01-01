# PX-100 ELECTRONIC LOAD


This document applies to PX-100 Electronic load version 2.70 with rs-232 TTL serial interface.

# Electrical diagram

Any USB TTL Serial adapter should do. Both 3.3V and 5V IO levels work. I used FT232 adapter from A.


| LOAD | RS-232 TTL adapter |
| -- | -- |
| GND | GND |
| TXD | RXD |
| RXD | TXD |

# Connection settings

Electronic load uses 9600 baud 8N1 (8 bits, no parity, 1 stop bit) configuration with no flow control.

# Binary protocol

Electronic load uses a binary protocol with 7-bytes control frames sent by host and either 1 or 7 bytes response frames. All other data is ignored, until the next command is received.
No line end characters is sent or expected.

The control frame looks like:
```
  0xB1 0xB2 CMD D1 D2 0xB6
```

with 2 header bytes `0xB1 0xB2` and a trailing byte `0xB6`

Data format of control commands differs from the query commands.

## Control commands
Control commands start with `0x0*` and the unit responds with 1 byte `0x6F`

First data byte carries the integer part, second data byte carries a fraction * 100

So 1.23 V will be tranmitted as 0x01 0x17 hexadecimal.

| Command | Data | Description |
| -- | -- | -- |
| 0x01 | 0x0100 - ON \ 0x0000 OFF | Enable or disable the load
| 0x02 | D1.D2  | Set current
| 0x03 | D1.D2  | Set cutoff voltage
| 0x04 | 16-bit unsigned integer | Set timeout in seconds
| 0x05 | 0x0000 | Reset counters

## Additional Control data

Credit: https://auto-scripting.com/2020/05/03/atorch-dl24-hack-1/
Explanation: https://github.com/syssi/esphome-atorch-dl24/blob/main/docs/protocol-design.md#type-indicator

Head, Head, Cmd , DC  ,
0xff, 0x55, 0x11, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x50	energy reset
0xff, 0x55, 0x11, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x51	cap reset
0xff, 0x55, 0x11, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x52	timing
0xff, 0x55, 0x11, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x53	no reaction
0xff, 0x55, 0x11, 0x02, 0x05, 0x00, 0x00, 0x00, 0x00, 0x54	timing, energy, cap reset
0xff, 0x55, 0x11, 0x02, 0x06, 0x00, 0x00, 0x00, 0x00, 0x55	no reaction
——–	——-
0xff, 0x55, 0x11, 0x02, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00	Setup button
(move cursor to left)
0xff, 0x55, 0x11, 0x02, 0x32, 0x00, 0x00, 0x00, 0x00, 0x01	ON/OFF button
0xff, 0x55, 0x11, 0x02, 0x33, 0x00, 0x00, 0x00, 0x00, 0x02	+ button
0xff, 0x55, 0x11, 0x02, 0x34, 0x00, 0x00, 0x00, 0x00, 0x03	– button

## From decompilation of E_Test
```java
    /* access modifiers changed from: private */
    public void send(int i, int i2, int i3, int i4, int i5) {
        final byte[] bArr = new byte[10];
        bArr[0] = -1;
        bArr[1] = 85;
        bArr[2] = 17;
        bArr[3] = (byte) i;
        bArr[4] = (byte) i2;
        bArr[5] = 0
        bArr[6] = (byte) i3;
        bArr[7] = (byte) i4;
        bArr[8] = (byte) i5;
        bArr[9] = (byte) ((((((((bArr[2] & 255) + (bArr[3] & 255)) + (bArr[4] & 255)) + (bArr[5] & 255)) + (bArr[6] & 255)) + (bArr[7] & 255)) + (bArr[8] & 255)) ^ 68); // checksum crc
        new Thread(new Runnable() {
            public void run() {
                if (BLEService.connectDevice == null || BLEService.connectDevice.getType() != 2) {
                    BLEService.sppSend(bArr);
                } else {
                    BLEService.send(bArr);
                }
            }
        }).start();

      // OR

          public void send(int i, int i2, int i3, int i4, int i5) {
        final byte[] bArr = {-1, 85, 17, (byte) i, (byte) i2, 0, (byte) i3, (byte) i4, (byte) i5, (byte) ((((((((bArr[2] & 255) + (bArr[3] & 255)) + (bArr[4] & 255)) + (bArr[5] & 255)) + (bArr[6] & 255)) + (bArr[7] & 255)) + (bArr[8] & 255)) ^ 68)};
        new Thread(new Runnable() { // from class: com.tang.etest.e_test.MainActivity.2
            @Override // java.lang.Runnable
            public void run() {
                if (BLEService.connectDevice != null && BLEService.connectDevice.getType() == 2) {
                    BLEService.send(bArr);
                } else {
                    BLEService.sppSend(bArr);
                }
            }
        }).start();
    }


      // Backlight level : 33
          private void DialogSelect() {
        final NumberPicker numberPicker = new NumberPicker(this);
        numberPicker.setDisplayedValues(new String[]{getString(R.string.Long_black), "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", getString(R.string.Long_bright)});
        numberPicker.setDescendantFocusability(393216);
        numberPicker.setMaxValue(60);
        numberPicker.setMinValue(0);
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setView((View) numberPicker);
        builder.setPositiveButton((CharSequence) getString(R.string.confirm), (DialogInterface.OnClickListener) new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialogInterface, int i) {
                MainActivity mainActivity = MainActivity.this;
                mainActivity.send(mainActivity.adu, 33, 0, 0, numberPicker.getValue());
            }
        }).setNegativeButton((CharSequence) getString(R.string.cancel), (DialogInterface.OnClickListener) new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialogInterface, int i) {
            }
        }).show();

      // Electricity price 34
                        if (!obj.equals("")) {
                    if (Double.parseDouble(obj) < 0.01d || Double.parseDouble(obj) > 9999.99d) {
                        Toast.makeText(MainActivity.this.getApplicationContext(), MainActivity.this.getString(R.string.f5), 1).show();
                        return;
                    }
                    Log.i("输入的数为", editText.getText().toString());
                    int parseDouble = (int) (Double.parseDouble(obj) * 100.0d);
                    byte b = (byte) (parseDouble / 65536);
                    MainActivity mainActivity = MainActivity.this;
                    int access$800 = mainActivity.adu;
                    mainActivity.send(access$800, 34, b, (byte) (parseDouble / 256), (byte) (parseDouble % 256));
  ```

            case R.id.button_jia: // plus
                send(this.adu, 51, 0, 0, 0);
                return;
            case R.id.button_jian: // minus
                send(this.adu, 52, 0, 0, 0);
                return;
            case R.id.button_ok:
                send(this.adu, 50, 0, 0, 0);
                return;
            case R.id.button_set:
                send(this.adu, 49, 0, 0, 0);
                return;



66
"\xffU\x01\x02\x00\x00'\x00\x03e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00!<\x00\x00\x00\x00B"

## Query commands
Query commands start with `0x1*` and the unit responds with 7 bytes:

```
  0xCA 0xCB D1 D2 D3 0xCE 0xCF
```
Request data bytes should be send as 0x00.

Response data format varies.

| Command | Response Data | Description |
| -- | -- | --
| 0x10 | 0x000000 OFF 0x000001 ON | Load enabled ?
| 0x11 | 24-bit integer | Voltage reading, mV
| 0x12 | 24-bit integer | Current reading, mA
| 0x13 | D1 hours, D2 minutes, D3 seconds | Elapsed or remaining time
| 0x14 | 24-bit integer | Capacity, mAH
| 0x15 | 24-bit integer | Capacity, mWH
| 0x16 | 24-bit integer | Mosfet temperature, °C
| 0x17 | 24-bit integer | Current setting, AH * 100, 1.23A would be sent as 123
| 0x18 | 24-bit integer | Cutoff voltage setting, V*100, 3.21V will be sent as 321
| 0x19 | D1 hours, D2 minutes, D3 seconds | Timer setting


# All Packets Observed During BT Scanning of D24P

```
ca:cb:00:00:00:ce:cf
ca:cb:00:00:01:ce:cf
ca:cb:00:00:03:ce:cf
ca:cb:00:00:06:ce:cf
ca:cb:00:00:16:ce:cf
ca:cb:00:00:17:ce:cf
ca:cb:00:01:2c:ce:cf
ca:cb:00:0f:8c:ce:cf
ca:cb:00:0f:8d:ce:cf
ca:cb:00:0f:9e:ce:cf
ca:cb:00:0f:a6:ce:cf
ca:cb:00:0f:c7:ce:cf
ca:cb:00:0f:db:ce:cf
ca:cb:00:0f:dc:ce:cf
ca:cb:00:0f:dd:ce:cf
ca:cb:00:0f:de:ce:cf
ca:cb:00:0f:df:ce:cf
ca:cb:00:0f:e0:ce:cf
ca:cb:00:25:00:ce:cf
ff:55:01:02:00:00:26:00:03:4f:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:25:3c:00:00:00:00:b7
ff:55:01:02:00:00:26:00:03:5e:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:15:3c:00:00:00:00:b6
ff:55:01:02:00:00:26:00:03:5f:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:17:3c:00:00:00:00:b1
ff:55:01:02:00:00:26:00:03:64:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:20:3c:00:00:00:00:47
ff:55:01:02:00:00:26:00:03:64:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:22:3c:00:00:00:00:41
ff:55:01:02:00:00:26:00:03:64:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:2c:3c:00:00:00:00:54
ff:55:01:02:00:00:26:00:03:64:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:30:3c:00:00:00:00:50
ff:55:01:02:00:00:26:00:03:64:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:18:00:00:00:2d:3c:00:00:00:00:56
ff:55:01:02:00:00:26:00:03:6a:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:18:00:00:00:31:3c:00:00:00:00:58
ff:55:01:02:00:00:26:00:03:6b:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:0d:3c:00:00:00:00:b3
ff:55:01:02:00:00:26:00:03:6b:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:29:3c:00:00:00:00:57
ff:55:01:02:00:00:26:00:03:6d:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:11:3c:00:00:00:00:b9
ff:55:01:02:00:00:26:00:03:6d:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:14:3c:00:00:00:00:44
ff:55:01:02:00:00:26:00:03:70:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:0a:3c:00:00:00:00:bd
ff:55:01:02:00:00:26:00:03:73:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:13:3c:00:00:00:00:41
ff:55:01:02:00:00:26:00:03:73:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:28:3c:00:00:00:00:5e
ff:55:01:02:00:00:26:00:03:74:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:10:3c:00:00:00:00:47
ff:55:01:02:00:00:26:00:03:85:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:06:3c:00:00:00:00:4e
ff:55:01:02:00:00:27:00:02:96:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:32:3c:00:00:00:00:0c
ff:55:01:02:00:00:27:00:03:52:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:16:3c:00:00:00:00:ac
ff:55:01:02:00:00:27:00:03:56:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:1b:3c:00:00:00:00:b5
ff:55:01:02:00:00:27:00:03:56:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:26:3c:00:00:00:00:b8
ff:55:01:02:00:00:27:00:03:56:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:2f:3c:00:00:00:00:42
ff:55:01:02:00:00:27:00:03:57:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:19:3c:00:00:00:00:b4
ff:55:01:02:00:00:27:00:03:57:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:1c:3c:00:00:00:00:b7
ff:55:01:02:00:00:27:00:03:58:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:18:3c:00:00:00:00:b4
ff:55:01:02:00:00:27:00:03:5c:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:1a:3c:00:00:00:00:b2
ff:55:01:02:00:00:27:00:03:5d:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:1d:3c:00:00:00:00:be
ff:55:01:02:00:00:27:00:03:5d:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:1e:3c:00:00:00:00:bf
ff:55:01:02:00:00:27:00:03:5d:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:23:3c:00:00:00:00:44
ff:55:01:02:00:00:27:00:03:5d:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:24:3c:00:00:00:00:45
ff:55:01:02:00:00:27:00:03:5d:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:2b:3c:00:00:00:00:4d
ff:55:01:02:00:00:27:00:03:61:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:18:00:00:00:2e:3c:00:00:00:00:55
ff:55:01:02:00:00:27:00:03:65:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:0e:3c:00:00:00:00:b7
ff:55:01:02:00:00:27:00:03:65:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:0f:3c:00:00:00:00:b0
ff:55:01:02:00:00:27:00:03:65:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:1f:3c:00:00:00:00:40
ff:55:01:02:00:00:27:00:03:65:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:21:3c:00:00:00:00:42
ff:55:01:02:00:00:27:00:03:65:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:2a:3c:00:00:00:00:54
ff:55:01:02:00:00:27:00:03:6c:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:12:3c:00:00:00:00:ba
ff:55:01:02:00:00:27:00:03:6e:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:08:3c:00:00:00:00:b2
ff:55:01:02:00:00:27:00:03:71:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:0c:3c:00:00:00:00:b9
ff:55:01:02:00:00:27:00:03:72:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:27:3c:00:00:00:00:5d
ff:55:01:02:00:00:27:00:03:74:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:07:3c:00:00:00:00:bf
ff:55:01:02:00:00:27:00:03:74:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:0b:3c:00:00:00:00:bb
ff:55:01:02:00:00:27:00:03:75:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:09:3c:00:00:00:00:ba
ff:55:01:02:00:00:28:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:06:3c:00:00:00:00:c0
ff:55:01:02:00:00:28:00:00:00:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:33:3c:00:00:00:00:f6
ff:55:01:02:00:00:28:00:00:00:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:18:00:00:00:32:3c:00:00:00:00:f6
ff:55:01:02:00:00:28:00:00:00:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:18:00:00:00:33:3c:00:00:00:00:f7
ff:55:01:02:00:00:28:00:00:55:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:33:3c:00:00:00:00:43
ff:55:01:02:00:00:29:00:00:00:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:33:3c:00:00:00:00:f7
ff:55:01:02:00:00:29:00:00:00:00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:18:00:00:00:33:3c:00:00:00:00:f0
ff:55:02:01:01:00:00:40
ff:55:02:01:02:00:00:41
ff:55:11:00:01:00:00:00:00:56
ff:55:11:00:32:00:00:00:00:07
ff:55:11:00:33:00:00:00:00:00
ff:55:11:00:34:00:00:00:00:01
ff:55:11:02:32:00:00:00:00:01
ff:55:11:2c:33:00:00:00:00:34
ff:55:11:2c:34:00:00:00:00:35
ff:55:11:41:31:00:00:00:00:c7
ff:55:11:b6:31:00:00:00:00:bc
ff:55:11:ca:31:00:00:00:00:48
ff:55:11:ce:34:00:00:00:00:57
ff:55:11:cf:01:00:00:00:00:a5
ff:55:11:cf:31:00:00:00:00:55
ff:55:11:f7:31:00:00:00:00:7d
```
