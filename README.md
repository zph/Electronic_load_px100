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

```
python main.py
```
to execute the control program.


# Running

The program can be run in GUI mode on Linux/Mac as `python main.py`.

The program can be executed via CLI for specific modes and a jupyter notebook is a convenient way to do so:

```python
import instruments
```

```python
i = instruments.Instruments()
```

```python
i.instruments
```

    [<instruments.px100.PX100 at 0x11153f860>]

```python
px = i.instruments[0]
```

```python
px.get_readings()
```

    {'is_on': 1.0,
     'voltage': 35.244,
     'current': 3.401,
     'time': datetime.time(1, 50, 21),
     'cap_ah': 7.013,
     'cap_wh': 262.2,
     'temp': 40.0,
     'set_current': 3.4,
     'set_voltage': 20.0,
     'set_timer': datetime.time(4, 10),
     'ts': datetime.datetime(2023, 12, 27, 21, 55, 41, 646358),
     'watts': 119.86484399999999,
     'voltage_cutoff': 20.0}

```python
px.maintain_constant_power(120)
```
