from table2ascii import table2ascii as t2a, PresetStyle

class tablemaker:
    def __init__(self):
        pass
        
    def make_table(self, header, body):
        if isinstance(body, dict):
            if all(isinstance(value, dict) for value in list(body.values())):
                body = [[key] + list(value.values()) for key, value in body.items()]
            elif all(isinstance(value, list) for value in body.values()):
                body = [[key] + value for key, value in body.items()]
            else:
                body = [[key, value] for key, value in body.items()]
        return t2a(header=header, body=body, column_widths=None)