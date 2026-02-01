"""
DuckDB service for data persistence and querying
Handles multi-resolution H3 aggregations with sliding windows
"""
import duckdb
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Iterator
import threading
from config import settings


class DuckDBService:
    """Singleton service for DuckDB operations"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, read_only: bool = False):
        if self._initialized:
            return
        
        self.db_path = settings.DUCKDB_PATH
        self.read_only = read_only
        self.conn = None
        self._write_lock = threading.Lock()
        self._initialized = True
        if not self.read_only:
            self.initialize_db()
    
    @contextmanager
    def _connection(self) -> Iterator[duckdb.DuckDBPyConnection]:
        conn = duckdb.connect(self.db_path, read_only=self.read_only)
        try:
            yield conn
        finally:
            conn.close()

    def _run_with_retry(self, func, retries: int = 150, delay: float = 0.02):
        """Retry with short fixed delay for faster response"""
        for attempt in range(retries):
            try:
                return func()
            except duckdb.IOException as e:
                if "Could not set lock" in str(e) and attempt < retries - 1:
                    time.sleep(delay)  # Fast fixed delay (150 * 0.02 = 3s max)
                    continue
                raise
            except Exception as e:
                # Log other exceptions but don't retry
                print(f"⚠️  Database error (attempt {attempt + 1}/{retries}): {e}")
                raise
    
    def initialize_db(self):
        """Initialize database schema with multi-resolution tables"""
        def _init():
            with self._connection() as conn:
                # Raw vehicle locations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS raw_locations (
                        bike_id VARCHAR,
                        lat DOUBLE,
                        lon DOUBLE,
                        timestamp TIMESTAMP,
                        is_reserved BOOLEAN,
                        is_disabled BOOLEAN,
                        vehicle_type_id VARCHAR
                    )
                """)
                
                # Create aggregation tables for each H3 resolution
                for resolution in settings.H3_RESOLUTIONS:
                    conn.execute(f"""
                        CREATE TABLE IF NOT EXISTS agg_res{resolution} (
                            h3_index VARCHAR PRIMARY KEY,
                            resolution INTEGER,
                            count INTEGER,
                            last_updated TIMESTAMP,
                            window_start TIMESTAMP,
                            window_end TIMESTAMP
                        )
                    """)
                
                # Create index for faster queries
                for resolution in settings.H3_RESOLUTIONS:
                    try:
                        conn.execute(f"""
                            CREATE INDEX IF NOT EXISTS idx_agg_res{resolution}_updated 
                            ON agg_res{resolution}(last_updated)
                        """)
                    except:
                        pass  # Index might already exist
                
                conn.commit()
                print(f"✅ DuckDB initialized at {self.db_path}")

        self._run_with_retry(_init)
    
    def insert_raw_locations(self, locations: List[Dict]):
        """Insert raw bike locations"""
        if not locations:
            return
        
        with self._write_lock:
            def _write():
                with self._connection() as conn:
                    # Prepare data for batch insert
                    values = [
                        (
                            loc.get("bike_id"),
                            loc.get("lat"),
                            loc.get("lon"),
                            loc.get("timestamp", datetime.utcnow()),
                            loc.get("is_reserved", False),
                            loc.get("is_disabled", False),
                            loc.get("vehicle_type_id")
                        )
                        for loc in locations
                    ]
                    
                    conn.executemany("""
                        INSERT INTO raw_locations 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, values)
                    conn.commit()

            self._run_with_retry(_write)
    
    def clear_aggregation(self, resolution: int):
        """Clear all aggregation data for a specific resolution"""
        with self._write_lock:
            def _write():
                with self._connection() as conn:
                    table_name = f"agg_res{resolution}"
                    conn.execute(f"DELETE FROM {table_name}")
                    conn.commit()
            
            self._run_with_retry(_write)
    
    def insert_aggregation(self, resolution: int, aggregations: List[Dict]):
        """Insert new aggregation data for a specific resolution (assumes table is already cleared)"""
        if not aggregations:
            return
        
        with self._write_lock:
            def _write():
                with self._connection() as conn:
                    table_name = f"agg_res{resolution}"
                    
                    values = [
                        (
                            agg["h3_index"],
                            agg["resolution"],
                            agg["count"],
                            agg.get("last_updated", datetime.utcnow()),
                            agg.get("window_start"),
                            agg.get("window_end")
                        )
                        for agg in aggregations
                    ]
                    
                    conn.executemany(f"""
                        INSERT INTO {table_name} 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, values)
                    conn.commit()

            self._run_with_retry(_write)
    
    def upsert_aggregation(self, resolution: int, aggregations: List[Dict]):
        """Upsert H3 aggregations for a specific resolution (legacy method)"""
        if not aggregations:
            return
        
        with self._write_lock:
            def _write():
                with self._connection() as conn:
                    table_name = f"agg_res{resolution}"
                    
                    # Delete old aggregations first
                    for agg in aggregations:
                        conn.execute(f"""
                            DELETE FROM {table_name} WHERE h3_index = ?
                        """, [agg["h3_index"]])
                    
                    # Insert new aggregations
                    values = [
                        (
                            agg["h3_index"],
                            agg["resolution"],
                            agg["count"],
                            agg.get("last_updated", datetime.utcnow()),
                            agg.get("window_start"),
                            agg.get("window_end")
                        )
                        for agg in aggregations
                    ]
                    
                    conn.executemany(f"""
                        INSERT INTO {table_name} 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, values)
                    conn.commit()

            self._run_with_retry(_write)
    
    def get_heatmap_data(self, resolution: int, min_count: int = 1) -> List[Dict]:
        """Retrieve aggregated heatmap data for a specific resolution"""
        def _read():
            with self._connection() as conn:
                table_name = f"agg_res{resolution}"
                
                return conn.execute(f"""
                    SELECT h3_index, count, last_updated
                    FROM {table_name}
                    WHERE count >= ?
                    ORDER BY count DESC
                """, [min_count]).fetchall()

        result = self._run_with_retry(_read)
        
        return [
            {
                "h3_index": row[0],
                "count": row[1],
                "last_updated": row[2]
            }
            for row in result
        ]
    
    def cleanup_old_data(self):
        """Remove data older than retention period"""
        with self._write_lock:
            def _write():
                with self._connection() as conn:
                    cutoff_time = datetime.utcnow() - timedelta(minutes=settings.RETENTION_MINUTES)
                    
                    # Clean raw locations
                    conn.execute("""
                        DELETE FROM raw_locations 
                        WHERE timestamp < ?
                    """, [cutoff_time])
                    
                    # Clean aggregations
                    for resolution in settings.H3_RESOLUTIONS:
                        conn.execute(f"""
                            DELETE FROM agg_res{resolution} 
                            WHERE last_updated < ?
                        """, [cutoff_time])
                    
                    conn.commit()

            self._run_with_retry(_write)
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        def _read():
            with self._connection() as conn:
                stats = {
                    "raw_count": conn.execute("SELECT COUNT(*) FROM raw_locations").fetchone()[0],
                }
                
                for resolution in settings.H3_RESOLUTIONS:
                    count = conn.execute(f"SELECT COUNT(*) FROM agg_res{resolution}").fetchone()[0]
                    stats[f"res{resolution}_count"] = count

                return stats

        stats = self._run_with_retry(_read)
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


_db_services: Dict[str, DuckDBService] = {}


def get_db_service(read_only: bool = False) -> DuckDBService:
    key = "ro" if read_only else "rw"
    if key not in _db_services:
        _db_services[key] = DuckDBService(read_only=read_only)
    return _db_services[key]
