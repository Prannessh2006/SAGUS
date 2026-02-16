from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, avg, count, sum as spark_sum, 
    when, lit, udf, collect_list, struct
)
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    IntegerType, FloatType, ArrayType, BooleanType
)
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsResult:
    job_name: str
    status: str
    records_processed: int
    output_path: Optional[str]
    metrics: Dict[str, Any]
    errors: List[str]


class SparkAnalyticsEngine:
    
    def __init__(self):
        self._spark = self._create_spark_session()
        self._app_name = settings.SPARK_APP_NAME
    
    def _create_spark_session(self) -> SparkSession:
        return (
            SparkSession.builder
            .appName(settings.SPARK_APP_NAME)
            .master(settings.SPARK_MASTER)
            .config("spark.driver.memory", settings.SPARK_DRIVER_MEMORY)
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .getOrCreate()
        )
    
    def stop(self) -> None:
        self._spark.stop()
    
    def process_curriculum_data(
        self,
        concepts_data: List[Dict[str, Any]],
        relationships_data: List[Dict[str, Any]]
    ) -> AnalyticsResult:
        logger.info("Processing curriculum data with PySpark")
        
        errors = []
        records_processed = 0
        
        try:
            concepts_schema = StructType([
                StructField("id", StringType(), False),
                StructField("name", StringType(), False),
                StructField("description", StringType(), True),
                StructField("domain", StringType(), True),
                StructField("grade_level", IntegerType(), True),
                StructField("difficulty", FloatType(), True),
                StructField("keywords", ArrayType(StringType()), True),
                StructField("curriculum_code", StringType(), True),
                StructField("estimated_time_minutes", IntegerType(), True)
            ])
            
            concepts_df = self._spark.createDataFrame(
                concepts_data, schema=concepts_schema
            )
            
            validation_errors = self._validate_concepts(concepts_df)
            errors.extend(validation_errors)
            
            relationships_schema = StructType([
                StructField("source_id", StringType(), False),
                StructField("target_id", StringType(), False),
                StructField("relationship_type", StringType(), False),
                StructField("strength", FloatType(), True)
            ])
            
            relationships_df = self._spark.createDataFrame(
                relationships_data, schema=relationships_schema
            )
            
            rel_errors = self._validate_relationships(relationships_df, concepts_df)
            errors.extend(rel_errors)
            
            domain_stats = self._calculate_domain_statistics(concepts_df)
            
            records_processed = len(concepts_data) + len(relationships_data)
            
            return AnalyticsResult(
                job_name="process_curriculum_data",
                status="success" if not errors else "partial",
                records_processed=records_processed,
                output_path=None,
                metrics=domain_stats,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Curriculum processing failed: {str(e)}")
            return AnalyticsResult(
                job_name="process_curriculum_data",
                status="failed",
                records_processed=0,
                output_path=None,
                metrics={},
                errors=[str(e)]
            )
    
    def _validate_concepts(self, df: DataFrame) -> List[str]:
        errors = []
        
        missing_ids = df.filter(col("id").isNull()).count()
        if missing_ids > 0:
            errors.append(f"Found {missing_ids} concepts with missing IDs")
        
        missing_names = df.filter(col("name").isNull()).count()
        if missing_names > 0:
            errors.append(f"Found {missing_names} concepts with missing names")
        
        duplicates = df.groupBy("id").count().filter(col("count") > 1)
        duplicate_count = duplicates.count()
        if duplicate_count > 0:
            errors.append(f"Found {duplicate_count} duplicate concept IDs")
        
        invalid_difficulty = df.filter(
            (col("difficulty") < 0) | (col("difficulty") > 1)
        ).count()
        if invalid_difficulty > 0:
            errors.append(f"Found {invalid_difficulty} concepts with invalid difficulty")
        
        return errors
    
    def _validate_relationships(
        self, 
        rel_df: DataFrame, 
        concepts_df: DataFrame
    ) -> List[str]:
        errors = []
        
        valid_ids = concepts_df.select("id").distinct()
        
        orphaned_sources = rel_df.join(
            valid_ids, 
            rel_df.source_id == valid_ids.id, 
            "left_anti"
        ).count()
        if orphaned_sources > 0:
            errors.append(f"Found {orphaned_sources} relationships with invalid source")
        
        orphaned_targets = rel_df.join(
            valid_ids, 
            rel_df.target_id == valid_ids.id, 
            "left_anti"
        ).count()
        if orphaned_targets > 0:
            errors.append(f"Found {orphaned_targets} relationships with invalid target")
        
        return errors
    
    def _calculate_domain_statistics(self, df: DataFrame) -> Dict[str, Any]:
        stats = df.groupBy("domain").agg(
            count("*").alias("concept_count"),
            avg("difficulty").alias("avg_difficulty"),
            avg("estimated_time_minutes").alias("avg_time"),
            collect_list("grade_level").alias("grade_levels")
        ).collect()
        
        return {
            row["domain"]: {
                "concept_count": row["concept_count"],
                "avg_difficulty": round(row["avg_difficulty"] or 0, 2),
                "avg_time": round(row["avg_time"] or 0, 1)
            }
            for row in stats
            if row["domain"]
        }
    
    def calibrate_difficulty(
        self,
        student_performance: List[Dict[str, Any]]
    ) -> AnalyticsResult:
        logger.info("Running difficulty calibration job")
        
        try:
            perf_schema = StructType([
                StructField("student_id", StringType(), False),
                StructField("concept_id", StringType(), False),
                StructField("mastery_level", FloatType(), False),
                StructField("time_spent_minutes", IntegerType(), True),
                StructField("attempts", IntegerType(), True),
                StructField("assessment_score", FloatType(), True)
            ])
            
            perf_df = self._spark.createDataFrame(
                student_performance, schema=perf_schema
            )
            
            difficulty_metrics = perf_df.groupBy("concept_id").agg(
                avg("mastery_level").alias("avg_mastery"),
                avg("time_spent_minutes").alias("avg_time"),
                avg("attempts").alias("avg_attempts"),
                avg("assessment_score").alias("avg_score"),
                count("student_id").alias("student_count")
            )
            
            calibrated = difficulty_metrics.withColumn(
                "calibrated_difficulty",
                (
                    (1 - col("avg_mastery")) * 0.4 +
                    (col("avg_attempts") / 5) * 0.3 +
                    (1 - col("avg_score")) * 0.3
                )
            ).withColumn(
                "calibrated_difficulty",
                when(col("calibrated_difficulty") > 1, 1.0)
                .when(col("calibrated_difficulty") < 0, 0.0)
                .otherwise(col("calibrated_difficulty"))
            )
            
            results = calibrated.select(
                "concept_id", 
                "calibrated_difficulty",
                "avg_mastery",
                "student_count"
            ).collect()
            
            calibration_data = {
                row["concept_id"]: {
                    "calibrated_difficulty": round(row["calibrated_difficulty"], 3),
                    "avg_mastery": round(row["avg_mastery"], 3),
                    "sample_size": row["student_count"]
                }
                for row in results
            }
            
            return AnalyticsResult(
                job_name="calibrate_difficulty",
                status="success",
                records_processed=len(student_performance),
                output_path=None,
                metrics={
                    "concepts_calibrated": len(calibration_data),
                    "calibration_data": calibration_data
                },
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Difficulty calibration failed: {str(e)}")
            return AnalyticsResult(
                job_name="calibrate_difficulty",
                status="failed",
                records_processed=0,
                output_path=None,
                metrics={},
                errors=[str(e)]
            )
    
    def analyze_learning_patterns(
        self,
        learning_sessions: List[Dict[str, Any]]
    ) -> AnalyticsResult:
        logger.info("Running learning pattern analysis")
        
        try:
            session_schema = StructType([
                StructField("session_id", StringType(), False),
                StructField("student_id", StringType(), False),
                StructField("concept_id", StringType(), False),
                StructField("session_order", IntegerType(), False),
                StructField("mastery_before", FloatType(), True),
                StructField("mastery_after", FloatType(), True),
                StructField("duration_minutes", IntegerType(), True),
                StructField("success", BooleanType(), True)
            ])
            
            sessions_df = self._spark.createDataFrame(
                learning_sessions, schema=session_schema
            )
            
            bottlenecks = sessions_df.groupBy("concept_id").agg(
                (spark_sum(when(col("success") == True, 1).otherwise(0)) / 
                 count("*")).alias("success_rate"),
                avg("duration_minutes").alias("avg_duration"),
                avg(col("mastery_after") - col("mastery_before")).alias("avg_progress")
            ).filter(col("success_rate") < 0.5).collect()
            
            sequence_patterns = sessions_df.groupBy("student_id", "session_id").agg(
                collect_list(struct("session_order", "concept_id")).alias("sequence")
            )
            
            progression = sessions_df.groupBy("concept_id").agg(
                avg("mastery_before").alias("avg_mastery_before"),
                avg("mastery_after").alias("avg_mastery_after"),
                avg(col("mastery_after") - col("mastery_before")).alias("avg_gain")
            ).collect()
            
            bottleneck_data = [
                {
                    "concept_id": row["concept_id"],
                    "success_rate": round(row["success_rate"], 3),
                    "avg_duration": round(row["avg_duration"], 1)
                }
                for row in bottlenecks
            ]
            
            progression_data = {
                row["concept_id"]: {
                    "avg_gain": round(row["avg_gain"], 3)
                }
                for row in progression
            }
            
            return AnalyticsResult(
                job_name="analyze_learning_patterns",
                status="success",
                records_processed=len(learning_sessions),
                output_path=None,
                metrics={
                    "bottleneck_concepts": bottleneck_data,
                    "progression_analysis": progression_data,
                    "total_sessions_analyzed": sessions_df.select("session_id").distinct().count()
                },
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            return AnalyticsResult(
                job_name="analyze_learning_patterns",
                status="failed",
                records_processed=0,
                output_path=None,
                metrics={},
                errors=[str(e)]
            )
    
    def partition_knowledge_graph(
        self,
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        num_partitions: int = 4
    ) -> AnalyticsResult:
        logger.info(f"Partitioning knowledge graph into {num_partitions} partitions")
        
        try:
            edges_df = self._spark.createDataFrame(relationships)
            concepts_df = self._spark.createDataFrame(concepts)
            
            partitioned = concepts_df.withColumn(
                "partition_id",
                col("grade_level") % num_partitions
            ).select("id", "name", "domain", "grade_level", "partition_id")
            
            assignments = partitioned.collect()
            
            partition_map = {
                row["id"]: row["partition_id"]
                for row in assignments
            }
            
            partition_counts = partitioned.groupBy("partition_id").count().collect()
            partition_sizes = {
                row["partition_id"]: row["count"]
                for row in partition_counts
            }
            
            return AnalyticsResult(
                job_name="partition_knowledge_graph",
                status="success",
                records_processed=len(concepts),
                output_path=None,
                metrics={
                    "partition_map": partition_map,
                    "partition_sizes": partition_sizes,
                    "num_partitions": num_partitions
                },
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Graph partitioning failed: {str(e)}")
            return AnalyticsResult(
                job_name="partition_knowledge_graph",
                status="failed",
                records_processed=0,
                output_path=None,
                metrics={},
                errors=[str(e)]
            )


analytics_engine: Optional[SparkAnalyticsEngine] = None


def get_analytics_engine() -> SparkAnalyticsEngine:
    global analytics_engine
    if analytics_engine is None:
        analytics_engine = SparkAnalyticsEngine()
    return analytics_engine
