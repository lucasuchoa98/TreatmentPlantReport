## Alto da boa vista e Parque Maceió


#Importando as bibliotecas padrões
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os

#Importando as demais bibliotecas
import jinja2
import pdfkit
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


mes_dict = {1: 'Janeiro', 2: 'Fevereiro', 3:'Março', 
            4:'Abril', 5:'Maio', 6:'Junho', 
            7:'Julho', 8:'Agosto', 9:'Setembro', 
            10:'Outubro', 11:'Novembro', 12:'Dezembro'}


def filter_by_client(dataframe:pd.DataFrame, client:str) -> pd.DataFrame:
    """Fitra a tabela de atributos a partir de um cliente

    Args:
        dataframe (pd.DataFrame): Tabela de atributos
        client (str): Um dos clientes disponíveis

    Returns:
        pd.DataFrame: Tabela de atributos filtrada
    """  
    result = dataframe.loc[[client]].copy()
    
    #print('Tabela de atributos filtrado pelo cliente com sucesso!')     
    
    return result


def filter_by_date(dataframe:pd.DataFrame, ano_filtro:str, mes_filtro :str, data_filtro:str, interval:bool=False, retro_month=6) -> pd.DataFrame:
    """Fitra a tabela de atributos a partir de uma determinada data

    Args:
        dataframe (pd.DataFrame): Tabela de atributos
        date (str): Data a ser filtrada
        interval (bool, optional): Ativa a opção de filtro por intervalo de datas. Valor padrão é Falso.
        retro_month (int, optional): Número de meses retroativos caso a opção de intervalo esteja ativada. Valor padrão é 6.

    Returns:
        pd.DataFrame: Tabela de atributos filtrada
    """
    if interval==True:
        
        date_str = datetime.strptime(data_filtro, '%Y-%m-%d')
        new_date = date_str - relativedelta(months=retro_month)
        end_date = data_filtro
        start_date = new_date.strftime('%Y-%m-%d')
        
        mask = (dataframe['Data'] >= start_date) & (dataframe['Data'] <= end_date)
        result = dataframe.loc[mask]
        
    else:
        
        # Converter a coluna "Data" para o formato de data
        dataframe['Data'] = pd.to_datetime(dataframe['Data'])

        # Filtrar o DataFrame a partir de uma data específica
        #data_filtro = pd.to_datetime(data_filtro)
        result = dataframe[(dataframe['Data'].dt.month == int(mes_filtro)) & (dataframe['Data'].dt.year == int(ano_filtro))]
        print(result)
        #result = dataframe[dataframe['Data'].dt.strftime('%Y-%m') == date].copy()
    
    #print('Tabela de atributos filtrado pela data com sucesso!')
    
    return result


def filter_by_param(dataframe:pd.DataFrame, param:str) -> pd.DataFrame:
    """Filtra a tabela de atributos a partir de um parâmetro analítico

    Args:
        dataframe (pd.DataFrame): Tabela de atributos
        param (str): parâmetros analítico

    Returns:
        pd.DataFrame: Tabela de atributos filtrada
    """
    result = dataframe.loc[(dataframe['Parâmetro'])==param].copy()
    
    #print('Tabela de atributos filtrado pelo parâmetro com sucesso!')
    
    return result


def filter_by_ponto(dataframe:pd.DataFrame, ponto:str) -> pd.DataFrame:
    """Filtra a tabela de atributos a partir do ponto do parâmetro analítico: Entrada ou Saída

    Args:
        dataframe (pd.DataFrame): Tabela de atributos
        ponto (str): Ponto de parâmetro analítico: Entrada ou Saída

    Returns:
        pd.DataFrame: Tabela de atributos filtrada
    """
    result = dataframe.loc[(dataframe['Ponto'])==ponto].copy()

    #print('Tabela de atributos filtrado pelo ponto com sucesso!')
    
    return result


def plot_bar(parametro:str, cliente:str, dataframe:pd.DataFrame) -> str:
    """Fornece um HTML com uma gráfico de barras

    Args:
        parametro (str): Parâmetro analítico
        cliente (str): Um dos clientes disponíveis
        dataframe (pd.DataFrame): Tabela de atributos

    Returns:
        str: Representação da figura HTML como uma div string
    """
    titulo = f"Resultados de {parametro} da ETE {cliente}"
    fig = px.bar(dataframe, x="Data", y="Resultado", title=titulo, labels={"Resultado":parametro}, color='Ponto', barmode='group')
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0))
    graph = fig.to_html(full_html = False, include_plotlyjs ='cdn')
    
    return graph

