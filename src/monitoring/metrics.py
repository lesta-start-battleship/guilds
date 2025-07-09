from prometheus_client import (
    Counter,
    Histogram,
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
    REGISTRY,
)


def init_metrics():
    class Metrics:
        def __init__(self):
            self.METRICS = {}

            self.METRICS['http_requests_count'] = Counter(
                'http_requests_count', 'Count of total HTTP requests.', ['method', 'code']
            )
            self.METRICS['http_requests_latency'] = Histogram(
                'http_requests_latency', 'Latency of total HTTP requests.', ['method', 'code']
            )

            self.METRICS['websocket_connections_total'] = Counter(
                'websocket_connections_total', 'Total number of websocket connections', ['path']
            )
            self.METRICS['websocket_messages_total'] = Counter(
                'websocket_messages_total', 'Total number of messages received via websocket', ['path']
            )

            # Отключение лишних коллекторов
            REGISTRY.unregister(GC_COLLECTOR)
            REGISTRY.unregister(PROCESS_COLLECTOR)
            REGISTRY.unregister(PLATFORM_COLLECTOR)

        def __getattribute__(self, name):
            if name == 'METRICS':
                return super().__getattribute__(name)
            metrics = super().__getattribute__('METRICS')
            if name in metrics:
                return metrics[name]
            return super().__getattribute__(name)

    return Metrics()


metrics = init_metrics()
