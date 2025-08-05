def bool_to_emoji(value: bool):
    if value == True:
        return '✅';
    
    return '❌';

def country_to_flag(country_code):
    # thanks to Kayy
    if len(country_code) != 2:
        return country_code
    
    return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)

def mask_email(email):
    # Show full email instead of masking
    return email

def mask_account_id(account_id):
    # Show full account ID instead of masking
    return account_id