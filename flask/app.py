
# Import Required Modules
from flask import Flask, render_template, request
import pandas as pd
import json
import plotly
import plotly.express as px
 
# Create Home Page Route
app = Flask(__name__)


@app.route('/')
def home():
    url=request.base_url
    url_class = url + 'classifier'
    url_reg = url + 'regression'

    return render_template('main.html', url_class=url_class,url_reg=url_reg)
 
@app.route('/regression')
def bar_regression():
    # Load dataframe from csv
    df = pd.read_csv(f'./flask/static/data/result_complete_regression.csv')

    value_type = request.args.get('value')

    if value_type == "" or value_type == None:
        value_type = "Accuracy"

    filtered = df.loc[df['Value'] == value_type]
     
    # Create Bar chart
    fig = px.bar(filtered, x='Dataset', y='Number', color='Model', barmode='group')
     
    # Create graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # create button urls
    url=request.base_url
    url = url + 'regression'
    url_blue = f'{url}?value=blue'
    url_acc = f'{url}?value=Accuracy'
    url_tacc = f'{url}?value=Train_Accuracy'
     
    # Use render_template to pass graphJSON to html
    return render_template('bar.html', graphJSON=graphJSON, url_blue=url_blue, url_acc=url_acc, url_tacc=url_tacc)

@app.route('/classifier')
def bar_classifier():
    # Load dataframe from csv
    df = pd.read_csv(f'./flask/static/data/result_complete_classifier.csv')

    value_type = request.args.get('value')

    if value_type == "" or value_type == None:
        value_type = "Accuracy"

    filtered = df.loc[df['Value'] == value_type]
     
    # Create Bar chart
    fig = px.bar(filtered, x='Dataset', y='Number', color='Model', barmode='group')
     
    # Create graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # create button urls
    url=request.base_url
    url = url + 'classifier'
    url_blue = f'{url}?value=blue'
    url_acc = f'{url}?value=Accuracy'
    url_tacc = f'{url}?value=Train_Accuracy'
     
    # Use render_template to pass graphJSON to html
    return render_template('bar.html', graphJSON=graphJSON, url_blue=url_blue, url_acc=url_acc, url_tacc=url_tacc)
 

if __name__ == '__main__':
    app.run(debug=True)