MINTmix - mixer application for MINT-MASSE
==========================================


MINTmix is a multichannel mixer application written in python.
it is intended for the use within the MINT-MASSE project, that aims at building
a distributed wireless acoustic sensor array.

MINT-architecture
-----------------
a number of small satellites (SMi's) are equipped with up to four microphones.
these satellites are controlled from a central computer (GOD).
the tasks of the satellites are to get the four microphone signals and either
stream them to the central computer (using some lossless protocol) or store the
data on disk, for later retrieval.
optionally, the satellites might do some pre-processing of the signal.

MINTmix controls the satellites, so they know what to do.



MINTmix architecture
--------------------
MINTmix has two components:
- MINTmix: a GUI running on the GOD machine. it allows the user to configure and
           monitor the SMi's.
- MINTsm : the daemon running on the SMi's that does what the MINTmix requests.


Communication
-------------
MINTmix discovers the SMi's by use of ZeroConf.
All control communication is done via [OSC](http://opensoundcontrol.org).
Audio data is sent back to GOD using RTSP/RTP, using a user-selected codec
(currently: L16).

Dependencies (MINTmix)
----------------------
+ python
+ python-pyside.qtcore
+ python-pyside.qtgui
+ python-avahi
+ python-netifaces
+ python-numpy
+ avahi-daemon

Dependencies (MINTsm)
---------------------
+ python
+ python-avahi
+ python-pyalsa
+ python-gst0.10
+ python-gst0.10-rtsp
+ avahi-daemon
- gstreamer0.10-alsa
