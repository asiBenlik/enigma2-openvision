# -*- coding: utf-8 -*-
import sys, os, time
import re
from Tools.HardwareInfo import HardwareInfo
from enigma import getBoxType
from Components.SystemInfo import SystemInfo

def getVersionString():
	return getImageVersionString()

def getImageVersionString():
	try:
		if os.path.isfile('/var/lib/opkg/status'):
			st = os.stat('/var/lib/opkg/status')
		else:
			st = os.stat('/usr/lib/ipkg/status')
		tm = time.localtime(st.st_mtime)
		if tm.tm_year >= 2011:
			return time.strftime("%Y-%m-%d %H:%M:%S", tm)
	except:
		pass
	return _("unavailable")

# WW -placeholder for BC purposes, commented out for the moment in the Screen
def getFlashDateString():
	return _("unknown")

def getBuildDateString():
	try:
		if os.path.isfile('/etc/version'):
			version = open("/etc/version","r").read()
			return "%s-%s-%s" % (version[:4], version[4:6], version[6:8])
	except:
		pass
	return _("unknown")

def getUpdateDateString():
	try:
		from glob import glob
		build = [x.split("-")[-2:-1][0][-8:] for x in open(glob("/var/lib/opkg/info/openvision-bootlogo.control")[0], "r") if x.startswith("Version:")][0]
		if build.isdigit():
			return  "%s-%s-%s" % (build[:4], build[4:6], build[6:])
	except:
		pass
	return _("unknown")

def getEnigmaVersionString():
	import enigma
	enigma_version = enigma.getEnigmaVersionString()
	if '-(no branch)' in enigma_version:
		enigma_version = enigma_version [:-12]
	return enigma_version

def getGStreamerVersionString(cpu):
	try:
		from glob import glob
		gst = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/gstreamer[0-9].[0-9].control")[0], "r") if x.startswith("Version:")][0]
		return "%s" % gst[1].split("+")[0].replace("\n","")
	except:
		return _("Not Required") if cpu.upper().startswith('HI') else _("Not Installed")

def getKernelVersionString():
	try:
		return open("/proc/version","r").read().split(' ', 4)[2].split('-',2)[0]
	except:
		return _("unknown")

def getHardwareTypeString():
	return HardwareInfo().get_device_model()

def getHardwareBrand():
	return HardwareInfo().get_device_brand()

def getImageTypeString():
	try:
		image_type = open("/etc/issue").readlines()[-2].strip()[:-6]
		return image_type.capitalize()
	except:
		return _("undefined")

