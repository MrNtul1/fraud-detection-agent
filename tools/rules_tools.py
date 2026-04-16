def check_amount(amount, avg_amount):
    """
    Compare transaction amount to user's normal behavior
    """

    ratio = amount / avg_amount if avg_amount > 0 else 1

    if ratio >= 5:
        return 3   # EXTREME spike
    elif ratio >= 3:
        return 2   # large spike
    elif ratio >= 2:
        return 1   # moderate spike
    else:
        return 0   # normal


def check_country(user_country, transaction_country, usually_international):
    """
    Check if user behavior matches transaction pattern
    """

    is_international = user_country != transaction_country

    if is_international and not usually_international:
        return 3   # very suspicious
    elif is_international and usually_international:
        return 1   # normal-ish behavior
    else:
        return 0   # local transaction