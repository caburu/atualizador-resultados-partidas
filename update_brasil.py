import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurações
API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
CSV_FILE = 'brasil.csv'
# Endpoint para Série A do Brasil
URL = "https://api.football-data.org/v4/competitions/BSA/matches"

def update():
    headers = {'X-Auth-Token': API_KEY}
    
    # Define o intervalo de busca: ontem e hoje
    ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    # Filtro de data diretamente na API para economizar banda
    params = {
        'dateFrom': ontem,
        'dateTo': hoje
    }

    print(f"Buscando jogos entre {ontem} e {hoje}...")
    response = requests.get(URL, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Erro na API: {response.status_code}")
        return

    data = response.json()
    matches = data.get('matches', [])

    # Se o arquivo brasil.csv não existir, criamos com o cabeçalho correto
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['id', 'timeA', 'gols_timeA', 'x', 'gols_timeB', 'timeB'])
    else:
        df = pd.read_csv(CSV_FILE)

    for match in matches:
        print(f"Processando jogo: {match['homeTeam']['name']} x {match['awayTeam']['name']} - Status: {match['status']}")
        if match['status'] == 'FINISHED':
            match_id = match['id']
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            gols_a = match['score']['fullTime']['home']
            gols_b = match['score']['fullTime']['away']

            # Verifica se o jogo já está no CSV para não duplicar
            if match_id not in df['id'].values:
                nova_linha = {
                    'id': match_id,
                    'timeA': home_team,
                    'gols_timeA': gols_a,
                    'x': 'x',
                    'gols_timeB': gols_b,
                    'timeB': away_team
                }
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                print(f"Adicionado: {home_team} {gols_a} x {gols_b} {away_team}")
            else:
                print(f"Jogo {match_id} já existe no CSV.")

    # Salva o arquivo
    df.to_csv(CSV_FILE, index=False)

if __name__ == "__main__":
    update()