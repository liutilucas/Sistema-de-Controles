from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch

def gerar_pdf_holerite(file_path, dados_empresa, dados_funcionario, dados_holerite):
    doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    # Estilo para o cabeçalho das tabelas
    styles.add(ParagraphStyle(name='TableHeader', fontSize=9, fontName='Helvetica-Bold', alignment=TA_CENTER))
    # Estilo para o corpo da tabela
    styles.add(ParagraphStyle(name='TableBody', fontSize=9))
    styles.add(ParagraphStyle(name='TableBodyRight', fontSize=9, alignment=TA_RIGHT))


    story.append(Paragraph(dados_empresa['nome'], styles['h1']))
    story.append(Paragraph(f"CNPJ: {dados_empresa['cnpj']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"DEMONSTRATIVO DE PAGAMENTO - {dados_holerite['periodo']}", styles['h2']))
    story.append(Spacer(1, 0.2*inch))

    dados_func_table_data = [
        [Paragraph('<b>Funcionário(a):</b>', styles['Normal']), Paragraph(dados_funcionario['nome'], styles['Normal'])],
        [Paragraph('<b>Função:</b>', styles['Normal']), Paragraph(dados_funcionario['funcao'], styles['Normal'])],
    ]
    t_func = Table(dados_func_table_data, colWidths=[1.5*inch, None])
    t_func.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_func)
    story.append(Spacer(1, 0.2*inch))

    itens_data = [
        [Paragraph('Descrição', styles['TableHeader']),
         Paragraph('Proventos (R$)', styles['TableHeader']),
         Paragraph('Descontos (R$)', styles['TableHeader'])]
    ]
    
    proventos = [item for item in dados_holerite['itens'] if item[1] == 'Provento']
    descontos = [item for item in dados_holerite['itens'] if item[1] == 'Desconto']

    max_rows = max(len(proventos), len(descontos))
    for i in range(max_rows):
        desc_p, val_p = (proventos[i][0], f"{proventos[i][2]:,.2f}") if i < len(proventos) else ('', '')
        desc_d, val_d = (descontos[i][0], f"{descontos[i][2]:,.2f}") if i < len(descontos) else ('', '')

        linha_tabela = [
            Paragraph(desc_p if desc_p else desc_d, styles['TableBody']),
            Paragraph(val_p, styles['TableBodyRight']),
            Paragraph(val_d, styles['TableBodyRight']),
        ]

    for descricao, tipo, valor in proventos:
        itens_data.append([Paragraph(descricao, styles['TableBody']), Paragraph(f"{float(valor):,.2f}", styles['TableBodyRight']), ''])
    
    for descricao, tipo, valor in descontos:
        itens_data.append([Paragraph(descricao, styles['TableBody']), '', Paragraph(f"{float(valor):,.2f}", styles['TableBodyRight'])])


    t_itens = Table(itens_data, colWidths=[None, 1.5*inch, 1.5*inch])
    t_itens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_itens)
    story.append(Spacer(1, 0.1*inch))
    
    totais_data = [
        [Paragraph('<b>Total Proventos:</b>', styles['Normal']), Paragraph(f"R$ {dados_holerite['total_proventos']:,.2f}", styles['Right']),
         Paragraph('<b>Total Descontos:</b>', styles['Normal']), Paragraph(f"R$ {dados_holerite['total_descontos']:,.2f}", styles['Right']),
         Paragraph('<b>Valor Líquido:</b>', styles['Normal']), Paragraph(f"R$ {dados_holerite['salario_liquido']:,.2f}", styles['Right'])]
    ]
    
    t_totais = Table(totais_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    t_totais.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_totais)

    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return False
# Arquivo: utils/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch

def gerar_pdf_holerite(file_path, dados_empresa, dados_funcionario, dados_holerite):
    """
    Gera um arquivo PDF de holerite com os dados fornecidos.
    """
    doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    # --- Estilos Customizados ---
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='TableHeader', fontSize=10, fontName='Helvetica-Bold'))

    # --- 1. Cabeçalho da Empresa ---
    story.append(Paragraph(dados_empresa['nome'], styles['h1']))
    story.append(Paragraph(f"CNPJ: {dados_empresa['cnpj']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"DEMONSTRATIVO DE PAGAMENTO - {dados_holerite['periodo']}", styles['h2']))
    story.append(Spacer(1, 0.2*inch))

    # --- 2. Dados do Funcionário ---
    dados_func_table = [
        [Paragraph('<b>Funcionário(a):</b>', styles['Normal']), Paragraph(dados_funcionario['nome'], styles['Normal'])],
        [Paragraph('<b>Função:</b>', styles['Normal']), Paragraph(dados_funcionario['funcao'], styles['Normal'])],
    ]
    t_func = Table(dados_func_table, colWidths=[1.5*inch, None])
    t_func.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(t_func)
    story.append(Spacer(1, 0.2*inch))

    # --- 3. Itens do Holerite (Proventos e Descontos) ---
    itens_data = [
        [Paragraph('<b>Descrição</b>', styles['TableHeader']),
         Paragraph('<b>Proventos (R$)</b>', styles['TableHeader']),
         Paragraph('<b>Descontos (R$)</b>', styles['TableHeader'])]
    ]
    
    proventos = [item for item in dados_holerite['itens'] if item[1] == 'Provento']
    descontos = [item for item in dados_holerite['itens'] if item[1] == 'Desconto']

    # Adiciona linhas à tabela, balanceando proventos e descontos
    max_rows = max(len(proventos), len(descontos))
    for i in range(max_rows):
        desc_p, val_p = (proventos[i][0], f"{proventos[i][2]:,.2f}") if i < len(proventos) else ('', '')
        desc_d, val_d = (descontos[i][0], f"{descontos[i][2]:,.2f}") if i < len(descontos) else ('', '')
        
        # Cria uma subtabela para alinhar os valores de proventos e descontos à direita
        sub_table_data = [[Paragraph(desc_p, styles['Normal']), Paragraph(val_p, styles['Right'])],
                          [Paragraph(desc_d, styles['Normal']), Paragraph(val_d, styles['Right'])]]
        
        itens_data.append([
            sub_table_data[0][0],
            sub_table_data[0][1],
            ''  # Coluna de descontos vazia para a linha de proventos
        ])
        itens_data.append([
            sub_table_data[1][0],
            '', # Coluna de proventos vazia para a linha de descontos
            sub_table_data[1][1]
        ])


    # Cria a tabela principal de itens
    t_itens = Table(itens_data, colWidths=[None, 1.5*inch, 1.5*inch])
    t_itens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
    ]))
    story.append(t_itens)
    story.append(Spacer(1, 0.1*inch))
    
    # --- 4. Totais ---
    totais_data = [
        ['Total Proventos:', f"R$ {dados_holerite['total_proventos']:,.2f}", 
         'Total Descontos:', f"R$ {dados_holerite['total_descontos']:,.2f}",
         'Valor Líquido:', f"R$ {dados_holerite['salario_liquido']:,.2f}"]
    ]
    
    t_totais = Table(totais_data, colWidths=[None, 1.2*inch, None, 1.2*inch, None, 1.2*inch])
    t_totais.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('ALIGN', (3,0), (3,0), 'RIGHT'),
        ('ALIGN', (5,0), (5,0), 'RIGHT'),
    ]))
    story.append(t_totais)

    # --- Constrói o PDF ---
    doc.build(story)