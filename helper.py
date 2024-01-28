def format_number(n):

    """
        Small helper function that formats numbers to be more readable.
    """

    if abs(n) >= 1e12: 
        # TRIL
        return f'{n / 1e12:.2f} TRIL'
    elif abs(n) >= 1e9: 
        # BIL
        return f'{n / 1e9:.2f} BIL'
    elif abs(n) >= 1e6: 
        # MIL
        return f'{n / 1e6:.2f} MIL'
    else:
        return f'{n:.2f}'