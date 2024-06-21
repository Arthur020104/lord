import streamlit as st
from FakeResponse import FakeResponse
import os

def main():
    st.set_page_config(page_title='Aprovação de Dados do CSV', layout='wide')
    st.title('Aprovação de Dados do CSV')

    # Referência ao arquivo CSV
    csv_reference = 'C:/Users/arthu/OneDrive/Área de Trabalho/Code/Work/lord/lord/FakeResponse/data.csv'
    # csv_reference = os.path.abspath(csv_reference)

    # Inicializar a classe FakeResponse
    fake_response = FakeResponse(csv_reference)
    df = fake_response.get_csv()

    # Exibir a tabela
    st.write('## Dados do CSV')
    edited_df = st.data_editor(df, num_rows="dynamic", height=500, width=1000)

    # Aprovação de dados
    st.write('## Aprovar Dados')
    for i, row in edited_df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f"<div style='border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;'>"
                    f"<strong>Entrada do Usuário:</strong> {row['user_input']}<br>"
                    f"<strong>Resposta:</strong> {row['response']}<br>"
                    f"<strong>Nó Atual:</strong> {row['current_node']}</div>", 
                    unsafe_allow_html=True
                )
            with col2:
                edited_df.at[i, 'checked'] = st.checkbox('Aprovar', key=f'approve_{i}', value=row['checked'])

    # Botão para salvar alterações
    if st.button('Salvar Alterações', key='save_button'):
        fake_response.df = edited_df
        fake_response.df.to_csv(csv_reference, index=False)
        st.success('Alterações salvas com sucesso!')

if __name__ == '__main__':
    main()
