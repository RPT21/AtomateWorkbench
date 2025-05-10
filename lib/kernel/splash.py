# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: lib/kernel/splash.py
# Compiled at: 2004-08-01 07:31:11
from wx import App, Frame

class SplashApp(App):
    __module__ = __name__

    def OnInit(self):
        return True


app = None
frame = None

def bringup():
    print('Bringing up splash')


def increment(jobDescription):
    print(jobDescription)


def bringdown():
    print('Bringing down splash')


# global app ## Warning: Unused global
# global frame ## Warning: Unused global
