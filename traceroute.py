from socket import *
import os
import sys
import struct
import time
import select
import binascii
import requests
import json

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

sequence_number = 0

def checksum(string):
# In this function we make the checksum of our packet
# hint: see icmpPing lab
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(string[count+1]) * 256 + ord(string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
# In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
# packet to be sent was made, secondly the checksum was appended to the header and
# then finally the complete packet was sent to the destination.

# Make the header in a similar way to the ping exercise.
# Append checksum to the header.

# Don’t send the packet yet , just return the final packet in this function.
    global sequence_number
    sequence_number += 1
    ID = os.getpid() & 0xFFFF

    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence_number)
    data = struct.pack("d", time.time())
    myChecksum = checksum(str(header + data, 'latin-1'))

    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence_number)

# So the function ending should look like this
    packet = header + data
    return packet

IP_CACHE = {}

def get_geolocation(ip):
    # Skip private IPs
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        return ""
    if ip in IP_CACHE:
        return IP_CACHE[ip]
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                city = data.get("city", "")
                region = data.get("regionName", "")
                country = data.get("country", "")
                org = data.get("org", "")
                
                loc_parts = [p for p in (city, region, country) if p]
                loc_str = ", ".join(loc_parts)
                
                geo_info = f"[{loc_str}]"
                if org:
                    geo_info += f" (ISP: {org})"
                
                IP_CACHE[ip] = geo_info
                time.sleep(0.5) # simple delay to respect 45 req/min free tier
                return f" {geo_info}"
    except Exception:
        pass
    
    IP_CACHE[ip] = ""
    return ""

def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #Fill in end
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)

                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect

                if timeLeft <= 0:
                    print(" * * * Request timed out.")

            except timeout:
                continue

            else:
                #Fill in start
                #Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                types, code = struct.unpack("bb", icmpHeader[:2])
                #Fill in end
                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    geo = get_geolocation(addr[0])
                    print(" %d rtt=%.0f ms %s%s" %(ttl, (timeReceived -t)*1000, addr[0], geo))

                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    geo = get_geolocation(addr[0])
                    print(" %d rtt=%.0f ms %s%s" %(ttl, (timeReceived-t)*1000, addr[0], geo))
                    return

                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    geo = get_geolocation(addr[0])
                    print(" %d rtt=%.0f ms %s%s" %(ttl, (timeReceived - timeSent)*1000, addr[0], geo))
                    return

                else:
                    print("error")

                break

            finally:
                mySocket.close()

if __name__ == '__main__':
    while True:
        print("\n=== ICMP Traceroute Utility ===")
        print("[1] google.com")
        print("[2] dlsu.instructure.com")
        print("[3] www.dlsu.edu.ph")
        print("[4] All")
        print("[5] Exit")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\nTraceroute to google.com:")
            get_route("google.com")
        elif choice == '2':
            print("\nTraceroute to dlsu.instructure.com:")
            get_route("dlsu.instructure.com")
        elif choice == '3':
            print("\nTraceroute to www.dlsu.edu.ph:")
            get_route("www.dlsu.edu.ph")
        elif choice == '4':
            print("\nTraceroute to google.com:")
            get_route("google.com")
            print("\nTraceroute to dlsu.instructure.com:")
            get_route("dlsu.instructure.com")
            print("\nTraceroute to www.dlsu.edu.ph:")
            get_route("www.dlsu.edu.ph")
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")