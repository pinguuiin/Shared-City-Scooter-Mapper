"""
Producer Runner Script
Runs the GBFS producer that fetches bike data and publishes to Kafka
"""
from app.consumers.gbfs_producer import GBFSProducer


def main():
    """Main entry point for the producer"""
    print("=" * 60)
    print("  Real-Time Shared Mobility Heatmap - GBFS Producer")
    print("=" * 60)
    
    # Create and run producer
    producer = GBFSProducer()
    producer.run()


if __name__ == "__main__":
    main()
