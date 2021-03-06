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

Dependencies
----
dependencies refer to the Debian package names (unless indicated otherwise).
deps prefixed with "+" are *absolute* (you really need them).
deps prefixed with "=" are *optional* (you probably want them).


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
+ puredata
+ pd-iemnet
+ pd-osc
+ pd-iemrtp

Dependencies (WILMAsm)
---------------------
+ python
+ python-avahi
+ python-pyalsa
= python-smbus 
= python-psutil
+ avahi-daemon
+ puredata
 * for proper timestamping of audio data, a specially patched version of Pd is
   used, available in the 'WILMA' branch at http://github.com/umlaeute/pd-vanilla
+ pd-iemnet
+ pd-osc
+ pd-iemrtp
