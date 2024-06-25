import pandas as pd
from random import randint
from fuzzywuzzy import process, fuzz
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

    def get_response(self, user_input, current_node, score_threshold=0.9):
        """
        Obtém uma resposta que corresponde à entrada do usuário, ao nó atual e ao status verificado,
        usando correspondência fuzzy.

        Args:
            user_input (str): Entrada do usuário.
            current_node (str): Nó atual.

        Returns:
            str: Uma resposta correspondente ou None se não houver correspondência.
        """
        try:
            # Filtra o dataframe para encontrar respostas no nó atual e com status verificado
            possible_responses = self.df[
                (self.df['current_node'] == current_node) &
                (self.df['checked'] == True)
            ]

            # Usa fuzzy matching para encontrar as entradas de usuário mais próximas
            matches = process.extract(user_input, possible_responses['user_input'], scorer=fuzz.ratio)
            
            # Filtra matches com score menor que 90
            matches = [match for match in matches if match[1] >= score_threshold*100 ]
            
            if not matches:
                return None
            
            # Encontra a pontuação máxima de similaridade
            max_score = max(matches, key=lambda x: x[1])[1]
            
            # Seleciona as respostas correspondentes às melhores pontuações
            best_matches = [match for match, score in matches if score == max_score]
            
            responses = possible_responses[possible_responses['user_input'].isin([match for match, score in best_matches])]['response'].values
            
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
            # Verifica se existe uma correspondência exata
            match = self.df[(self.df['user_input'] == user_input) & 
                            (self.df['response'] == response) & 
                            (self.df['current_node'] == current_node)]
            
            if not match.empty:
                print('Entrada já existe no CSV. Não será adicionada novamente.')
                return
            
            # Cria uma nova entrada
            new_entry = {
                'user_input': user_input,
                'response': response,
                'current_node': current_node,
                'checked': checked
            }
            
            # Adiciona a nova entrada ao DataFrame
            self.df = pd.concat([self.df, pd.DataFrame(new_entry, index=[0])], ignore_index=True)
            self.df.to_csv(self.csv_reference, index=False)
            print('Adicionando nova resposta ao CSV.')
        
        except Exception as e:
            print(f'An error occurred while adding the response: {e}')
    def get_csv(self):
        return self.df