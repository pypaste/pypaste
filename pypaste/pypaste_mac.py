# -*- coding: utf-8 -*-

"""Mac module."""

from .pypaste import PyPasteBase as _PyPaste
import ctypes as _ct
import ctypes.util as _ctu


class Callable:
    def __init__(self, callable, argtypes=[], restype=None):
        callable.argtypes = argtypes
        callable.restype = restype

        self._callable = callable

    def __call__(self, *args):
        return self._callable(*args)


class MacPaste(_PyPaste):
    def __init__(self):
        self._appkit = _ct.cdll.LoadLibrary(
                _ctu.find_library('AppKit'))
        self._pbtype = _ct.c_void_p.in_dll(self._appkit, "NSPasteboardTypeString")
        self._foundation = _ct.cdll.LoadLibrary(
                _ctu.find_library('Foundation'))
        self._objc = _ct.cdll.LoadLibrary(_ctu.find_library('objc'))

        self._objc.objc_getClass.argtypes = [_ct.c_char_p]
        self._objc.objc_getClass.restype = _ct.c_void_p
        self._objc.sel_registerName.argtypes = [_ct.c_char_p]
        self._objc.sel_registerName.restype = _ct.c_void_p
        self._objc.objc_msgSend.restype = _ct.c_void_p
        # bjc_msgSend.argtypes = [_ct.c_void_p, _ct.c_void_p]

        self._objc.class_getProperty.argtypes = [_ct.c_void_p, _ct.c_char_p]

    @property
    def appkit(self):
        return self._appkit

    @property
    def objc(self):
        return self._objc

    def _sel_name(self, value):
        return self.objc.sel_registerName(value.encode('utf-8'))

    def _call_method(self, classptr, name, *args, argtypes=None, restype=_ct.c_void_p):
        if argtypes is None:
            argtypes = [_ct.c_void_p] * len(args)

        sel = self._sel_name(name)
        self.objc.objc_msgSend.argtypes = [_ct.c_void_p] * 2 + argtypes
        self.objc.objc_msgSend.restype = restype
        val = self.objc.objc_msgSend(classptr, sel, *args)
        return val

    def _get_property(self, classptr, propertyname, restype=_ct.c_void_p):
        self._objc.class_getProperty.restype = restype
        return self.objc.class_getProperty(classptr, propertyname.encode('utf-8'))

    def _get_attributes(self, property):
        self.objc.property_getAttributes.argtypes = [_ct.c_void_p]
        self.objc.property_getAttributes.restype = _ct.c_char_p
        att = self.objc.property_getAttributes(property)
        return att

    def __enter__(self):
        NSAutoreleasePool = self.objc.objc_getClass(b'NSAutoreleasePool')

        self._pool = self._call_method(
                NSAutoreleasePool, 'alloc')
        self._pool = self._call_method(
                self._pool, 'init')

        NSPasteboard = self.objc.objc_getClass(b'NSPasteboard')
        self._pboard = self._call_method(NSPasteboard, "generalPasteboard")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._call_method(
                self._pool, 'release')

    @property
    def clipboard(self):
        ptr = self._call_method(self._pboard, "stringForType:", self._pbtype)
        return str(self._call_method(ptr, "UTF8String", restype=_ct.c_char_p))

    @clipboard.setter
    def clipboard(self, value):
        NSString = self.objc.objc_getClass(b"NSString")

        size = Callable(self.objc.class_getInstanceSize, argtypes=[_ct.c_void_p], restype=_ct.c_size_t)(NSString)
        cbuf = _ct.create_string_buffer(size)
        NSStringConst = Callable(self.objc.objc_constructInstance, argtypes=[_ct.c_void_p, _ct.c_void_p], restype=_ct.c_void_p)
        ns_string = NSStringConst(NSString, _ct.byref(cbuf))
        ns_string = self._call_method(ns_string, "initWithUTF8String:", value.__str__().encode('UTF-8'), argtypes=[_ct.c_char_p], restype=_ct.c_void_p)

        val = self._call_method(self._pboard, "setString:forType:", ns_string, self._pbtype, restype=_ct.c_bool)

        NSStringDest = Callable(self.objc.objc_destructInstance, argtypes=[_ct.c_void_p], restype=_ct.c_void_p)
        NSStringDest(ns_string)
