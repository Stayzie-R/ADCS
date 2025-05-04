SUMMARY = "WiFi auto-connect script with init.d integration"
DESCRIPTION = "Script that automatically connects to WiFi using predefined config"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"
PR = "r2"

SRC_URI = "git://github.com/Stayzie-R/ADCS.git;protocol=https;branch=main"
SRCREV = "${AUTOREV}"
S = "${WORKDIR}/git/L4S_yocto_files/wifi-connection"

inherit update-rc.d

INITSCRIPT_NAME = "wifi-auto"
INITSCRIPT_PARAMS = "defaults"

do_install() {
    etc=${D}${sysconfdir}
    bin=${D}${bindir}

    install -d ${bin}
    install -m 0755 ${WORKDIR}/wifi-auto.sh ${bin}/wifi-auto

    install -d ${etc}/init.d
    install -m 0755 ${WORKDIR}/wifi-auto.init ${etc}/init.d/wifi-auto

    install -d ${etc}
    install -m 0600 ${WORKDIR}/wifi-config ${etc}/wifi-config
}

FILES:${PN} += "${sysconfdir}/init.d/wifi-auto ${sysconfdir}/wifi-config"

