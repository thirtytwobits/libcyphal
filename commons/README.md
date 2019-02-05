# libuavcan commons

The commons is a set of implementations that are optional but complementary to the core libuavcan header library. Certain features are built-in to libuavcan but may be reimplemented or extended by users of the library. Other features (like platform adapters) are not part of the core library but are provided to help with testing and integration.

All commons sub-projects are provided under the same license as libuavcan.

## dsdl2cpp

A DSDL-to-C++ transpiler written in Python and using [pydsdl](https://github.com/UAVCAN/pydsdl) for DSDL parsing. This is used by the libuavcan tests to generate DSDL for native unit tests and on-target testing. It can be integrated into projects that only need to generate C++ from DSDL.

## SocketCAN Platform Adapter

[SocketCAN](https://www.kernel.org/doc/Documentation/networking/can.txt) is an API that is gaining popularity and support in Linux operating systems and other posix-like RTOS-es. The libuavcan commons provides a platform adapter that is useful as a reference for users interested in using libuacan on top of SocketCAN and is also used by some of the examples provided for libuavcan.

