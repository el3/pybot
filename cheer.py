def cheer(t='Usage: cheer("str",n=color,C=[color,...],s=star,p=padding)',n=0,C=3*[0],s="*",p=" "): print( "".join(map(lambda u,s=s,p=p: "%02d"%(u%16)+p+s, C))+"  %02d%s "%(n,t)+"".join(map(lambda u,s=s,p=p: "%02d"%(u%16)+p+s,C[::-1])))

def cheer2(t='Usage: cheer("str",n=color,C=[color,...],s=star,p=padding)',n=0,C=3*[0],s="*",p=" ",f=(lambda c,)
