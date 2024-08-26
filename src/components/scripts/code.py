from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import uuid

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

INDEX_NAME = 'report_runs_index'

# Define the mapping
mapping = {
    "mappings": {
        "properties": {
            "report_id": {"type": "keyword"},
            "runId": {"type": "keyword"},
            "lastProcessingDate": {"type": "date"},
            "processStartTime": {"type": "date"},
            "processEndTime": {"type": "date"},
            "totalTimeTaken": {"type": "text"},
            "status": {"type": "keyword"},
            "runSummary": {
                "type": "object",
                "properties": {
                    "matches": {"type": "text"},
                    "matches_info": {
                        "type": "object",
                        "dynamic": True,
                        "properties": {
                            "count": {"type": "integer"},
                            "ITEM_IDS": {"type": "text", "index": False}
                        }
                    },
                    "unmatched_info": {
                        "type": "object",
                        "dynamic": True,
                        "properties": {
                            "count": {"type": "integer"},
                            "ITEM_IDS": {"type": "text", "index": False}
                        }
                    }
                }
            }
        }
    }
}

# Create the index with the mapping
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Created index: {INDEX_NAME}")

# Function to insert run data
def insert_run_data(report_id):
    run_data = {
        "report_id": report_id,
        "runId": str(uuid.uuid4()),
        "lastProcessingDate": datetime.now().isoformat(),
        "processStartTime": datetime.now().isoformat(),
        "processEndTime": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "totalTimeTaken": "30 minutes",
        "status": "Completed",
        "runSummary": {
            "matches": "3/5",
            "matches_info": {
                "RUL01": {
                    "count": 102,
                    "ITEM_IDS": "|".join([str(i) for i in range(1, 103)])
                },
                "RUL03": {
                    "count": 45,
                    "ITEM_IDS": "|".join([str(i) for i in range(200, 245)])
                },
                "RUL04": {
                    "count": 32,
                    "ITEM_IDS": "|".join([str(i) for i in range(300, 332)])
                }
            },
            "unmatched_info": {
                "RUL02": {
                    "count": 20,
                    "ITEM_IDS": "|".join([str(i) for i in range(400, 420)])
                },
                "RUL05": {
                    "count": 15,
                    "ITEM_IDS": "|".join([str(i) for i in range(500, 515)])
                }
            }
        }
    }

    result = es.index(index=INDEX_NAME, body=run_data)
    return result['_id']

# Insert dummy data
dummy_report_id = "REPORT_001"
inserted_id = insert_run_data(dummy_report_id)
print(f"Inserted run data with ID: {inserted_id}")