# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../pkg_plugin.py
# Compiled at: 2004-07-24 10:26:33
import sys, os, zipfile
print(('package plugin', sys.argv))
if len(sys.argv) < 3:
    print('No plugin specified')
    sys.exit(13)
plugin_dir = '../plugins'
plugin_source = sys.argv[1]
plugin_name = sys.argv[2]
includes_ext = []
if len(sys.argv) > 3:
    includes_ext = sys.argv[3].strip().split(',')
print(('Creating ', plugin_name, ' -> ', plugin_source))
fullpath = os.path.join(os.getcwd(), plugin_source)
print(('\t', fullpath))
entries = os.walk(fullpath)
fullname = os.path.join(os.getcwd(), plugin_name + '.zip')
print(('Creating ', fullname))
zf = zipfile.ZipFile(fullname, 'w')
for (dirpath, dirnames, filenames) in entries:
    print((dirpath, dirnames, filenames))
    currdir = os.path.basename(dirpath)
    for filename in filenames:
        if len(includes_ext) > 0:
            (name, ext) = os.path.splitext(filename)
            if len(ext) > 0:
                ext = ext[1:]
            print(('Checking', ext))
            if ext not in includes_ext:
                print('No existe')
                continue
        print(('\t', filename, '->', os.path.join(currdir, filename)))
        zf.write(os.path.join(dirpath, filename), os.path.join(currdir, filename))

zf.close()
