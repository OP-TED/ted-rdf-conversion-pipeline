from pymongo import MongoClient
from mapping_suite_sdk.core.adapters.repository import MongoDBRepository
from mapping_suite_sdk.mapping_suite.models import MappingSuite
from src.ted_sws import config


class MappingSuiteRepositoryMongoDB(MongoDBRepository[MappingSuite]):
    """Repository for storing MappingSuite objects in MongoDB."""
    
    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        database_name = database_name or config.MONGO_DB_AGGREGATES_DATABASE_NAME
        super().__init__(
            model_class=MappingSuite,
            mongo_client=mongodb_client,
            database_name=database_name,
            collection_name="mapping_suite_collection"
        )
    
    def add(self, mapping_suite: MappingSuite) -> MappingSuite:
        """Add a mapping suite if it doesn't exist."""
        try:
            self.read(mapping_suite.id)
            return mapping_suite  # Already exists
        except Exception:
            return self.create(mapping_suite)
    
    def get(self, reference: str) -> MappingSuite:
        """Get suite by ID (alias for read)."""
        return self.read(reference)
    
    def list(self):
        """List all suites (alias for read_many)."""
        return self.read_many()
    
    def delete(self, suite_id: str) -> None:
        """Delete suite by ID (alias for inherited delete)."""
        super().delete(suite_id)
