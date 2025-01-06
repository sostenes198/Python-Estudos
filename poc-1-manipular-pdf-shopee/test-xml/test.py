from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from io import BytesIO
import xml.etree.ElementTree as ET


# Função para extrair dados do XML
def parse_xml(xml_string):
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}  # Namespace
    root = ET.fromstring(xml_string)

    # Dados principais da NF-e
    emit = root.find(".//nfe:emit", ns)
    dest = root.find(".//nfe:dest", ns)
    prod = root.find(".//nfe:det/nfe:prod", ns)
    total = root.find(".//nfe:total/nfe:ICMSTot", ns)
    cobr = root.find(".//nfe:cobr/nfe:fat", ns)

    # Extraindo dados do XML
    data = {
        "emitente": {
            "nome": emit.find("nfe:xNome", ns).text,
            "cnpj": emit.find("nfe:CNPJ", ns).text,
            "endereco": emit.find("nfe:enderEmit/nfe:xLgr", ns).text,
            "bairro": emit.find("nfe:enderEmit/nfe:xBairro", ns).text,
            "cidade": emit.find("nfe:enderEmit/nfe:xMun", ns).text,
            "uf": emit.find("nfe:enderEmit/nfe:UF", ns).text,
        },
        "destinatario": {
            "nome": dest.find("nfe:xNome", ns).text,
            "cpf": dest.find("nfe:CPF", ns).text,
            "endereco": dest.find("nfe:enderDest/nfe:xLgr", ns).text,
            "bairro": dest.find("nfe:enderDest/nfe:xBairro", ns).text,
            "cidade": dest.find("nfe:enderDest/nfe:xMun", ns).text,
            "uf": dest.find("nfe:enderDest/nfe:UF", ns).text,
        },
        "produto": {
            "descricao": prod.find("nfe:xProd", ns).text,
            "valor_unitario": prod.find("nfe:vUnCom", ns).text,
            "quantidade": prod.find("nfe:qCom", ns).text,
            "valor_total": prod.find("nfe:vProd", ns).text,
        },
        "total": {
            "valor_total_nf": total.find("nfe:vNF", ns).text,
            "valor_desconto": total.find("nfe:vDesc", ns).text,
        },
        "fatura": {
            "numero": cobr.find("nfe:nFat", ns).text,
            "valor_original": cobr.find("nfe:vOrig", ns).text,
            "valor_liquido": cobr.find("nfe:vLiq", ns).text,
        }
    }
    return data


# Função para gerar o PDF
def generate_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 50, "Nota Fiscal Eletrônica (NF-e)")

    # Dados do Emitente
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 80, "Emitente:")
    c.drawString(50, height - 100, f"Nome: {data['emitente']['nome']}")
    c.drawString(50, height - 120, f"CNPJ: {data['emitente']['cnpj']}")
    c.drawString(50, height - 140, f"Endereço: {data['emitente']['endereco']}, {data['emitente']['bairro']}")
    c.drawString(50, height - 160, f"Cidade/UF: {data['emitente']['cidade']}/{data['emitente']['uf']}")

    # Dados do Destinatário
    c.drawString(30, height - 190, "Destinatário:")
    c.drawString(50, height - 210, f"Nome: {data['destinatario']['nome']}")
    c.drawString(50, height - 230, f"CPF: {data['destinatario']['cpf']}")
    c.drawString(50, height - 250, f"Endereço: {data['destinatario']['endereco']}, {data['destinatario']['bairro']}")
    c.drawString(50, height - 270, f"Cidade/UF: {data['destinatario']['cidade']}/{data['destinatario']['uf']}")

    # Dados do Produto
    c.drawString(30, height - 300, "Produto:")
    c.drawString(50, height - 320, f"Descrição: {data['produto']['descricao']}")
    c.drawString(50, height - 340, f"Quantidade: {data['produto']['quantidade']}")
    c.drawString(50, height - 360, f"Valor Unitário: R$ {data['produto']['valor_unitario']}")
    c.drawString(50, height - 380, f"Valor Total: R$ {data['produto']['valor_total']}")

    # Totais da NF
    c.drawString(30, height - 410, "Totais:")
    c.drawString(50, height - 430, f"Valor Total da NF: R$ {data['total']['valor_total_nf']}")
    c.drawString(50, height - 450, f"Desconto: R$ {data['total']['valor_desconto']}")

    # Dados da Fatura
    c.drawString(30, height - 480, "Fatura:")
    c.drawString(50, height - 500, f"Número: {data['fatura']['numero']}")
    c.drawString(50, height - 520, f"Valor Original: R$ {data['fatura']['valor_original']}")
    c.drawString(50, height - 540, f"Valor Líquido: R$ {data['fatura']['valor_liquido']}")

    # Gerando o Código de Barras
    c.drawString(30, height - 580, "Código de Barras:")
    barcode_value = f"NFe31241154085722000115550010000058306721969456"
    barcode = code128.Code128(barcode_value, barHeight=50, barWidth=1)
    barcode.drawOn(c, 50, height - 800)

    # Finalizar PDF
    c.showPage()
    c.save()
    buffer.seek(0)

    with open("nota_fiscal_com_codigo_de_barras.pdf", "wb") as f:
        f.write(buffer.getvalue())


