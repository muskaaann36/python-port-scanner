import socket
import argparse


def check_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((host, port))
    s.close()
    return result == 0


def get_service(port):
    try:
        return socket.getservbyport(port)
    except OSError:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Simple TCP port scanner")
    parser.add_argument("host", help="IP address or hostname to scan")
    parser.add_argument("-s", "--start", type=int, default=1, help="first port")
    parser.add_argument("-e", "--end", type=int, default=1024, help="last port")
    args = parser.parse_args()

    print(f"Scanning {args.host} from port {args.start} to {args.end}...")

    open_count = 0
    for port in range(args.start, args.end + 1):
        if check_port(args.host, port):
            print(f"Port {port} is OPEN ({get_service(port)})")
            open_count += 1

    print(f"Done. {open_count} open port(s) found.")


if __name__ == "__main__":
    main()
