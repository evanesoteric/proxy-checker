import socket
import requests
import logging
from multiprocessing import Pool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_proxies():
    try:
        with open('proxies.txt', 'r') as f:
            proxies = f.read().splitlines()
            proxies = list(filter(None, proxies))
        logging.info(f"Loaded {len(proxies)} proxies.")
        return proxies
    except FileNotFoundError:
        logging.error("The 'proxies.txt' file was not found.")
        raise
    except Exception as e:
        logging.error(f"An error occurred while loading proxies: {e}")
        raise

def is_proxy_alive(proxy):
    try:
        ip, port = proxy.split(':')
        if not ip.replace('.', '').isdigit():
            ip = socket.gethostbyname(ip)
        test_url = "http://www.example.com"
        proxies = {"http": f"http://{ip}:{port}", "https": f"https://{ip}:{port}"}
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            logging.info(f"Proxy {proxy} is alive.")
            return f"{ip}:{port}"
        else:
            logging.warning(f"Proxy {proxy} is dead. Status code: {response.status_code}")
            return None
    except socket.gaierror:
        logging.warning(f"Hostname resolution failed for proxy: {proxy}")
        return None
    except requests.exceptions.ProxyError:
        logging.warning(f"Proxy error encountered for proxy: {proxy}")
        return None
    except requests.exceptions.ConnectTimeout:
        logging.warning(f"Connection timeout for proxy: {proxy}")
        return None
    except requests.exceptions.ReadTimeout:
        logging.warning(f"Read timeout for proxy: {proxy}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred for proxy {proxy}: {e}")
        return None

def check_proxies(proxies):
    try:
        with Pool(4) as pool:
            results = pool.map(is_proxy_alive, proxies)
        alive_proxies = list(filter(None, results))
        with open('good-proxies.txt', 'w') as f:
            for proxy in alive_proxies:
                f.write(f"{proxy}\n")
        logging.info(f"Saved {len(alive_proxies)} alive proxies to 'good-proxies.txt'.")
    except Exception as e:
        logging.error(f"An error occurred while checking proxies: {e}")
        raise

def main():
    try:
        proxies = load_proxies()
        if proxies:
            check_proxies(proxies)
    except Exception as e:
        logging.error(f"An error occurred in the main process: {e}")

if __name__ == "__main__":
    main()
