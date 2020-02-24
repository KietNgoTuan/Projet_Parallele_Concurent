"""
Author:NGO TUAN KIET
Voici c est une partie de mon projet sur le PPC
On creer un nombre de processus appelle"House" et jouer avec eux
"""

from multiprocessing import Process ,Manager ,Queue,Value
import random as rd
import time
import socket as sk
import sys

"""
Creer un processus Environnment qui recoit l annoncement du bulletin (Climat Process) via Socket
Et le passe aux processus House via Memoire Partage 

"""
class Enviromment(Process):
    # Environnement contient e principe TCP(host,port) pour communiquer a Clmat et
    # le temp pour enregistrer le valeur recois
      def __init__(self,host,port):
          super().__init__()
          self.temp=0
          self.host=host
          self.port=port
          self.connectToWeather(host,port)
      #Methode de connecter avec Le climat(Weather process)
      #Quand il a recu le valeur renvoie le msg "ok"
      def connectToWeather(self, host,port):

          try:
              s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
          except sk.error:
              time.sleep(1)
              sys.exit()
          while True:
              try:
                  s.connect((host, port))
                  break
              except sk.error:
                  print('............')
                  time.sleep(3)
          while True:
              dataByte = s.recv(1024)
              data = dataByte.decode('utf-8')
              if data:
                  value = data.split()
                  self.temp = float(value[2])
                  msg1 = "ok"
                  s.send(msg1.encode('utf-8'))
                  break
              else:
                  print("Server error")
                  s.close()
                  break
          s.close()

"""Processus House qui gene tous les parametre des maisons et les communquer entre eux et avec Marche"""
class House(Process):
    #House contient tous les parametres pour communiquer avec la Marche ,
    # en plus ,un ID ,le nombre d'argent , le facteur climat ,la production et consommation d energy
    # avec un queue particulaire ,les autres pour faciliter a traiter des cas differents
    def __init__(self,id,host,argent,n):

        super().__init__()
        self.id = id
        self.argent = argent
        self.taux =0 #le taux entre la production et la consommation
        self.receive=[]
        self.send=False #Indiquer que la maison demande une seule fois l'energy
        mp=Manager()
        self.request =mp.Queue()
        self.host=host
        self.valide =False #Indiquer tous les maisons sont fini de partager
        self.connect=False #Indiquer il a bien connecte a la Marche
        self.weather=0
        self.prod = rd.randrange(2, 50)
        self.consom = rd.randrange(2, 50)
        self.initiale(n)

    #Generation du facteur climat et le taux entre la production et la consommation
    def initiale(self,n):
        self.Weatherinfuence(n)
        self.taux = self.prod - self.consom
        if self.taux== 0:
            self.valide=True
    #Traitement la production et la consommation selon le facteur climat
    def Weatherinfuence(self,n):
        self.weather=round(n,3)
        if self.weather!=0:

          if self.weather>1:
           self.consom = int(self.consom / self.weather)
           self.prod = int(self.prod / self.weather)
          else:
              self.consom = int(self.consom * self.weather)
              self.prod = int(self.prod *self.weather)
        else:
            print("Error of weather")

    #Envoyer une demande d'energy au queue commun
    def sendRequesttoHome(self,queue):

        queue.put([self.request,abs(self.taux)])
        msg =str(self.id) + " Send request "+str(abs(self.taux))
        affichage(msg)
        return queue
    #Recevoir des demandes d'energy du queue commun
    def RequestfromHome(self,queue):
        if queue.empty():
            return

        besoin=queue.get()
        product = besoin[1]
        if self.taux>0:
           #Si la demande > son taux,il va le traiter jusqu a taux =0 et met le reste au queue commun
           if product >self.taux:
              self.valide = True
              reste = product - self.taux
              product=self.taux
              self.request=besoin[0]
              self.taux=reste
              msg = str(self.id) + " Receive request " + str(product)
              affichage(msg)
              self.sendRequesttoHome(queue)
              self.taux = 0
              self.request=Queue()
           #Si non ,il traite comme normal
           elif product <=self.taux:
               self.taux=self.taux-product
               msg = str(self.id) + " Receive request " + str(product)
               affichage(msg)
           self.prod=self.prod-product
           besoin[0].put(product)
        #si taux =0, il arrete de raiter
        if self.taux == 0:
            self.valide = True
    #Recevoir l'energy d autres maisons
    def ReadFromHome(self):
        value =self.request.get()
        self.prod=self.prod+value
        self.taux=self.taux+value
        msg=str(self.id)+" Take "+str(value)
        affichage(msg)

    #Communiquer avec la Marche via socket
    def connectToMarket(self,host):
      port=4999
      try:
        s= sk.socket(sk.AF_INET,sk.SOCK_STREAM)
      except sk.error:
          time.sleep(1)
          sys.exit()
      #Demande de connecter tous temps
      while True:
       try:
        s.connect((host,port))
        break
       except sk.error:
          print('............')
          time.sleep(1)

      msg1=str(self.id)+ " a "+str(abs(self.taux))
      msg2=str(self.id)+ " v "+str(abs(self.taux))


      while True:
          if self.taux <0:#Si manque d'energie ,l'acheter  de la marche avec argent
            s.send(msg1.encode('utf-8'))
            affichage(msg1)
            #print("Send complete " + msg1)
            dataByte =s.recv(1024)
            data =dataByte.decode('utf-8')
            msg=str(self.id)+" Receive complete " + str(data)
            #print("receive complete " +data)
            if data :
                value=data.split()
                if "-1" in value:
                    #print("Market out of stock in market")
                    affichage(" receive none because out of stock in market")
                    break
                price =float(value[1])
                if self.argent > price:
                 self.prod =self.prod + int(value[2])
                 self.argent =float(self.argent) - price
                 pricetopay = price
                 billet=str(pricetopay)
                 s.send(billet.encode('utf-8'))
                 #print("Send complete " +billet)
                else:
                  #print("vous n avez pas assez d argent")
                  msg = "Home "+ str(self.id) + "  dont have enough money"
                  affichage(msg)
                  err="-1"
                  s.send(err.encode('utf-8'))
                affichage(msg)
                break 
            else:
                print("Server error")
                break

          else:#Si surplus d'energie ,le vendre a la Marche et recuperer l'argent
            s.send(msg2.encode('utf-8'))
            #print("Send complete " + msg2)
            affichage(msg2)
            dataByte =s.recv(1024)
            data=dataByte.decode('utf-8')
            msg=str(self.id)+" Receive complete " + str(data)

            #print("Receive complete " + data)
            if data :
                value=data.split()
                money =float(value[1])
                if money >0 :
                    self.argent = float(self.argent)+money
                    self.prod =self.prod -self.taux
                affichage(msg)
                break
            else:
                print("Server error")
                break

      self.connect=True
      s.close()

