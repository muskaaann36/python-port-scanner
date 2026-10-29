import socket
from scanner import check_port, validate_args


def test_open_port_is_detected():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))  # port 0 means "OS, pick any free port"
    server.listen(1)
    port = server.getsockname()[1]
    try:
        _, is_open, _ = check_port("127.0.0.1", port)
        assert is_open is True
    finally:
        server.close()


def test_closed_port_is_detected():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()  # now nothing is listening on that port
    _, is_open, _ = check_port("127.0.0.1", port)
    assert is_open is False


def test_valid_range_has_no_error():
    assert validate_args(1, 1024) is None


def test_start_greater_than_end_is_rejected():
    assert validate_args(100, 50) is not None


def test_port_out_of_range_is_rejected():
    assert validate_args(0, 100) is not None
    assert validate_args(1, 70000) is not None
