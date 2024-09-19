from abc import ABC, abstractmethod
from controllers.matching_matrix_controller.config.elasticsearch_client import es_connect

class BaseStrategy(ABC):
    def __init__(self, rule_params, op_filters, strategy_id):
        self.rule_params = rule_params
        self.op_filters = op_filters
        self.strategy_id = strategy_id

    def scroll_transactions(self, query, scroll_id=None):
        try:
            es = es_connect()
            if scroll_id:
                response = es.scroll(scroll_id=scroll_id, scroll='1m')
            else:
                response = es.search(index=matched_data_index, body=query, scroll='1m', size=10000)

            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            transactions = [hit['_source'] for hit in hits]
            return scroll_id, transactions
        except Exception as e:
            raise ValueError(f'Failed to get matches for the filter: {e}')

    @abstractmethod
    def validate_strategy(self):
        pass

    @abstractmethod
    def build_query(self):
        pass

    @abstractmethod
    def process_matches(self, matches):
        pass

    @abstractmethod
    def find_matches(self):
        pass
