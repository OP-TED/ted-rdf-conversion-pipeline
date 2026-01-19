import pytest
from unittest.mock import Mock, patch

from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from mapping_suite_sdk.mapping_suite.models import MappingSuite


@pytest.fixture
def mock_mapping_suite():
    """Mock MappingSuite object."""
    suite = Mock(spec=MappingSuite)
    suite.id = "test_suite_123"
    return suite


@pytest.fixture
def repository():
    """Initialize repository with mocked base class."""
    with patch('src.ted_sws.data_manager.adapters.mapping_suite_repository.MongoDBRepository.__init__', return_value=None):
        repo = MappingSuiteRepositoryMongoDB(mongodb_client=Mock())
        # Initialize the client attribute that __del__ expects
        repo.client = Mock()
    return repo


class TestMappingSuiteRepositoryMongoDB:
    """Unit tests for custom MappingSuiteRepositoryMongoDB methods."""
    
    def test_add_new_suite(self, repository, mock_mapping_suite):
        """Test adding a new mapping suite."""
        with patch.object(repository, 'read', side_effect=Exception("Not found")):
            with patch.object(repository, 'create', return_value=mock_mapping_suite) as mock_create:
                result = repository.add(mock_mapping_suite)
                mock_create.assert_called_once_with(mock_mapping_suite)
                assert result == mock_mapping_suite
    
    def test_add_existing_suite(self, repository, mock_mapping_suite):
        """Test adding existing suite doesn't create duplicate."""
        with patch.object(repository, 'read', return_value=mock_mapping_suite):
            with patch.object(repository, 'create') as mock_create:
                result = repository.add(mock_mapping_suite)
                mock_create.assert_not_called()
                assert result == mock_mapping_suite
    
    def test_get_suite_by_id(self, repository, mock_mapping_suite):
        """Test get() is an alias for read()."""
        with patch.object(repository, 'read', return_value=mock_mapping_suite) as mock_read:
            result = repository.get("test_suite_123")
            mock_read.assert_called_once_with("test_suite_123")
            assert result == mock_mapping_suite
    
    def test_list_all_suites(self, repository, mock_mapping_suite):
        """Test list() is an alias for read_many()."""
        suites = [mock_mapping_suite]
        with patch.object(repository, 'read_many', return_value=suites) as mock_read_many:
            result = repository.list()
            mock_read_many.assert_called_once()
            assert result == suites
    
    def test_delete_suite_calls_super(self, repository):
        """Test delete() calls super().delete with the suite_id."""
        with patch.object(repository.__class__.__bases__[0], 'delete') as mock_super_delete:
            repository.delete("test_suite_123")
            mock_super_delete.assert_called_once_with("test_suite_123")
