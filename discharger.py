import instruments

# Discharge tester and recorder
# Features:
# -

TARGET_VOLTAGE = 4.18

def main():
  i = instruments.Instruments()
  tester = i.instruments[0]
  tester.reset()
  tester.turnOn()
  measurement = tester.readAll(read_all_aux=True)
  tester.set_current(1)
