import dash
from dash import dcc, html, Input, Output
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
# Загрузка данных
df = pd.read_csv('data.csv')

# Инициализация приложения
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Для развертывания

# Макет дашборда
app.layout = dbc.Container([
    html.H1("Дашборд по анализу заявок на кредитование", className="text-center my-4"),
    html.P("Интерактивный инструмент для анализа эффективности обработки заявок на кредитование.", className="lead text-center"),

    dbc.Row([
        dbc.Col([
            html.Label("Выберите период анализа"),
            dcc.Dropdown(
                id='dropdown-period',
                options=[
                    {'label': 'По дням', 'value': 'D'},
                    {'label': 'По неделям', 'value': 'W'},
                    {'label': 'По месяцам', 'value': 'ME'}
                ],
                value='ME'
            )
        ], width=4),
        dbc.Col([
            html.Label("Фильтр по типу кредита"),
            dcc.Dropdown(
                id='dropdown-type',
                options=[{'label': t, 'value': t} for t in df['ТипКредита'].unique()],
                value=df['ТипКредита'].unique().tolist(),
                multi=True
            )
        ], width=8)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='approved-vs-rejected'), width=6),
        dbc.Col(dcc.Graph(id='avg-loan-by-type'), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='processing-time-histogram'), width=6),
        dbc.Col(dcc.Graph(id='scatter-rating-vs-income'), width=6)
    ]),

    dbc.Row([
        dbc.Col(html.Div(id='indicators'), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.H4("Таблица заявок"),
            dash_table.DataTable(
                id='datatable',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                page_size=10
            )
        ])
    ])

], fluid=True)

# --- Callbacks ---
@app.callback(
    [Output('approved-vs-rejected', 'figure'),
     Output('avg-loan-by-type', 'figure'),
     Output('processing-time-histogram', 'figure'),
     Output('scatter-rating-vs-income', 'figure'),
     Output('datatable', 'data'),
     Output('indicators', 'children')],
    [Input('dropdown-period', 'value'),
     Input('dropdown-type', 'value')]
)
def update_charts(period, loan_types):
    filtered_df = df[df['ТипКредита'].isin(loan_types)]

    # Агрегация по времени
    dfg = filtered_df.resample(period, on='Дата').agg({
        'ЗаявкаID': 'count',
        'Одобрено': 'sum',
        'Сумма': 'mean'
    }).reset_index()
    dfg['Отказано'] = dfg['ЗаявкаID'] - dfg['Одобрено']

    # График одобрено / отказано
    approved_fig = px.line(dfg, x='Дата', y=['Одобрено', 'Отказано'], title='Одобрено vs Отказано')

    # Средняя сумма по типам
    avg_loan_fig = px.bar(filtered_df.groupby('ТипКредита')['Сумма'].mean().reset_index(),
                          x='ТипКредита', y='Сумма', title='Средняя сумма кредита по типу')

    # Распределение времени обработки
    time_hist_fig = px.histogram(filtered_df, x='ВремяОбработки', title='Распределение времени обработки')

    # Корреляция скоринга и дохода
    scatter_fig = px.scatter(filtered_df, x='Доход', y='Скоринг', color='ТипКредита',
                             title='Скоринг vs Доход клиента')

    # Индикаторы
    total_apps = len(filtered_df)
    approval_rate = round(filtered_df['Одобрено'].sum() / total_apps * 100, 2)
    avg_time = round(filtered_df['ВремяОбработки'].mean(), 2)

    indicators = html.Div([
        dbc.Alert(f"Всего заявок: {total_apps}", color="primary"),
        dbc.Alert(f"Процент одобрения: {approval_rate}%", color="success"),
        dbc.Alert(f"Среднее время обработки: {avg_time} ч", color="info")
    ])

    return approved_fig, avg_loan_fig, time_hist_fig, scatter_fig, filtered_df.to_dict('records'), indicators

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)
