import pycurl
import argparse
from io import BytesIO
from lxml import html

parser = argparse.ArgumentParser(description='Modify SFR router config')
parser.add_argument('-ra', metavar='XXX.XXX.XXX.XXX',dest='routerip',help='router ip address')
parser.add_argument('--login', metavar='****',dest='routerlogin',help='login of router web ui')
parser.add_argument('--password', metavar='****',dest='routerpass',help='password of router web ui')
parser.add_argument('-e',dest='enable',action='store_true',help=' enable all port that respect the filters in arguments')
parser.add_argument('-d',dest='disable',action='store_true',help=' disable all port that respect the filters in arguments')
parser.add_argument('-pe',dest='portext',metavar='PPPP or PPPP-PPPP',help=' define wich port or range of ports should be used for the filter ')

# -a add port option
# -r remove port option
# -e enable port option
# -d disable port option
# -n roule's name
# -tt tcp protocole
# -ty udp protocole
# -tb both
# -pe port extern  PPP or PPP-PPP
# -i address to forward
# -pi port intern PPP or PPP-PPP
args = parser.parse_args()
print(args);

tablexpath = "//table[@id='nat_config']//tbody//tr"

if(args.routerpass != None and args.routerlogin != None and args.routerip != None):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL,args.routerip+'/login')
        c.setopt(c.COOKIEFILE,"cookie")
        c.setopt(c.COOKIEJAR,"cookie")
        c.setopt(c.FOLLOWLOCATION,1)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POSTFIELDS, "login="+args.routerlogin+"&password="+args.routerpass)
        c.perform()
        reponse = buffer.getvalue()
        if(reponse.find(str.encode(args.routerpass)) == -1):
            c.close()
            exit(" Connexion au router impossible ")
        c.close()

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL,args.routerip+'/network/nat')
c.setopt(c.COOKIEFILE,"cookie")
c.setopt(c.COOKIEJAR,"cookie")
c.setopt(c.FOLLOWLOCATION,1)
c.setopt(c.WRITEDATA, buffer)
c.perform()
reponse = buffer.getvalue()
tree = html.fromstring(str(reponse))
print(tree.xpath(tablexpath))
ids = []
for tr in tree.xpath(tablexpath):
    ok = 1
    idligne = tr.xpath("td//span[@class='col_number']/text()")
    if(len(idligne) != 0):
        idligne = idligne[0]
        portext = tr.xpath("td[@data-title='Ports externes']/text()")[0]
        if(portext != args.portext):
            ok = 0
        if(ok == 1):
            ids.append(idligne)    
print(ids)
for id in ids :
    buffer = BytesIO()
    c = pycurl.Curl()
    poststr = "login="+args.routerlogin+"&password="+args.routerpass
    c.setopt(c.URL,args.routerip+'/network/nat')
    c.setopt(c.COOKIEFILE,"cookie")
    c.setopt(c.COOKIEJAR,"cookie")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION,1)
    if(args.enable == True):
        poststr = poststr+"&action_enable."+id+"=1"
    if(args.disable == True):
        poststr = poststr+"&action_disable."+id+"=1"
    print(poststr)
    c.setopt(c.POSTFIELDS,poststr)
    c.perform()
c.close()        