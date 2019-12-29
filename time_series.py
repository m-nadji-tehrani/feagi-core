from pandas import Series
from pandas import DataFrame
import pandas as pd
from matplotlib import pyplot
series = pd.read_csv('daily-minimum-temperatures.csv', header=0)
groups = series.groupby(pd.Grouper(key='Date'))
years = DataFrame()

for name, group in groups:
	years[name.year] = group.values
years.plot(subplots=True, legend=False)
pyplot.show()