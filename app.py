from flask import Flask
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import PchipInterpolator

def create_app():
    app=Flask(__name__)

    from main import main as main_blueprint
   
    app.register_blueprint(main_blueprint)
    return app



