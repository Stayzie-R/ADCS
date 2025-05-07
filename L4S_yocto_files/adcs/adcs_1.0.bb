SUMMARY = "ADCS Application"
DESCRIPTION = "Satellite Attitude Determination and Control System with sensors"
LICENSE = "CLOSED"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/Proprietary;md5=0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"

SRC_URI = "git://github.com/RosovaAnastazie/ADCS.git;protocol=https;branch=main"
SRCREV = "${AUTOREV}"

S = "${WORKDIR}/git"

do_install:append() {
    install -d ${D}${bindir}/adcs
    install -m 0755 ${S}/adcs.py ${D}${bindir}/adcs/adcs.py
    install -m 0644 ${S}/sun_sensor.py ${D}${bindir}/adcs/sun_sensor.py
    install -m 0644 ${S}/photoresistor.py ${D}${bindir}/adcs/photoresistor.py
    install -m 0644 ${S}/config.py ${D}${bindir}/adcs/config.py
}

