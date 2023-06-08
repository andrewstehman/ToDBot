def get_aliases():
    aliases = open('alias.txt', 'r')
    d = {}
    for line in aliases.readlines():
        items = line.split(',')
        alias = items[0].strip()
        mob = items[1].strip()
        if mob in d:
            d[mob] = d[mob] + alias + ", "
        else:
            d[mob] = alias + ", "

    for key in d:
        line = key + ": " + key + ", " + d[key]
        print(line[:len(line)-2])

get_aliases()