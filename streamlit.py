import streamlit as st

st.set_page_config(page_icon=:gear:, page_title="Gestão da Manutenção", layout="wide")

caminho = "manutencao.txt"

@st.cache_data
def ler_manutencao(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    dados = {}
    maquina_atual = None
    tipo_atual = None
    subtipo_atual = None

    for linha in linhas:
        linha = linha.rstrip()

        if not linha.strip():
            continue

        if linha.startswith("[") and linha.endswith("]"):
            maquina_atual = linha[1:-1].strip().upper()
            dados[maquina_atual] = {}
            tipo_atual = None
            subtipo_atual = None
        elif linha.startswith("        - ") and subtipo_atual:  # 8 espaços + "-"
            instrucao = linha.strip()[2:].strip()
            dados[maquina_atual][tipo_atual][subtipo_atual].append(instrucao)
        elif linha.startswith("    ") and tipo_atual == "PREVENTIVA":
            subtipo_atual = linha.strip().replace(":", "").upper()
            if subtipo_atual:
                dados[maquina_atual][tipo_atual][subtipo_atual] = []
        elif linha.startswith("    - ") and tipo_atual != "PREVENTIVA":
            instrucao = linha.strip()[2:].strip()
            dados[maquina_atual][tipo_atual].append(instrucao)
        elif ":" in linha:
            tipo = linha.strip().replace(":", "").upper()
            tipo_atual = tipo
            if tipo == "PREVENTIVA":
                dados[maquina_atual][tipo] = {}
                subtipo_atual = None
            else:
                dados[maquina_atual][tipo] = []

    return dados

dados_manutencao = ler_manutencao(caminho)

if not dados_manutencao:
    st.error("Nenhum dado encontrado.")
else:
    maquina = st.sidebar.selectbox("Selecione a máquina", list(dados_manutencao.keys()))
    tipo = st.sidebar.selectbox("Tipo de manutenção", list(dados_manutencao[maquina].keys()))

    if tipo == "PREVENTIVA":
        subtipo = st.sidebar.selectbox("Periodicidade", list(dados_manutencao[maquina][tipo].keys()))
        instrucoes = dados_manutencao[maquina][tipo][subtipo]
        st.subheader(f"{maquina} - {tipo} ({subtipo})")
    else:
        instrucoes = dados_manutencao[maquina][tipo]
        st.subheader(f"{maquina} - {tipo}")
    if tipo != "INFORMAÇÕS GERAIS": 
        st.markdown("### Instruções")
    else:
        st.markdown("### Informações")  
        
    for item in instrucoes:
        st.markdown(f"- {item}")