def cap4_text(dataframe:pd.DataFrame, cliente:str) -> str:
    """Fornece um texto a partir da tabela de atributos filtrada pelo cliente e data

    Args:
        dataframe (pd.DataFrame): Tabela de atributos
        cliente (str): Um dos clintes disponíveis

    Returns:
        str: Texto do capítulo 4
    """
    lim_conama430 = {'ph':[5,9],'temperatura':40,'sólidos sedimentáveis':1, 'dbo':120,'óleos e graxas':100,'eficiência':60,}
    todos = True
    eficiencia_conc = 'Regular'
    alem_da_conama = False
    parametros_fora = ""
    df_copy = dataframe.copy()

    print('passei aqui')
    for parametro, resultado in zip(df_copy.Parâmetro, df_copy.Resultado):
        
        if parametro.lower() == 'ph':
            
            if resultado<lim_conama430['ph'][0] or resultado>lim_conama430['ph'][1]:
                
                todos = False
                parametros_fora = parametros_fora+", "+parametro
                break
            
        elif parametro.lower() == 'eficiência':
            
            if resultado<lim_conama430['eficiência']:
                
                todos, eficiencia_conc = False, 'Regular'
                parametros_fora = parametros_fora+", "+parametro
                
        else:
            
            if parametro not in lim_conama430.keys():
                
                alem_da_conama = True
                
            elif resultado>lim_conama430[parametro.lower()]:
                
                todos = False
                parametros_fora = parametros_fora+","+parametro           
         
    if todos == True:
        
        texto1 = f"Todos os parâmetros atenderam as especificações dispostas na Resolução do CONAMA nº 430/11. "
        
    else:
        
        texto1 = f'Os resultados de {parametros_fora} não atenderam as especificações dispostas na Resolução CONAMA n° 430/2011. '
    print('passei aqui2')
    ef_remo = filter_by_param(df_copy,param="Eficiência")
    print('passei aqui3')
    ef_remo = ef_remo['Resultado'].tolist()[0]
    print('passei aqui4')
    ef_remo_str = str(ef_remo).replace(".",",")
    print('passei aqui5')
    dbo = filter_by_param(df_copy, param="DBO")
    print('passei aqui6')
    dbo_saida = filter_by_ponto(dbo, ponto='Saída')
    print('passei aqui7')
    dbo_saida = dbo_saida['Resultado'].tolist()[0]
    print('passei aqui8')
    dbo_saida_str = str(dbo_saida)
    print('passei aqui9')
    dbo_entrada = filter_by_ponto(dbo, ponto='Entrada')
    print('passei aqui10')
    dbo_entrada = dbo_entrada['Resultado'].tolist()[0]
    print('passei aqui11')
    dbo_entrada_str = str(dbo_entrada)
    print('passei aqui12')     
    texto2 = f"A eficiência de remoção de matéria orgânica apresentada no processo foi de {ef_remo_str}%"
    print('passei aqui13')
    if ef_remo >=60:
        
        texto3= f", valor consideravelmente acima dos 60% de eficiência de remoção estabelecido pela resolução supracitada."
        texto4=""
        texto5=""
        
    else:
        
        texto3 = f". Observa-se que, apesar da eficiência de remoção de matéria orgânica estando abaixo de 60%, a concentração de DBO na saída da ETE ({dbo_saida_str} mg/L) foi inferior a concentração máxima especificada na resolução (120 mg/L)."
        texto4 = f"Observa-se também que a DBO de entrada na ETE foi {dbo_entrada_str } mg/L, valor que pode ser considerado baixo para um efluente sanitário de acordo com a literatura e parâmetros do projeto da ETE do {cliente}."
        texto5 = f"Dessa forma, considera-se que a eficiência de remoção da matéria orgânica na ETE está subestimada."
    
    result = texto1+texto2+texto3+texto4+texto5
    print(result)
    return result
    
