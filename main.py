import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import math

# Lê o arquivo CSV com os dados das Olimpíadas
df = pd.read_csv('C:\\python_projects\\leitura_olimpiadas\\olympics_dataset.csv')

# Função para abreviar nomes compostos: mantém o primeiro nome completo e abrevia o segundo com 3 letras + ponto
def abreviador(nome):
    partes = nome.split()
    if len(partes) > 1:
        primeiro = partes[0]
        segundo = partes[1][:3] + '.'
        return f"{primeiro} {segundo}"
    else:
        return nome

print('Esse programa faz gráficos baseados em modalidades das Olimpiadas.\n')

# Solicita ao usuário o tipo de gráfico desejado: países ou atletas
pesquisa = int(input(('- Digite 1 se deseja um gráfico de países com mais medalhas\n'
                     '- Digite 2 se deseja um gráfico de atletas com mais medalha\n')))

# Loop para garantir entrada válida do usuário para o tipo de gráfico
while True:
    if pesquisa == 1:
        escolha = 'Paises'           # Define o texto para título e labels
        escolha_usuario = 'Team'     # Coluna do DataFrame para países
        print('Você escolheu fazer um gráfico baseado em países.\n')
        break
    elif pesquisa == 2:
        escolha = 'Atletas'          # Define o texto para título e labels
        escolha_usuario = 'Name'     # Coluna do DataFrame para atletas
        print('Você escolheu fazer um gráfico baseado em atletas.\n')
        break
    else:
        print('Voce digitou um número fora do raio estabelecido. Por favor, tente novamente:\n\n')
        pesquisa = int(input('Digite 1 ou 2: '))

# Solicita o nome do esporte para filtrar os dados (em inglês)
esporte_escolhido = input('Digite o nome do esporte que deseja fazer o gráfico EM INGLÊS: ')
esporte_escolhido = esporte_escolhido.capitalize()  # Capitaliza a primeira letra para padronização
print(f'Você escolheu {esporte_escolhido}!')

# Solicita o gênero dos atletas para filtrar (masculino, feminino ou ambos)
quantidade_graficos = int(input('\nDigite 1 para fazer um gráfico de apenas atletas masculinos\n' \
                                'Digite 2 para apenas femininos\n' \
                                'Digite 3 para fazer ambos os gráficos\n'))

# Loop para garantir entrada válida do usuário para o gênero
while True:
    if quantidade_graficos == 1:
        genero = 'Masculino'
        sexo_atletas = 'M'
        break
    elif quantidade_graficos == 2:
        genero = 'Feminino'
        sexo_atletas = 'F'
        break
    elif quantidade_graficos == 3:
        genero = 'de Ambos os Sexos'
        sexo_atletas = ''  # String vazia para não filtrar por sexo
        break
    else:
        print('Voce digitou um número fora do raio estabelecido. Por favor, tente novamente:')
        quantidade_graficos = int(input('\n\nDigite 1 para fazer um gráfico de apenas atletas masculinos\n' \
                                'Digite 2 para apenas femininos\n' \
                                'Digite 3 para fazer ambos os gráficos\n'))

# Monta o título do gráfico com base nas escolhas do usuário
titulo = f"Top 10 dos {escolha} com mais medalhas no {esporte_escolhido} {genero} na história das Olimpíadas"

# Aplica a função abreviadora na coluna escolhida (países ou atletas) e cria uma nova coluna com os nomes abreviados
df['pais_ou_nome_abreviado'] = df[escolha_usuario].apply(abreviador)

# Filtra o DataFrame para:
# - linhas onde o atleta ganhou medalha (não 'No medal')
# - o esporte contém o texto digitado (case insensitive)
# - o sexo do atleta corresponde ao filtro escolhido (ou todos se vazio)
tabela = df.loc[
    (df['Medal'] != 'No medal') & 
    (df['Sport'].str.contains(esporte_escolhido, flags=re.I)) & 
    (df['Sex'].str.contains(sexo_atletas))
]

# Cria uma tabela dinâmica (pivot table) contando a quantidade de medalhas por esporte e nome abreviado
filtro = pd.pivot_table(
    tabela,
    index=['Sport', 'pais_ou_nome_abreviado'],  # índice por esporte e nome abreviado
    columns='Medal',                            # colunas separadas por tipo de medalha
    aggfunc='size',                            # conta o número de ocorrências
    fill_value=0                               # preenche com zero onde não houver medalha daquele tipo
)

# Cria uma nova coluna 'Total' somando as medalhas Bronze, Silver e Gold
filtro['Total'] = filtro['Bronze'] + filtro['Silver'] + filtro['Gold']

# Ordena o DataFrame pelo total de medalhas, do maior para o menor
filtro_ordenado = filtro.sort_values('Total', ascending=False)

# Seleciona os 10 primeiros (top 10) com maior total de medalhas
top10 = filtro_ordenado.head(10)

# Obtém o total de medalhas para cada equipe no top 10
totals = top10['Total']

# Obtém o valor máximo de medalhas no top 10 para definir escala do gráfico
max_val = totals.max()

# Calcula o intervalo para os ticks do eixo y (arredondando para cima)
intervalo = math.ceil(max_val / 5)

# Arredonda o valor máximo para cima para o próximo múltiplo do intervalo
max_tick = (int(max_val / intervalo) + 1) * intervalo  

# Cria os ticks do eixo y de 0 até max_tick, com passo igual ao intervalo
ticks = np.arange(0, max_tick + 1, intervalo)

# Obtém os nomes abreviados do índice do DataFrame para usar no eixo x do gráfico
escolha_usuario_grafico = top10.index.get_level_values('pais_ou_nome_abreviado')   

# Cria a figura e o eixo do gráfico com tamanho personalizado
fig, ax = plt.subplots(figsize=(10,6))

# Plota o gráfico de barras com os nomes abreviados no eixo x e total de medalhas no eixo y
# Define zorder alto para que as barras fiquem na frente de outros elementos gráficos
bars = ax.bar(escolha_usuario_grafico, totals, zorder=3)

# Configura o título e os rótulos dos eixos no objeto ax
ax.set_title(titulo)
ax.set_xlabel('Países' if escolha_usuario == 'Team' else 'Atletas')
ax.set_ylabel('N. de medalhas')

# Define os ticks principais do eixo y com o intervalo calculado
ax.yaxis.set_major_locator(plt.MultipleLocator(intervalo))

# Define os ticks menores do eixo y com metade do intervalo (para barras menores na grade)
ax.yaxis.set_minor_locator(plt.MultipleLocator(max(intervalo / 2, 1)))

# Ativa a grade para os ticks principais (linhas maiores)
ax.grid(which='major', axis='y', linestyle='-', linewidth=1, color='black', zorder=0)

# Ativa a grade para os ticks menores (linhas menores e pontilhadas)
ax.grid(which='minor', axis='y', linestyle=':', linewidth=0.5, color='gray', alpha=0.7, zorder=0)

# Rotaciona os labels do eixo x para 45 graus e alinha à direita para melhor leitura
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

# Ajusta o limite máximo do eixo y para o valor calculado max_tick
ax.set_ylim(0, max_tick)

# Ajusta o layout para evitar cortes nos elementos do gráfico
plt.tight_layout()

# Salva o gráfico em arquivo PDF
plt.savefig('grafico.png')

# Exibe o gráfico na tela
plt.show()
