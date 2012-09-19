#!/usr/bin/env python
import os, sys, time,re
import subprocess
import random
from netaddr import *

#AT this directory you should have the pcaps that you want to merge, transform and etc
PCAP_SOURCE="./base_traces"

BITTWIST="/usr/bin/bittwist"
BITTWISTE="/usr/bin/bittwiste"
EDITCAP="/usr/bin/editcap"
TCPDUMP="/usr/sbin/tcpdump"

#FIXME
#slower than my grandma trying to open her internet explorer
def get_random_ip():
    ip_list = list(IPNetwork('192.0.0.0/22'))
    random.shuffle(ip_list)
    return [ str(x) for x in ip_list ][0]

def set_new_ip(filename,oip,nip):
    filename_out = os.path.join(PCAP_SOURCE,"%d_%s" % (time.time(),filename.split('/')[-1]))
    subprocess.call([BITTWISTE,"-I",filename,"-O",filename_out,"-T","ip","-s","%s,%s" % (oip,nip),"-d","%s,%s" % (oip,nip)])

def progressbar(pos):
    slash = ['-','\\','|','/','-']
    return [pos + 1,slash[pos]]

def get_pcaps(madir = PCAP_SOURCE):
    #FIXME
    #we are just supporting files with pcap extension.
    return [ os.path.join(madir,x) for x in os.listdir(madir) if re.search('.*\.pcap$',x)]

def check_bin_exist(bin_name):
    if not os.path.isfile(bin_name):
        return False
    else:
        return True

def run_tcpdump(iface = "lo",filename="foo.pcap"):
    return subprocess.Popen([TCPDUMP,"-i","lo","-w",filename])

def run_bittwist(iface = "lo"):
    pcap_files = get_pcaps()
    cmd_args = [BITTWIST,"-i","lo","-l","2"] + get_pcaps()
    return subprocess.Popen(cmd_args)


#... AND GOT SAID: "INT MAIN"
if __name__ == '__main__':
    
   #bittwist options should be available to the user
   #loop (how often it should loop thru the pcaps)
   #bit rate (how fast should we generate the traffic)
   #base timestamp (which timestamp our first packet will have
   #TBD
   if not os.geteuid()==0:
           sys.exit("\nOnly root can run this script\n")

   for exe in [BITTWIST,BITTWISTE,EDITCAP,TCPDUMP]:
       if not check_bin_exist(exe):
           print "please install the following requirements and check the path"
           print "Please install bittwise from http://bittwist.sourceforge.net/index.html"
           print "apt-get install editcap"
           print "apt-get install tcpdump"
           sys.exit(1)


   #you can remove it, if you are sure that you don't have localhost addr in your pcap
   print "randomizing localhost ip..."
   for pcap in os.listdir(PCAP_SOURCE):
       nip = get_random_ip()
       set_new_ip(os.path.join(PCAP_SOURCE,pcap),"127.0.0.1",nip)

   print "lets start to generate files"
   tcpdump = run_tcpdump()
   bittwist = run_bittwist()

   #bittwist.wait()
   pos = 0
   while bittwist.poll() == None:
    if pos == 4: pos = 0
    pos, slash = progressbar(pos)
    sys.stdout.write('%c\r' % (slash))
    sys.stdout.flush()
    time.sleep(1)
   print "Wow..finally"
   tcpdump.terminate()