def cap_5_text(dataframe:pd.DataFrame, cliente: str) -> str:
    """Fornece um texto a partir da tabela atributos filtrada por cliente e data

    Args:
        dataframe (pd.DataFrame): Tabela de atributos
        cliente (str): Um dos clientes disponíveis

    Returns:
        str: Texto do capítulo 5
    """
    df_copy = dataframe.copy()
    ef_remo = filter_by_param(df_copy,param="Eficiência")
    ef_remo = ef_remo['Resultado'].tolist()[0]
    
    if ef_remo<70:
        
        quali = 'regular'
        
    elif ef_remo>=70 and ef_remo<80:
        
        quali = 'boa'
        
    elif ef_remo>=80 and ef_remo<90:
        
        quali = 'ótima'
        
    else:
        
        quali='excelente'
    
    laboratorio = 'Análise Ambiental'
    
    if cliente=="Novo Jardim" or cliente=="Paradise Beach" or cliente=='Recanto das Lagoas':
        
        laboratorio = "Qualitex"
    
    text1 = f"Conforme o relatório de ensaios apresentado pelo laboratório da {laboratorio} "
    text2 = f"referente aos pontos de entrada e saída da ETE {cliente}, "
    text3 = f"a estação apresentou valores dentro dos limites determinados pela legislação ambiental vigente. " 
    text4 = f"Portanto, em decorrência do monitoramento e das manutenções realizadas, a eficiência do sistema foi considerada {quali}."
    
    return text1+text2+text3+text4

def get_date() -> str:
    """Fornece a data do dia em que o programa foi gerado

    Returns:
        str: Texto contendo a cidade e a data
    """
    today = date.today()
    mes = int(today.strftime("%m"))
    ano = today.strftime("%Y")
    
    return "Maceió, " + mes_dict[mes] + " de " + ano

def get_data_str(ano:str, mes:str) -> str:
    """Fornece um texto contendo a data de entrada

    Args:
        ano (str): Ano
        mes (str): Mês

    Returns:
        str: Texto no formato: Mês de ano
    """
    mes = int(mes)
    return f"{mes_dict[mes]} de {ano}" 
    
def render_html(df1:pd.DataFrame, df2:pd.DataFrame, cap2_text:str, cap4_text:str, cap5_text:str, cliente:str, data:str, ano:str, hoje:str):

    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_dir))
    template = env.get_or_select_template('template.html')
    filename = os.path.join(root, 'html', f'{cliente}.html')
    
    with open(filename,'w') as fh:
        fh.write(template.render(
            cliente=cliente,colunas1=df1.columns.to_list(), colunas2=['Razão Social:', 'CNPJ:', 'Endereço:'],
            data=data, ano=ano,df1 = df1.to_dict(orient='records'),
            df2 = df2.to_dict(orient='records'), cap2_text = cap2_text, cap4_text = cap4_text,
            cap5_text = cap5_text, hoje = hoje
        ))
        
    if cap4_text!="" and cap5_text!="":
        print(f"Gerando PDF {cliente} ... ")
        pdf_path = f'Relatório Mensal ({data}) - {cliente}.pdf'    
        html2pdf(filename, pdf_path)
        
    else:
        print(f"{cliente} com problemas nos textos do cap4 e cap5")
    

def html2pdf(html_path:str, pdf_path:str):
    """
    Convert html to pdf using pdfkit which is a wrapper of wkhtmltopdf
    """
    options = {
        'page-size': 'Letter', 'margin-top': '0.30in', 'margin-right': '0.75in',
        'margin-bottom': '0.5in', 'margin-left': '0.75in', 'encoding': "UTF-8",
        'footer-font-size':'6', 'footer-font-name':'cambria', 'footer-spacing':'6',
        'footer-center': 'ANALISE AMBIENTAL, SOLUÇÕES EM MEIO AMBIENTE\nRua R, nº 14, Quadra 9 Lote 14, Cidade Universitária, Maceió - AL\nCNPJ: 23.049.977/0001-07',
        'no-outline': None, 'enable-local-file-access': None
    }
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    
    with open(html_path) as f:

        pdfkit.from_file(f, pdf_path, configuration=config, options=options)
        
