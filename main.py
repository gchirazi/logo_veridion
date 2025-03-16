import pandas as pd
import requests
import cv2  # Procesare imagini
import numpy as np
import os
from sklearn.cluster import HDBSCAN  # Algoritm de clustering
from skimage.metrics import structural_similarity as ssim  # Calcul de similaritate intre imagini

# Returnez link-ul logo-ului folosind api-ul clearbit
def get_clearbit_logo(domain):
    return f"https://logo.clearbit.com/{domain}"

# Salvez logo-ul
def download_image(url, filename):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            return filename
    except requests.RequestException:
        return None

# Preprocesez imaginea
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Citesc imaginea in tonuri de gri
    if img is None:
        return None  # Dacă imaginea nu poate fi incarcata, returnez none
    img = cv2.resize(img, (32, 32))  # Redimensionez la 32x32 pentru rapiditate si pentru a ajuta
    #clusteringul in cazul in care un logo este blurat
    return img

def compute_similarity(img1, img2):
    return ssim(img1, img2)  # Calculez similaritatea dintre două imagini

# Incarc fisierul parquet
file_path = "logos.snappy.parquet"
df = pd.read_parquet(file_path)

df["logo_url"] = df["domain"].apply(get_clearbit_logo)  # Generez URL-ul logo-ului pentru fiecare domeniu

# Creez un folder pentru salvarea logo-urilor
os.makedirs("logos", exist_ok=True)

downloaded_logos = []  # Lista pentru a stoca logo-urile descarcate
for domain, url in zip(df["domain"], df["logo_url"]):
    filename = f"logos/{domain}.png"
    if download_image(url, filename):
        downloaded_logos.append((domain, filename))

# Procesare imagini
features = []  # Lista de caracteristici vizuale ale logo-urilor
processed_domains = []  # Lista domeniilor procesate
image_paths = []  # Lista cailor catre imagini
images = {}  # Dicționar pentru a stoca imaginile preprocesate
for domain, filename in downloaded_logos:
    img = preprocess_image(filename)
    if img is not None:
        features.append(img.flatten())  # Adaug imaginea aplatizata in lista de caracteristici
        processed_domains.append(domain)
        image_paths.append(filename)
        images[domain] = img  # Stochez imaginea preprocesata pentru utilizare ulterioara

# Clustering cu HDBSCAN, cel mai accurat in acest proiect cu logo-uri deoarece este varianta high density
features = np.array(features)
clustering = HDBSCAN(min_cluster_size=2, metric="euclidean").fit(features)

df_clusters = pd.DataFrame({"domain": processed_domains, "cluster": clustering.labels_, "image_path": image_paths})

# Reclustering pe baza SSIM
cluster_groups = {}
similarity_threshold = 0.8  # Prag de similaritate

for cluster_id in df_clusters["cluster"].unique():
    if cluster_id == -1:
       continue  # Ignor logo-urile care nu au fost grupate initial
    cluster_data = df_clusters[df_clusters["cluster"] == cluster_id]
    for i, domain1 in enumerate(cluster_data["domain"]):
        for j, domain2 in enumerate(cluster_data["domain"]):
            if i < j:
                score = compute_similarity(images[domain1], images[domain2])  # Calculez SSIM-ul
                if score >= similarity_threshold:
                    cluster_groups.setdefault(cluster_id, set()).update([domain1, domain2])  # Adaug logo-urile similare in acelasi cluster

# Creare raport HTML pentru vizualizarea clusterelor
os.makedirs("cluster_reports", exist_ok=True)
html_content = """<html><head><title>Logo Clusters</title></head><body><h1>Clustered Logos</h1>"""
for cluster_id, domains in cluster_groups.items():
    html_content += f"<h2>Cluster {cluster_id}</h2><div style='display:flex;flex-wrap:wrap;'>"
    for domain in domains:
        image_path = df_clusters[df_clusters["domain"] == domain]["image_path"].values[0]
        html_content += f"<div style='margin:10px;text-align:center;'><img src='../{image_path}' width='100'><br>{domain}</div>"
    html_content += "</div><hr>"
html_content += "</body></html>"

with open("cluster_reports/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)  # Salvez HTML-ul

# Salvare rezultate intr-un fișier CSV
df_clusters.to_csv("logo_clusters.csv", index=False)
