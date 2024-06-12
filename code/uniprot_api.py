import requests
from tqdm import tqdm
import gzip
from io import BytesIO
import pandas as pd

base_url = "https://rest.uniprot.org/uniprotkb/search?compressed=true&fields=accession%2Creviewed%2Cid%2Cprotein_name%2Cgene_names%2Corganism_name%2Cec%2Corganism_id%2Crhea%2Cxref_alphafolddb%2Cxref_pdb%2Cxref_brenda%2Cxref_biocyc%2Cxref_pathwaycommons%2Cxref_sabio-rk%2Cxref_reactome%2Cxref_plantreactome%2Cxref_signor%2Cxref_signalink%2Cxref_unipathway&format=tsv&query=%28*%29+AND+%28reviewed%3Atrue%29+AND+%28proteins_with%3A1%29+AND+%28proteins_with%3A13%29"

size = 500
offset = 0
all_data = []

response = requests.get(f"{base_url}&size=1")
if response.status_code == 200:
    total_results = int(response.headers.get("x-total-results", 0))
else:
    print(f"Fehler beim Abrufen der Daten: {response.status_code}")
    total_results = 0

with tqdm(total=total_results, desc="Abrufen der Daten", unit=" Eintrag") as pbar:
    while offset < total_results:
        url = f"{base_url}&size={size}&offset={offset}"
        response = requests.get(url)
        
        if response.status_code == 200:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
                data = f.read().decode('utf-8')
            if not data.strip():
                break
            all_data.append(data)
            offset += size
            pbar.update(size)
        else:
            print(f"Fehler beim Abrufen der Daten: {response.status_code}")
            break

combined_data = "\n".join(all_data)

df = pd.read_csv(BytesIO(combined_data.encode('utf-8')), sep='\t')

df_filtered = df[["Entry", "EC number", "PDB"]]
df_filtered = df_filtered.dropna(subset=['Entry', 'EC number'], how='all')
df_filtered['EC number'] = df_filtered['EC number'].str.split(';').str[0]
df_filtered['PDB'] = df_filtered['PDB'].fillna('').str.split(';')
df_split = df_filtered.explode('PDB')
df_split = df_split[df_split['PDB'] != '']
df_split.dropna(subset=['Entry', 'EC number', 'PDB'], how='any', inplace=True)

df_split.to_csv('../data/data_preparation/uniprot/raw_uniprot_data.tsv', sep='\t', index=False)
df_split.head()