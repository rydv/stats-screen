@app.route('/api/report-run/<report_id>', methods=['GET'])
def get_report_run(report_id):
    try:
        result = es.search(index='report_runs_index', body={
            "query": {
                "term": {"report_id": report_id}
            },
            "sort": [
                {"processStartTime": {"order": "desc"}}
            ],
            "size": 1
        })

        if result['hits']['total']['value'] == 0:
            return jsonify({"status": "error", "message": "Report run not found"}), 404

        report_run = result['hits']['hits'][0]['_source']

        # Remove ITEM_IDS from the response
        if 'runSummary' in report_run:
            if 'matches_info' in report_run['runSummary']:
                for rule in report_run['runSummary']['matches_info']:
                    if 'ITEM_IDS' in report_run['runSummary']['matches_info'][rule]:
                        del report_run['runSummary']['matches_info'][rule]['ITEM_IDS']
            if 'unmatched_info' in report_run['runSummary']:
                for rule in report_run['runSummary']['unmatched_info']:
                    if 'ITEM_IDS' in report_run['runSummary']['unmatched_info'][rule]:
                        del report_run['runSummary']['unmatched_info'][rule]['ITEM_IDS']

        return jsonify({
            "status": "success",
            "data": report_run
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    


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

    result = es.index(index='report_runs_index', body=run_data)
    return result['_id']