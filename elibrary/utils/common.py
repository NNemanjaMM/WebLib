from datetime import date, datetime, timedelta
from flask_login import current_user
from elibrary import db
from elibrary.models import Event, EventType
from elibrary.utils.custom_validations import FieldValidator

class CommonDate:
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

class EventWriter:
    @staticmethod
    def write(type, object_id, message):
        event = Event()
        event.time = datetime.now()
        event.librarian = current_user.username
        event.type = type
        event.object_id = object_id
        event.message = message
        db.session.add(event)
        # bez db.session.commit() jer ce se onsvakako uraditi za upis podatka u bazu

class CommonFilter:
    @staticmethod
    def process_related_date_filters(my_query, args_filter, filter_has_errors, from_field, to_field, f_from, f_to, field_from_name, field_to_name, db_table, db_column_name, validate_future_date):
        from_value = None
        if not (f_from == None or f_from == ""):
            from_field.data = f_from
            from_value = FieldValidator.convert_and_validate_date(from_field, validate_future_date)
            if not from_value == None:
                my_query = my_query.filter(getattr(db_table, db_column_name) >= from_value.strftime('%Y-%m-%d'))
                args_filter[field_from_name] = f_from
            else:
                filter_has_errors = True
        if not (f_to == None or f_to == ""):
            to_field.data = f_to
            to_value = FieldValidator.convert_and_validate_date(to_field, validate_future_date)
            if not to_value == None:
                if not from_value == None:
                    if FieldValidator.validate_date_order(from_value, to_value, to_field):
                        my_query = my_query.filter(getattr(db_table, db_column_name) <= to_value.strftime('%Y-%m-%d'))
                        args_filter[field_to_name] = f_to
                    else:
                        filter_has_errors = True
                else:
                    my_query = my_query.filter(getattr(db_table, db_column_name) <= to_value.strftime('%Y-%m-%d'))
                    args_filter[field_to_name] = f_to
            else:
                filter_has_errors = True
        return my_query, args_filter, filter_has_errors

    @staticmethod
    def process_related_number_filters(my_query, args_filter, filter_has_errors, from_field, to_field, f_from, f_to, field_from_name, field_to_name, db_table, db_column_name):
        from_value = None
        if not (f_from == None or f_from == ""):
            from_field.data = f_from
            from_value = FieldValidator.convert_and_validate_number(from_field)
            if not from_value == None:
                my_query = my_query.filter(getattr(db_table, db_column_name) >= from_value)
                args_filter[field_from_name] = f_from
            else:
                filter_has_errors = True
        if not (f_to == None or f_to == ""):
            to_field.data = f_to
            to_value = FieldValidator.convert_and_validate_number(to_field)
            if not to_value == None:
                if not from_value == None:
                    if FieldValidator.validate_number_order(from_value, to_value, to_field):
                        my_query = my_query.filter(getattr(db_table, db_column_name) <= to_value)
                        args_filter[field_to_name] = f_to
                    else:
                        filter_has_errors = True
                else:
                    my_query = my_query.filter(getattr(db_table, db_column_name) <= to_value)
                    args_filter[field_to_name] = f_to
            else:
                filter_has_errors = True
        return my_query, args_filter, filter_has_errors

    @staticmethod
    def process_equal_number_filter(my_query, args_filter, filter_has_errors, field, f_field, field_name, db_table, db_column_name):
        if not (f_field == None or f_field == ""):
            field.data = f_field
            compare_value = FieldValidator.convert_and_validate_number(field)
            if not compare_value == None:
                my_query = my_query.filter(getattr(db_table, db_column_name) == compare_value)
                args_filter[field_name] = compare_value
            else:
                filter_has_errors = True
        return my_query, args_filter, filter_has_errors

    @staticmethod
    def process_like_filter(my_query, args_filter, filter_has_errors, form, field, f_field, field_name, validators, db_table, db_column_name):
        if not (f_field == None or f_field == ""):
            field.data = f_field
            if FieldValidator.validate_field(form, field, validators):
                my_query = my_query.filter(getattr(db_table, db_column_name).like('%' + f_field + '%'))
                args_filter[field_name] = f_field
            else:
                filter_has_errors = True
        return my_query, args_filter, filter_has_errors
