import yaml
import os

cachingHost = '127.0.0.1'
cachingPort = 5050

in_env = os.getenv('FLASK_SERVICE_SERVICE_HOST', None)

caching_service_host = "caching-service.default" if in_env else cachingHost
caching_service_port = 5050 if in_env else cachingPort

cachingServerRoute = f"http://{caching_service_host}:{caching_service_port}"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

