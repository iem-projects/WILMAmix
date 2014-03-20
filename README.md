WILMix - mixer application for WILMA
====================================


WILMix is a multichannel mixer application written in python.
it is intended for the use within the WILMA (WIreless
Large-scale Microphone Array) project, that aims at building
a distributed wireless acoustic sensor array.

WILMA-architecture
-----------------
a number of small satellites (SMi's) are equipped with up to four microphones.
these satellites are controlled from a central computer (CU).
the tasks of the satellites are to get the four microphone signals and either
stream them to the central computer (using some lossless protocol) or store the
data on disk, for later retrieval.
optionally, the satellites might do some pre-processing of the signal.

WILMix controls the satellites, so they know what to do.



WILMix architecture
--------------------
WILMix has two components:
- WILMix: a GUI running on the CU machine. it allows the user to configure and
           monitor the SMi's.
- WILMAsm : the daemon running on the SMi's that does what the WILMix requests.


Communication
-------------
WILMix discovers the SMi's by use of ZeroConf.
All control communication is done via [OSC](http://opensoundcontrol.org).
Audio data is sent back to the CU using RTSP/RTP, using a user-selected codec
(currently: L16).

Dependencies (WILMix)
----------------------
+ python
+ python-pyside.qtcore
+ python-pyside.qtgui
+ python-pyside.qtnetwork
+ python-avahi
+ python-netifaces
+ python-numpy
+ avahi-daemon

Dependencies (WILMAsm)
---------------------
+ python
+ python-avahi
+ python-pyalsa
= python-smbus 
= python-psutil
//+ python-gst0.10
//+ python-gst0.10-rtsp
+ avahi-daemon
- gstreamer0.10-alsa
+ puredata


Installation
------------
a patched version of 'puredata' (as found on
http://github.com/umlaeute/pd-vanilla#beaglebone) must be available as 'pd'.
