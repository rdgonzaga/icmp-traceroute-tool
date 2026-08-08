# ICMP Traceroute Tool
> Authors: CHIU, Lance, DESCALZO, Alberto, GONZAGA, Rainer | NSCOM02 S04 
 
Python based tool that implements the traceroute utility using ICMP Echo Request and Reply messages via Raw Sockets. It maps the path that data packets take to a destination server across an IP network, record RTT and IP addresses of intermediate routers/hops. The tool also integrates with the `ip-api.com` service to automatically display geolocation data (City, Region, Country) and ISP information for each hop.

## Requirements & Usage
* Python 3.6+

1. Open a terminal (Command Prompt, PowerShell, or bash) with Administrator/root privileges.
2. Run the script:
   ```bash
   python traceroute.py
   ```

## Troubleshooting (Windows)

By default the Windows Defender Firewall strictly blocks incoming ICMP Type 11 messages. If your traceroute requests are all timing out, either temporarily disable or add an excetion to allow all inbound ICMPv4 traffic.

One can do this either through Control Panel or the ff. netsh command:
```cmd
netsh advfirewall firewall add rule name="Allow ICMPv4-In" protocol=icmpv4:any,any dir=in action=allow
```


## Declaration of Tools and AI Use

1. **Google Gemini 3.1**
2. **GPT Sol 5.6**

All LLMs used for analyzing the project specifications, identifying remaining tasks, completing the host execution logic, explaining ICMP protocol mechanics regarding firewalls and dropped packets, and troubleshooting cross-platform (Windows/Linux) raw socket behaviors.

### AI Prompts Used

1. *"Can you explain the structure of an ICMP Time Exceeded packet and how to parse it from the IP header?"*
2. *"How do I calculate the ICMP header checksum correctly in Python 3 using the struct module?"*
3. *"Why do raw sockets require Administrator/root privileges?"*
4. *"Running py traceroute.py.. all my requests just time out, why is that? Could it be a firewall issue?"*
5. *"How do I extract the exact round-trip time (RTT) from the struct.unpack payload?"*
6. *"Ran this on my VPS [output showing timeouts and successful final hop] is this normal? Why do some routers drop the ICMP packets?"*

## References

1. Postel, J. (1981). *Internet Control Message Protocol* (RFC 792). IETF. https://datatracker.ietf.org/doc/html/rfc792
2. Python Software Foundation. (n.d.). *socket — Low-level networking interface*. Python 3 Documentation. https://docs.python.org/3/library/socket.html
3. Python Software Foundation. (n.d.). *struct — Interpret bytes as packed binary data*. Python 3 Documentation. https://docs.python.org/3/library/struct.html
4. IP-API.com. (n.d.). *JSON API Documentation*. IP-API. https://ip-api.com/docs/api:json
5. Microsoft. (n.d.). *Windows Defender Firewall with Advanced Security*. Microsoft Learn. https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/