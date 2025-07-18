import os
import requests
from dotenv import load_dotenv
import traceback
from app.utils.web_scraper import extract_text_with_selenium
from bs4 import BeautifulSoup
import openai
import re
import array
import hdbscan
import numpy as np
import json
from sklearn.decomposition import TruncatedSVD

load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
TAVILY_API_URL = 'https://api.tavily.com/search'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
openai.api_key = OPENAI_API_KEY


def extract_text_with_bs4(url):
    try:
        if not url.startswith('http'):
            url = f'https://{url}'
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None

def search_company_website(company_name):
    if not TAVILY_API_KEY:
        return None
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": f"{company_name} official website",
        "search_type": "web",
        "num_results": 1
    }
    try:
        resp = requests.post(TAVILY_API_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('results'):
            return data['results'][0].get('url')
    except Exception:
        traceback.print_exc()
    return None

def preprocess_webpage_text(text):
    # Remove long continuous spaces and normalize whitespace
    return re.sub(r'\s+', ' ', text).strip()

def generate_buyer_persona_from_text(raw_text, lead_data=None):
    if not raw_text or not OPENAI_API_KEY:
        return None
    context = preprocess_webpage_text(raw_text)
    data_context = f"Lead Data: {lead_data}\n" if lead_data else ""
    prompt = (
        "Given the following company webpage text and lead data, generate a detailed buyer persona for the company. "
        "The persona should include: key attributes (such as industry, company size, typical decision makers, goals, mission, vision, etc. ONLY IF MENTIONED IN THE TEXT OR DATA), "
        "at least 2 direct quotes from the text that support the persona, and present the result as a JSON object with clear key-value pairs. "
        "Do not include any other text in your response other than the JSON.\n\n"
        f"{data_context}Webpage Text: {context}\n\nPersona:"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a B2B marketing analyst."},
                      {"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )
        persona = response.choices[0].message.content.strip()
        return persona.strip("```").strip("json")
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None

def generate_buyer_persona_embedding(persona):
    if not persona or not OPENAI_API_KEY:
        return None
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=persona
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(e)
        traceback.print_exc()
        return None

def embedding_to_bytes(embedding):
    if embedding is None:
        return None
    return array.array('f', embedding).tobytes()

def filter_persona_json(persona_str):
    try:
        persona = json.loads(persona_str)
        filtered = {k: v for k, v in persona.items() if v not in [None, "", [], {}]}
        return json.dumps(filtered, ensure_ascii=False)
    except Exception:
        return persona_str

def cluster_lead_embeddings(embeddings_bytes_list):
    # Convert bytes to numpy arrays
    embeddings = []
    for emb_bytes in embeddings_bytes_list:
        if emb_bytes:
            arr = np.frombuffer(emb_bytes, dtype=np.float32)
            embeddings.append(arr)
    if not embeddings:
        return []
    embeddings = np.stack(embeddings)
    # SVD dimensionality reduction to 32 features
    if embeddings.shape[0] > 32:
        svd = TruncatedSVD(n_components=32, random_state=42)
        reduced = svd.fit_transform(embeddings)
    else:
        reduced = embeddings[:, :32] if embeddings.shape[1] > 32 else embeddings
    # HDBSCAN clustering
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
    labels = clusterer.fit_predict(reduced)
    max_label = max(labels)
    new_labels = []
    for i in labels:
        if i == -1:
            new_labels.append(max_label + 1)
            max_label += 1
        else:
            new_labels.append(i)
    return new_labels

def process_lead(lead_data):
    # lead_data: dict, expects at least company name and maybe website
    website = lead_data.get('website') or lead_data.get('Website')
    raw_text = None
    if website:
        text = extract_text_with_bs4(website)
        if text and len(text.split()) >= 25:
            raw_text = text
        else:
            text_selenium = extract_text_with_selenium(website)
            if text_selenium:
                raw_text = text_selenium
    # If no website or failed to scrape, try TavilySearch
    if not raw_text:
        company_name = lead_data.get('name') or lead_data.get('Name')
        if company_name:
            found_url = search_company_website(company_name)
            if found_url:
                text = extract_text_with_bs4(found_url)
                if text and len(text.split()) >= 25:
                    raw_text = text
                else:
                    text_selenium = extract_text_with_selenium(found_url)
                    if text_selenium:
                        raw_text = text_selenium
    # Generate persona if we have raw_text
    buyer_persona = None
    buyer_persona_embedding = None
    if raw_text:
        persona_raw = generate_buyer_persona_from_text(raw_text, lead_data)
        buyer_persona = filter_persona_json(persona_raw) if persona_raw else None
        if buyer_persona:
            embedding = generate_buyer_persona_embedding(buyer_persona)
            buyer_persona_embedding = embedding_to_bytes(embedding) if embedding else None
    return raw_text, buyer_persona, buyer_persona_embedding 