from multiprocessing import Process ,Event
from multiprocessing.managers import BaseManager
import random as rd
import sys ,time,os
import socket as sk
"""Object contient le climat parametre"""
class Parametre:
    def temperature(self):
        temp=0
        temp=rd.randrange(-10,35,1)
        return temp
    def climat(self):
        climat=""
        weather =["soleil","normal","pluie","neige","catas"]
        i=rd.randint(0,4)
        climat=weather[i]
        return climat
#Creer une type de Manager appellee"Para"
class WeatherParametre(BaseManager):
    pass
WeatherParametre.register("Para",Parametre)

"""
Processsus pour calcule le facteur clmat grace a la memoire partage avec Parametre 
et renvoie a Environnemnt(du House(Process)) et Marche
"""
class Climat(Process):
    #Il contient tous les para pour connecter TCP ,avec le facteur pour la temperature et pour le climat,le iD
    def __init__(self,id,port,host):
        super().__init__()
        self.temp=0
        self.climat=""
        self.port=port
        self.host=host
        self.id=0
        self.valide=False
    #Generer tous les facteurs et les envoyer renvoie a Environnemnt(du House(Process)) et Marche
    def controller(self,event):

        with WeatherParametre() as manager:
            parametre=manager.Para()
            self.temp=parametre.temperature()
            self.climat=parametre.climat()
        facteur1=self.tempfacteur()
        facteur2=self.climatfacteur()
        facteur3=facteur1+facteur2
        facteur =round(facteur3,3)
        msg="Weather : " +str(self.temp) + "*C and " + self.climat
        affichage(msg)
        event.set()
        self.connectToHome(self.host,facteur)
        self.connectToMarket(self.host,facteur)
        sys.exit()
    #Connecter a la Marche pour lui donne le facteur climat
    def connectToMarket(self,host,facteur):
        port=5000
        try:
            s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        except sk.error:
            #print("ne peut pas creer un socket")
            time.sleep(1)
            sys.exit()
        while True:
         try:
            s.connect((host, port))
            break
         except sk.error:
            print('............')

        msg1=str(self.id)+" "+str(facteur)
        while True:
            s.send(msg1.encode('utf-8'))
            #print("Send complete")
            dataByte = s.recv(1024)
            data = dataByte.decode('utf-8')
            #print("receive complete " + data)
            if data:
                if "ok"in data:
                    self.valide=True
                break
            else:
                print("Error server")
                break
        s.close()


    #Connecter a l'Environnement pour lui donne le facteur climat
    def connectToHome(self,host,facteur):

        sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        port = 9000
        sock.bind((host, port))
        msg1 = str(self.temp) + " " + str(self.climat) + " " + str(facteur)
        sock.listen(5)
        client, adress = sock.accept()
        while True:
            try:

             client.send(msg1.encode('utf-8'))
             dataByte = client.recv(1024)
             data = dataByte.decode('utf-8')
             if "ok" in data:
                 #print("Home received")
                 break
             else:
                 print("Error")
                 break
            except:

                break
        client.close()
        sock.close()
    #Traiter le Temperature pour donner le facteur temp
    def tempfacteur(self):
        #print(self.temp)
        if self.temp in range(10,25):
            return 0.5*(1/self.temp)
        elif self.temp in range(0,10) :
            if self.temp==0:
                return 1.5
            else:
                return 1.5*(1/abs(self.temp))
        elif self.temp in range(-10,-1):
            return 2*(1/abs(self.temp))
        else:
            return 1/abs(self.temp)

    # Traiter le Climat pour donner le facteur climat
    def climatfacteur(self):
        #print(self.climat)
        if self.climat=="normal":
            return 0.25
        elif self.climat=="pluie":
            return 0.6
        elif self.climat=="soleil":
            return 0.4
        elif self.climat=="neige":
            return 0.8
        elif self.climat=="catas":
            return 1
        else:
            return 0

"""Fonction generale pour demarche ,recoit un signal d l horlore pour commence"""
def signa(queue,event):

    value=queue.get()
    queue.task_done()
    # Attende le signal de l'horlorge pour continuer et met le event
    if value==0:
        climat = Climat(0, 5000, "192.168.2.100")
        climat.start()
        #changez - vous le adress IP avec celui de vous pour communiquer TCP
        climat.controller(event)
        climat.join()
"""Fonction pour afficher"""
def affichage(msg):
    f = open("project_Energy.txt", 'a')
    f.write( msg + '\n')
    f.close()


"""Tous au desus est pour tester seulement ce processus"""
"""if __name__ == '__main__':
    event=Event()
    climat=Climat(0,5000,"192.168.2.100")
    climat.controller(event)"""