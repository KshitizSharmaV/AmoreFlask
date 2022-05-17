import yaml
import os

with open("CachingService.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
cachingHost = cfg["amoreCachingService"]["hostname"]
cachingPort = cfg["amoreCachingService"]["port"]

env_host = os.getenv('CACHING_SERVICE_SERVICE_HOST', None)
env_port = os.getenv('CACHING_SERVICE_SERVICE_PORT', None)

caching_service_host = env_host if env_host else cachingHost
caching_service_port = env_port if env_port else cachingPort

cachingServerRoute = f"http://{caching_service_host}:{caching_service_port}"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

