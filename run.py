import jinja2
import pdfkit
import pandas as pd
from datetime import date
import os

import matplotlib.pyplot as plt
#import os
#import plotly
import plotly.express as px
import plotly.graph_objects as go


mes_dict = {
    1: 'Janeiro', 
    2: 'Fevereiro', 
    3:'Março', 
    4:'Abril', 
    5:'Maio', 
    6:'Junho', 
    7:'Julho', 
    8:'Agosto', 
    9:'Setembro', 
    10:'Outubro', 
    11:'Novembro',
    12:'Dezembro'
}

def filter_by_client(dataframe:pd.DataFrame, client:str):
    print(f"-------------------------------------------------------{client}-----------------------------------------------------")
    result = dataframe.loc[[client]].copy()
    print(result)
    return result

def filter_by_date(dataframe:pd.DataFrame,date:str):
    """
    Date format: 'AAAA-MM'
    """
    result = dataframe[dataframe['Data'].dt.strftime('%Y-%m') == date].copy()
    return result

def filter_by_param(dataframe:pd.DataFrame, param:str):
    """
    Eficiência, DBO, DBO, 
    Sólidos sedimentáveis, ph, Turbidez, 
    Temperatura, Cloro Residual Livre, 
    Coliformes termotolerantes, etc.
    """
    result = dataframe.loc[(dataframe['Parâmetro'])==param].copy()
    return result

def filter_by_ponto(dataframe:pd.DataFrame, ponto:str):
    """
    Pontos: Entrada, Saída
    """
    result = dataframe.loc[(dataframe['Ponto'])==ponto].copy()
    return result


def plot_bar(parametro:str, cliente:str, dataframe:pd.DataFrame):
    #ax = df.plot.barh(x="Data",y="Resultado", rot=0)
    #fig = ax.get_figure()
    #fig.savefig('C:/RelatoriosETE/figura.png')

    titulo = f"Resultados de {parametro} da ETE {cliente}"

    fig = px.bar(dataframe,x="Data", y="Resultado", 
                title=titulo, labels={"Resultado":parametro},
                color='Ponto', barmode='group')

    #fig.update_traces(textposition='outside')

    fig.update_layout(
        margin=dict(l=0,r=0,b=0,t=0)
        )

    fig.write_image("figura.png", engine="kaleido")


    
