SUMMARY = "WiFi auto-connect script with init.d integration"
DESCRIPTION = "Script that automatically connects to WiFi using predefined config"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"
PR = "r2"

SRC_URI = "file://wifi-auto.sh \
           file://wifi-auto.init \
           file://wifi-config"

S = "${WORKDIR}"

inherit update-rc.d

INITSCRIPT_NAME = "wifi-auto"
INITSCRIPT_PARAMS = "defaults"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/wifi-auto.sh ${D}${bindir}/wifi-auto

    install -d ${D}${sysconfdir}/init.d
    install -m 0755 ${WORKDIR}/wifi-auto.init ${D}${sysconfdir}/init.d/wifi-auto

    install -d ${D}${sysconfdir}
    install -m 0600 ${WORKDIR}/wifi-config ${D}${sysconfdir}/wifi-config
}

FILES:${PN} += "${sysconfdir}/init.d/wifi-auto ${sysconfdir}/wifi-config"