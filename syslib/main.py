# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../main.py
# Compiled at: 2005-07-11 23:40:38
import sys, base, os
from pathlib import Path
print('pid:', os.getpid())
sys.path.insert(0, 'syslib')
sys.path.insert(0, 'lib')
import lib.kernel.boot

def init():
    lib.kernel.boot.boot()


if __name__ == '__main__':

    # Directorio actual del script
    base_directory = str(Path(__file__).resolve().parent.parent)

    sys.path.insert(0, base_directory + "\\plugins\\adr2100\\")
    sys.path.insert(0, base_directory + "\\plugins\\core\\")
    sys.path.insert(0, base_directory + "\\plugins\\et2216e\\")
    sys.path.insert(0, base_directory + "\\plugins\\executionengine\\")
    sys.path.insert(0, base_directory + "\\plugins\\extendededitor\\")
    sys.path.insert(0, base_directory + "\\plugins\\furnacezone\\")
    sys.path.insert(0, base_directory + "\\plugins\\goosemonitor\\")
    sys.path.insert(0, base_directory + "\\plugins\\grapheditor\\")
    sys.path.insert(0, base_directory + "\\plugins\\graphview\\")
    sys.path.insert(0, base_directory + "\\plugins\\grideditor\\")
    sys.path.insert(0, base_directory + "\\plugins\\hardware\\")
    sys.path.insert(0, base_directory + "\\plugins\\help\\")
    sys.path.insert(0, base_directory + "\\plugins\\labbooks\\")
    sys.path.insert(0, base_directory + "\\plugins\\mfc\\")
    sys.path.insert(0, base_directory + "\\plugins\\mks146\\")
    sys.path.insert(0, base_directory + "\\plugins\\mks647bc\\")
    sys.path.insert(0, base_directory + "\\plugins\\mkspdr2000\\")
    sys.path.insert(0, base_directory + "\\plugins\\panelview\\")
    sys.path.insert(0, base_directory + "\\plugins\\poi\\")
    sys.path.insert(0, base_directory + "\\plugins\\pressure_gauge\\")
    sys.path.insert(0, base_directory + "\\plugins\\resources\\")
    sys.path.insert(0, base_directory + "\\plugins\\resourcesui\\")
    sys.path.insert(0, base_directory + "\\plugins\\rs485\\")
    sys.path.insert(0, base_directory + "\\plugins\\safetyinterlock\\")
    sys.path.insert(0, base_directory + "\\plugins\\schematicspanel\\")
    sys.path.insert(0, base_directory + "\\plugins\\ui\\")
    sys.path.insert(0, base_directory + "\\plugins\\up150\\")
    sys.path.insert(0, base_directory + "\\plugins\\update\\")
    sys.path.insert(0, base_directory + "\\plugins\\validator\\")

    init()
