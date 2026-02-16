from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Optional, List, Dict, Any
import logging
from contextlib import asynccontextmanager
from fastapi import Request
from app.core.config import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    
    def __init__(self):
        self._driver: Optional[AsyncDriver] = None
        self._uri = settings.NEO4J_URI
        self._user = settings.NEO4J_USER
        self._password = settings.NEO4J_PASSWORD
        self._database = settings.NEO4J_DATABASE
    
    async def connect(self) -> None:
        try:
            self._driver = AsyncGraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE
            )
            await self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self._uri}")
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            raise
        except AuthError as e:
            logger.error(f"Neo4j authentication failed: {e}")
            raise
    
    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed")
    
    @asynccontextmanager
    async def session(self) -> AsyncSession:
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized. Call connect() first.")
        
        async with self._driver.session(database=self._database) as session:
            yield session
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        async with self.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records
    
    async def execute_write(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        async with self.session() as session:
            result = await session.run(query, parameters or {})
            summary = await result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "nodes_deleted": summary.counters.nodes_deleted,
                "relationships_created": summary.counters.relationships_created,
                "relationships_deleted": summary.counters.relationships_deleted,
                "properties_set": summary.counters.properties_set
            }
    
    async def create_constraint(self, label: str, property_name: str) -> None:
        query = f"""
        CREATE CONSTRAINT {label}_{property_name}_unique IF NOT EXISTS
        FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE
        """
        await self.execute_query(query)
        logger.info(f"Created constraint on {label}.{property_name}")
    
    async def create_index(self, label: str, property_name: str) -> None:
        query = f"""
        CREATE INDEX {label}_{property_name}_index IF NOT EXISTS
        FOR (n:{label}) ON (n.{property_name})
        """
        await self.execute_query(query)
        logger.info(f"Created index on {label}.{property_name}")
    
    async def clear_database(self) -> None:
        query = "MATCH (n) DETACH DELETE n"
        await self.execute_query(query)
        logger.warning("Database cleared - all nodes and relationships deleted")


neo4j_client = Neo4jClient()


def get_neo4j_client(request: Request) -> Neo4jClient:
    return request.app.state.neo4j_client
