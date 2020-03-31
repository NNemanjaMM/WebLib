from datetime import date

class Common:
    @staticmethod
    def get_age(date_to_count):
        today = date.today()
        return int(today.year - date_to_count.year - ((today.month, today.day) < (date_to_count.month, date_to_count.day)))
