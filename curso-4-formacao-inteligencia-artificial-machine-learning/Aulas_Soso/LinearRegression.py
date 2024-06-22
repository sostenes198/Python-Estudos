from numpy import *


class LinearRegression:
    def __init__(self, x, y) -> None:
        self.__x = x
        self.__y = y
        self.__correlation_coefficient = self.__calculate_correlation()
        self.__inclination = self.__calculate_inclination()
        self.__intercept = self.__calculate_intercept()

    def __calculate_correlation(self):
        covariance = cov(self.__x, self.__y, bias=True)[0][1]
        variance_x = var(self.__x)
        variance_y = var(self.__y)
        return covariance / sqrt(variance_x * variance_y)

    def __calculate_inclination(self):
        stdx = std(self.__x)
        stdy = std(self.__y)
        return self.__correlation_coefficient * (stdy / stdx)

    def __calculate_intercept(self):
        mean_x = mean(self.__x)
        mean_y = mean(self.__y)
        return mean_y - mean_x * self.__inclination

    def prevision(self, value):
        return self.__intercept + (self.__inclination * value)
