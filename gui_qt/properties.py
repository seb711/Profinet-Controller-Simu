import PyQt5.QtCore as QtCore


class PropertyMeta(type(QtCore.QObject)):
    def __new__(cls, name, bases, attrs):
        for key in list(attrs.keys()):
            attr = attrs[key]
            if not isinstance(attr, Property):
                continue
            initial_value = attr.initial_value
            type_ = type(initial_value)
            notifier = QtCore.pyqtSignal(type_)
            attrs[key] = PropertyImpl(
                initial_value, name=key, type_=type_, notify=notifier)
            attrs[signal_attribute_name(key)] = notifier
        return super().__new__(cls, name, bases, attrs)


class Property:
    """ Property definition.

    This property will be patched by the PropertyMeta metaclass into a PropertyImpl type.
    """
    def __init__(self, initial_value, name=''):
        self.initial_value = initial_value
        self.name = name


class PropertyImpl(QtCore.pyqtProperty):
    """ Actual property implementation using a signal to notify any change. """
    def __init__(self, initial_value, name='', type_=None, notify=None):
        super().__init__(type_, self.getter, self.setter, notify=notify)
        self.initial_value = initial_value
        self.name = name

    def getter(self, inst):
        return getattr(inst, value_attribute_name(self.name), self.initial_value)

    def setter(self, inst, value):
        setattr(inst, value_attribute_name(self.name), value)
        notifier_signal = getattr(inst, signal_attribute_name(self.name))
        notifier_signal.emit(value)

def signal_attribute_name(property_name):
    """ Return a magic key for the attribute storing the signal name. """
    return f'_{property_name}_prop_signal_'


def value_attribute_name(property_name):
    """ Return a magic key for the attribute storing the property value. """
    return f'_{property_name}_prop_value_'