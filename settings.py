from PyQt5.QtCore import QSettings

def get_settings():
  settings = QSettings()
  output = {}
  output["cell_label"] = settings.value("MainWindow/cellLabel")
  return output
