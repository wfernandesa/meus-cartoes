import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from num2words import num2words
import time

# --- CONFIGURAÇÃO E CONEXÃO ---
def conectar_planilha():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = None
    
    # 1. Tenta buscar nas Secrets (Cenário: Streamlit Cloud)
    try:
        if "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    except:
        pass

    # 2. Se não conseguiu via Secrets, tenta o arquivo JSON local
    if creds is None:
        try:
            nome_json = 'controle-cartoes-william-6c294864d24b.json'
            creds = Credentials.from_service_account_file(nome_json, scopes=scope)
        except Exception as e:
            st.error(f"Erro ao carregar arquivo JSON local: {e}")
            return None

    try:
        client = gspread.authorize(creds)
        # Abre a planilha "Pessoal" na aba "Pagina1"
        return client.open("Pessoal").worksheet("Pagina1")
    except Exception as e:
        st.error(f"Erro de acesso à planilha: {e}")
        return None

# --- INICIALIZAÇÃO DO ESTADO (Para limpar os campos) ---
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0

def resetar_formulario():
    st.session_state.form_id += 1
    st.rerun()

# --- INTERFACE ---
st.set_page_config(page_title="Controle de Cartões", page_icon="💳")

st.title("💳 Gestão de Cartões de Crédito")

# Criamos uma chave única para o formulário atual
f_key = f"v_{st.session_state.form_id}"

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        data_compra = st.date_input(
            "Data da Compra", 
            value=date.today(), 
            format="DD/MM/YYYY",
            key=f"data_{f_key}"
        )
        responsavel = st.selectbox(
            "Quem comprou?", 
            ["Selecione um Comprador","Carlos", "William", "Débora", "Telma", "Luiz Paulo"],
            key=f"resp_{f_key}"
        )
    
    with col2:
        cartao = st.selectbox(
            "Cartão Utilizado", 
            ["Selecione um Cartão","Cartão Marisa", " Cartão Nubank", " Cartão Digio", "Cartão Inter"],
            key=f"cartao_{f_key}"
        )
        valor = st.number_input(
            "Valor total (R$)", 
            min_value=0.0, 
            step=0.01, 
            format="%.2f",
            key=f"valor_{f_key}"
        )
        
        extenso_final = ""
        if valor > 0:
            try:
                extenso_final = num2words(valor, lang='pt_BR', to='currency')
                st.caption(f"**Extenso:** {extenso_final.capitalize()}")
            except:
                pass

    parcelado = st.toggle("A compra é parcelada?", key=f"parc_{f_key}")
    
    qtd_parcelas = 1
    if parcelado:
        qtd_parcelas = st.number_input(
            "Número de parcelas", 
            min_value=2, 
            max_value=48, 
            step=1, 
            value=2,
            key=f"qtd_{f_key}"
        )
        valor_da_parcela = valor / qtd_parcelas
        parcela_br = f"{valor_da_parcela:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        st.info(f"💳 **Parcelamento:** {qtd_parcelas}x de R$ {parcela_br}")
    else:
        valor_br = f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        st.info(f"💳 **Compra à vista:** R$ {valor_br}")
    
    descricao = st.text_area(
        "Descrição da compra", 
        height=100,      
        max_chars=500,    
        placeholder="Detalhes da compra...",
        key=f"desc_{f_key}"
    )
    
    btn_salvar = st.button("Salvar na Planilha", type="primary", use_container_width=True)

# --- LÓGICA DE ENVIO ---
if btn_salvar:
    if valor <= 0:
        st.warning("O valor deve ser maior que zero!")
    else:
        with st.spinner("Registrando no banco de dados..."):
            aba = conectar_planilha()
            if aba:
                nova_linha = [
                    data_compra.strftime("%d/%m/%Y"), 
                    responsavel, 
                    cartao, 
                    valor, 
                    "Sim" if parcelado else "Não", 
                    qtd_parcelas, 
                    descricao,
                    extenso_final.capitalize()
                ]
                
                try:
                    aba.append_row(nova_linha)
                    st.success(f"Compra registrada com sucesso!")
                    st.balloons()
                    
                    # Aguarda 2 segundos para o usuário ver o sucesso
                    time.sleep(2)
                    
                    # Muda o form_id para forçar o Streamlit a destruir os campos antigos e criar novos (limpos)
                    st.session_state.form_id += 1
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

st.caption("Sistema exclusivo para uso familiar desenvolvido por: William Fernandes Araujo.")