import yaml

with open("CachingService.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
cachingHost = cfg["amoreCachingService"]["hostname"]
cachingPort = cfg["amoreCachingService"]["port"]
cachingServerRoute = f"http://{cachingHost}:{cachingPort}"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

