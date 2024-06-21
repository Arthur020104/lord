import pandas as pd
from random import randint

class FakeResponse:
    def __init__(self, csv_reference):
        """
        Inicializa a classe FakeResponse, carregando dados de um arquivo CSV.
        Se o arquivo CSV não puder ser aberto, cria um dataframe vazio e salva no arquivo CSV.

        Args:
            csv_reference (str): O caminho para o arquivo CSV contendo os dados.
        """
        self.csv_reference = csv_reference
        try:
            self.df = pd.read_csv(csv_reference)
        except FileNotFoundError:
            self.df = pd.DataFrame({
                'user_input': [''],
                'response': [''],
                'current_node': [''],
                'checked': [False]
            })
            print(f'Error opening CSV file: {csv_reference}. Creating an empty dataframe.')
            self.df.to_csv(csv_reference, index=False)
        except pd.errors.EmptyDataError:
            print(f'CSV file {csv_reference} is empty. Creating an empty dataframe.')
            self.df = pd.DataFrame({
                'user_input': [''],
                'response': [''],
                'current_node': [''],
                'checked': [False]
            })
            self.df.to_csv(csv_reference, index=False)
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            raise

    def get_response(self, user_input, current_node):
        """
        Obtém uma resposta que corresponde à entrada do usuário, ao nó atual e ao status verificado.

        Args:
            user_input (str): Entrada do usuário.
            current_node (str): Nó atual.

        Returns:
            str: Uma resposta correspondente ou None se não houver correspondência.
        """
        try:
            # Filtra o dataframe para encontrar respostas que correspondam à entrada do usuário, ao nó atual e ao status verificado
            responses = self.df[
                (self.df['user_input'] == user_input) &
                (self.df['current_node'] == current_node) &
                (self.df['checked'] == True)
            ]['response'].values
            
            if len(responses) == 0:
                return None
            elif len(responses) == 1:
                return responses[0]
            else:
                return responses[randint(0, len(responses) - 1)]
        except Exception as e:
            print(f'An error occurred while getting the response: {e}')
            return None

    def add_response(self, user_input, response, current_node, checked=False):
        """
        Adiciona uma nova resposta ao dataframe e salva no arquivo CSV.

        Args:
            user_input (str): Entrada do usuário.
            response (str): Resposta correspondente.
            current_node (str): Nó atual.
            checked (bool): Status verificado. Padrão é False.
        Returns:
            None
        """
        try:
            new_entry = {
                'user_input': user_input,
                'response': response,
                'current_node': current_node,
                'checked': checked
            }
            self.df = pd.concat([self.df, pd.DataFrame(new_entry, index=[0])], ignore_index=True)
            self.df.to_csv(self.csv_reference, index=False)
            print('Adicionando nova resposta ao CSV.')
        except Exception as e:
            print(f'An error occurred while adding the response: {e}')
    def get_csv(self):
        return self.df