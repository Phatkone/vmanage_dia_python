import dns.resolver as resolver

def ARecord(fqdn):
    dig = resolver.query(fqdn,'A')
    if type(dig) == dict:
        return dig
    else:
        return False