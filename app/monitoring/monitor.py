import time
from collections import defaultdict


class TrafficMonitor:

    def __init__(self):

        self.total_requests = 0
        self.total_bytes = 0

        self.cache_hits = 0
        self.cache_misses = 0

        self.response_times = []

        self.unique_urls = set()
        self.ip_requests = defaultdict(int)

        self.start_time = time.time()

    # =========================================
    # RECORD REQUEST
    # =========================================

    def record_request(
        self,
        client_ip,
        url,
        method,
        response_status,
        response_size,
        response_time,
        cache_status
    ):

        self.total_requests += 1

        self.total_bytes += response_size

        self.unique_urls.add(url)

        self.ip_requests[client_ip] += 1

        self.response_times.append(response_time)

        if cache_status == "HIT":
            self.cache_hits += 1

        elif cache_status == "MISS":
            self.cache_misses += 1

    # =========================================
    # REQUESTS PER SECOND
    # =========================================

    def requests_per_second(self):

        elapsed = time.time() - self.start_time

        if elapsed <= 0:
            return 0

        return self.total_requests / elapsed

    # =========================================
    # BYTES PER SECOND
    # =========================================

    def bytes_per_second(self):

        elapsed = time.time() - self.start_time

        if elapsed <= 0:
            return 0

        return self.total_bytes / elapsed

    # =========================================
    # CACHE HIT RATE
    # =========================================

    def cache_hit_rate(self):

        total_cache_requests = (
            self.cache_hits +
            self.cache_misses
        )

        if total_cache_requests == 0:
            return 0

        return (
            self.cache_hits /
            total_cache_requests
        ) * 100

    # =========================================
    # CACHE MISS RATE
    # =========================================

    def cache_miss_rate(self):

        total_cache_requests = (
            self.cache_hits +
            self.cache_misses
        )

        if total_cache_requests == 0:
            return 0

        return (
            self.cache_misses /
            total_cache_requests
        ) * 100

    # =========================================
    # AVERAGE RESPONSE TIME
    # =========================================

    def average_response_time(self):

        if not self.response_times:
            return 0

        return (
            sum(self.response_times)
            / len(self.response_times)
        )

    # =========================================
    # MOST ACTIVE IP
    # =========================================

    def most_active_ip(self):

        if not self.ip_requests:
            return None

        return max(
            self.ip_requests,
            key=self.ip_requests.get
        )

    # =========================================
    # FEATURE VECTOR
    # =========================================

    def get_features(self):

        return {

            "requests_per_second":
                round(
                    self.requests_per_second(),
                    2
                ),

            "bytes_per_second":
                round(
                    self.bytes_per_second(),
                    2
                ),

            "unique_urls":
                len(self.unique_urls),

            "cache_hit_rate":
                round(
                    self.cache_hit_rate(),
                    2
                ),

            "cache_miss_rate":
                round(
                    self.cache_miss_rate(),
                    2
                ),

            "average_response_time":
                round(
                    self.average_response_time(),
                    2
                ),

            "total_requests":
                self.total_requests,

            "total_bytes":
                self.total_bytes,

            "most_active_ip":
                self.most_active_ip()
        }

    # =========================================
    # RESET
    # =========================================

    def reset(self):

        self.total_requests = 0
        self.total_bytes = 0

        self.cache_hits = 0
        self.cache_misses = 0

        self.response_times.clear()

        self.unique_urls.clear()

        self.ip_requests.clear()

        self.start_time = time.time()