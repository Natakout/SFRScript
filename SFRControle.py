import pycurl
import argparse
from io import BytesIO
from lxml import html
import string
import re

parser = argparse.ArgumentParser(description='Modify SFR router config')
parser.add_argument('-ra', metavar='XXX.XXX.XXX.XXX',dest='routerip',help='router ip address')
parser.add_argument('--login', metavar='****',dest='routerlogin',help='login of router web ui')
parser.add_argument('--password', metavar='****',dest='routerpass',help='password of router web ui')
parser.add_argument('-e',dest='enable',action='store_true',help=' enable all port that respect the filters in arguments')
parser.add_argument('-d',dest='disable',action='store_true',help=' disable all port that respect the filters in arguments')
parser.add_argument('-pe',dest='portext',metavar='PPPP or PPPP-PPPP',help=' define wich extern port or range of ports should be used for the filter ')
parser.add_argument('-pi',dest='portint',metavar='PPPP or PPPP-PPPP',help=' define wich intern port or range of ports should be used for the filter ')
parser.add_argument('-n',dest='name',metavar='NNNN',help=' define wich name should be used for the filter ')
parser.add_argument('-tt',dest='tcp',action='store_true',help='define that UDP protocol should be used for the filter ')
parser.add_argument('-tu',dest='udp',action='store_true',help='define that UDP protocol should be used for the filter ')
parser.add_argument('-tb',dest='both',action='store_true',help='define that UDP and TCP protocol should be used for the filter ')
parser.add_argument('-i',dest='ipforw',metavar='PPPP or PPPP-PPPP',help=' define wich ip to forward should be used for the filter ')
# -a add port option
# -r remove port option
args = parser.parse_args()
print(args);

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL,args.routerip+'/login')
c.setopt(c.COOKIEFILE,"cookie")
c.setopt(c.COOKIEJAR,"cookie")
c.setopt(c.FOLLOWLOCATION,1)
c.setopt(c.WRITEDATA, buffer)

tablexpath = "//table[@id='nat_config']//tbody//tr"
idxpath = "td//span[@class='col_number']/text()"
portextxpath = "td[@data-title='Ports externes']/text()"
portintxpath = "td[@data-title='Ports de destination']/text()"
ipforwxpath = "td[@data-title='IP de destination']/text()"
namexpath = "td[@data-title='Nom']/text()"
protocolxpath = "td[@data-title='Protocole']/text()"
regex = re.compile(r'[\n\t\t]')


if(args.routerpass != None and args.routerlogin != None and args.routerip != None):
        c.setopt(c.POSTFIELDS, "login="+args.routerlogin+"&password="+args.routerpass)
        c.perform()
        reponse = buffer.getvalue()
        if(reponse.find(str.encode(args.routerpass)) == -1):
            c.close()
            exit(" Connexion au router impossible ")
c.setopt(c.URL,args.routerip+'/network/nat')
c.perform()
reponse = buffer.getvalue()
tree = html.fromstring(str(reponse))
print(tree.xpath(tablexpath))
ids = []
for tr in tree.xpath(tablexpath):
    ok = 1
    idligne = tr.xpath(idxpath)
    if(len(idligne) != 0):
        idligne = idligne[0]
        portext = re.sub(r'[\\n\\t\\t]', '', str(tr.xpath(portextxpath)[0]))
        portint = re.sub(r'[\\n\\t\\t]', '', str(tr.xpath(portintxpath)[0]))
        name = re.sub(r'[\\n\\t\\t]', '', str(tr.xpath(namexpath)[0]))
        protocol = re.sub(r'[\\n\\t\\t]', '', str(tr.xpath(protocolxpath)[0]))
        ipforw = re.sub(r'[\\n\\t\\t]', '', str(tr.xpath(ipforwxpath)[0]))
        print(protocol)
        ## add other parameters
        if(portext != args.portext and args.portext != None):
            ok = 0
        if(portint != args.portint and args.portint != None):
            ok = 0
        if(ipforw != args.ipforw and args.ipforw != None):
            ok = 0
        if(name != args.name and args.name != None):
            ok = 0
        if(protocol != "TCP" and args.tcp == True):
            ok = 0
        if(protocol != "UDP" and args.udp == True):
            ok = 0
        if(protocol != "les deux" and args.both == True):
            ok = 0
        if(ok == 1):
            ids.append(idligne)    
print(ids)
for id in ids :
    poststr = "login="+args.routerlogin+"&password="+args.routerpass
    ## add other action
    if(args.enable == True):
        poststr = poststr+"&action_enable."+id+"=1"
    if(args.disable == True):
        poststr = poststr+"&action_disable."+id+"=1"
    print(poststr)
    c.setopt(c.POSTFIELDS,poststr)
    c.perform()
c.close()        