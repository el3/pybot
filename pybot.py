import socket
from io import StringIO
import sys, time, pydoc, os
from multiprocessing import Process, Value


server = "chat.freenode.net"
channels = sys.argv[3].split(",")

botnick = sys.argv[1]

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, 6667))
irc.setblocking(0)
irc.send(bytes("USER {user} {user} {user} :This is a fun bot!\r\n".format(user=botnick),"utf8"))
irc.send(bytes("NICK {}\r\n".format(botnick),"utf8"))
irc.send(bytes("PRIVMSG nickserv :iNOOPE\r\n","utf8"))
irc.send(bytes("PRIVMSG nickserv :identify {}\r\n".format(sys.argv[2]),"utf8"))
irc.settimeout(2)
sys.argv[2]=0
time.sleep(10)

for i in channels:
    irc.send(bytearray("JOIN {}\r\n".format(i),"utf8"))
    
    
class Capturing(list):

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


def output_help_to_file(request):
    f = open("help.txt", 'w')
    sys.stdout = f
    pydoc.help(request)
    f.close()
    sys.stdout = sys.__stdout__
    return


tell = {}
globals_dict = {}

def bot():
    
    running = True
    
    while running:
        try:
            msg=str(irc.recv(2040),"utf8")
        except:
            t.value = int(time.time())
            continue
        try:
            nick = msg.split("!")[0][1:]
            
            if msg.find("JOIN ") != -1 or nick in tell:
                print(tell)
                message = tell[nick]
                del tell[nick]
                ret = "PRIVMSG {} :{}\r\n".format("",message[:448])
                irc.send(bytes(ret,"utf8"))

            show_error = False

            if msg.find(" PRIVMSG") != -1:
                who = msg[1:msg.find("!")]
                cmd = msg[msg.find(" :")+2:].strip()
                channel = msg[msg.find("#"):msg.find(" :")]

                cmd = cmd.replace("os.dup2","")
                cmd = cmd.replace("socket","")
                cmd = cmd.replace("subprocess","")
                cmd = cmd.replace("while","While")
                cmd = cmd.replace("fork()","")

                if(cmd[0:5] == "tell "):
                    words = cmd[5:].split()
                    nick = words[0]
                    message = " ".join(words[1:])
                    if nick in tell:
                        tell[nick] += "Hi {}. {} asked me to tell you, {}...".format(nick,who,message)
                    else:
                        tell[nick] = "Hi {}. {} asked me to tell you, {}...".format(nick,who,message)
                    print(tell)
                    
                if(cmd[0:6] == "exit()"):
                    t.value = -1
                    
                if(cmd[0] == ">"):
                    show_error = True
                    cmd = cmd.replace(">","",1)

                if cmd[0:5] == "help(":
                    print("help")
                    req = cmd[5:cmd.find(")")]
                    try:
                        output_help_to_file(req)
                        link = os.popen('pastebinit -i help.txt -f python').read()
                        ret = "PRIVMSG {} :{}\r\n".format(channel,link)
                        irc.send(bytes(ret,"utf8"))
                        continue
                    except Exception as e:
                        print(e)

                try:
                    with Capturing() as output:
                        exec(cmd, globals_dict)
                    if len(output) > 0:
                        ch = ""
                        ch1= ""
                        out = output[0]
                        if out[0:4] == "/me ":
                            ch = chr(1)+"ACTION "
                            out = out[4:]
                        ret = "PRIVMSG {} :{ch}{}{ch1}\r\n".format(channel,out,ch=ch,ch1=ch1)
                        irc.send(bytes(ret,"utf8"))
                       
                except Exception as e:
                    print(e)
                    if(show_error):
                        ret = "PRIVMSG {} :{}\r\n".format(channel,str(e))
                        irc.send(bytes(ret,"utf8"))

            if str(msg).find('PING') != -1:
                irc.send(bytes('PONG {}\r\n'.format(msg.split()[1]),"utf8"))
        except Exception as e:
            print(e)
        t.value = int(time.time())


t = Value("i",int(time.time()))
p = Process(target=bot)
p.start()

while True:
    if t.value == -1:
        p.terminate()
        exit()
    if int(time.time()) - t.value > 10:
        p.terminate()
        p = Process(target=bot)
        p.start()
    time.sleep(1)
