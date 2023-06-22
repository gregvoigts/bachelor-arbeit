
# Import Required Modules
from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px
 
# Create Home Page Route
app = Flask(__name__)
 
 
@app.route('/')
def bar_with_plotly():
   
   # Students data available in a list of list
    students = [['Akash', 34, 'Sydney', 'Australia'],
                ['Rithika', 30, 'Coimbatore', 'India'],
                ['Priya', 31, 'Coimbatore', 'India'],
                ['Sandy', 32, 'Tokyo', 'Japan'],
                ['Praneeth', 16, 'New York', 'US'],
                ['Praveen', 17, 'Toronto', 'Canada']]
     
    # Convert list to dataframe and assign column values
    df = pd.read_csv('./flask/static/data/result_complete.csv')
     
    # Create Bar chart
    fig = px.bar(df, x='Dataset', y='Number', color='Model', barmode='group')
     
    # Create graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
     
    # Use render_template to pass graphJSON to html
    return render_template('bar.html', graphJSON=graphJSON)
 
 
if __name__ == '__main__':
    app.run(debug=True)