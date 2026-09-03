from flask import Flask, request, Response
import requests
import time

from cache.cache_manager import CacheManager
from monitoring.monitor import TrafficMonitor


app = Flask(__name__)


BACKEND_URL = "http://127.0.0.1:5001"

CACHE_SIZE = 5

# 1

# COMPONENTS


cache_manager = CacheManager(max_size=CACHE_SIZE)

monitor = TrafficMonitor()


# CACHE SAFETY


def is_cacheable(response):

    cache_control = response.headers.get(
        "Cache-Control",
        ""
    ).lower()

    if "private" in cache_control:
        return False

    if "no-store" in cache_control:
        return False


    if response.status_code != 200:
        return False

    return True



# TTL EXTRACTION


def get_ttl(response):

    cache_control = response.headers.get(
        "Cache-Control",
        ""
    ).lower()

    if "max-age=" in cache_control:

        try:

            value = cache_control.split(
                "max-age="
            )[1]

            value = value.split(",")[0]

            return int(value)

        except ValueError:
            pass

    # Default TTL
    return 60


# MONITORING STATISTICS


@app.route("/monitor/stats")
def monitor_stats():

    return monitor.get_features()


# =========================================
# CACHE STATISTICS
# =========================================

@app.route("/cache/stats")
def cache_stats():

    return cache_manager.stats()


# =========================================
# CLEAR CACHE
# =========================================

@app.route("/cache/clear")
def clear_cache():

    cache_manager.clear()

    return {
        "message": "Cache cleared successfully"
    }


# =========================================
# REVERSE PROXY
# =========================================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):

    start_time = time.time()

    # =====================================
    # CACHE KEY
    # =====================================

    cache_key = (
        request.method
        + ":"
        + request.full_path
    )

    cache_key = cache_key.rstrip("?")

    # =====================================
    # CACHE LOOKUP
    # =====================================

    if request.method == "GET":

        cached_item = cache_manager.get(
            cache_key
        )

        if cached_item is not None:

            response_time = (
                time.time() - start_time
            ) * 1000

            print(
                f"[CACHE HIT] "
                f"{request.full_path}"
            )

            # Record monitoring data
            monitor.record_request(

                client_ip=request.remote_addr,

                url=request.path,

                method=request.method,

                response_status=
                    cached_item["status"],

                response_size=
                    len(cached_item["content"]),

                response_time=response_time,

                cache_status="HIT"
            )

            return Response(

                cached_item["content"],

                status=cached_item["status"],

                headers=cached_item["headers"]
            )

    # =====================================
    # CACHE MISS
    # =====================================

    if request.method == "GET":

        print(
            f"[CACHE MISS] "
            f"{request.full_path}"
        )

    # =====================================
    # FORWARD REQUEST TO BACKEND
    # =====================================

    backend_url = (
        f"{BACKEND_URL}/{path}"
    )

    try:

        backend_response = requests.request(

            method=request.method,

            url=backend_url,

            params=request.args,

            data=request.get_data(),

            headers={
                key: value
                for key, value
                in request.headers
                if key.lower() != "host"
            },

            timeout=5
        )

    except requests.RequestException as error:

        return Response(

            f"Backend connection error: {error}",

            status=502
        )

    # =====================================
    # RESPONSE HEADERS
    # =====================================

    response_headers = {}

    for key, value in backend_response.headers.items():

        if key.lower() not in [

            "content-encoding",

            "transfer-encoding",

            "connection"
        ]:

            response_headers[key] = value

    # =====================================
    # CACHE SECURITY CHECK
    # =====================================

    if (

        request.method == "GET"

        and is_cacheable(
            backend_response
        )
    ):

        ttl = get_ttl(
            backend_response
        )

        cache_manager.put(

            key=cache_key,

            content=backend_response.content,

            status=backend_response.status_code,

            headers=response_headers,

            ttl=ttl
        )

        print(
            f"[CACHE STORE] "
            f"{request.full_path} "
            f"TTL={ttl}s"
        )

    else:

        print(
            f"[CACHE BYPASS] "
            f"{request.full_path}"
        )

    # =====================================
    # MONITORING
    # =====================================

    response_time = (
        time.time() - start_time
    ) * 1000

    monitor.record_request(

        client_ip=request.remote_addr,

        url=request.path,

        method=request.method,

        response_status=
            backend_response.status_code,

        response_size=
            len(backend_response.content),

        response_time=response_time,

        cache_status="MISS"
    )

    # =====================================
    # RETURN RESPONSE TO CLIENT
    # =====================================

    return Response(

        backend_response.content,

        status=backend_response.status_code,

        headers=response_headers
    )


# =========================================
# START PROXY
# =========================================

if __name__ == "__main__":

    print(
        "================================="
    )

    print(
        " Secure Smart Cache Proxy"
    )

    print(
        "================================="
    )

    print(
        "Proxy running on:"
    )

    print(
        "http://localhost:5000"
    )

    print(
        "Backend server:",
        BACKEND_URL
    )

    print(
        "Cache capacity:",
        CACHE_SIZE
    )

    print(
        "Monitoring:"
    )

    print(
        "http://localhost:5000/monitor/stats"
    )

    print(
        "================================="
    )

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )