import re
import pandas as pd
from typing import Dict, List
from datetime import datetime
from controllers.matching_matrix_controller.config.config import *
from controllers.matching_matrix_controller.config.elasticsearch_client import es_connect
from controllers.matching_matrix_controller.modules.field import Field
from controllers.matching_matrix_controller.modules.rule_params import RuleParams
from controllers.matching_matrix_controller.modules.base_rule import BaseRule

class Rule(BaseRule):
    def __init__(self, rule_params: RuleParams, l_s: str, d_c: str, fields: List[Field]):
        super().__init__(rule_params, l_s, d_c, fields)
        # self.date_frmt = self._get_date_frmt()

    def _get_date_frmt(self):
        for field in self.filter1_params['fields']:
            if field.valdt_flag:
                return field.valdt_params["date_format"]

    def _exp_flag_check(self):
        filter1_flag = any([field.exp_flag for field in self.filter1_params['fields']])
        return filter1_flag

    def _filter_query_formatter(self, filter_params, filter_id):
        try:
            print('---')
            print(f'Formatting query for filter-{filter_id}')
            rule_params = self.rule_params
            query = {
                "query": {
                    "bool": {
                        "filter": [
                            # {
                            #     "range": {
                            #         "LAST_ACTION_DATE": {
                            #             "format": "strict_date_optional_time",
                            #             "gte": str(from_date) + "T00:00:00Z",
                            #             "lte": str(to_date) + "T23:59:59Z"
                            #         }
                            #     }
                            # }
                        ]
                    }
                }
            }
            conditions = {
                "bool": {
                    "must": [
                        {"term": {
                            # "AGENT_CODE": rule_params.agent_code,
                            "COUNTRY": rule_params.category_code
                        }}
                    ],
                    "should": [],
                    "minimum_should_match": 1
                }
            }

            set_ids = rule_params.set_id
            if set_ids != 'ALL':
                condition = {"terms": {"LOCAL_ACC_NO": set_ids}}
                conditions["bool"]["must"].append(condition)

            if filter_params['d_c'] != 'A':
                tran_type = [f"{filter_params['l_s']} {filter_params['d_c']}R"]
            else:
                tran_type = [f"{filter_params['l_s']} CR", f"{filter_params['l_s']} DR"]

            print(f'Trans Type: {tran_type}')
            condition = {"terms": {"C_OR_D": tran_type}}
            conditions["bool"]["must"].append(condition)

            print(f'Filter-{filter_id} values:')
            for field in filter_params['fields']:
                if field.value:
                    # print(f'{field.name} - {field.search_agg_exp}')
                    condition = {"regexp": {field.name: f'.*{field.search_agg_exp}.*'}}
                    conditions["bool"]["should"].append(condition)

            query["query"]["bool"]["filter"].append(conditions)

            q = {
                'track_total_hits': True,
                **query,
                "_source": selected_fields
            }

            # print(f'Filter-{filter_id} query: {q}')
            return q
        except Exception as e:
            raise ValueError(f"Failed to format query for the rule: {e}")
        
    def _get_filter_matches(self, query):
        try:
            scroll_id = None
            es = es_connect()
            res = es.search(index=matched_data_index, body=query, scroll='2m', size=1000)
            scroll_id = res['_scroll_id']
            hits = res['hits']['hits']
            all_hits = hits

            while len(hits) > 0:
                response = es.scroll(scroll_id=scroll_id, scroll='2m')
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
                all_hits.extend(hits)

            df = pd.DataFrame([hit['_source'] for hit in all_hits])
            return df

        except Exception as e:
            raise ValueError(f'Failed to get matches for the filter: {e}')
        finally:
            if scroll_id:
                es.clear_scroll(scroll_id=scroll_id)

    def validate_ref_values(self):
        pass

    def _extract_matched_value(self, row, filter_field_values):
        matched_values = []
        for field in filter_field_values:
            if field.exp_flag:
                # print(field.name, field.search_agg_exp)
                match = re.findall(field.search_agg_exp, row[field.name])
                # print(f'match: {match}')
                if len(match):
                    if isinstance(match[0], tuple):
                        matched_values.extend(list(match[0]))
                    else:
                        matched_values.append(match[0])
                # print(matched_values)
                # print('------')
        
        matched_values.sort()
        # print(" | ".join(matched_values))
        return " | ".join(matched_values)
    
    def _get_other_leg(self, row):
        frmtted_fetch_val_date = self._format_date(row['fetched_val_date'])
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"RELATIONSHIP_ID": row['RELATIONSHIP_ID']}},
                        {"term": {"VALUE_DATE": frmtted_fetch_val_date}}
                    ],
                    "must_not": [
                        {"term": {"ITEM_ID": row['ITEM_ID']}}
                    ]
                }
            },
            "_source": selected_fields
        }
        es = es_connect()
        res = es.search(index=matched_data_index, body=query)
        hits = res["hits"]["hits"]
        if len(hits) > 0:
            return hits[0]["_source"]
        return None
    
    def _format_date(self, date_string):
        try:
            date_format = self._get_date_frmt()
            date_obj = datetime.strptime(date_string, date_format)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return date_string
    
    def find_matches(self):
        queries = {
            "filter1": None,
            # "filter2": None,
        }
        queries['filter1'] = self._filter_query_formatter(self.filter1_params, 1)
        # queries['filter2'] = self._filter_query_formatter(self.filter2_params, 2)

        filter1_matches = self._get_filter_matches(queries['filter1'])
        # filter2_matches = self._get_filter_matches(queries['filter2'])

        print(f'# filter-1 matches: {len(filter1_matches)}')
        # print(f'# filter-2 matches: {len(filter2_matches)}')
        if not len(filter1_matches):
            print('Matches not found for the provided value date case')
            return pd.DataFrame(columns=selected_fields)
        else:
            value_date_flag = self.rule_params.value_date
            exp_flag = self._exp_flag_check()

            filter1_matches['fetched_val_date'] = filter1_matches.apply(
                lambda row: self._extract_matched_value(row, self.filter1_params['fields']), axis=1)

            other_legs = []
            for _, row in filter1_matches.iterrows():
                try:
                    other_leg = self._get_other_leg(row)
                    if other_leg:
                        df_otl = pd.DataFrame([other_leg])
                        other_legs.append(df_otl)
                except:
                    pass

            del filter1_matches['fetched_val_date']
            filter2_matches = pd.concat(other_legs).drop_duplicates().reset_index(drop=True)

            matches_df = pd.concat([filter1_matches, filter2_matches]).drop_duplicates().reset_index(drop=True)

            matches_df['AMOUNT'] = matches_df['AMOUNT'].apply(lambda x: float(str(x).replace(',', '')) if isinstance(x, str) else x)
            matches_df['CONVERTED_AMT'] = matches_df.apply(lambda x: float(x['AMOUNT']) if 'DR' in x['C_OR_D'] else -float(x['AMOUNT']), axis=1)

            result = matches_df.groupby(['RELATIONSHIP_ID'])['CONVERTED_AMT'].sum().reset_index()
            dist_rel_ids = result[result['CONVERTED_AMT'] == 0]['RELATIONSHIP_ID'].tolist()

            # matched_rels = [rel_id for rel_id in dist_rel_ids if rel_id not in matched_rels_all]
            matches_df = matches_df[matches_df['RELATIONSHIP_ID'].isin(dist_rel_ids)].sort_values(by=['RELATIONSHIP_ID']).reset_index(drop=True)

            # if len(matches_df):
            #     matches_df['VALUE_DATE'] = pd.to_datetime(matches_df['VALUE_DATE'])
            #     if value_date_flag.upper() == "YES":
            #         matches_df = matches_df.groupby('RELATIONSHIP_ID').filter(lambda x: x['VALUE_DATE'].nunique() == 1).reset_index(drop=True)
            #     elif value_date_flag.upper() == "NO":
            #         matches_df = matches_df.groupby('RELATIONSHIP_ID').filter(lambda x: x['VALUE_DATE'].nunique() > 1).reset_index(drop=True)

            matches_df['Rule_Id'] = self.rule_params.unique_rule_id
            matches_df.drop(['CONVERTED_AMT'], axis=1, inplace=True)

            # matched_rels_all += matched_rels
            # rule_matches.append(matches_df)

            print(f'Matches for {self.rule_params.unique_rule_id}: {len(matches_df)}')
            return matches_df