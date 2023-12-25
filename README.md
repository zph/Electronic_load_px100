# Electronic_load_px100
150W Electronic load / Battery discharge capacity tester PX-100 protocol and control software.

Tested to work with board revisions 2.70 and 2.8

# Binary protocol

See the [v2.70 binary Protocol description](protocol_PX-100_2_70.md)

# Models compatible

* DL24 180W Atorch Discharge Capacity Tester from AliExpress
* PX100 150W Battery Discharge Capacity Tester

# Control software

### Main features:

- Control all load features
- Voltage and Current plot vs time
- Save logs to CSV at exit and at device reset
- Internal resistance measurement at user-defined voltage steps
- Software-defined CC-CV discharge to speed up capacity tests for low current discharge

# Installing

## Windows

An installer can be downloaded from the [releases section](https://github.com/misdoro/Electronic_load_px100/releases/latest)

Please use -x86.exe if you are running 32-bit windows.

## Linux / macOS

Python is required to run this software. Version 3.6 or newer is required.

Run the following line in terminal to install dependencies:
```
pip install --user -r requirements.txt
```

Then run
```
python main.py
```
to execute the control program.