def cap4_text(dataframe:pd.DataFrame, cliente:str) -> str:
    """
    Recebe o df filtrado por cliente e data -> retorna uma string
    """
    df_copy = dataframe.copy()
    lim_conama430 = {
        'ph':[5,9],
        'temperatura':40,
        'sólidos sedimentáveis':1,
        'dbo':120,
        'óleos e graxas':100,
        'eficiência':0.60
    }
    todos = True
    eficiencia_conc = 'Regular'
    alem_da_conama = False
    parametros_fora = ""
    print("Cheguei aqui antes do zip!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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
    print("Cheguei aqui depois do zip!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")           
    if todos == True:
        texto1 = f"Todos os parâmetros atenderam as especificações dispostas na Resolução do CONAMA nº 430/11. "
    else:
        texto1 = f'Os resultados de {parametros_fora} não atenderam as especificações dispostas na Resolução CONAMA n° 430/2011. '
    
    
    ef_remo = filter_by_param(df_copy,param="Eficiência")
    ef_remo = ef_remo['Resultado'].tolist()[0]*100
    ef_remo_str = str(ef_remo).replace(".",",")
    
    dbo = filter_by_param(df_copy, param="DBO")
    dbo_saida = filter_by_ponto(dbo, ponto='Saída')
    dbo_saida = dbo_saida['Resultado'].tolist()[0]
    dbo_saida_str = str(dbo_saida)
    
    dbo_entrada = filter_by_ponto(dbo, ponto='Entrada')
    dbo_entrada = dbo_entrada['Resultado'].tolist()[0]
    dbo_entrada_str = str(dbo_entrada)
        
    texto2 = f"A eficiência de remoção de matéria orgânica apresentada no processo foi de {ef_remo_str}%"
    
    if ef_remo >=60:
        texto3= f", valor consideravelmente acima dos 60% de eficiência de remoção estabelecido pela resolução supracitada."
        texto4=""
        texto5=""
    else:
        texto3 = f". Observa-se que, apesar da eficiência de remoção de matéria orgânica estando abaixo de 60%, a concentração de DBO na saída da ETE ({dbo_saida_str} mg/L) foi inferior a concentração máxima especificada na resolução (120 mg/L)."
        texto4 = f"Observa-se também que a DBO de entrada na ETE foi {dbo_entrada_str } mg/L, valor que pode ser considerado baixo para um efluente sanitário de acordo com a literatura e parâmetros do projeto da ETE do {cliente}."
        texto5 = f"Dessa forma, considera-se que a eficiência de remoção da matéria orgânica na ETE está subestimada."
    
    return texto1+texto2+texto3+texto4+texto5
    
def cap_5_text(dataframe, cliente):
    
    df_copy = dataframe.copy()
    
    ef_remo = filter_by_param(df_copy,param="Eficiência")
    ef_remo = ef_remo['Resultado'].tolist()[0]*100
    
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

def get_date(): 
    "Get today's date in German format"
    today = date.today()
    mes = int(today.strftime("%m"))
    ano = today.strftime("%Y")
    return "Maceió, " + mes_dict[mes] + " de " + ano

def get_data_str(ano:str, mes:str) -> str:
    mes = int(mes)
    return f"{mes_dict[mes]} de {ano}" 
    
def render_html(df1,df2, cap2_text, cap4_text, cap5_text, cliente, data, ano, hoje):
    """
    df1 -> Resultados da ETE
    df2 -> Responsavel pela ETE
    cap2_text -> Descricao da ETE
    """
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_dir))
    template = env.get_or_select_template('template.html')
    
    filename = os.path.join(root, 'html', f'{cliente}.html')
    #print(df.columns.to_list())
    #print(df.to_dict(orient='records'))
    with open(filename,'w') as fh:
        fh.write(template.render(
            cliente=cliente,
            colunas1=df1.columns.to_list(),
            colunas2=['Razão Social:', 'CNPJ:', 'Endereço:'],
            data=data,
            ano=ano,
            df1 = df1.to_dict(orient='records'),
            df2 = df2.to_dict(orient='records'),
            cap2_text = cap2_text,
            cap4_text = cap4_text,
            cap5_text = cap5_text,
            hoje = hoje,
        ))
    print(f"Gerando PDF {cliente} ... ")
    pdf_path = f'{cliente}.pdf'    
    html2pdf(filename, pdf_path)
    

