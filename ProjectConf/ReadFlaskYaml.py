import yaml
import os

with open("CachingService.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
cachingHost = cfg["amoreCachingService"]["hostname"]
cachingPort = cfg["amoreCachingService"]["port"]

in_env = os.getenv('FLASK_SERVICE_SERVICE_HOST', None)

caching_service_host = "caching-service.default" if in_env else cachingHost
caching_service_port = 5050 if in_env else cachingPort

cachingServerRoute = f"http://{caching_service_host}:{caching_service_port}"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

