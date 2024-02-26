from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../Cogent-AI.db'
db = SQLAlchemy(app)

# Reflect the database tables
# Base = automap_base()
# Base.prepare(db.engine, reflect=True)
with app.app_context():
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)
    # Client = Base.classes.client
# Dynamically create model classes for each table
for table_name in Base.classes.keys():
    # Access the class object corresponding to the table
    table_class = Base.classes[table_name]

    # Define a new model class dynamically using type()
    # This allows us to create classes with dynamic names
    new_model_class = type(table_class.__name__, (db.Model,), {'__tablename__': table_name})
    print("new_model_class>>>>>>>>>>>>>",new_model_class)
    # Assign the columns from the reflected table to the new model class
    for column in table_class.__table__.columns:
        setattr(new_model_class, column.name, column)

    # Add the new model class to the globals() dictionary
    globals()[table_class.__name__] = new_model_class
    print("globals>>>>>>>>>>>>>>",globals(),"table_name>>>>>>>>>.",table_name)


# Route to handle retrieving one record from a dynamically mapped table
# @app.route('/Cogent/<table_name>/<int:record_id>', methods=['GET'])
def get_record(table_name, record_id):
    print("table_name<<<<<<<<<Inner",table_name,"record_id>>>>>>>>",record_id)
    # Get the model class dynamically based on the table name
    if table_name in globals():
        table_class = globals()[table_name]
        # Query the database for the record with the specified ID
        record = table_class.query.get(record_id)
        if record:
            # If the record is found, convert it to a dictionary
            record_data = {column.name: getattr(record, column.name) for column in record.__table__.columns}
            return jsonify(record_data)
        else:
            return 'Record not found', 404
    else:
        return 'Table not found', 404



if __name__ == '__main__':
    app.run(debug=True)
