"""Basic tests for the Python 3.6 and 3.9 base container images."""
from bci_tester.data import PYTHON36_CONTAINER
from bci_tester.data import PYTHON39_CONTAINER


CONTAINER_IMAGES = [PYTHON36_CONTAINER, PYTHON39_CONTAINER]


def test_python_version(auto_container):
    """Test that the python version equals the value from the environment variable
    ``PYTHON_VERSION``.

    """
    reported_version = auto_container.connection.run_expect(
        [0], "python3 --version"
    ).stdout.strip()
    version_from_env = auto_container.connection.run_expect(
        [0], "echo $PYTHON_VERSION"
    ).stdout.strip()

    assert reported_version == f"Python {version_from_env}"


def test_pip(auto_container):
    """Check that :command:`pip` is installed and its version equals the value from
    the environment variable ``PIP_VERSION``.

    """
    assert auto_container.connection.pip.check().rc == 0
    reported_version = auto_container.connection.run_expect(
        [0], "pip --version"
    ).stdout
    version_from_env = auto_container.connection.run_expect(
        [0], "echo $PIP_VERSION"
    ).stdout.strip()

    assert f"pip {version_from_env}" in reported_version


def test_tox(auto_container):
    """Ensure we can use :command:`pip` to install :command:`tox`."""
    auto_container.connection.run_expect([0], "pip install --user tox")


def test_python_webserver(auto_container):
    """Test that the simple python webserver answers to an internal get request"""
    comd = [
        "zypper --non-interactive install wget;",
        "touch file-to-get;"
        + "(timeout 120s python3 -m http.server &);"
        + "for x in 1 2 3 4;"
        + "do wget -T 120 -o log.txt http://localhost:8000/file-to-get;"
        + "[ $? -eq 0 ] && break || sleep 5;"
        + "done;",
        'grep -c "200 OK" log.txt;',
    ]
    reported_cmd = ""

    for c in range(0, len(comd)):
        reported_cmd = auto_container.connection.run_expect(
            [0],
            comd[c],
        ).stdout.strip()

    assert reported_cmd == "1"
