import logging
import time
import requests

from config import configuration as config

def measure_latency_and_update_apim():
    """
    Make calls to the simulator endpoints to measure the latency.
    Then call the helper API published in APIM to pass this information
    so that it can be used in the latency-routing policy
    In a real scenario, this would be scheduled to run periodically
    """

    # There are various considerations to take into account when measuring the latency
    # to compare across endpoints.
    # For example, do you want to measure the time for a complete response or the
    # time to receive the first token (via streaming)?
    # Also, the response time for a full response will be heavily affected by the number
    # of generated tokens in the response
    # The measurement used here takes a balanced view by measuring the time to receive the full
    # response but setting max_tokens to 10 to limit the degree of variation in the
    # number of tokens in the response (and hence the response time)

    def measure_latency(endpoint: str,
                        deployment_name: str,
                        api_key: str):
        """Helper to measure the latency of an endpoint"""
        time_start = time.perf_counter()
        try:
            response = requests.post(
                url=f"https://{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={config.aoai_api_version}",
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "model": deployment_name,
                    "messages" : [
                        {"role": "system", "content": ""},
                        {"role": "user", "content": "Once upon a time"}
                        ],
                    "max_tokens": 10,
                },
                timeout=60,
            )
            response.raise_for_status()
            time_end = time.perf_counter()
            return time_end - time_start
        except requests.ReadTimeout:
            logging.warning("Request to %s timed out", endpoint)
            return float("inf")

    backends_with_latency = []
    for i in range(len(config.endpoints)):
        latency = measure_latency (
                    config.endpoints[i]["endpoint"],
                    config.endpoints[i]["deployment_name"],
                    config.endpoints[i]["api_key"]
                    )
        data = {
                "endpoint": config.endpoints[i]["endpoint"],
                "deployment_name": config.endpoints[i]["deployment_name"],
                "backend-id": config.endpoints[i]["backend_id"],
                "latency": latency
            }
        backends_with_latency.append(data)

    # sort with lowest latency first
    backends_with_latency = sorted(backends_with_latency, key=lambda x: x["latency"])
    for backend in backends_with_latency:
        logging.info(
            "    %s: %s : %s ms",
            backend["endpoint"],
            backend["deployment_name"],
            backend["latency"] * 1000,
        )
    sorted_backends = [backend["backend-id"] for backend in backends_with_latency]

    payload = {"preferredBackends": sorted_backends}
    response = requests.post(
        url=f"{config.apim_url}/helpers/set-preferred-backends",
        json=payload,
        headers={"ocp-apim-subscription-key": config.apim_api_key},
    )
    response.raise_for_status()
    logging.info("Updated APIM with preferred backends: %s", response.text)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    while (True):
        try:
            measure_latency_and_update_apim()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            logging.info(f"next iteration in {config.sleep_timeout} seconds")
            time.sleep(config.sleep_timeout)
   