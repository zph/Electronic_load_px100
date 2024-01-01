from construct import Struct, Int8ub, Int16ub, Int24ub, Int32ub, Const, Computed, this, Byte, Enum, Switch

# ## Packet layout
#
# |    Offset | Field        | Block size | Note                                      |
# | --------: | ------------ | ---------- | ----------------------------------------- |
# |      `00` | Magic Header | 2 byte     | `FF 55`                                   |
# |      `02` | Message Type | 1 byte     | [Message Type](#type-indicator)           |
# |      `03` | Payload      |            |                                           |
# | Last byte | Checksum     | 1 byte     | [Checksum Algorithm](#checksum-algorithm) |
#
# ### Type indicator
#
# |         Type | Value | Payload size | Note                                  |
# | -----------: | ----- | ------------ | ------------------------------------- |
# | Message Type | `01`  | 32 byte      | Report                                |
# | Message Type | `02`  | 4 byte       | [Reply](#reply)                       |
# | Message Type | `11`  | 6 byte       | [Command](#command)                   |
# |            - | -     | -            | -                                     |
# |  Device Type | `01`  |              | [AC Meter Report](#ac-meter-report)   |
# |  Device Type | `02`  |              | [DC Meter Report](#dc-meter-report)   |
# |  Device Type | `03`  |              | [USB Meter Report](#usb-meter-report) |

### DC Meter Report

# > There are currently no unpurchased product tests
#
# | Offset | Field            | Block size | Note                                |
# | -----: | ---------------- | ---------- | ----------------------------------- |
# |   `03` | Device Type      | 1 byte     | `02` [Device Type](#type-indicator) |
# |   `04` | Voltage          | 3 byte     | 24 bit BE (divide by 10)            |
# |   `07` | Amp              | 3 byte     | 24 bit BE (divide by 1000)          |
# |   `0A` | Watt             | 3 byte     | 24 bit BE (divide by 10)            |
# |   `0D` | W·h              | 4 byte     | 32 bit BE (divide by 100)           |
# |   `11` | Price (per kW·h) | 3 byte     | 24 bit BE (divide by 100)           |
# |   `14` |                  | 4 byte     | unknown value                       |
# |   `18` | Temperature      | 2 byte     | 16 bit BE                           |
# |   `1A` | Hour             | 2 byte     | 16 bit BE                           |
# |   `1C` | Minute           | 1 byte     |                                     |
# |   `1D` | Second           | 1 byte     |                                     |
# |   `1E` | Backlight        | 1 byte     |                                     |

# Example b"\xffU\x01\x02\x00\x00'\x00\x03e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00!<\x00\x00\x00\x00B"

DCMeterReport = Struct(
    "voltage_raw" / Int24ub,
    "voltage" / Computed(this.voltage_raw / 10),
    "amperage_raw" / Int24ub,
    "amperage" / Computed(this.amperage_raw / 1000),
    "amp_hours_raw" / Int24ub,
    "amp_hours" / Computed(this.amp_hours_raw / 100),
    "watt_hours_raw" / Int32ub,
    "watt_hours" / Computed(this.watt_hours_raw * 10),
    "price_per_wh_raw" / Int24ub,
    "price_per_wh" / Computed(this.price_per_wh_raw / 100),
    "unknown1" / Int32ub,
    "temperature" / Int16ub,
    "hour" / Int16ub,
    "minute" / Byte,
    "second" / Byte,
    "backlight" / Byte,
)

ACMeterReport = Struct(
    "voltage_raw" / Int24ub,
    "voltage" / Computed(this.voltage_raw / 10),
    "amperage_raw" / Int24ub,
    "amperage" / Computed(this.amperage_raw / 1000),
    "wattage_raw" / Int24ub,
    "wattage" / Computed(this.wattage_raw / 10),
    "watt_hours_raw" / Int32ub,
    "watt_hours" / Computed(this.watt_hours_raw / 100),
    "price_per_wh_raw" / Int24ub,
    "price_per_wh" / Computed(this.price_per_wh_raw / 100),
    "frequency_raw" / Int8ub,
    "frequency" / Computed(this.frequency_raw / 10),
    "power_factor_raw" / Int8ub,
    "power_factor" / Computed(this.power_factor_raw / 1000),
    "temperature" / Int16ub,
    "hour" / Int16ub,
    "minute" / Byte,
    "second" / Byte,
    "backlight" / Byte,
)

