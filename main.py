from flask import Flask, Blueprint, render_template, request, jsonify
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import PchipInterpolator
import numpy as np
import os

main = Blueprint('main', __name__)

@main.route("/")
def main_interface():
    return render_template('indianaaonr.html')


@main.route("/generate_fig")
def generate_fig():
    cell = int(request.args.get('cell'))
    fig_creation_aonr(cell)
    return jsonify({"url": "/static/images/fig.html"})

@main.route("/generate_eonr_fig")
def generate_eonr_fig():
    cell = int(request.args.get('cell'))
    grainPrice = int(request.args.get('grain_price'))
    nPrice = float(request.args.get('n_price'))
    fig_creation_eonr(cell,grainPrice,nPrice)
    return jsonify({"url": "/static/images/fig2.html"})


def fig_creation_aonr(cell):
    simulations = pd.read_csv('static/simulations.csv')

    simulations['Yield'] = simulations['Yield'].astype(int)
    simulations['id_cell'] = simulations['id_cell'].astype(int)
    simulations['id_within_cell'] = simulations['id_within_cell'].astype(int)

    simulations['Yield'] = pd.to_numeric(simulations['Yield'], errors='coerce')
    simulations['Nitrogen'] = pd.to_numeric(simulations['Nitrogen'], errors='coerce')

    simulations = (
        simulations
            .groupby(['Nitrogen', 'region', 'id_cell', 'id_within_cell'], as_index=False)
            .agg({'Yield': 'mean'})
    )

    df_cell = simulations[simulations['id_cell'] == cell]

    if df_cell.empty:
        return

    max_row = df_cell.loc[df_cell['Yield'].idxmax()]
        
    x = pd.to_numeric(df_cell['Nitrogen'], errors='coerce')
    y = pd.to_numeric(df_cell['Yield'], errors='coerce')

    pchip = PchipInterpolator(x, y)
    x_smooth = np.linspace(x.min(), x.max(), 200)
    y_smooth = pchip(x_smooth)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines',
                             name='Yield Curve',
                             line=dict(color='steelblue', width=3)))
    fig.add_trace(go.Scatter(x=[max_row['Nitrogen']], y=[max_row['Yield']],
                             mode='markers+text',
                             name='Max Yield',
                             marker=dict(color='red', size=12)))
    fig.add_shape(type='line',
                  x0=max_row['Nitrogen'], y0=0,
                  x1=max_row['Nitrogen'], y1=max_row['Yield'],
                  line=dict(color='green', width=3, dash='dash'))

    fig.update_layout(
        xaxis_title='Nitrogen (kg/ha)',
        yaxis_title='Yield (t/ha)',
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False, showline=True, linecolor='black'),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)')
    )
    

    fig.write_html('static/images/fig.html')


def fig_creation_eonr(cell,grainPrice,nPrice):
    simulations = pd.read_csv('static/simulations.csv')

    simulations['Yield'] = simulations['Yield'].astype(int)
    simulations['id_cell'] = simulations['id_cell'].astype(int)
    simulations['id_within_cell'] = simulations['id_within_cell'].astype(int)

    simulations['Yield'] = pd.to_numeric(simulations['Yield'], errors='coerce')
    simulations['Nitrogen'] = pd.to_numeric(simulations['Nitrogen'], errors='coerce')

    simulations = (
        simulations
            .groupby(['Nitrogen', 'region', 'id_cell', 'id_within_cell'], as_index=False)
            .agg({'Yield': 'mean'})
    )

    df_cell = simulations[simulations['id_cell'] == cell]


    df_cell['Economic'] = df_cell['Yield'] * grainPrice - df_cell['Nitrogen'] * nPrice


    max_row = df_cell.loc[df_cell['Economic'].idxmax()]


    x = pd.to_numeric(df_cell['Nitrogen'], errors='coerce')
    y = pd.to_numeric(df_cell['Economic'], errors='coerce')
    pchip = PchipInterpolator(x, y)
    x_smooth = np.linspace(x.min(), x.max(), 200)
    y_smooth = pchip(x_smooth)


    fig = go.Figure()


    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=y_smooth,
        mode='lines',
        name='Economic Return Curve',
        line=dict(color='steelblue', width=3),
    ))


    fig.add_trace(go.Scatter(
        x=[max_row['Nitrogen']],
        y=[max_row['Economic']],
        mode='markers+text',
        name='EONR',
        marker=dict(color='red', size=12)
    ))


    fig.add_shape(
        type='line',
        x0=max_row['Nitrogen'],
        y0=0,
        x1=max_row['Nitrogen'],
        y1=max_row['Economic'],
        line=dict(color='green', width=3, dash='dash')
    )


    fig.update_layout(
        xaxis_title='Nitrogen (kg/ha)',
        yaxis_title='Economic Return (USD/ha)',
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False, showline=True, linecolor='black'),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)')
    )
    
    fig.write_html('static/images/fig2.html')