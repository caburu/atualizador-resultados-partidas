import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurações
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
CSV_FILE = 'resultados.csv'
URL = "https://api.football-data.org/v4/competitions/WC/matches"

# Dicionário para mapear nomes da API (Inglês) para o seu CSV (Português)
# Adicione todos os países do seu arquivo aqui
mapa_nomes = {
    "United States of America": "Estados Unidos",
    "South Africa": "África do Sul",
    "Ivory Coast": "Costa do Marfim",
    "DR Congo": "RD Congo",
    "Korea Republic": "Coreia do Sul",
    "Czech Republic": "República Tcheca",
    "Saudi Arabia": "Arábia Saudita",
    "New Zealand": "Nova Zelândia",
    "Cape Verde": "Cabo Verde",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina",
    "Mexico": "México",
    "Canada": "Canadá",
    "Qatar": "Catar",
    "Switzerland": "Suíça",
    "Paraguay": "Paraguai",
    "Australia": "Austrália",
    "Turkey": "Turquia",
    "Brazil": "Brasil",
    "Morocco": "Marrocos",
    "Scotland": "Escócia",
    "Germany": "Alemanha",
    "Curacao": "Curaçao",
    "Ecuador": "Equador",
    "Japan": "Japão",
    "Sweden": "Suécia",
    "Netherlands": "Holanda",
    "Tunisia": "Tunísia",
    "Belgium": "Bélgica",
    "Iran": "Irã",
    "Egypt": "Egito",
    "Spain": "Espanha",
    "Uruguay": "Uruguai",
    "France": "França",
    "Iraq": "Iraque",
    "Norway": "Noruega",
    "Algeria": "Argélia",
    "Jordan": "Jordânia",
    "Uzbekistan": "Uzbequistão",
    "Colombia": "Colômbia",
    "England": "Inglaterra",
    "Ghana": "Gana",
    "Panama": "Panamá",
    "Croatia": "Croácia",
    "Austria": "Áustria",
}

def update():
    headers = {'X-Auth-Token': API_KEY}
    
    # Define a janela: Ontem e Hoje (para garantir jogos que terminaram de madrugada)
    ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        'dateFrom': ontem,
        'dateTo': hoje
    }

    print(f"Buscando atualizações entre {ontem} e {hoje}...")
    response = requests.get(URL, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Erro na API: {response.status_code}")
        return

    data = response.json()
    matches = data.get('matches', [])

    if not matches:
        print("Nenhum jogo finalizado encontrado no período.")
        return

    # Carrega o CSV original
    df = pd.read_csv(CSV_FILE)
    mudou = False

    if not matches:
        print("Nenhum jogo finalizado encontrado no período.")
        return

    for match in matches:
        if match['status'] == 'FINISHED':
            home_api = match['homeTeam']['name']
            away_api = match['awayTeam']['name']
            
            home_pt = mapa_nomes.get(home_api, home_api)
            away_pt = mapa_nomes.get(away_api, away_api)
            
            gols_a = match['score']['fullTime']['home']
            gols_b = match['score']['fullTime']['away']

            # Busca a linha onde os times batem
            mask = (df['timeA'] == home_pt) & (df['timeB'] == away_pt)
            
            if mask.any():
                # Verifica se o valor no CSV já é o mesmo (evita escrita desnecessária)
                idx = df.index[mask][0]
                if pd.isna(df.at[idx, 'gols_timeA']) or int(df.at[idx, 'gols_timeA']) != gols_a:
                    df.loc[mask, 'gols_timeA'] = gols_a
                    df.loc[mask, 'gols_timeB'] = gols_b
                    mudou = True
                    print(f"Atualizado: {home_pt} {gols_a} x {gols_b} {away_pt}")
            else:
                print(f"Jogo {home_pt} {gols_a} x {gols_b} {away_pt} não encontrado no CSV. Verifique se os nomes estão corretos no mapa de nomes.")

    if mudou:
        df.to_csv(CSV_FILE, index=False)
        print("Arquivo resultados.csv atualizado.")
    else:
        print("Nada novo para atualizar no CSV.")

if __name__ == "__main__":
    update()