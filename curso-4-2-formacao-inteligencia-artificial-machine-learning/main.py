from numpy import array

from Aulas_Soso.LinearRegression import LinearRegression


x = array([1, 2, 3, 4, 5])
y = array([2, 4, 6, 8, 10])
lr = LinearRegression(x, y)
prevision = lr.prevision(6)
print(prevision)