USBMeterReport = Struct(
    "voltage_raw" / Int24ub,
    "voltage" / Computed(this.voltage_raw / 10),
    "amperage_raw" / Int24ub,
    "amperage" / Computed(this.amperage_raw / 1000),
    "amp_hours_raw" / Int24ub,
    "amp_hours" / Computed(this.amp_hours_raw / 10),
    "watt_hours_raw" / Int32ub,
    "watt_hours" / Computed(this.watt_hours_raw / 100),
    "usb_d_minus_raw" / Int16ub,
    "usb_d_minus" / Computed(this.usb_d_minus_raw / 100),
    "usb_d_plus_raw" / Int16ub,
    "usb_d_plus" / Computed(this.usb_d_plus_raw / 100),
    "temperature" / Int16ub,
    "hour" / Int16ub,
    "minute" / Byte,
    "second" / Byte,
    "backlight" / Byte,
)

# Note no checksum on report entries
Report = Struct(
    "device_type" / Enum(Int8ub, ac_meter=1, dc_meter=2, usb_meter=3),
    "report_data" / Switch(lambda this: int(this.device_type), { 1:ACMeterReport, 2:DCMeterReport, 3:USBMeterReport })
)

# Length 21
# "\xffU\x02\x01\x01\x00\x00@"
Reply = Struct(
    "state" / Enum(Byte, ok=1, unsupported=3),
    "unknown" / Int24ub
)

# "\xca\xcb\x00\x00\x00\xce\xcf"
CommandDataReply = Struct(
    "data" / Int24ub,
    "suffix" / Const(b"\xCE\xCF"),
)

SubCommand = Struct(

)

# "\xffU\x11\x00\x01\x00\x00\x00\x00V"
Command = Struct(
    "device_type" / Enum(Byte, ac_meter=1, dc_meter=2, usb_meter=3, unknown1=0, unknown2=44, unknown3=207), #, 206, 202, 182, 65, 247),
    "command" / Enum(Byte, reset_wh=1, reset_ah=2, reset_duration=3, reset_all=5, plus_button=11, minus_button=12, set_backlight_time=21, set_price=22, setup=31, enter=32, plus_button_usb=33, minus_button_usb=34, enter_2=49, ok_2=50, plus_button_3=51, minus_button_3=52),
    "value" / Int32ub
    # Checksum? of Byte
)

# Note spec in repo declares a command as 11 but really it's 0x11 ie 17
Message = Struct(
    "message_type" / Enum(Int8ub, report=1, reply=2, command=0x11),
    "payload" / Switch(lambda this: int(this.message_type), { 1:Report, 2:Reply, 0x11:Command })
)

# Length 20
# "\xca\xcb\x00\x00\x00\xce\xcf"
UrMessage = Struct(
    "header" / Enum(Byte, command_data_reply=202, message=255),
    "header2" / Byte,
    "payload" / Switch(lambda this: int(this.header), { 202:CommandDataReply, 255:Message, })
)

# report.parse(b"\xffU\x01\x02\x00\x00'\x00\x03e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00!<\x00\x00\x00\x00B")

# Format: "ff:55:01:02:00:00:28:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:17:00:00:00:06:3c:00:00:00:00:c0"
# Gathered by File > Export Packet Dissections > As JSON
# Extract via jq: > jq --raw-output '.[] | ._source.layers.btspp[]' < ~/Downloads/packets.json > report_packet_lines.txt
def parse_wireshark_data(data):
    bx = bytearray.fromhex(data.replace(":", ""))
    print(Message.parse(bx))
