def remove_double_quotes(input_string):
    if input_string.startswith('"') and input_string.endswith('"'):
        return input_string[1:-1]
    else:
        return input_string
