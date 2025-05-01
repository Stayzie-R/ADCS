# Integrating ADCS Application into Linux4Space Distribution

This guide outlines the steps to integrate the ADCS application into the [Linux4Space](https://linux4space.org) distribution and deploy it on the BeagleBone Black Wireless (BBB) board.

The Linux4Space distribution used for this integration can be found [here](https://gitlab.com/linux4space/BBW-ADCS) for reference.

## ADCS Application Integration

The ADCS application was integrated into the Linux4Space distribution using a custom recipe. You can find the recipe for ADCS [here](/L4S_yocto_files/adcs/adcs_1.0.bb).
Once the distribution is built, the ADCS application will be included in the image, and it can be run directly on the target device.

## Wi-Fi Auto-Connect Script Integration
In addition, a Wi-Fi auto-connect script was added to automatically connect the device to Wi-Fi using predefined credentials. The necessary files for Wi-Fi configuration are located in the  [directory](/L4S_yocto_files/wifi-connection):

- `wifi-auto.sh`: The main script for connecting to Wi-Fi based on the wifi-config file.
- `wifi-auto.init`: A standard init script to start/stop the Wi-Fi auto-connect process.
- `wifi-config`: The configuration file containing the Wi-Fi SSID and PSK.
- `wifi-auto_1.0.bb`: The Yocto recipe for integrating the Wi-Fi files to L4S.

## Docker-Based Yocto Build Environment
A Docker container based on Ubuntu 20.04 was used to build the Linux4Space distribution to ensure consistency and avoid host-related issues. The setup is defined in the [Dockerfile](/L4S_yocto_files/Dockerfile), which installs all required dependencies and prepares the environment for Yocto builds.



## Running the Image on BeagleBone Black Wireless

**1. Download the [Image]()** 

**2. Flash to SD Card**

Format the microSD card as FAT32 with an MBR partition table, then use a tool like balenaEtcher to flash the downloaded `l4s-adcs-image-beaglebone.rootfs.wic.xz` file directly onto a microSD card. This card will be used to boot the BBB.

**3. Boot from SD**

Insert the SD card into the BBB. While plugging in the power, hold the BOOT button for ~5 seconds to boot from the card instead of internal memory. The new system should start automatically.

**4. Flash to Internal eMMC (Optional)**

To permanently install the system to internal storage:

<div style="margin-left: 30px;">

  <h3>4.1 Decompress the image</h3>
  <p>Run the following command to decompress the <code>.wic.xz</code> file:</p>
  <pre><code>xz -d -k l4s-adcs-image-beaglebone.rootfs.wic.xz
  </code></pre>

  <h3>4.2 Copy the <code>.wic</code> file</h3>
  <p>Copy the decompressed <code>.wic</code> file to a second SD card (or USB drive) connected via a <strong>USB hub</strong>.</p>

  <h3>4.3 Check the connected devices</h3>
  <p>Run <code>blkid</code> to list the connected devices:</p>
  <pre><code>blkid
  </code></pre>

  <h3>4.4 Mount the device on BBB</h3>
  <p>Mount the device that contains the <code>.wic</code> image. Note that <code>/dev/sda1</code> might vary based on the output of <code>blkid</code>:</p>
  <pre><code>mkdir /mnt/sd
mount /dev/sda1 /mnt/sd
  </code></pre>

  <h3>4.5 Write the image to eMMC</h3>
  <p>Use <code>dd</code> to write the image to eMMC:</p>
  <pre><code>dd if=/mnt/sd/l4s-adcs-image-beaglebone.rootfs.wic of=/dev/mmcblk1 bs=64K
  </code></pre>

  <h3>4.6 Update the bootloader configuration</h3>
  <ul>
    <li>Create a mount point and mount the boot partition:
      <pre><code>mkdir /mnt/boot
mount /dev/mmcblk1p1 /mnt/boot
      </code></pre>
    </li>
    <li>Edit the <code>extlinux.conf</code> file:
      <pre><code>nano /mnt/boot/extlinux/extlinux.conf
      </code></pre>
    </li>
    <li>Set the <code>APPEND</code> line to:
      <pre><code>APPEND root=/dev/mmcblk1p2 rootwait rw ...
      </code></pre>
    </li>
  </ul>

  <h3>4.7 Shutdown the device</h3>
  <p>Shutdown the device and <strong>remove all microSD cards</strong>.</p>

</div>





