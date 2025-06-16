import streamlit as st

st.set_page_config(page_icon=":gear:", page_title="Gestão da Manutenção", layout="wide")

# Configuração do arquivo de dados
ARQUIVO_DADOS = "manutencao_final.txt"


def ler_arquivo_dados(caminho_arquivo):
    """Lê o arquivo de dados de manutenção"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        st.error(f"❌ Arquivo '{caminho_arquivo}' não encontrado!")
        st.info("📝 Certifique-se de que o arquivo existe no mesmo diretório do script.")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {str(e)}")
        return None


def processar_dados_texto(texto):
    """Processa o texto e retorna dados estruturados"""
    linhas = texto.strip().split('\n')
    dados = {}
    maquina_atual = None
    categoria_atual = None
    subcategoria_atual = None

    for linha in linhas:
        linha_original = linha
        linha = linha.strip()

        if not linha:
            continue

        # Identifica máquina/equipamento
        if linha.startswith('[') and linha.endswith(']'):
            maquina_atual = linha[1:-1].strip().upper()
            dados[maquina_atual] = {}
            categoria_atual = None
            subcategoria_atual = None

        # Identifica categoria principal (sem indentação, termina com :)
        elif linha.endswith(':') and not linha_original.startswith('    '):
            categoria_atual = linha[:-1].strip().upper()
            # Verifica se é uma categoria que tem subcategorias
            if categoria_atual in ['PREVENTIVA', 'PROCEDIMENTOS DE MANUTENÇÃO']:
                dados[maquina_atual][categoria_atual] = {}
            else:
                dados[maquina_atual][categoria_atual] = []
            subcategoria_atual = None

        # Identifica subcategoria (com 4 espaços de indentação, termina com :)
        elif linha_original.startswith('    ') and linha.endswith(':') and not linha_original.startswith('        '):
            subcategoria_atual = linha[:-1].strip().upper()
            if categoria_atual in ['PREVENTIVA', 'PROCEDIMENTOS DE MANUTENÇÃO']:
                dados[maquina_atual][categoria_atual][subcategoria_atual] = []

        # Identifica itens (começam com - e podem ter diferentes níveis de indentação)
        elif '- ' in linha:
            item = linha.split('- ', 1)[1].strip()

            if subcategoria_atual and categoria_atual in ['PREVENTIVA', 'PROCEDIMENTOS DE MANUTENÇÃO']:
                dados[maquina_atual][categoria_atual][subcategoria_atual].append(item)
            elif categoria_atual and categoria_atual not in ['PREVENTIVA', 'PROCEDIMENTOS DE MANUTENÇÃO']:
                dados[maquina_atual][categoria_atual].append(item)

    return dados


@st.cache_data
def carregar_dados():
    """Carrega e processa os dados do arquivo"""
    dados_texto = ler_arquivo_dados(ARQUIVO_DADOS)
    if dados_texto:
        return processar_dados_texto(dados_texto)
    return {}


# Carregamento dos dados
dados_manutencao = carregar_dados()

# Interface principal
st.title("🔧 Sistema de Gestão de Manutenção")
st.markdown("---")

if not dados_manutencao:
    st.error("❌ Nenhum dado de manutenção encontrado.")
else:
    # Sidebar para seleções
    st.sidebar.header("🔍 Seleções")

    # Seleção da máquina/equipamento
    maquina = st.sidebar.selectbox(
        "🏭 Selecione o equipamento:",
        list(dados_manutencao.keys()),
        help="Escolha o equipamento para visualizar as informações de manutenção"
    )

    # Seleção do tipo de manutenção
    tipos_disponiveis = list(dados_manutencao[maquina].keys())
    tipo = st.sidebar.selectbox(
        "📋 Tipo de informação:",
        tipos_disponiveis,
        help="Selecione o tipo de manutenção ou informação"
    )

    # Seleção de subcategoria se necessário
    subtipo = None
    if isinstance(dados_manutencao[maquina][tipo], dict):
        subtipos_disponiveis = list(dados_manutencao[maquina][tipo].keys())
        subtipo = st.sidebar.selectbox(
            "📅 Periodicidade/Sistema:",
            subtipos_disponiveis,
            help="Selecione a periodicidade ou sistema específico"
        )
        instrucoes = dados_manutencao[maquina][tipo][subtipo]
        titulo_secao = f"{maquina} - {tipo} ({subtipo})"
    else:
        instrucoes = dados_manutencao[maquina][tipo]
        titulo_secao = f"{maquina} - {tipo}"

    # Exibição do conteúdo principal
    st.header(titulo_secao)

    # Definir o título da seção baseado no tipo
    if tipo == "INFORMAÇÕS GERAIS":
        st.subheader("ℹ️ Informações Gerais")
    elif tipo == "PEÇA/COMPONENTES":
        st.subheader("💰 Custos de Peças e Componentes")
    else:
        if subtipo:
            st.subheader(f"📝 Procedimentos - {subtipo}")
        else:
            st.subheader("📝 Procedimentos")

    # Exibição das instruções/informações
    if instrucoes:
        for i, item in enumerate(instrucoes, 1):
            if tipo == "PEÇA/COMPONENTES":
                # Formatação especial para custos
                st.markdown(f"**{i}.** {item}")
            else:
                st.markdown(f"• {item}")
    else:
        st.info("Nenhuma informação disponível para esta seleção.")

    # Informações adicionais na sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"📊 **Estatísticas:**\n"
        f"• Equipamentos cadastrados: {len(dados_manutencao)}\n"
        f"• Tipos de informação: {len(tipos_disponiveis)}\n"
        f"• Itens na seleção atual: {len(instrucoes) if instrucoes else 0}"
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Sistema de Gestão de Manutenção | Desenvolvido com Streamlit"
    "</div>",
    unsafe_allow_html=True
)
