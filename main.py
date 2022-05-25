"""
This is main file for Japan City Temperature Analyis Project
by Preawpan Thamapipol
"""

from backend import JapanTemperature
from JapanTempUI import JapanTempReportUI

if __name__ == '__main__':
    database = JapanTemperature()
    ui = JapanTempReportUI(database)
    ui.run()
