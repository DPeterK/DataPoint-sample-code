DataPoint Sample Code
=====================

Example Python code to retrieve data stored in the Met Office's DataPoint weather &amp; climate data repository.

The script `datapoint_access.py` performs data retrieval from DataPoint based on user-selected inputs. Data is returned in json format and parsed into a Python dictionary for downstream use.

A usage example is also provided in `example.py`. This demonstrates using `datapoint_access.py` to retrieve observations data for Heathrow airport and then retrieve all pressure observations from the returned dictionary of observations.


DataPoint
---------

DataPoint is a Met Office weather and climate data repository that may be used for free to retrieve such weather and climate data. See http://www.metoffice.gov.uk/datapoint; please follow the link to register for free to use the data and services provided by DataPoint.

For documentation on how to use DataPoint: http://www.metoffice.gov.uk/datapoint/documentation. <br />
Please also note the terms and conditions: http://www.metoffice.gov.uk/datapoint/support/terms-conditions.


### Note ###
To download weather and climate data from DataPoint you must supply your unique API Key. This will be provided upon registration with DataPoint.
