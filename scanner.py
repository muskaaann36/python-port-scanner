import socket
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor


def grab_banner(s):
    try:
        s.settimeout(3)
        data = s.recv(1024)
        return data.decode(errors="ignore").strip()
    except (socket.timeout, OSError):
        return ""


def check_port(host, port, timeout=1.0, retries=2):
    for _ in range(retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            result = s.connect_ex((host, port))
            if result == 0:
                return port, True, grab_banner(s)
            if result == 111:  # refused: definitely closed, no retry needed
                return port, False, ""
        finally:
            s.close()
    return port, False, ""


def get_service(port):
    try:
        return socket.getservbyport(port)
    except OSError:
        return "unknown"


def validate_args(start, end):
    """Return an error message if the ports are invalid, otherwise None."""
    if not (1 <= start <= 65535 and 1 <= end <= 65535):
        return "Ports must be between 1 and 65535."
    if start > end:
        return "Start port must not be greater than end port."
    return None


def main():
    parser = argparse.ArgumentParser(description="Simple TCP port scanner")
    parser.add_argument("host", help="IP address or hostname to scan")
    parser.add_argument("-s", "--start", type=int, default=1, help="first port")
    parser.add_argument("-e", "--end", type=int, default=1024, help="last port")
    parser.add_argument("-t", "--threads", type=int, default=100, help="number of threads")
    parser.add_argument("-o", "--output", help="save results to this file")
    args = parser.parse_args()

    error = validate_args(args.start, args.end)
    if error:
        print(f"Error: {error}")
        sys.exit(1)

    try:
        ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"Error: could not resolve '{args.host}'. Check the spelling and your internet.")
        sys.exit(1)

    print(f"Scanning {args.host} ({ip}) from port {args.start} to {args.end} "
          f"with {args.threads} threads...")

    start_time = time.time()
    ports = range(args.start, args.end + 1)

    pool = ThreadPoolExecutor(max_workers=args.threads)
    try:
        results = list(pool.map(lambda p: check_port(ip, p), ports))
    except KeyboardInterrupt:
        print("\nScan cancelled.")
        pool.shutdown(wait=False, cancel_futures=True)
        sys.exit(130)
    pool.shutdown()

    lines = []
    for port, is_open, banner in results:
        if is_open:
            line = f"Port {port} is OPEN ({get_service(port)})"
            if banner:
                line += f"  banner: {banner}"
            lines.append(line)

    for line in lines:
        print(line)

    elapsed = time.time() - start_time
    summary = f"Done. {len(lines)} open port(s) found in {elapsed:.2f} seconds."
    print(summary)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"Scan of {args.host} ({ip}), ports {args.start}-{args.end}\n")
            f.write("\n".join(lines) + "\n")
            f.write(summary + "\n")
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
