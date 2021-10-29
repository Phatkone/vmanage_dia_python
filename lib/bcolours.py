def cprint(string: str, type: str = "endc") -> None:
    colours = {
        'PURPLE': '\033[95m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
    }
    if type.lower() in ['purple','blue','cyan','green','yellow','red','bold','underline']:
        print("{}{}{}".format(colours[type.upper()],string,colours['ENDC']))
    else:
        print(string)