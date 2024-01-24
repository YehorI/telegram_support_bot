import re


def validate_and_format_number(input_number):
    if input_number:
        # Remove all spaces and hyphens
        stripped_number = re.sub(r'\D', '', input_number)

        # Check if it starts with '8', replace with '+7'
        if stripped_number.startswith('8'):
            stripped_number = '7' + stripped_number[1:]

        # Match against the pattern +7 followed by 10 digits
        if re.match(r'7\d{10}$', stripped_number):
            # Reformat to +7 XXX XXX XX XX
            formatted_number = "+7 {} {} {} {}".format(stripped_number[1:4], stripped_number[4:7], stripped_number[7:9], stripped_number[9:])
            return formatted_number

        # If the number is not valid, return None
    return None
