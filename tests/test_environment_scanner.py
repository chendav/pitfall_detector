"""Tests for environment scanner functionality."""

import pytest
from unittest.mock import patch, MagicMock
from pitfall_detector.environment_scanner import EnvironmentScanner


class TestEnvironmentScanner:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = EnvironmentScanner()
    
    def test_init(self):
        """Test scanner initialization."""
        assert self.scanner is not None
        assert hasattr(self.scanner, 'known_tools')
        assert hasattr(self.scanner, 'detected_tools')
    
    @patch('pitfall_detector.environment_scanner.pkg_resources')
    def test_scan_python_packages(self, mock_pkg_resources):
        """Test Python package scanning."""
        # Mock installed packages
        mock_pkg = MagicMock()
        mock_pkg.project_name = 'streamlit'
        mock_pkg.version = '1.25.0'
        mock_pkg.location = '/usr/local/lib/python3.9/site-packages'
        
        mock_pkg_resources.working_set = [mock_pkg]
        
        result = self.scanner._scan_python_packages()
        
        assert 'streamlit' in result
        assert result['streamlit']['version'] == '1.25.0'
        assert result['streamlit']['detection_method'] == 'pip_installed'
    
    @patch('pitfall_detector.environment_scanner.socket.socket')
    def test_is_port_in_use(self, mock_socket):
        """Test port checking."""
        # Mock socket connection
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0  # Port is in use
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        result = self.scanner._is_port_in_use(8501)
        assert result is True
        
        # Test port not in use
        mock_sock.connect_ex.return_value = 1  # Port is not in use
        result = self.scanner._is_port_in_use(8501)
        assert result is False
    
    @patch('pitfall_detector.environment_scanner.subprocess.run')
    def test_scan_docker_containers(self, mock_run):
        """Test Docker container scanning."""
        # Mock successful docker ps output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "streamlit_app\tstreamlit:latest\t8501->8501/tcp"
        mock_run.return_value = mock_result
        
        result = self.scanner._scan_docker_containers()
        
        assert any('streamlit' in key for key in result.keys())
    
    @patch('pitfall_detector.environment_scanner.subprocess.run')
    def test_scan_docker_containers_not_available(self, mock_run):
        """Test Docker scanning when Docker is not available."""
        # Mock Docker not found
        mock_run.side_effect = FileNotFoundError()
        
        result = self.scanner._scan_docker_containers()
        
        # Should return empty dict without errors
        assert isinstance(result, dict)
    
    @patch('pitfall_detector.environment_scanner.os.getenv')
    def test_scan_environment_variables(self, mock_getenv):
        """Test environment variable scanning."""
        # Mock environment variables
        def mock_env_get(var):
            env_vars = {
                'OPENAI_API_KEY': 'sk-abcdef123456...',
                'STREAMLIT_SERVER_PORT': '8501'
            }
            return env_vars.get(var)
        
        mock_getenv.side_effect = mock_env_get
        
        result = self.scanner._scan_environment_variables()
        
        assert 'OPENAI_API_KEY' in result
        assert 'STREAMLIT_SERVER_PORT' in result
        # API key should be masked
        assert result['OPENAI_API_KEY'].startswith('sk-abcde') and '...' in result['OPENAI_API_KEY']
    
    def test_map_service_to_tool(self):
        """Test service name to tool name mapping."""
        assert self.scanner._map_service_to_tool('streamlit') == 'streamlit'
        assert self.scanner._map_service_to_tool('gradio') == 'gradio'
        assert self.scanner._map_service_to_tool('unknown_service') == 'unknown_service'
    
    @patch("builtins.open", new_callable=MagicMock)
    def test_parse_requirements(self, mock_open):
        """Test requirements.txt parsing."""
        # Mock file content
        mock_open.return_value.__enter__.return_value.__iter__.return_value = [
            "streamlit>=1.0.0\n",
            "requests>=2.0.0\n", 
            "# comment\n"
        ]
        
        from pathlib import Path
        file_path = Path("requirements.txt")
        
        result = self.scanner._parse_requirements(file_path)
        
        # Should detect streamlit
        assert any('streamlit' in key for key in result.keys())
    
    @patch('pitfall_detector.environment_scanner.Path.exists')
    def test_scan_project_files_no_directory(self, mock_exists):
        """Test project file scanning when directory doesn't exist."""
        mock_exists.return_value = False
        
        result = self.scanner._scan_project_files('/nonexistent/path')
        
        assert result == {}
    
    def test_aggregate_detected_tools(self):
        """Test tool aggregation from scan results."""
        scan_results = {
            'python_packages': {
                'streamlit': {
                    'detection_method': 'pip_installed',
                    'version': '1.25.0',
                    'location': '/usr/local/lib'
                }
            },
            'running_services': {
                'streamlit_port_8501': {
                    'service': 'streamlit',
                    'port': 8501,
                    'detection_method': 'running_service'
                }
            },
            'project_files': {},
            'docker_containers': {},
            'conda_environments': {}
        }
        
        result = self.scanner._aggregate_detected_tools(scan_results)
        
        assert len(result) == 1
        assert result[0]['name'] == 'streamlit'
        assert 'pip_installed' in result[0]['detection_methods']
        assert 'running_service' in result[0]['detection_methods']
        assert '1.25.0' in result[0]['versions']
    
    @patch.multiple(
        'pitfall_detector.environment_scanner.EnvironmentScanner',
        _scan_python_packages=MagicMock(return_value={'streamlit': {'version': '1.0', 'detection_method': 'pip_installed'}}),
        _scan_running_services=MagicMock(return_value={}),
        _scan_project_files=MagicMock(return_value={}),
        _scan_docker_containers=MagicMock(return_value={}),
        _scan_conda_environments=MagicMock(return_value={}),
        _scan_environment_variables=MagicMock(return_value={})
    )
    def test_scan_all(self):
        """Test comprehensive environment scanning."""
        result = self.scanner.scan_all(project_path='/test/path')
        
        # Check all expected keys are present
        expected_keys = [
            'python_packages', 'running_services', 'project_files',
            'docker_containers', 'conda_environments', 'environment_variables',
            'detected_ai_tools'
        ]
        
        for key in expected_keys:
            assert key in result
        
        # Check aggregated tools
        assert isinstance(result['detected_ai_tools'], list)