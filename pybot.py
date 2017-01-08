import socket
from io import StringIO
import sys, time, pydoc, os

server = "chat.freenode.net"
channel = "#irc_test"
botnick = "a_crazy_bot"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, 6667))
irc.send(bytes("USER {user} {user} {user} :This is a fun bot!\r\n".format(user=botnick),"utf8"))
irc.send(bytes("NICK {}\r\n".format(botnick),"utf8"))
irc.send(bytes("PRIVMSG nickserv :iNOOPE\r\n","utf8"))
irc.send(bytes("PRIVMSG nickserv :identify {}\r\n".format(sys.argv[1]),"utf8"))
sys.argv[1]=0
time.sleep(2)
irc.send(bytearray("JOIN {}\r\n".format(channel),"utf8"))


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
    f = file("help.txt", 'w')
    sys.stdout = f
    pydoc.help(request)
    f.close()
    sys.stdout = sys.__stdout__
    return

def bot():

    running = True
    while running:
        msg=str(irc.recv(2040),"utf8")
        show_error = False
        if msg.find(" PRIVMSG") != -1:
            who = msg[1:msg.find("!")]
            cmd = msg[msg.find(" :")+2:].strip()
            channel = msg[msg.find("#"):msg.find(" :")]

            if(cmd[0] == ">"):
                show_error = True
                cmd = cmd.replace(">","",1)

            if cmd[0:5] == "help(":
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
                    exec(cmd)
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
                if(show_error):
                    ret = "PRIVMSG {} :{}\r\n".format(channel,str(e))
                    irc.send(bytes(ret,"utf8"))

        if str(msg).find('PING') != -1:
            irc.send(bytes('PONG {}\r\n'.format(msg.split()[1]),"utf8"))


while True:
    bot()
