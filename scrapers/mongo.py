from datetime import datetime
from warnings import warn

import itertools
import pymongo
import time

class MongoSession:
    def __init__(self, session, db="scrapers"):
        self.client = pymongo.MongoClient(session)
        self.db = self.client[db]
        self.session_time = datetime.now()

    # Load documents functions
    def load(self, record, collection):
        upload_time = int(time.time() * 1000000)
        record['created_at'] = record['updated_at'] = upload_time

        return self.db[collection].insert_one(record)

    def load_many(self, records, collection):
        for record in records:
            self.load(record, collection)

    def update(self, using_vars, updated_fields, collection, upsert=False):
        updated_fields['updated_at'] = int(time.time() * 1e6)
        if upsert:
            if self.db[collection].count(using_vars) == 0:
                updated_fields['created_at'] = updated_fields['updated_at']

        return self.db[collection].update(using_vars, {'$set': updated_fields}, upsert)

    def update_many(self, using_list_of_vars, records, collection, upsert=False):
        for record in records:
            using_vars = {key: record[key] for key in using_list_of_vars}
            self.update(using_vars, record, collection, upsert)


    # Drop documents functions
    def drop_by_criteria(self, criteria, collection):
        rv = None
        if criteria in [None, {}]:
            warn("There should be at least one criteria for dropping documents.")
        else:
            rv = self.db[collection].delete_many(criteria)

        return rv

    # Utils
    @staticmethod
    def remove_keys(dict_to_clean, list_of_keys):
        for key in list_of_keys:
            if key in dict_to_clean:
                del dict_to_clean[key]
        return dict_to_clean
