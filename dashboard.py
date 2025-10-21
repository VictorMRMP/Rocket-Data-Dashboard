import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import numpy as np

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard do Foguete"),
    dcc.Upload(
        id="upload-data",
        children=html.Div(["Arraste e solte ou clique para fazer upload do arquivo"]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        },
        multiple=False
    ),
    html.Div(id="output-data-upload", style={"display": "flex", "flexDirection": "column"}),
])

# Função para calcular os ângulos de Pitch, Roll e Yaw
def calculate_orientation(data):
    """
    Calcula os ângulos de Pitch, Roll e Yaw a partir dos dados do giroscópio (gx, gy, gz).
    """
    data["gx"] = pd.to_numeric(data["gx"], errors="coerce")
    data["gy"] = pd.to_numeric(data["gy"], errors="coerce")
    data["gz"] = pd.to_numeric(data["gz"], errors="coerce")

    data["pitch"] = np.arctan2(data["gy"], np.sqrt(data["gx"]**2 + data["gz"]**2)) * (180 / np.pi)
    data["roll"] = np.arctan2(-data["gx"], data["gz"]) * (180 / np.pi)
    
    data["yaw"] = np.cumsum(data["gz"])  # Aproximação simples para o yaw
    return data

# Função para processar o arquivo e extrair dados
def parse_contents(contents):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    data = pd.read_csv(
        io.StringIO(decoded.decode("utf-8")),
        skiprows=1,
        names=["tempo", "aceleracao", "altitude", "pressao", "latitude", "longitude", "gx", "gy", "gz", "paraquedas"]
    )
    
    # Verificar se o DataFrame não está vazio
    if data.empty:
        return "Erro: O arquivo está vazio ou não contém dados válidos."
    
    # Verificar se as colunas esperadas existem
    expected_columns = ["tempo", "aceleracao", "altitude", "pressao", "latitude", "longitude", "gx", "gy", "gz", "paraquedas"]
    missing_columns = [col for col in expected_columns if col not in data.columns]
    if missing_columns:
        return f"Erro: Colunas faltando: {', '.join(missing_columns)}"
    
    # Exibir as primeiras linhas para depuração
    print(data.head())  # Depuração
    
    # Limpeza de valores não numéricos
    data["aceleracao"] = pd.to_numeric(data["aceleracao"], errors="coerce")
    data["altitude"] = pd.to_numeric(data["altitude"], errors="coerce")
    data["pressao"] = pd.to_numeric(data["pressao"], errors="coerce")
    data["latitude"] = pd.to_numeric(data["latitude"], errors="coerce")
    data["longitude"] = pd.to_numeric(data["longitude"], errors="coerce")
    
    # Limpeza de valores não numéricos nos dados de giroscópio
    data["gx"] = pd.to_numeric(data["gx"], errors="coerce")
    data["gy"] = pd.to_numeric(data["gy"], errors="coerce")
    data["gz"] = pd.to_numeric(data["gz"], errors="coerce")
    
    # Garantir que não haja valores nulos
    data = data.dropna()
    
    # Verificar novamente se o DataFrame está vazio após a limpeza
    if data.empty:
        return "Erro: O arquivo contém apenas valores nulos após a limpeza."
    
    data = calculate_orientation(data)  # Calcula a orientação (Pitch, Roll, Yaw)
    
    return data

# Callback para atualizar os gráficos e informações
@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
)
def update_dashboard(contents):
    if contents is None:
        return "Por favor, envie um arquivo para visualizar os dados."
    
    # Processa os dados do arquivo
    data = parse_contents(contents)
    
    # Se houve erro ao processar, exibe a mensagem de erro
    if isinstance(data, str) and data.startswith("Erro"):
        return data
    
    # Gráfico de Aceleração
    fig_aceleracao = go.Figure()
    fig_aceleracao.add_trace(go.Scatter(x=data["tempo"], y=data["aceleracao"], mode="lines+markers", name="Aceleração"))
    fig_aceleracao.update_layout(title="Aceleração Temporal", xaxis_title="Tempo (s)", yaxis_title="Aceleração (m/s²)")

    # Gráfico de Altitude
    fig_altitude = go.Figure()
    fig_altitude.add_trace(go.Scatter(x=data["tempo"], y=data["altitude"], mode="lines+markers", name="Altitude"))
    fig_altitude.update_layout(title="Altitude Temporal", xaxis_title="Tempo (s)", yaxis_title="Altitude (m)")

    # Gráfico de Orientação (Pitch, Roll, Yaw)
    fig_pitch = go.Figure()
    fig_pitch.add_trace(go.Scatter(x=data["tempo"], y=data["pitch"], mode="lines+markers", name="Pitch"))
    fig_pitch.update_layout(title="Inclinação (Pitch)", xaxis_title="Tempo (s)", yaxis_title="Ângulo (graus)")

    fig_roll = go.Figure()
    fig_roll.add_trace(go.Scatter(x=data["tempo"], y=data["roll"], mode="lines+markers", name="Roll"))
    fig_roll.update_layout(title="Rolagem (Roll)", xaxis_title="Tempo (s)", yaxis_title="Ângulo (graus)")

    fig_yaw = go.Figure()
    fig_yaw.add_trace(go.Scatter(x=data["tempo"], y=data["yaw"], mode="lines+markers", name="Yaw"))
    fig_yaw.update_layout(title="Guinada (Yaw)", xaxis_title="Tempo (s)", yaxis_title="Ângulo (graus)")

    # Mapa Interativo
    fig_mapa = go.Figure(go.Scattermapbox(
        lat=data["latitude"],
        lon=data["longitude"],
        mode="markers+lines",
        marker=dict(size=10, color="red"),
        text=data["tempo"],
    ))
    fig_mapa.update_layout(
        title="Trajetória no Mapa",
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=data["latitude"].iloc[0], lon=data["longitude"].iloc[0]),
            zoom=12
        )
    )

    # Informações Textuais
    informacoes = [
        html.H4("Informações Atualizadas:"),
        html.P(f"Pressão Atmosférica Atual: {data['pressao'].iloc[-1]} hPa"),
        html.P(f"Localização Atual: Latitude {data['latitude'].iloc[-1]}, Longitude {data['longitude'].iloc[-1]}"),
        html.P(f"Orientação Atual: Pitch {data['pitch'].iloc[-1]}°, Roll {data['roll'].iloc[-1]}°, Yaw {data['yaw'].iloc[-1]}°"),
        html.P(f"Status do Paraquedas: {data['paraquedas'].iloc[-1]}")
    ]

    # Layout Final
    return html.Div([
        html.Div([
            dcc.Graph(figure=fig_aceleracao, style={"width": "33%", "display": "inline-block"}),
            dcc.Graph(figure=fig_altitude, style={"width": "33%", "display": "inline-block"}),
            dcc.Graph(figure=fig_pitch, style={"width": "33%", "display": "inline-block"}),
        ], style={"display": "flex", "justifyContent": "space-around"}),
        
        html.Div([
            dcc.Graph(figure=fig_roll, style={"width": "33%", "display": "inline-block"}),
            dcc.Graph(figure=fig_yaw, style={"width": "33%", "display": "inline-block"}),
            dcc.Graph(figure=fig_mapa, style={"width": "33%", "display": "inline-block"}),
        ], style={"display": "flex", "justifyContent": "space-around"}),
        
        html.Div(informacoes)
    ])

if __name__ == "__main__":
    app.run(debug=True)
