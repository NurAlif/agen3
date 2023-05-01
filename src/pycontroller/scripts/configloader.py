import configparser

walk_balance_conf_path = '/home/nvidia/robotis/src/pycontroller/scripts/config/walk_balance.ini'


walk_balance_parser = configparser.RawConfigParser()   
walk_balance_parser.read(walk_balance_conf_path)

print(walk_balance_parser.sections())

def saveWalkBalanceConf():
    with open('example.ini', 'w') as configfile:
        walk_balance_parser.write(configfile)

def reload_walk_balance_conf():
    walk_balance_parser.read(walk_balance_conf_path)

def read_walk_balance_conf(group, item):
    walk_balance_parser = configparser.RawConfigParser()   
    walk_balance_parser.read(walk_balance_conf_path)

    print("read conf data "+ item +" : ")
    data = float(walk_balance_parser[group][item])
    print(data)
    return data