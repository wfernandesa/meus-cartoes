import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from num2words import num2words

# --- CONFIGURAÇÃO E CONEXÃO ---
def conectar_planilha():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file('suas-credenciais.json', scopes=scope)
        client = gspread.authorize(creds)
        # Lembre-se de conferir se o nome abaixo é igual ao da sua planilha no Drive
        return client.open("NOME_DA_SUA_PLANILHA").sheet1
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# --- INTERFACE ---
st.set_page_config(page_title="Controle de Cartões", page_icon="💳")

st.title("💳 Gestão de Cartões de Crédito")

qtd_parcelas = 1
extenso_final = ""

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        data_compra = st.date_input(
            "Data da Compra", 
            value=date.today(), 
            format="DD/MM/YYYY"
        )
        responsavel = st.selectbox("Quem comprou?", ["Carlos", "William", "Débora", "Telma"])
    
    with col2:
        cartao = st.selectbox("Cartão Utilizado", ["Marisa", "Nubank", "Digio"])
        valor = st.number_input("Valor total (R$)", min_value=0.0, step=0.01, format="%.2f")
        
        if valor > 0:
            try:
                extenso_final = num2words(valor, lang='pt_BR', to='currency')
                st.caption(f"**Extenso:** {extenso_final.capitalize()}")
            except:
                pass

    parcelado = st.toggle("A compra é parcelada?")
    
    if parcelado:
        qtd_parcelas = st.number_input("Número de parcelas", min_value=2, max_value=48, step=1, value=2)
        valor_da_parcela = valor / qtd_parcelas
        
        # Formata o valor da parcela (1.250,50)
        parcela_br = f"{valor_da_parcela:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        st.info(f"💳 **Parcelamento no Cartão:** {cartao} | **{qtd_parcelas}x de R$ {parcela_br}**")
    else:
        # Formata o valor total à vista (1.250,50)
        valor_br = f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        st.info(f"💳 **Compra à vista no Cartão:** {cartao} | **R$ {valor_br}**")
    
    descricao = st.text_area(
        "Descrição da compra", 
        height=100,      
        max_chars=500,    
        placeholder="Descreva os detalhes da compra aqui..."
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
                    st.toast("Sucesso!", icon="✅")
                    st.success(f"Compra registrada com sucesso!")
                    st.snow()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

st.caption("Sistema de uso pessoal e familiar. Sem necessidade de login.")