"""2 Fonction pour simuler entre Maison"""
#Les Maisons exchange dans un queue commun
def simulationHome(h,queuedemande):
  if h.taux<0:
          h.valide=True
          if h.send==False:
             h.sendRequesttoHome(queuedemande)
             h.send=True
  else :
         while (h.valide == False ):
            time.sleep(0.1)
            h.RequestfromHome(queuedemande)
            if queuedemande.empty():
             break

def HometoHome(h):
    queuedemande = Queue()
    check = []
    n = 0
    while True:
        for i in h:
            n += 1
            simulationHome(i, queuedemande)
            if i.valide:
                check.append(i.valide)
        if (all(check) and len(check) >= len(h)) or (queuedemande.empty() and n >= len(h)):
            #Si le queue commun est vide ou il n y a pas l exchange possible ,sortie de la boucle
            n = 0
            break

    for i in h:
        while i.request.empty() != True:
            i.ReadFromHome()
"""Fonction gener des maisons ,
 changez - vous le adress IP avec celui de vous pour communiquer TCP """
def generation(n):

    h1 = House(0, "192.168.2.100", 1000, n)
    h2 = House(1, "192.168.2.100", 1000, n)
    h3 = House(2, "192.168.2.100", 1000, n)
    h4 = House(3, "192.168.2.100", 1000, n)
    h5 = House(4, "192.168.2.100", 1000, n)
    h = [h1, h2, h3, h4, h5]
    return h
"""Fonction generale pour demarche ,recoit un signal d l horlore pour commence"""
def signa(queue,event):
   event.wait()
   value=queue.get()
   queue.task_done()
   # Attende le signal event et le signal de l'horlorge pour continuer
   e = Enviromment("192.168.2.100", 9000)#changez - vous le adress IP avec celui de vous pour communiquer TCP
   n=Value('f',e.temp).value
   if value==0:
     h = generation(n)
     affichageGeneral(h)
     for i in h:
        i.start()
     HometoHome(h)
     for i in h:
        while (i.taux != 0 and i.connect != True):
            i.connectToMarket(i.host)
        i.join()

     affichageGeneral(h)


""" 2 Fonction pour afficher """
def affichageGeneral(h):
    f = open("project_Energy.txt", 'a')
    f.write("Home ID Production Consommation Argent " +'\n')
    for i in h :

        msg="Home " + str(i.id) + "      "+str(i.prod)+"         "+str(i.consom)+"       "+str(i.argent)
        f.write(msg + '\n')
    f.write("---------------------------" + '\n')
    f.close()
def affichage(msg):
    f = open("project_Energy.txt", 'a')
    f.write("Home "+msg +'\n')
    f.write('\n')
    f.close()

"""Tous au desus est pour tester seulement ce processus"""

"""if __name__ == '__main__':
    e = Enviromment("192.168.2.100", 9000)
    n=Value('i',e.temp).value
    h1 = House(0, "192.168.2.100", 1000, n)
    h2 = House(1, "192.168.2.100", 1000, n)
    h3 = House(2, "192.168.2.100", 1000, n)
    h4 = House(3, "192.168.2.100", 1000, n)
    h5 = House(4, "192.168.2.100", 1000, n)
    h = [h1, h2, h3, h4, h5]
    for i in h:
        i.start()
        
        print(i.taux)

    HometoHome(h)

    for i in h:
        while (i.taux != 0 and i.connect != True):
            i.connectToMarket(i.host)
        i.join()
    print("sadas")"""