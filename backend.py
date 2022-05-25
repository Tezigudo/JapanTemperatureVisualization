"""
This module contains the backend of the application.
"""


from typing import List

import pandas as pd

FILEPATH = 'https://cloudbox.ku.ac.th/index.php/s/HKQzGzAJdMkZgYj/download'


class JapanTemperature:
    """
    JapanTemp Model class for UI
    """

    def __init__(self) -> None:
        """
        Initialize the temp and city attribute
        it will be change into pandas dataframe and Series after reading a file
        """
        self.__temp = []
        self.__city = []

    def _readfile(self) -> None:
        """
        Read a file then set a instance
        it will be called in UI
        """

        # configuration for data
        temp = pd.read_csv(FILEPATH)
        # set Date column to date type
        temp['Date'] = pd.to_datetime(temp['Date'])
        temp.set_index('Date', inplace=True)
        temp.dropna(axis=1, inplace=True)
        temp.sort_index(axis=1, inplace=True)
        # last year has only 1 data from 365 needed to drop out
        temp.drop(temp.index[temp.index.year == max(
            temp.index.year.unique())], inplace=True)
        # assign attribute
        self.__temp = temp
        self.__city = self.temp.columns

    @property
    def temp(self) -> pd.DataFrame:
        """get Japan Data temperature of each city

        Returns:
            pd.DataFrame -- DataFrame of Japan Temperature pf each city
        """
        return self.__temp

    @property
    def city(self) -> pd.core.indexes.base.Index:
        """Get all city of dataframe

        Returns:
            pd.core.indexes.base.Index -- Series of Japanese city
        """
        return self.__city

    def __get_date(self) -> List[pd.Timestamp]:
        """All date of Data

        Returns:
            List[pd.Timestamp] -- a list of date
        """
        return list(self.__temp.index) if len(self.__temp != 0) else []

    def __get_year(self) -> List[int]:
        """All year of Data

        Returns:
            List[int] -- a list of year
        """
        if len(self.__temp) != 0:
            # assume that data have no missing year
            return list(range(self.date[0].year, self.date[-1].year + 1))
        return []

    @property
    def date(self) -> List[pd.Timestamp]:
        """get all date of data

        Returns:
            List[pd.Timestamp] -- empty list if data isn't read
                                  else a list of date in data in TImestamp format
        """
        return self.__get_date()

    @property
    def year(self) -> List[int]:
        """get all year of data

        Returns:
            List[int] -- empty list if data isn't read else a list of year in data
        """
        # assume that data have no missing year
        return self.__get_year()

    def get_temps(self, city: str) -> pd.Series:
        """get the temperature of a city in Japan

        Arguments:
            city {str} -- a city in Japan

        Raises:
            TypeError: Raises if param city isn't a string it will raise
            CityNotFoundError: Raises if city not in Japan or invlid city

        Returns:
            pd.Series -- a Series of Japanese Temperature of specific city in all date
        """
        if not isinstance(city, str):
            raise TypeError('city must be a string')
        if city != '' and city not in self.city:
            raise CityNotFoundError(f'{city} not in Japan')
        return self.temp[city]

    def overall_mode(self, city: str) -> pd.Series:
        """get the overall temperature of a city in Japan

        Arguments:
            city {str} -- a city in Japan

        Returns:
            pd.Series -- Series of Japanese Temperature of specific city in all date
        """
        return self.get_temps(city)

    def year_mode(self, city: str, year: int) -> pd.Series:
        """get the temperature of a city in Japan in a specific year it for year mode in UI

        Arguments:
            city {str} -- specfic city in Japan
            year {int} -- specific year in data

        Returns:
            pd.Series -- a series of Temperature filtered by city and year
        """
        return self.get_temps(city)[f'{year}-01-01': f'{year}-12-31']

    def month_mode(self, city: str, year: int, month: int) -> pd.Series:
        """get the temperature of a city in Japan in a specific month it for month mode in UI

        Arguments:
            city {str} -- specfic city in Japan
            year {int} -- specific year in data
            month {int} -- specific month of selected year and city in data

        Returns:
            pd.Series -- a series of Temperature filtered by city and month
        """
        last_day = pd.Period(f'{year}-{month}', freq='M').end_time.day
        return self.get_temps(city)[f'{year}-{month}-01': f'{year}-{month}-{last_day}']

    def get_describe(self, data: pd.Series) -> pd.core.series.Series:
        """get description of current data that plotted in UI

        Arguments:
            data {pd.Series} -- series of Temperature

        Returns:
            pd.core.series.Series -- description of current data
        """
        # not include coount index
        return data.describe()[1:]


class CityNotFoundError(Exception):
    """
    Exception if city not found or not in Japan
    """
