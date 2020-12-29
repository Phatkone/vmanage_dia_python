import dns.name
import dns.message
import dns.query
import dns.flags

def dig(fqdn, nameserver = '8.8.8.8'):# Qtype="A", nameserver = '8.8.8.8'):
    domain = dns.name.from_text(fqdn)
    if not domain.is_absolute():
        domain = domain.concatenate(dns.name.root)
    #if Qtype == "A":
    #    rdata = dns.rdatatype.A
    #elif Qtype == "MX":
    #    rdata = dns.rdatatype.MX
    #elif Qtype == "any":
    #    rdata = dns.rdatatype.ANY
    #else:
    #    rdata = dns.rdatatype.A
    rdata = dns.rdatatype.A
    request = dns.message.make_query(domain, rdata)
    request.flags |= dns.flags.AD
    request.find_rrset(request.additional, dns.name.root, 65535, dns.rdatatype.OPT, create=True, force_unique=True)
    response = dns.query.udp(request, nameserver)
    entries = []
    if len(response.answer) < 1:
        return []
    for a in response.answer[0].items:
        entries.append(str(a))
    return entries