def main(filePath:str, sheet_name:str, original_df:pd.DataFrame, clientes_list:list, cliente:str, mode:int, ano:str, mes:str, data_relatorio:str):
    
    df_copy = original_df.set_index('Cliente').copy()
        
    try:
        iter_df_client_filtered = filter_by_client(df_copy, cliente).copy()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    try:
        iter_df = filter_by_date(iter_df_client_filtered, ano_filtro=ano, mes_filtro=mes, data_filtro=data_relatorio).copy()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    try:
        iter_df['Data'] = iter_df['Data'].dt.strftime('%d-%m-%Y')
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    try:
        iter_df['Resultado'] = iter_df['Resultado'].apply(lambda x: round(x,2) if isinstance(x,float) else x)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
        
    #iter_df_date_filtered = filter_by_date(iter_df_client_filtered, date=data_relatorio, interval=True)
    #plot_df = filter_by_param(iter_df_date_filtered, 'Eficiência')

    #df = filter_by_param(df,param=parametro)

    ### LEMBRAR DE VERIFICAR O FILEPATH
    filePath2 = r'G:\Meu Drive\_Lucas\Controle de Qualidade\Dados\dados_ete.xlsx'
    sheet_name2 = 'responsavel'
    df_responsavelETE = pd.read_excel(io=filePath2,sheet_name=sheet_name2)
    df_responsavelETE = df_responsavelETE.set_index('Cliente')
    
    try:
        
        df_responsavelETE = filter_by_client(df_responsavelETE, cliente)
        
    except:
        
        print(f"{cliente} sem responsavel")
    
    ### LEMBRAR DE VERIFICAR O FILEPATH
    filePath3 = r'G:\Meu Drive\_Lucas\Controle de Qualidade\Dados\dados_ete.xlsx'
    sheet_name3 = 'desc_ete_sheet'
    df_descETE = pd.read_excel(io=filePath3,sheet_name=sheet_name3)
    df_descETE = df_descETE.set_index('Cliente')
    
    try:
        
        df_descETE = filter_by_client(df_descETE, cliente)
        cap2_text = df_descETE.values[0][0]
        
    except:
        cap2_text = ""
        print(f"{cliente} sem descricao de ete")
    
    data_str = get_data_str(ano, mes)
    cap4_text_str = ""
    cap5_text_str = ""
    
    try:
        
        cap4_text_str = cap4_text(iter_df, cliente=cliente)
        
    except:
        
        print('Erro na obtencao do texto do capitulo 4')

    try:
        
        cap5_text_str = cap_5_text(iter_df, cliente=cliente)
        
    except:
        
        print('Erro na obtencao do texto do capitulo 5')
                        
    render_html(df1=iter_df, df2=df_responsavelETE, cap2_text=cap2_text, 
                cap4_text=cap4_text_str, cap5_text=cap5_text_str, cliente=cliente, 
                data=data_str, ano=ano, hoje=get_date())
    
if __name__ == "__main__":
  
    ### LEMBRAR DE VERIFICAR O FILEPATH
    filePath = r'G:\Meu Drive\_Lucas\Controle de Qualidade\Dados\Resultados ETE2.xlsx'
    sheet_name = 'Acompanhamento da ETE'
    original_df = pd.read_excel(io=filePath, sheet_name=sheet_name, header=1)
    clientes_list = original_df['Cliente'].unique()
    run_mode = [0,1,2]
    
    while True:
        
        print('Modos de operação:')
        print('0 - Sair')
        print('1 - Gerar relatórios para todos os clientes')
        print('2 - Gerar relatório para cliente Específico')
        resposta = int(input('Digite o modo de Operação: ') or "2")
        
        if resposta not in run_mode:
            
            print('A opção selecionada não esta na lista de modos disponíveis')
            
        else:

            if resposta==0:
                
                exit()
                                
            # Todos os clientes
            if resposta==1:
                
                msg_data_relatorio = 'Digite aqui o ano, mês e dia limite do(s) relatório(s) -> formato AAAA-MM: '
                data_relatorio = input(msg_data_relatorio) or "2023-03"
                ano, mes = data_relatorio.split("-")
                
                print(clientes_list)
                
                for cliente in clientes_list:
                    
                    main(filePath=filePath, sheet_name=sheet_name, 
                         original_df=original_df, clientes_list=clientes_list, 
                         data_relatorio=data_relatorio,mode=2, 
                         cliente=cliente, ano=ano, mes=mes)
                    print('-------------------------------\n-------------------------------')
            
            # Cliente específico
            if resposta==2:
                
                msg_data_relatorio = 'Digite aqui o ano, mês e dia limite do(s) relatório(s) -> formato AAAA-MM: '
                data_relatorio = input(msg_data_relatorio) or "2023-03"              
                ano, mes = data_relatorio.split("-")
                for i, cl in enumerate(clientes_list):
                    print(f'{i} - {cl}')

                #print(*clientes_list, sep='\n')
                cliente = input('Digite aqui o nome do um cliente: ') or "Alto da Boa Vista"
                
                main(filePath=filePath, sheet_name=sheet_name, 
                     original_df=original_df, clientes_list=clientes_list, 
                     mode=2, cliente=cliente, ano=ano, 
                     mes=mes, data_relatorio=data_relatorio)