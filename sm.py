import requests
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import pandas as pd
import time
import openpyxl

# Configurazione globale dei headers per le richieste
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36"
}

def fetch_robots_txt(domain):
    """
    Recupera il contenuto del robots.txt e restituisce eventuali URL di sitemap trovati.
    """
    robots_url = urljoin(domain, "/robots.txt")
    print(f"Checking robots.txt at: {robots_url}")

    try:
        response = requests.get(robots_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        sitemaps = []
        for line in response.text.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_url = line.split(":", 1)[1].strip()
                sitemaps.append(sitemap_url)

        return sitemaps

    except requests.exceptions.RequestException as e:
        print(f"Error fetching robots.txt: {e}")
        return []

def try_common_sitemap_paths(domain):
    """
    Prova percorsi comuni per trovare una sitemap se non specificata nel robots.txt.
    """
    print("No sitemaps found in robots.txt. Trying common paths...")
    common_paths = [
        "/sitemap.xml",
        "/sitemap-index.xml",
        "/sitemap_index.xml",
        "/sitemapindex.xml",
        "/sitemap/sitemap.xml",
        "/sitemaps/sitemap.xml",
        "/sitemap/sitemap-index.xml",
        "/sitemaps/sitemap-index.xml",
        "/sitemap/sitemap_index.xml",
        "/sitemaps/sitemap_index.xml",
        "/sitemap/sitemapindex.xml"
    ]

    sitemaps = []
    for path in common_paths:
        sitemap_url = urljoin(domain, path)
        try:
            response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                print(f"Sitemap found at: {sitemap_url}")
                sitemaps.append(sitemap_url)
                break
        except requests.exceptions.RequestException:
            continue

    return sitemaps

def process_sitemap(sitemap_url):
    """
    Processa una sitemap (index o child) e restituisce una lista di URL.
    """
    try:
        response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        urls = []
        if root.tag.endswith("sitemapindex"):
            print(f"Sitemap index found at: {sitemap_url}")
            for sitemap in root.findall(".//{*}sitemap"):
                loc = sitemap.find(".//{*}loc")
                if loc is not None:
                    urls.extend(process_sitemap(loc.text.strip()))
        elif root.tag.endswith("urlset"):
            print(f"Sitemap child found at: {sitemap_url}")
            for url in root.findall(".//{*}url"):
                loc = url.find(".//{*}loc")
                if loc is not None:
                    urls.append(loc.text.strip())

        return urls

    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing sitemap XML: {e}")
        return []

def check_urls_status(urls, pause=0):
    """
    Verifica lo status code per ciascun URL e restituisce un DataFrame.
    """
    url_status = []
    total_urls = len(urls)  # Conteggio totale degli URL

    # Usa una sessione persistente per migliorare le prestazioni
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for i, url in enumerate(urls, start=1):  # start=1 per iniziare da 1 invece di 0
            try:
                response = session.head(url, timeout=2, allow_redirects=False)
                print(f"[{i}/{total_urls}] Checking URL: {url} - Status Code: {response.status_code}")
                url_status.append({"URL": url, "Status Code": response.status_code})
            except requests.exceptions.RequestException:
                print(f"[{i}/{total_urls}] Error checking URL: {url}")
                url_status.append({"URL": url, "Status Code": "Error"})

    return pd.DataFrame(url_status)

def main():
    """
    Funzione principale per orchestrare le operazioni.
    """
    domain = input("Enter the domain (e.g., example.com): ")
    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = "https://" + domain

    # Step 1: Recupero sitemaps dal robots.txt
    sitemaps = fetch_robots_txt(domain)

    # Step 2: Se non ci sono sitemaps, prova percorsi comuni
    if not sitemaps:
        sitemaps = try_common_sitemap_paths(domain)

    if not sitemaps:
        print("No sitemaps found. Exiting.")
        return

    # Step 3: Processa tutte le sitemaps trovate
    all_urls = []
    for sitemap in sitemaps:
        all_urls.extend(process_sitemap(sitemap))

    if not all_urls:
        print("No URLs found in the sitemaps. Exiting.")
        return

    # stampa il numero di URL trovati
    print(f"Total URLs found in sitemap(s): {len(all_urls)}")

    # Step 4: Verifica gli URL trovati
    print("Checking status codes for the found URLs...")
    df = check_urls_status(all_urls, pause=1)

    # Step 5: Stampa il DataFrame risultante
    print("\nFinal Results:")
    print(df)
    
    # Step 6: Salva i risultati in un file Excel
    output_file = "url_status_codes.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\nResults saved to {output_file}")


# Avvia il programma
if __name__ == "__main__":
    main()
