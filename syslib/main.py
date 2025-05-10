# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../main.py
# Compiled at: 2005-07-11 23:40:38
import sys, base, os
# from pathlib import Path
print('pid:', os.getpid())
sys.path.insert(0, 'syslib')
sys.path.insert(0, 'lib')
import lib.kernel.boot

def add_subfolders_to_syspath(base_path):
    for dirpath, dirnames, filenames in os.walk(base_path):
        if dirpath not in sys.path:
            sys.path.append(dirpath)

def init():
    lib.kernel.boot.boot()


if __name__ == '__main__':
    # Directorio actual del script
    # base_directory = str(Path(__file__).resolve().parent.parent)

    # Ruta base desde donde quieres incluir todas las subcarpetas
    # add_subfolders_to_syspath(base_directory)

    init()
