# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/configurationelement.py
# Compiled at: 2004-11-19 02:10:12
"""
This class lazily loads a node from an xml using the minidom and
offers access to that data.  The children are created automatically
when they are accessed, this is so that we don't traverse the 
DOM twice, once more after the minidom has parsed it
"""
import encodings, encodings.aliases, xml.dom.minidom

def loadFile(filename):
    """Creates a new configuration element and attempts to parse the 
        file, if error, then returns None"""
    element = ConfigurationElement()
    try:
        element.loadFile(filename)
        return element
    except Exception, msg:
        print 'Error loading element:', Exception, msg

    return None
    return


def loadFromString(buffer):
    """Creates a new configuration element and attempts to parse the 
        buffer, if error, then returns None"""
    element = ConfigurationElement()
    try:
        element.loadFromString(buffer)
        return element
    except Exception, msg:
        print 'Error loading element:', Exception, msg

    return None
    return


def new(name):
    element = ConfigurationElement()
    element.document = xml.dom.minidom.Document()
    element.node = element.document.createElement(name)
    element.document.appendChild(element.node)
    element.setName(name)
    return element


class ConfigurationElement(object):
    __module__ = __name__

    def __init__(self, parent=None):
        self.parent = parent
        self.value = None
        self.attributes = {}
        self.children = []
        self.name = None
        return

    def loadFromString(self, buffer):
        """May throw an ioexception"""
        self.document = xml.dom.minidom.parseString(buffer)
        node = self.document.firstChild
        if node == None:
            raise Exception, 'Malformed config element has no default node'
        self.re_Create(node)
        return

    def loadFile(self, filename):
        """May throw an ioexception"""
        self.document = xml.dom.minidom.parse(filename)
        node = self.document.firstChild
        if node == None:
            raise Exception, 'Malformed config element has no default node'
        self.re_Create(node)
        return

    def re_Create(self, node):
        self.children = []
        if node.nodeType == node.ELEMENT_NODE:
            self.name = node.tagName
            for key in node.attributes.keys():
                self.attributes[key] = node.attributes[key].value

            for kid in node.childNodes:
                if kid.nodeType == node.ELEMENT_NODE:
                    n = ConfigurationElement(self)
                    n.re_Create(kid)
                    self.children.append(n)
                elif kid.nodeType == node.TEXT_NODE:
                    self.value = kid.data

    def _toxml(self, document, parent):
        node = document.createElement(self.getName())
        parent.appendChild(node)
        for (key, value) in self.attributes.items():
            node.setAttribute(key, value)

        if self.value is not None:
            vn = document.createTextNode(self.value)
            node.appendChild(vn)
        for kid in self.children:
            node.appendChild(kid._toxml(document, node))

        return node
        return

    def tostring(self):
        return self.toxml().toxml()

    def toxml(self):
        document = xml.dom.minidom.Document()
        self._toxml(document, document)
        return document

    def createChild(self, name):
        n = ConfigurationElement(self)
        n.name = name
        self.children.append(n)
        return n

    def setAttribute(self, name, value):
        self.attributes[name] = value

    def getAttribute(self, name):
        if not self.attributes.has_key(name):
            return None
        return self.attributes[name]
        return

    def getAttributeNames(self):
        return self.attributes.keys()

    def getChildren(self, name=None):
        if name is not None:
            return self.getChildrenNamed(name)
        return self.children
        return

    def getChildrenNamed(self, name):
        nl = []
        for kid in self.children:
            if kid.getName() == name:
                nl.append(kid)

        return nl

    def createChildIfNotExists(self, name):
        child = self.getChildNamed(name)
        if child is None:
            child = self.createChild(name)
        return child
        return

    def getChildNamed(self, name):
        kids = self.getChildrenNamed(name)
        if len(kids) == 0:
            return None
        return kids[0]
        return

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value.strip()

    def reprAttrs(self):
        if len(self.getAttributeNames()) == 0:
            return ''
        names = self.getAttributeNames()
        buff = ''
        sep = ''
        for name in names:
            buff += "%s%s='%s'" % (sep, name, self.getAttribute(name))
            sep = ', '

        return buff

    def clone(self, original):
        """ DEEP CLONE!!! """
        for name in original.getAttributeNames():
            self.setAttribute(name, original.getAttribute(name))

        if original.getValue() is not None:
            self.setValue(original.getValue().strip())
        for originalChild in original.getChildren():
            newChild = self.createChild(originalChild.getName())
            newChild.clone(originalChild)

        return

    def __repr__(self):
        return "[ConfigurationElement: name='%s', attrs=(%s), childCount='%i', value='%s']" % (self.getName(), self.reprAttrs(), len(self.getChildren()), self.getValue())


if __name__ == '__main__':
    config = loadFile('simple.xml')
    c = config.createChild('longhotsummer')
    c.setAttribute('eat', 'fat')
    d = config.createChild('pudding')
    e = d.createChild('pop')
    e.setValue('Comidita Cho')
    xml = config.toxml()
    print xml.toxml()
    print 'don'
