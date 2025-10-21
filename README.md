# Dashboard de Análise de Voo de Foguete

Este é um projeto de dashboard web interativo desenvolvido com Dash (Python) para a visualização e análise de dados de telemetria de voos de foguetes universitários.

A aplicação permite que o usuário faça o upload de um arquivo de dados (CSV) e visualiza instantaneamente gráficos sobre a aceleração, altitude, orientação (Pitch, Roll, Yaw) e trajetória do foguete.

## Funcionalidades

* **Upload de Arquivo:** Interface simples para arrastar e soltar (ou clicar) e enviar o arquivo de dados do voo.
* **Gráficos Interativos:** Visualização de múltiplos gráficos gerados com Plotly:
    * Aceleração vs. Tempo
    * Altitude vs. Tempo
    * Orientação (Pitch) vs. Tempo
    * Orientação (Roll) vs. Tempo
    * Orientação (Yaw) vs. Tempo
* **Trajetória de Voo:** Um mapa interativo (usando Scattermapbox) que plota a trajetória do foguete com base nas coordenadas de latitude e longitude.
* **Painel de Informações:** Exibição dos dados mais recentes de:
    * Pressão Atmosférica
    * Localização (Latitude e Longitude)
    * Orientação (Pitch, Roll, Yaw)
    * Status do Paraquedas
* **Cálculos Automáticos:** O script calcula automaticamente os ângulos de Pitch e Roll a partir dos dados brutos do giroscópio (gx, gy, gz).

## Como Usar

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado. Você precisará instalar as seguintes bibliotecas:

```bash
pip install dash pandas plotly numpy

## Formato dos Dados

Para que o dashboard funcione corretamente, o arquivo enviado deve ser um arquivo `.csv` (valores separados por vírgula).

O script foi programado para **ignorar a primeira linha** do arquivo (usando `skiprows=1`), tratando-a como um cabeçalho. Em seguida, ele atribui nomes específicos às colunas.

Portanto, seus dados **devem seguir exatamente** a seguinte ordem de colunas:

| Coluna | Nome Esperado | Exemplo | Descrição |
| :--- | :--- | :--- | :--- |
| 1 | `tempo` | `1` | Tempo de voo (preferencialmente em segundos) |
| 2 | `aceleracao` | `58.5` | Aceleração (ex: m/s²) |
| 3 | `altitude` | `20` | Altitude (ex: metros) |
| 4 | `pressao` | `101300` | Pressão atmosférica (ex: hPa) |
| 5 | `latitude` | `-23.36352921` | Coordenada de Latitude |
| 6 | `longitude` | `-48.01247025` | Coordenada de Longitude |
| 7 | `gx` | `0.1` | Dado do giroscópio (eixo X) |
| 8 | `gy` | `0.2` | Dado do giroscópio (eixo Y) |
| 9 | `gz` | `0.3` | Dado do giroscópio (eixo Z) |
| 10 | `paraquedas` | `FECHADO` | Status do paraquedas (texto) |

### Exemplo de Arquivo Válido

Seu arquivo deve se parecer com o exemplo abaixo. Note que a primeira linha (`tempo,aceleracao,...`) será ignorada pelo script, e os dados a partir da segunda linha serão lidos.
```csv
tempo,aceleracao,altitude,pressao,latitude,longitude,gx,gy,gz,paraquedas
0,0,0,101325,-23.36352921,-48.01247025,0,0,0,FECHADO
1,58.5,20,101300,-23.36352921,-48.01247025,0.1,0.2,0.3,FECHADO
2,45.0,90,101250,-23.36352921,-48.01247025,0.1,0.3,0.4,FECHADO
3,30.0,200,101150,-23.36352921,-48.01246643,0.2,0.4,0.5,FECHADO
4,15.0,350,101000,-23.36352921,-48.01246643,0.3,0.5,0.6,FECHADO
5,0.0,500,100850,-23.36352921,-48.01246643,0.2,0.4,0.5,FECHADO
6,-10.0,700,100700,-23.36352921,-48.01246643,-0.1,-0.2,-0.3,FECHADO
7,-20.0,897,100500,-23.36352921,-48.01246643,-0.2,-0.3,-0.4,FECHADO
8,-15.0,850,100550,-23.36195946,-48.01098251,-0.3,-0.4,-0.5,ABERTO
9,-10.0,700,100700,-23.36148262,-48.01065445,-0.4,-0.5,-0.6,ABERTO
