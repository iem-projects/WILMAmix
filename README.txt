MINTmix - mixer application for MINT-MASSE
==========================================

modules:
	SMi
		4-channel monitoring
		single gain
		WLAN/eth


Plan:
	auf SMi's rennen python-controller der über OSC ferngesteuert wird und
	die ganze appstart/connection logik übernehmen

streaming:
	jacktrip:
		+ gute latenzzeiten
		- schlecht zu integrieren (keine lib)
	rtsp (gstreamer)
		+ einfacher zu integrieren, aber:
		- derweil hohe latenzen (500ms roundtrip)
		- (de)payloader müssen noch implentiert werden