# Carregar XML e gerar PDF
xml_string = """<?xml version="1.0" encoding="UTF-8"?><nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00"><NFe xmlns="http://www.portalfiscal.inf.br/nfe"><infNFe versao="4.00" Id="NFe31241154085722000115550010000058306721969456"><ide><cUF>31</cUF><cNF>72196945</cNF><natOp>venda de mercadoria a nao contribuinte</natOp><mod>55</mod><serie>1</serie><nNF>5830</nNF><dhEmi>2024-11-15T09:45:20-03:00</dhEmi><dhSaiEnt>2024-11-15T09:45:20-03:00</dhSaiEnt><tpNF>1</tpNF><idDest>1</idDest><cMunFG>3145208</cMunFG><tpImp>1</tpImp><tpEmis>6</tpEmis><cDV>6</cDV><tpAmb>1</tpAmb><finNFe>1</finNFe><indFinal>1</indFinal><indPres>0</indPres><procEmi>0</procEmi><verProc>Bling 1.0</verProc><dhCont>2024-11-15T09:45:06-03:00</dhCont><xJust>Sem comunicacao com a SEFAZ</xJust></ide><emit><CNPJ>54085722000115</CNPJ><xNome>Manoel Santos de Oliveira Junior</xNome><enderEmit><xLgr>Rua Geraldo Antonio de Lacerda</xLgr><nro>349</nro><xBairro>Cidade Nova I</xBairro><cMun>3145208</cMun><xMun>Nova Serrana</xMun><UF>MG</UF><CEP>35520572</CEP><cPais>1058</cPais><xPais>Brasil</xPais><fone>37999731624</fone></enderEmit><IE>0048320490073</IE><CRT>1</CRT></emit><dest><CPF>08448970608</CPF><xNome>Andreia Rocha</xNome><enderDest><xLgr>Rua Sustenido</xLgr><nro>92</nro><xCpl>Belo Horizonte</xCpl><xBairro>Santana do Cafezal</xBairro><cMun>3106200</cMun><xMun>Belo Horizonte</xMun><UF>MG</UF><CEP>30250170</CEP><cPais>1058</cPais><xPais>Brasil</xPais></enderDest><indIEDest>9</indIEDest></dest><det nItem="1"><prod><cProd>CFOP5102</cProd><cEAN>SEM GTIN</cEAN><xProd>Sandalia Chinelo Rasteirinha Feminina h Simples Dia a Dia Casual Barato nude,39</xProd><NCM>64029990</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1.0000</qCom><vUnCom>69.00</vUnCom><vProd>69.00</vProd><cEANTrib>SEM GTIN</cEANTrib><uTrib>UN</uTrib><qTrib>1.0000</qTrib><vUnTrib>69.00</vUnTrib><vDesc>38.33</vDesc><indTot>1</indTot><nItemPed>1</nItemPed></prod><imposto><vTotTrib>15.83</vTotTrib><ICMS><ICMSSN102><orig>0</orig><CSOSN>102</CSOSN></ICMSSN102></ICMS><PIS><PISAliq><CST>01</CST><vBC>69.00</vBC><pPIS>0.00</pPIS><vPIS>0.00</vPIS></PISAliq></PIS><COFINS><COFINSAliq><CST>01</CST><vBC>69.00</vBC><pCOFINS>0.00</pCOFINS><vCOFINS>0.00</vCOFINS></COFINSAliq></COFINS></imposto></det><total><ICMSTot><vBC>0.00</vBC><vICMS>0.00</vICMS><vICMSDeson>0.00</vICMSDeson><vFCP>0.00</vFCP><vBCST>0.00</vBCST><vST>0.00</vST><vFCPST>0.00</vFCPST><vFCPSTRet>0.00</vFCPSTRet><vProd>69.00</vProd><vFrete>0.00</vFrete><vSeg>0.00</vSeg><vDesc>38.33</vDesc><vII>0.00</vII><vIPI>0.00</vIPI><vIPIDevol>0.00</vIPIDevol><vPIS>0.00</vPIS><vCOFINS>0.00</vCOFINS><vOutro>0.00</vOutro><vNF>30.67</vNF><vTotTrib>15.83</vTotTrib></ICMSTot></total><transp><modFrete>1</modFrete><vol><pesoL>0.000</pesoL><pesoB>0.000</pesoB></vol></transp><cobr><fat><nFat>005830</nFat><vOrig>69.00</vOrig><vDesc>38.33</vDesc><vLiq>30.67</vLiq></fat><dup><nDup>001</nDup><dVenc>2024-12-15</dVenc><vDup>30.67</vDup></dup></cobr><pag><detPag><indPag>1</indPag><tPag>15</tPag><vPag>30.67</vPag></detPag></pag><infAdic><infCpl>DOCUMENTO EMITIDO POR ME OU EPP OPTANTE PELO SIMPLES NACIONAL. NAO GERA DIREITO A CREDITO DE ISS E IPI.&lt;br /&gt;Total aproximado de tributos: R$ 15,83 (51,61%)  Federais R$ 4,13 (13,45%)  Estaduais R$ 5,52 (18,00%) . Fonte IBPT.</infCpl></infAdic><infRespTec><CNPJ>01056417000139</CNPJ><xContato>Organisys Software SA</xContato><email>fiscal@bling.com.br</email><fone>05430579470</fone></infRespTec></infNFe><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/><Reference URI="#NFe31241154085722000115550010000058306721969456"><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/><Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/><DigestValue>5/uQdM0Aw1pC37D5MMFw2h6972o=</DigestValue></Reference></SignedInfo><SignatureValue>AIerB3l4HRDe8cU0Kkqs1hyhlxwTOmF75H2TygH1mjrPOuVPd5sXDgEWT3nlMyG7vvRbnxrNj1vL7rb20TJKrD+xjLBtt+PGEuGkwzkKVPYfmBFYVBd+aBY2QMIPWQLxpRy54QnvesfG+T1+LsUqaRWLV7SnyWZHYpvA9LZCM6g2SmuOD0+8PbS858sNxvEKPa96/icko8KEZ6H8xioM5M3KdjXlEC4BngU3xc1/yfDkjjs3iIdsrfXPnlmd6g38lJEbNsi2M0PtXPmBjvCb4k8vAinejBSpVZA/iPZkavGceNtn7K24BQ/Izf4mv0RZAvYilT5gJ/Bhet5fqmYgww==</SignatureValue><KeyInfo><X509Data><X509Certificate>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</X509Certificate></X509Data></KeyInfo></Signature></NFe><protNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00"><infProt Id="ID631240002255405"><tpAmb>1</tpAmb><verAplic>SVC_AN_5.1.7</verAplic><chNFe>31241154085722000115550010000058306721969456</chNFe><dhRecbto>2024-11-15T09:45:21-03:00</dhRecbto><nProt>631240002255405</nProt><digVal>5/uQdM0Aw1pC37D5MMFw2h6972o=</digVal><cStat>100</cStat><xMotivo>Autorizado o uso da NF-e</xMotivo></infProt></protNFe></nfeProc>"""  # Substitua pelo conteúdo do XML fornecido
dados = parse_xml(xml_string)
generate_pdf(dados)

print("PDF gerado com sucesso: nota_fiscal_com_codigo_de_barras.pdf")
