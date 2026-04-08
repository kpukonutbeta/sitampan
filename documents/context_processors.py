import socket
import netifaces

def local_ip(request):
    """
    Context processor to provide the local IP address of the server,
    prioritizing 192.168.x.x intranet addresses.
    """
    ip_list = []
    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()
        for iface in interfaces:
            addrs = netifaces.ifaddresses(iface)
            # AF_INET is for IPv4
            if netifaces.AF_INET in addrs:
                for link in addrs[netifaces.AF_INET]:
                    ip = link.get('addr')
                    if ip and not ip.startswith('127.'):
                        ip_list.append(ip)
    except Exception:
        pass

    # Prioritize 192.168.x.x
    preferred_ip = next((ip for ip in ip_list if ip.startswith('192.168.')), None)
    
    # Fallback to the first non-loopback IP found, or localhost
    final_ip = preferred_ip or (ip_list[0] if ip_list else '127.0.0.1')
        
    return {
        'SERVER_IP': final_ip
    }