def html2pdf(html_path, pdf_path):
    """
    Convert html to pdf using pdfkit which is a wrapper of wkhtmltopdf
    """     
    options = {
        'page-size': 'Letter',
        'margin-top': '0.35in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
 
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    with open(html_path) as f:
        #pdfkit.from_file(f, pdf_path, options=options)
        pdfkit.from_file(f, pdf_path, configuration=config, options=options)
    
if __name__ == "__main__":

    #cliente="Alma Viva"
    #parametro = "DBO"
    
    ###carregar os dados das ETE para fazer a tabela
    filePath = r'H:\Meu Drive\_Lucas\Controle de Qualidade\Dados\Resultados ETE2.xlsx'
    sheet_name = 'Acompanhamento da ETE'
    original_df = pd.read_excel(io=filePath, sheet_name=sheet_name, header=1)
    clientes_list = original_df['Cliente'].unique()
    df_copy = original_df.set_index('Cliente').copy()
    
    run_mode = {
        1:'Sim',
        2:'Não'
    }
    print(run_mode.keys())
    
    while True:
        print('Modos de operação: \n 1 - Gerar relatórios para todos os clientes\n 2 - Gerar relatório para cliente Específico')
        resposta = int(input('Digite o modo de Operação: '))
        
        if resposta not in run_mode.keys():
            print('A opção selecionada não esta na lista de modos disponíveis')
        else:
            if run_mode[resposta]=='Não':
                print(clientes_list)
                cliente = input('Digite aqui o nome do um cliente: ')
                #data_relatorio = '2022-12'
                data_relatorio = input('Digite aqui o ano e o mês do(s) relatório(s) -> formato AAAA-MM: ') or '2023-05'         
                ano, mes = data_relatorio.split("-")
                try:
                    iter_df = filter_by_client(df_copy, cliente).copy()
                    iter_df = filter_by_date(iter_df, date=data_relatorio)
                    iter_df['Data'] = iter_df['Data'].dt.strftime('%d-%m-%Y')
                    iter_df['Resultado'] = iter_df['Resultado'].apply(lambda x: round(x,2) if isinstance(x,float) else x)
                    print(iter_df)
                except:
                    print(cliente, ' não tem dado')

                #df = filter_by_param(df,param=parametro)
                
                ### Carregar os dados dos responsaveis pelas ETE
                filePath2 = r'H:\Meu Drive\_Lucas\Controle de Qualidade\Dados\dados_ete.xlsx'
                sheet_name2 = 'responsavel'
                df_responsavelETE = pd.read_excel(io=filePath2,sheet_name=sheet_name2)
                df_responsavelETE = df_responsavelETE.set_index('Cliente')
                try:
                    df_responsavelETE = filter_by_client(df_responsavelETE, cliente)
                except:
                    print(f"{cliente} sem responsavel")
                
                ### Carregar os dados da descricao das ETE
                filePath3 = r'H:\Meu Drive\_Lucas\Controle de Qualidade\Dados\dados_ete.xlsx'
                sheet_name3 = 'desc_ete_sheet'
                df_descETE = pd.read_excel(io=filePath3,sheet_name=sheet_name3)
                df_descETE = df_descETE.set_index('Cliente')
                try:
                    df_descETE = filter_by_client(df_descETE, cliente)
                    cap2_text = df_descETE.values[0][0]
                except:
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
                
                    
                render_html(df1=iter_df, 
                            df2=df_responsavelETE, 
                            cap2_text=cap2_text, 
                            cap4_text=cap4_text_str, 
                            cap5_text=cap5_text_str, 
                            cliente=cliente, 
                            data=data_str, 
                            ano=ano, 
                            hoje=get_date()
                            )


            else:
                data_relatorio = input('Digite aqui o ano e o mês do(s) relatório(s) -> formato AAAA-MM: ')
                ano, mes = data_relatorio.split("-")
                for cliente in clientes_list:
                    try:
                        iter_df = filter_by_client(df_copy, cliente).copy()
                        iter_df = filter_by_date(iter_df, date=data_relatorio)
                        iter_df['Data'] = iter_df['Data'].dt.strftime('%d-%m-%Y')
                        iter_df['Resultado'] = iter_df['Resultado'].apply(lambda x: round(x,2) if isinstance(x,float) else x) 
                    except:
                        print(cliente, ' não tem dado')
                        break

                    #df = filter_by_param(df,param=parametro)
                    
                    ### Carregar os dados dos responsaveis pelas ETE
                    filePath2 = r'H:\Meu Drive\_Lucas\Controle de Qualidade\Dados\dados_ete.xlsx'
                    sheet_name2 = 'responsavel'
                    df_responsavelETE = pd.read_excel(io=filePath2,sheet_name=sheet_name2)
                    df_responsavelETE = df_responsavelETE.set_index('Cliente')
                    try:
                        df_responsavelETE = filter_by_client(df_responsavelETE, cliente)
                    except:
                        print(f"{cliente} sem responsavel")
                    
                    ### Carregar os dados da descricao das ETE
                    filePath3 = r'H:\Meu Drive\_Lucas\Controle de Qualidade\Dados\dados_ete.xlsx'
                    sheet_name3 = 'desc_ete_sheet'
                    df_descETE = pd.read_excel(io=filePath3,sheet_name=sheet_name3)
                    df_descETE = df_descETE.set_index('Cliente')
                    try:
                        df_descETE = filter_by_client(df_descETE, cliente)
                        cap2_text = df_descETE.values[0][0]
                    except:
                        print(f"{cliente} sem descricao de ete")
                    
                    
                    data_str = get_data_str(ano, mes)
                    cap4_text_str = ""
                    cap5_text_str = ""
                    
                    try:
                        cap4_text_str = cap4_text(iter_df, cliente=cliente)
                    except:
                        print('Erro na obtencao do texto do capitulo 4, verifique se existem dados no ano/mes digitado')

                    try:
                        cap5_text_str = cap_5_text(iter_df, cliente=cliente)
                    except:
                        print('Erro na obtencao do texto do capitulo 5, verifique se existem dados no ano/mes digitado')
                    
                        
                    render_html(df1=iter_df, 
                                df2=df_responsavelETE, 
                                cap2_text=cap2_text, 
                                cap4_text=cap4_text_str, 
                                cap5_text=cap5_text_str, 
                                cliente=cliente, 
                                data=data_str, 
                                ano=ano, 
                                hoje=get_date()
                                )
            
            