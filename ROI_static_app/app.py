# Flask Setup
from flask import Flask, request, render_template
import spreadsheet
import pandas as pd

app = Flask(__name__, template_folder='./templates')

roi_sheet = spreadsheet.sheet_init()
row = 2


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title="Home Page")


@app.route('/index', methods=['GET', 'POST'])
def costdata():
    if request.method == 'POST':
        global row
        User = request.form['User']
        Cloud = request.form['Cloud']
        OS = request.form['OS']
        RAM = float(request.form['RAM'])
        vCPUs = int(request.form['vCPUs'])
        Number_of_Nodes = int(request.form['No of Nodes'])
        StorageType = request.form['Storage Type']
        StorageUnitSize = int(request.form['Storage Size'])
        Number_of_Storage_Units = int(request.form['Storage Unit Quantity'])

        if request.form.get('submit_button') == 'submit':
            # send data to gsheet
            data = [User, Cloud, OS, RAM, vCPUs, Number_of_Nodes, StorageType,
                    StorageUnitSize, Number_of_Storage_Units]
            UserSheet = roi_sheet.worksheet('Dashboard 1')
            UserSheet.insert_row(data, row)
            row = row + 1

            if Cloud == "AWS":
                node_cost, store_cost = spreadsheet.aws_cost(
                    RAM, vCPUs, OS, StorageUnitSize, Cloud, Number_of_Nodes, StorageType, Number_of_Storage_Units)
            elif Cloud == "GCP":
                node_cost, store_cost = spreadsheet.gcp_cost(
                    RAM, vCPUs, OS, StorageUnitSize, Cloud, Number_of_Nodes, StorageType, Number_of_Storage_Units)
            else:
                node_cost = spreadsheet.azure_cost(
                    RAM, vCPUs, OS, StorageUnitSize, Cloud, Number_of_Nodes, StorageType, Number_of_Storage_Units)

            node_cost.index.name = None

            labels = node_cost['Machine or Service'].values.tolist()
            values = node_cost['monthly cost node'].values.tolist()

            return render_template('index.html', title="Dashboard", labels=labels, values=values, tables=[node_cost.head().to_html(index=False), store_cost.head().to_html(index=False)],
                                   titles=["", "{} Node Data".format(Cloud), "{} Storage Data".format(Cloud)])

        elif request.form.get('submit_button') == "compare":
            aws_node_cost, aws_store_cost = spreadsheet.aws_cost(
                RAM, vCPUs, OS, StorageUnitSize, Cloud, Number_of_Nodes, StorageType, Number_of_Storage_Units)
            gcp_node_cost, gcp_store_cost = spreadsheet.gcp_cost(
                RAM, vCPUs, OS, StorageUnitSize, Cloud, Number_of_Nodes, StorageType, Number_of_Storage_Units)
            azure_node_cost = spreadsheet.azure_cost(
                RAM, vCPUs, OS, StorageUnitSize, Cloud, Number_of_Nodes, StorageType, Number_of_Storage_Units)
            combine_cost, gcp_cost, aws_cost, azure_cost = spreadsheet.cost_data_combine(
                aws_node_cost, gcp_node_cost, azure_node_cost, gcp_store_cost, aws_store_cost, StorageType, Number_of_Storage_Units)

            labels = combine_cost['Machine or Service'].values.tolist()
            values = combine_cost['Monthly Cost with Storage'].values.tolist()

            return render_template('index.html', title="Dashboard", labels=labels, values=values,
                                   tables=[aws_cost.to_html(index=False), gcp_cost.to_html(index=False), azure_cost.to_html(index=False)], titles=['Ae', 'AWS', 'GCP Node', 'Azure Node'], Heading="Compare Data")
    elif request.method == 'GET':
        return render_template('index.html', title="Dashboard")


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=9999)
