from datetime import date, timedelta

class Common:
    @staticmethod
    def get_age(date_to_count):
        today = date.today()
        return int(today.year - date_to_count.year - ((today.month, today.day) < (date_to_count.month, date_to_count.day)))

    @staticmethod
    def add_year(value):
        if value.year == 2099 or value.year == 2100:
            return value + timedelta(365)
        elif value.month > 2 and value.year % 4 == 3:
            return value + timedelta(366)
        elif value.month < 3 and value.year % 4 == 0:
            return value + timedelta(366)
        else:
            return value + timedelta(365)
