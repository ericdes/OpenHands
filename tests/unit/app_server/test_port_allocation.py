import os
import platform
from unittest.mock import MagicMock, patch

import pytest

from openhands.app_server.sandbox.docker_sandbox_service import (
    SAFE_PORT_RANGE,
    DockerSandboxService,
)


@pytest.fixture
def mock_service():
    """Create a service instance with mocked dependencies."""
    return DockerSandboxService(
        sandbox_spec_service=MagicMock(),
        container_name_prefix='oh-test-',
        host_port=3000,
        container_url_pattern='http://localhost:{port}',
        mounts=[],
        exposed_ports=[],
        health_check_path=None,
        httpx_client=MagicMock(),
        max_num_sandboxes=5,
        docker_client=MagicMock(),
    )


def test_find_unused_port_windows_wsl(mock_service):
    """Test that _find_unused_port uses safe range on WSL2."""
    with (
        patch('openhands.app_server.sandbox.docker_sandbox_service.IS_WINDOWS_OR_WSL', True),
        patch('socket.socket') as mock_socket,
        patch('random.randint', return_value=35000) as mock_randint
    ):
        # Mock successful bind
        mock_socket.return_value.__enter__.return_value.bind.return_value = None

        port = mock_service._find_unused_port()

        assert port == 35000
        mock_randint.assert_called_with(SAFE_PORT_RANGE[0], SAFE_PORT_RANGE[1])


def test_find_unused_port_default(mock_service):
    """Test that _find_unused_port uses default OS behavior on other systems."""
    with (
        patch('openhands.app_server.sandbox.docker_sandbox_service.IS_WINDOWS_OR_WSL', False),
        patch('socket.socket') as mock_socket
    ):
        # Mock getsockname to return a port
        mock_sock_instance = mock_socket.return_value.__enter__.return_value
        mock_sock_instance.getsockname.return_value = ('', 12345)

        port = mock_service._find_unused_port()

        assert port == 12345
        mock_sock_instance.bind.assert_called_with(('', 0))


def test_find_unused_port_retry(mock_service):
    """Test that _find_unused_port retries if port is in use."""
    with (
        patch('openhands.app_server.sandbox.docker_sandbox_service.IS_WINDOWS_OR_WSL', True),
        patch('socket.socket') as mock_socket,
        patch('random.randint', side_effect=[30001, 30002])
    ):
        # First bind fails, second succeeds
        mock_socket.return_value.__enter__.return_value.bind.side_effect = [OSError(), None]

        port = mock_service._find_unused_port()

        assert port == 30002
