import socket
import argparse
import time
from concurrent.futures import ThreadPoolExecutor


def check_port(host, port, timeout=1.0, retries=2):
    for attempt in range(retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            result = s.connect_ex((host, port))
            if result == 0:
                return port, True, grab_banner(s)
            if result == 111:  # connection refused: definitely closed, no retry needed
                return port, False, ""
        finally:
            s.close()
    return port, False, ""


def grab_banner(s):
    try:
        s.settimeout(3)
        data = s.recv(1024)
        return data.decode(errors="ignore").strip()
    except (socket.timeout, OSError):
        return ""


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
    parser.add_argument("-t", "--threads", type=int, default=100, help="number of threads")
    args = parser.parse_args()

    print(f"Scanning {args.host} from port {args.start} to {args.end} "
          f"with {args.threads} threads...")

    start_time = time.time()
    ports = range(args.start, args.end + 1)

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        results = pool.map(lambda p: check_port(args.host, p), ports)

    open_count = 0
    for port, is_open, banner in results:
        if is_open:
            open_count += 1
            line = f"Port {port} is OPEN ({get_service(port)})"
            if banner:
                line += f"  banner: {banner}"
            print(line)

    elapsed = time.time() - start_time
    print(f"Done. {open_count} open port(s) found in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    main()
