"""
Consumer Runner Script
Runs the aggregation worker that consumes GBFS data and creates H3 aggregations
"""
from consumers.gbfs_consumer import BatchGBFSConsumer
from consumers.aggregation_worker import aggregation_worker


def main():
    """Main entry point for the consumer"""
    print("=" * 60)
    print("  Real-Time Shared Mobility Heatmap - Consumer Worker")
    print("=" * 60)
    
    # Create batch consumer with aggregation worker
    # Batch size set to 1000 for Aachen (~598 scooters)
    consumer = BatchGBFSConsumer(
        batch_handler=aggregation_worker.get_batch_handler(),
        batch_size=1000,
        batch_timeout_ms=5000
    )
    
    # Start consuming
    consumer.run()


if __name__ == "__main__":
    main()
