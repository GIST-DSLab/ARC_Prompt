import pandas as pd

a = pd.read_csv('prediction.csv')
b = a['prediction']
c = a['label']
d = a[a['prediction'] == a['label']]
d.to_csv('correct.csv', index=None)