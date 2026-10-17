
import requests
import folium

import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Obter o token da SPTrans
TOKEN = os.getenv("SPTRANS_TOKEN")

# Linha de ônibus escolhida
LINHA = "875A-10"

# Endereço da API
URL = "https://api.olhovivo.sptrans.com.br/v2.1"

# Mantém a sessão autenticada nas consultas
sessao = requests.Session()


# 1. Autenticar na API
resposta = sessao.post(
    URL + "/Login/Autenticar",
    params={"token": TOKEN}
)

if resposta.text.lower() != "true":
    print("Erro na autenticação. Verifique seu token.")
    exit()

print("Autenticação realizada!")


# 2. Buscar a linha de ônibus
resposta = sessao.get(
    URL + "/Linha/Buscar",
    params={"termosBusca": LINHA}
)
linhas = resposta.json()
print(linhas)

# Encontrar a linha desejada
codigo_linha = None

for linha in linhas:
    if linha["lt"] == "875A" and linha["tl"] == 10:
        codigo_linha = linha["cl"]
        break

if codigo_linha is None:
    print("Linha não encontrada. Verifique o número escolhido.")
    exit()


# 3. Buscar as paradas da linha
resposta = sessao.get(
    URL + "/Parada/BuscarParadasPorLinha",
    params={"codigoLinha": codigo_linha}
)
paradas = resposta.json()


# 4. Buscar a posição dos ônibus em circulação
resposta = sessao.get(
    URL + "/Posicao/Linha",
    params={"codigoLinha": codigo_linha}
)
dados = resposta.json()
onibus = dados.get("vs", [])


# 5. Criar o mapa
latitudes = [p["py"] for p in paradas if p["py"]]
longitudes = [p["px"] for p in paradas if p["px"]]

if latitudes:
    centro = [sum(latitudes) / len(latitudes),
              sum(longitudes) / len(longitudes)]
else:
    centro = [-23.5505, -46.6333]

mapa = folium.Map(location=centro, zoom_start=13)


# Adicionar as paradas em azul
for parada in paradas:
    if parada["py"] and parada["px"]:
        folium.Marker(
            location=[parada["py"], parada["px"]],
            popup=parada["np"],
            tooltip="Parada de ônibus",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)


# Adicionar os ônibus em vermelho
for veiculo in onibus:
    if veiculo["py"] and veiculo["px"]:
        folium.Marker(
            location=[veiculo["py"], veiculo["px"]],
            popup="Ônibus: " + str(veiculo["p"]),
            tooltip="Ônibus em circulação",
            icon=folium.Icon(color="red", icon="bus")
        ).add_to(mapa)


# 6. Salvar o mapa
mapa.save("mapa.html")

print("Paradas encontradas:", len(paradas))
print("Ônibus encontrados:", len(onibus))
print("Mapa salvo em mapa.html")
