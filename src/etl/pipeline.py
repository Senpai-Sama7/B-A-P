"""
ETL Pipeline for data extraction, transformation, and loading.
"""

import asyncio
import pandas as pd
from typing import Any, Dict
from datetime import datetime
from src.models.analytics_models import PipelineRequest
from src.core.cache import get_redis
from src.utils.logger import get_logger
from src.utils.performance import AsyncPerformanceMonitor

logger = get_logger()


class ETLPipeline:
    """ETL Pipeline orchestrator."""

    def __init__(self) -> None:
        self.logger = get_logger()

    async def extract_data(self, request: PipelineRequest, user: str) -> Dict[str, Any]:
        """
        Extract data from various sources (database, files, APIs).

        Args:
            request: Pipeline request with dataset_id and parameters
            user: User who initiated the pipeline

        Returns:
            Dictionary containing extracted raw data
        """
        async with AsyncPerformanceMonitor(f"extract_data_{request.dataset_id}"):
            try:
                # Simulate data extraction
                await asyncio.sleep(0.1)

                # TODO: Implement real data extraction from:
                # - Database queries
                # - File storage (S3, local filesystem)
                # - External APIs
                # - Streaming sources

                params = request.parameters or {}

                raw_data = {
                    "dataset_id": request.dataset_id,
                    "source": params.get("source", "unknown"),
                    "records": [
                        {"id": i, "value": i * 10, "category": f"cat_{i % 3}"} for i in range(100)
                    ],
                    "metadata": {
                        "extracted_at": datetime.utcnow().isoformat(),
                        "extracted_by": user,
                        "record_count": 100,
                    },
                }

                self.logger.info(
                    f"Extracted data for {request.dataset_id}",
                    user=user,
                    record_count=len(raw_data["records"]),
                )

                return raw_data

            except Exception as e:
                self.logger.error(
                    f"Data extraction failed for {request.dataset_id}: {e}", exc_info=True
                )
                raise

    async def transform_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw data with cleaning, enrichment, and aggregations.

        Args:
            raw_data: Raw extracted data

        Returns:
            Dictionary containing transformed data
        """
        dataset_id = raw_data.get("dataset_id", "unknown")

        async with AsyncPerformanceMonitor(f"transform_data_{dataset_id}"):
            try:
                await asyncio.sleep(0.1)

                # Convert to pandas DataFrame for transformation
                df = pd.DataFrame(raw_data["records"])

                # Data cleaning
                df = df.dropna()  # Remove null values
                df = df.drop_duplicates()  # Remove duplicates

                # Data enrichment
                df["value_squared"] = df["value"] ** 2
                df["timestamp"] = datetime.utcnow()

                # Aggregations
                summary_stats: Dict[str, Any] = {
                    "total_records": len(df),
                    "mean_value": float(df["value"].mean()),
                    "std_value": float(df["value"].std()),
                    "min_value": float(df["value"].min()),
                    "max_value": float(df["value"].max()),
                }
                if "category" in df.columns:
                    summary_stats["category_counts"] = df["category"].value_counts().to_dict()

                # Convert back to dict
                transformed_records = df.to_dict(orient="records")

                transformed_data = {
                    "dataset_id": dataset_id,
                    "records": transformed_records,
                    "summary": summary_stats,
                    "metadata": {
                        **raw_data.get("metadata", {}),
                        "transformed_at": datetime.utcnow().isoformat(),
                        "transformation_version": "1.0",
                    },
                }

                self.logger.info(
                    f"Transformed data for {dataset_id}",
                    record_count=len(transformed_records),
                    summary=summary_stats,
                )

                return transformed_data

            except Exception as e:
                self.logger.error(
                    f"Data transformation failed for {dataset_id}: {e}", exc_info=True
                )
                raise

    async def load_data(
        self, transformed_data: Dict[str, Any], request: PipelineRequest, user: str
    ) -> None:
        """
        Load transformed data to target destinations.

        Args:
            transformed_data: Transformed data to load
            request: Original pipeline request
            user: User who initiated the pipeline
        """
        dataset_id = request.dataset_id

        async with AsyncPerformanceMonitor(f"load_data_{dataset_id}"):
            try:
                await asyncio.sleep(0.1)

                # Load to cache for quick access
                cache = await get_redis()
                await cache.set(f"etl:result:{dataset_id}", transformed_data["summary"], ttl=3600)
                await cache.set(f"etl:status:{dataset_id}", "completed", ttl=3600)

                # TODO: Load to permanent storage:
                # - Database tables
                # - Data warehouse (Snowflake, BigQuery, Redshift)
                # - Object storage (S3, GCS, Azure Blob)
                # - Search index (Elasticsearch)
                # - Analytics platform

                self.logger.info(
                    f"Loaded data for {dataset_id}",
                    user=user,
                    record_count=transformed_data.get("summary", {}).get("total_records", 0),
                )

            except Exception as e:
                self.logger.error(f"Data loading failed for {dataset_id}: {e}", exc_info=True)
                raise

    async def run(self, request: PipelineRequest, user: str) -> None:
        """
        Orchestrate the complete ETL pipeline.

        Args:
            request: Pipeline request with dataset_id and parameters
            user: User who initiated the pipeline
        """
        try:
            self.logger.info(f"Starting ETL pipeline for {request.dataset_id}", user=user)

            # Execute ETL stages
            raw_data = await self.extract_data(request, user)
            transformed_data = await self.transform_data(raw_data)
            await self.load_data(transformed_data, request, user)

            self.logger.info(f"ETL pipeline completed for {request.dataset_id}", user=user)

        except Exception as e:
            self.logger.error(
                f"ETL pipeline failed for {request.dataset_id}: {e}", user=user, exc_info=True
            )

            # Update cache with failure status
            try:
                cache = await get_redis()
                await cache.set(f"etl:status:{request.dataset_id}", "failed", ttl=3600)
                await cache.set(f"etl:error:{request.dataset_id}", str(e), ttl=3600)
            except Exception as cache_error:
                self.logger.error(f"Failed to update cache with error status: {cache_error}")

            raise


# Global pipeline instance
pipeline = ETLPipeline()


async def run_etl_pipeline(request: PipelineRequest, user: str) -> None:
    """Run the ETL pipeline (wrapper for backward compatibility)."""
    await pipeline.run(request, user)
