import requests
from bs4 import BeautifulSoup

def obterTarifaResidencialVerde() -> dict:
    """
    Função para obter as tarifas de energia do site da CEMIG usando web scrapping
    Retorna um array com as tarifas por bandeira.
    """
    url = "https://www.cemig.com.br/atendimento/valores-de-tarifas-e-servicos/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sections = soup.find_all('section', class_='table')

    if len(sections) >= 7:
        seventh_section = sections[6]

        bandeira_verde_td = seventh_section.find('td')
        bandeira_verde_valor = bandeira_verde_td.find_next('td').text.strip() if bandeira_verde_td else None

        return float(bandeira_verde_valor.replace(",", "."))

def obter_tarifas_cemig(classe: str) -> dict:
    """
    Função para obter as tarifas de energia do site da CEMIG usando web scrapping
    Retorna um array com as tarifas por bandeira.
    """
    url = "https://www.cemig.com.br/atendimento/valores-de-tarifas-e-servicos/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')    

    tabela = soup.find('table', {'class': 'table'})

    tarifas = {}

    for row in tabela.find_all('tr')[1:]:
        cols = row.find_all('td')
        
        if len(cols) == 5:
            if classe == "Comercial":  
                tarifa_verde = obterTarifaResidencialVerde()
            else:
                tarifa_verde = float(cols[1].text.strip().replace(",", "."))
           
            tarifa_amarela = float(cols[2].text.strip().replace(",", "."))
            tarifa_vermelha1 = float(cols[3].text.strip().replace(",", "."))
            tarifa_vermelha2 = float(cols[4].text.strip().replace(",", "."))

            tarifas = {
                "VERDE": tarifa_verde,
                "AMARELA": tarifa_amarela,
                "VERMELHA 1": tarifa_vermelha1,
                "VERMELHA 2": tarifa_vermelha2
            }

    return tarifas

def calculadora(consumo: list, classe: str, bandeira: str) -> tuple:
    """
    Retorna uma tupla com economia anual, mensal, desconto aplicado e cobertura.
    A tarifa é obtida automaticamente através da função obter_tarifas_cemig().
    """
    tarifas = obter_tarifas_cemig(classe)
    
    if bandeira not in tarifas:
        raise ValueError(f"Bandeira tarifária inválida: {bandeira}")
    
    tarifa = tarifas[bandeira]
    
    consumo_medio = sum(consumo) / len(consumo)
    
    if consumo_medio < 10000:
        descontos = {"Residencial": 0.18, "Comercial": 0.16, "Industrial": 0.12}
        cobertura = 0.90
    elif 10000 <= consumo_medio <= 20000:
        descontos = {"Residencial": 0.22, "Comercial": 0.18, "Industrial": 0.15}
        cobertura = 0.95
    else:
        descontos = {"Residencial": 0.25, "Comercial": 0.22, "Industrial": 0.18}
        cobertura = 0.99

    if classe not in descontos:
        raise ValueError("Classe de tarifa inválida. Deve ser 'Residencial', 'Comercial' ou 'Industrial'.")

    desconto_aplicado = descontos[classe]

    economia_mensal = consumo_medio * tarifa * desconto_aplicado * cobertura
    economia_anual = economia_mensal * 12

    return (
        round(economia_anual, 2),
        round(economia_mensal, 2),
        round(desconto_aplicado, 2),
        round(cobertura, 2),
    )

if __name__ == "__main__":
    print("Testando...")
    
    assert calculadora([1518, 1071, 968], "Industrial", "VERMELHA 2") == (
        1349.86,
        112.49,
        0.12,
        0.90,
    ) 

    assert calculadora([1000, 1054, 1100], "Residencial", "VERMELHA 1") == (
        1725.61,
        143.8,
        0.18,
        0.90
    )

    assert calculadora([973, 629, 726], "Comercial", "AMARELA") == (
        1097.6,
        91.47,
        0.16,
        0.90
    )

    assert calculadora([15000, 14000, 16000], "Industrial", "VERMELHA 1") == (
        21656.81,
        1804.73,
        0.15,
        0.95
    )

    assert calculadora([12000, 11000, 11400], "Residencial", "VERDE") == (
        22997.8,
        1916.48,
        0.22,
        0.95
    )

    assert calculadora([17500, 16000, 16400], "Comercial", "AMARELA") == (
        27938.08,
        2328.17,
        0.18,
        0.95
    )

    assert calculadora([30000, 29000, 29500], "Industrial", "VERMELHA 1") == (
        53262.07,
        4438.51,
        0.18,
        0.99
    )

    assert calculadora([22000, 21000, 21400], "Residencial", "AMARELA") == (
        52186.84,
        4348.9,
        0.25,
        0.99
    )

    assert calculadora([25500, 23000, 21400], "Comercial", "VERDE") == (
        48697.35,
        4058.11,
        0.22,
        0.99
    )

    print("Todos os testes passaram!")
    