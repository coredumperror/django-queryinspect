import time
from django.db import connection
from qinspect.middleware import QueryInspectMiddleware, cfg


class QueryInspectContextManager():
    """
    Code called within this context manager is profiled by django-queryinspect.
    The results will be presented when the context manager exits.
    """

    def __enter__(self):
        if cfg['enabled']:
            self.request_start = time.time()
            self.conn_queries_len = len(connection.queries)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if cfg['enabled']:
            request_time = time.time() - self.request_start

            infos = QueryInspectMiddleware.get_query_infos(
                connection.queries[self.conn_queries_len:])

            num_duplicates = QueryInspectMiddleware.check_duplicates(infos)
            QueryInspectMiddleware.check_stddev_limit(infos)
            QueryInspectMiddleware.check_absolute_limit(infos)
            # Can call ootput_states() with response={} because the only thing
            # it does to response is add keys.
            QueryInspectMiddleware.output_stats(
                infos, num_duplicates, request_time, {})
