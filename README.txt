MINTmix - mixer application for MINT-MASSE
==========================================

modules:
	SM
		4-channel monitoring
		single gain
		WLAN/eth


	zeroconf(domain=local)
		gibt liste von vorhandenen SMi zurück (IPv4)
			->schnittstelle (lan/wlan)
			->port
			


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