def getCPUInfoString():
	try:
		cpu_count = 0
		cpu_speed = 0
		processor = ""
		for line in open("/proc/cpuinfo").readlines():
			line = [x.strip() for x in line.strip().split(":")]
			if not processor and line[0] in ("system type", "model name", "Processor"):
				processor = line[1].split()[0]
			elif not cpu_speed and line[0] == "cpu MHz":
				cpu_speed = "%1.0f" % float(line[1])
			elif line[0] == "processor":
				cpu_count += 1

		if processor.startswith("ARM") and os.path.isfile("/proc/stb/info/chipset"):
			processor = "%s (%s)" % (open("/proc/stb/info/chipset").readline().strip().upper(), processor)

		if not cpu_speed:
			try:
				cpu_speed = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000
			except:
				try:
					import binascii
					cpu_speed = int(int(binascii.hexlify(open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb').read()), 16) / 100000000) * 100
				except:
					cpu_speed = "-"

		temperature = None
		if os.path.isfile('/proc/stb/fp/temp_sensor_avs'):
			temperature = open("/proc/stb/fp/temp_sensor_avs").readline().replace('\n','')
		elif os.path.isfile('/proc/stb/power/avs'):
			temperature = open("/proc/stb/power/avs").readline().replace('\n','')
		elif os.path.isfile('/proc/stb/fp/temp_sensor'):
			temperature = open("/proc/stb/fp/temp_sensor").readline().replace('\n','')
		elif os.path.isfile('/proc/stb/sensors/temp0/value'):
			temperature = open("/proc/stb/sensors/temp0/value").readline().replace('\n','')
		elif os.path.isfile('/proc/stb/sensors/temp/value'):
			temperature = open("/proc/stb/sensors/temp/value").readline().replace('\n','')
		elif os.path.isfile("/sys/devices/virtual/thermal/thermal_zone0/temp"):
			try:
				temperature = int(open("/sys/devices/virtual/thermal/thermal_zone0/temp").read().strip())/1000
			except:
				pass
		elif os.path.isfile("/proc/hisi/msp/pm_cpu"):
			try:
				temperature = re.search('temperature = (\d+) degree', open("/proc/hisi/msp/pm_cpu").read()).group(1)
			except:
				pass
		if temperature:
			return "%s %s MHz (%s) %s°C" % (processor, cpu_speed, ngettext("%d core", "%d cores", cpu_count) % cpu_count, temperature)
		return "%s %s MHz (%s)" % (processor, cpu_speed, ngettext("%d core", "%d cores", cpu_count) % cpu_count)
	except:
		return _("undefined")

def getCPUBrand():
	if SystemInfo["AmlogicFamily"]:
		return _("Amlogic")
	elif SystemInfo["HiSilicon"] or os.path.isfile("/proc/hisi/msp/pm_cpu") or os.path.isfile("/usr/bin/hihalt"):
		return _("HiSilicon")
	else:
		return _("Broadcom")

def getCPUArch():
	if SystemInfo["ArchIsARM64"]:
		return _("ARM64")
	elif SystemInfo["ArchIsARM"]:
		return _("ARM")
	else:
		return _("Mipsel")

def getFlashType():
	if SystemInfo["SmallFlash"]:
		return _("Small - Lite image")
	else:
		return _("Normal - Vision image")

def getVisionVersion():
	try:
		return open("/etc/visionversion","r").read().strip()
	except:
		return _("It's not a genuine Open Vision!")

def getVisionRevision():
	try:
		return open("/etc/visionrevision","r").read().strip()
	except:
		return _("It's not a genuine Open Vision!")

def getVisionModule():
	if SystemInfo["OpenVisionModule"]:
		return _("Loaded")
	else:
		return _("Unknown, multiboot situation!")

def getDriverInstalledDate():
	try:
		from glob import glob
		try:
			if getBoxType() in ("dm800","dm8000"):
				driver = [x.split("-")[-2:-1][0][-9:] for x in open(glob("/var/lib/opkg/info/*-dvb-modules-*.control")[0], "r") if x.startswith("Version:")][0]
				return  "%s-%s-%s" % (driver[:4], driver[4:6], driver[6:])
			else:
				driver = [x.split("-")[-2:-1][0][-8:] for x in open(glob("/var/lib/opkg/info/*-dvb-modules-*.control")[0], "r") if x.startswith("Version:")][0]
				return  "%s-%s-%s" % (driver[:4], driver[4:6], driver[6:])
		except:
			try:
				driver = [x.split("Version:") for x in open(glob("/var/lib/opkg/info/*-dvb-proxy-*.control")[0], "r") if x.startswith("Version:")][0]
				return  "%s" % driver[1].replace("\n","")
			except:
				driver = [x.split("Version:") for x in open(glob("/var/lib/opkg/info/*-platform-util-*.control")[0], "r") if x.startswith("Version:")][0]
				return  "%s" % driver[1].replace("\n","")
	except:
		return _("unknown")

def getPythonVersionString():
	try:
		import commands
		status, output = commands.getstatusoutput("python -V")
		return output.split(' ')[1]
	except:
		return _("unknown")

def GetIPsFromNetworkInterfaces():
	import socket, fcntl, struct, array, sys
	is_64bits = sys.maxsize > 2**32
	struct_size = 40 if is_64bits else 32
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	max_possible = 8 # initial value
	while True:
		_bytes = max_possible * struct_size
		names = array.array('B')
		for i in range(0, _bytes):
			names.append(0)
		outbytes = struct.unpack('iL', fcntl.ioctl(
			s.fileno(),
			0x8912,  # SIOCGIFCONF
			struct.pack('iL', _bytes, names.buffer_info()[0])
		))[0]
		if outbytes == _bytes:
			max_possible *= 2
		else:
			break
	namestr = names.tostring()
	ifaces = []
	for i in range(0, outbytes, struct_size):
		iface_name = bytes.decode(namestr[i:i+16]).split('\0', 1)[0].encode('ascii')
		if iface_name != 'lo':
			iface_addr = socket.inet_ntoa(namestr[i+20:i+24])
			ifaces.append((iface_name, iface_addr))
	return ifaces

# For modules that do "from About import about"
about = sys.modules[__name__]
