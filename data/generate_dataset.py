import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

CATEGORIAS = ["Show Musical", "Teatro", "Exposição", "Festival", "Stand-up", "Dança", "Cinema", "Workshop"]
BAIRROS = ["Meireles", "Aldeota", "Centro", "Varjota", "Benfica", "Maraponga", "Messejana", "Beira Mar"]
LOCAIS = {
    "Meireles": ["Teatro RioMar", "Centro Cultural Dragão do Mar", "Arena Meireles"],
    "Aldeota": ["Cineteatro São Luiz", "Espaço Cultural Aldeota", "Teatro Glauco Rodrigues"],
    "Centro": ["Teatro José de Alencar", "Praça do Ferreira", "Centro Cultural BNB"],
    "Varjota": ["Espaço Varjota", "Clube Náutico"],
    "Benfica": ["UFC Campus", "Espaço Benfica"],
    "Beira Mar": ["Anfiteatro da Beira Mar", "Iate Clube"],
    "Maraponga": ["Shopping Maraponga", "Centro Comunitário"],
    "Messejana": ["Casa de Cultura", "Praça Central"]
}

ARTISTAS = [
    "Banda Cearense", "Trio Nordestino", "Orquestra Fortaleza", "Grupo Folclórico CE",
    "DJ Nordeste", "Companhia de Teatro Local", "Coral Universitário", "Artistas Visuais CE",
    "Humoristas do Nordeste", "Ballet Fortaleza", "Cineclube Dragão", "Instrutores SENAC"
]

records = []
start_date = datetime(2024, 1, 1)

for i in range(350):
    categoria = random.choice(CATEGORIAS)
    bairro = random.choice(BAIRROS)
    local = random.choice(LOCAIS[bairro])

    # Capacity by category
    cap_map = {
        "Show Musical": (300, 3000), "Teatro": (80, 400), "Exposição": (50, 500),
        "Festival": (500, 5000), "Stand-up": (100, 600), "Dança": (80, 300),
        "Cinema": (60, 200), "Workshop": (20, 80)
    }
    cap_range = cap_map[categoria]
    capacidade = random.randint(*cap_range)

    # Occupancy rates by category
    ocp_map = {
        "Show Musical": (0.60, 0.98), "Teatro": (0.40, 0.90), "Exposição": (0.20, 0.70),
        "Festival": (0.70, 1.0), "Stand-up": (0.50, 0.95), "Dança": (0.35, 0.85),
        "Cinema": (0.30, 0.80), "Workshop": (0.50, 1.0)
    }
    ocp_range = ocp_map[categoria]
    ocupacao_pct = round(random.uniform(*ocp_range), 2)
    publico = int(capacidade * ocupacao_pct)

    # Ticket prices
    preco_map = {
        "Show Musical": (40, 250), "Teatro": (20, 80), "Exposição": (0, 30),
        "Festival": (50, 400), "Stand-up": (30, 100), "Dança": (20, 60),
        "Cinema": (15, 35), "Workshop": (50, 200)
    }
    preco = round(random.uniform(*preco_map[categoria]), 2)

    # Date and time
    days_offset = random.randint(0, 545)
    data = start_date + timedelta(days=days_offset)
    hora_options = ["14:00", "16:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
    hora = random.choice(hora_options)

    duracao = random.choice([60, 90, 120, 150, 180, 240])
    artista = random.choice(ARTISTAS)
    gratuito = preco == 0 or random.random() < 0.08
    if gratuito:
        preco = 0.0

    receita = round(publico * preco, 2)

    records.append({
        "id": i + 1,
        "nome_evento": f"{categoria} — {artista} #{i+1}",
        "categoria": categoria,
        "local": local,
        "bairro": bairro,
        "data": data.strftime("%Y-%m-%d"),
        "hora": hora,
        "duracao_min": duracao,
        "capacidade": capacidade,
        "publico": publico,
        "ocupacao_pct": ocupacao_pct,
        "preco_ingresso": preco,
        "gratuito": gratuito,
        "receita_total": receita,
        "artista": artista,
    })

df = pd.DataFrame(records)
df.to_csv("/home/claude/cultinsights/data/eventos.csv", index=False)
print(f"Dataset gerado: {len(df)} eventos")
print(df.head(3).to_string())
