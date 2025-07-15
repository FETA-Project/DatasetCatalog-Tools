"""
Module containing interval blacklist class.
"""
class IntervalBlacklist:
    def __init__(self):
        self.intervals = []

    def add_interval(self, start, end):
        """
        Adds interval to blacklist.

        :param start:
            Lower boundary of the interval
        :type start:
            int
        :param end:
            Upper boundary of the interval
        :type end:
            int
        """
        if start > end:
            print("Start of the interval must be lower or equal to end.")
            return
        self.intervals.append((start, end))
        self.intervals.sort()  # Udržujeme intervaly zoradené

    def is_blacklisted(self, value):
        """
        Checks if given value is in currently blacklisted intervals.

        :param value:
            Value to check
        :type value:
            int
        :return:
            True if value is blacklisted, False if not.
        :rtype:
            bool
        """
        for start, end in self.intervals:
            if start <= value <= end:
                return True
        return False