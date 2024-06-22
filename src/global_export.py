import pdcglobal


def export():
    # Get all the variables from pdcglobal.py
    variables = [var for var in dir(pdcglobal) if not var[0].islower()]

    # Add the variables to the globals() dictionary
    for var in variables:
        print(f"Exporting {var} as {getattr(pdcglobal, var)}")
        globals()[var] = getattr(pdcglobal, var)

    print(f"Globals()[IF_EQUIPABLE] = {globals()["IF_EQUIPABLE"]}")
