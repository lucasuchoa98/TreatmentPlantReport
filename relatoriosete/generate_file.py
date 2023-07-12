from fpdf import FPDF

import datetime

def plot_table(dataframe):
    df_copy = dataframe.copy()
    table_fig = go.Figure(data=[go.Table(
        header=dict(values=list(df_copy.columns),
                    fill_color='paleturquoise',
                    line_color='darkslategray',
                    align='left'),
        cells=dict(values=[df_copy.Ponto, df_copy.Parâmetro, df_copy.Unidade,  df_copy.Data, df_copy.Resultado],
                line_color='darkslategray',
                fill_color='white',
                align='left'))
    ])

    table_fig.update_layout(
        margin=dict(l=10,r=10,b=10,t=10)
        )   
    table_fig.write_image('table.png', engine="kaleido", width=700, height=330)

    """
    plotly.io.write_image(fig,file='pltx.png', format='png', width=700, height=450)
    pltx=(os.getcwd()+'/'+"pltx.png")

    """

cliente = "Alma Viva"
data = "Dezembro de 2022"

title = f'Relatório Mensal de Operação da ETE do {cliente} - {data}'

result_text = r'Todos os parâmetros atenderam as especificações dispostas na Resolução do CONAMA nº 430/11. A eficiência na remoção de DBO da estação de tratamento foi de 85,60%, valor consideravelmente acima do limite mínimo de 60,00 estabelecido pela resolução supracitada.'
conclusion_text = r'Conforme o relatório de ensaios apresentado pelo laboratório da Análise Ambiental, referente aos pontos de entrada e saída da ETE do Residencial Jardins, a estação apresentou valores dentro dos limites determinados pela legislação ambiental vigente. Portanto, em decorrência do monitoramento e das manutenções realizadas, a eficiência do sistema foi considerada ótima.'

data_atual = str(datetime.date.today())

class PDF(FPDF):
    """    
    def chapter_title(self, num, label):
        # Times 12
        self.set_font('Times', '', 12)
        # Background color
        self.set_fill_color(255, 255, 255)
        # Title
        self.cell(0, 6, '%d - %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)
    """
    def header(self):
        # Times bold 15
        self.set_font('Times', 'B', 11)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(255,255,255)
        self.set_fill_color(255,255,255)
        self.set_text_color(0, 0, 0)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Times italic 8
        self.set_font('Times', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_body(self, name, num, label):
        
        # Times 12
        self.set_font('Times', '', 12)
        # Background color
        self.set_fill_color(255, 255, 255)
        # Title
        self.cell(0, 6, '%d - %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)
        if num==1:
            
            # Read text file
            with open(name, 'r', encoding='utf-8') as fh:
                txt = fh.read()
            # Times 12
            self.set_font('Times', '', 12)
            # Output justified text
            self.multi_cell(0, 5, txt)
            # Line break
            self.ln()
        if num==2:
            self.set_font('Times', '', 12)
            self.cell(0, 5, 'Monitoramento diário')
            self.ln()
            self.set_font('Times', '', 12)
            self.cell(0, 5, 'Limpeza Geral da ETE')
            self.ln()
            self.set_font('Times', '', 12)
            self.cell(0, 5, 'Coleta para análises')
            self.ln()
        if num==3:
            self.set_font('Times','', 12)
            # Output justified text
            texto = f"Os resultados analíticos obtidos em ensaios realizados nas amostras coletadas no mês de {data} encontram-se na Tabela 1."
            self.multi_cell(0, 5, texto)
            self.ln()
            
            self.set_font("Times","",12)
            self.cell(0,0,"Tabela 1 - Resultados das análises",0,0,"C")
            self.ln(5)
            
            self.image('table.png', h=90)
            self.ln()
            self.set_font('Times', '', 12)
            self.multi_cell(0, 5, result_text)
        if num==4:
            self.set_font('Times','', 12)
            # Output justified text
            self.multi_cell(0, 5, conclusion_text)
            self.ln()

            self.set_font("Times","",12)
            self.cell(80,5,align="r",txt=f"Maceió/AL, {data_atual}")
            self.ln()  

    def print_chapter(self, name, num, label):
        #self.add_page()
        #self.chapter_title(num, title)
        if num==1:
            self.add_page()
            
        self.chapter_body(name, num, label)

pdf = PDF()
pdf.set_title(title)
pdf.set_author('Jules Verne')
pdf.print_chapter(num=1, label='ESTAÇÃO DE TRATAMENTO', name='JARDINS_1.txt')
pdf.print_chapter(num=2, label='ATIVIDADES REALIZADAS', name='20k_c2.txt')
pdf.print_chapter(num=3, label='RESULTADOS DAS ANÁLISES', name='20k_c2.txt')
pdf.print_chapter(num=4, label='CONCLUSÃO', name='20k_c2.txt')
pdf.output('tuto3.pdf', 'F')
