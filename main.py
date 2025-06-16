import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dash_table

# Инициализация приложения
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Макет дашборда
app.layout = dbc.Container([
    html.H1("Дашборд по заявкам на кредит", className="text-center my-4"),

    # Выбор периода
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
        ], width=4)
    ]),

    # Графики
    dbc.Row([
        dbc.Col(dcc.Graph(id='approved-vs-rejected'), width=6),
        dbc.Col(dcc.Graph(id='avg-loan-by-type'), width=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-rating-vs-income'), width=12)
    ]),

    dbc.Row([
        dbc.Col(html.Div(id='indicators'), width=12)
    ]),

    # Таблица данных
    dbc.Row([
        dbc.Col([
            html.H4("Все заявки"),
            dash_table.DataTable(
                id='datatable',
                columns=[{"name": i, "id": i} for i in pd.read_csv('data.csv').columns if i != 'Телефон'],
                data=[],  # заполняется через callback
                page_size=10,
                sort_action='native',
                filter_action='native',
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': '#f2f2f2', 'fontWeight': 'bold'}
            )
        ])
    ])

], fluid=True)


# --- Callback для обновления графиков и таблицы ---
@app.callback(
    [Output('approved-vs-rejected', 'figure'),
     Output('avg-loan-by-type', 'figure'),
     Output('scatter-rating-vs-income', 'figure'),
     Output('indicators', 'children'),
     Output('datatable', 'data'),
     Output('datatable', 'columns')],
    Input('interval-component', 'n_intervals'),
    Input('dropdown-period', 'value')
)
def update_charts(n, period):
    df = pd.read_csv('data.csv')
    df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')

    # Агрегация по выбранному периоду
    dfg = df.resample(period, on='Дата').agg({
        'Одобрено': 'sum',
        'ЗаявкаID': 'count',
        'Сумма': 'mean'
    }).reset_index()
    dfg['Отказано'] = dfg['ЗаявкаID'] - dfg['Одобрено']

    # 1. Одобрено / отклонено
    line_fig = px.line(dfg, x='Дата', y=['Одобрено', 'Отказано'], title='Одобрено vs Отклонено')

    # 2. Средняя сумма по типу (только Автокредит)
    avg_loan_fig = px.bar(df.groupby('ТипКредита')['Сумма'].mean().reset_index(),
                          x='ТипКредита', y='Сумма',
                          title='Средняя сумма кредита по типу')

    # 3. Корреляция скоринга и дохода
    scatter_fig = px.scatter(df, x='Доход', y='Скоринг', color='ТипКредита',
                             title='Скоринг vs Доход клиента')

    # 4. Индикаторы
    total_apps = len(df)
    approval_rate = round(df['Одобрено'].sum() / total_apps * 100, 2) if total_apps > 0 else 0
    avg_score = round(df['Скоринг'].mean(), 2)

    indicators = html.Div([
        dbc.Alert(f"Всего заявок: {total_apps}", color="primary"),
        dbc.Alert(f"Процент одобрения: {approval_rate}%", color="success"),
        dbc.Alert(f"Средний скоринг: {avg_score}", color="info")
    ])

    # Таблица данных
    table_columns = [{"name": col, "id": col} for col in df.columns if col != 'Телефон']
    table_data = df.to_dict('records')

    return (
        line_fig,
        avg_loan_fig,
        scatter_fig,
        indicators,
        table_data,
        table_columns
    )


# --- Добавляем автообновление ---
app.layout.children.append(
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # каждые 10 секунд
        n_intervals=0
    )
)

if __name__ == '__main__':
    app.run(debug=True)