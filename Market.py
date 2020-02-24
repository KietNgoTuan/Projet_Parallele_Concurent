from multiprocessing import Process ,Event,Queue
import os,time,signal
import random as rd
import socket as sk
import threading as t
"""Processus de la marche qui va prend un facteur externe via signal ,un facteur climat via socket,
un facteur interne , buy and sell and communique avec les maisons via socket
"""
class Marche(Process):
    #Il conteint 5 valeur statique qui va etre change selon evolution du temps
    #Il s'agit :le nombre d'enrgie stocke ,d'argent,d'energie  vendue,d'energie achetee,et de prix d l'energie
    __stock=1000
    __argent=1000
    __sold=0
    __bought=0
    __price=2

    # Il contient tous les para pour connecter TCP ,les 2 faceurs externes ,le id
    def __init__(self,host,port):
        super().__init__()
        self.id = os.getpid()
        self.weather = 0
        self.facteur = 0
        self.stock=Marche.__stock
        self.argent=Marche.__argent
        self.sold=Marche.__sold
        self.bought=Marche.__bought
        self.price=Marche.__price
        self.host=host
        self.port =port
        self.queue=Queue()
    #Creer un thread pour parler avec Climat(Process) via socket via la methode "listentoWeather"
    def controllerWeather(self):
        sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        port=5000
        sock.bind((self.host,port))
        sock.listen(5)
        while True:
         try:
                client, adress = sock.accept()
                thread = t.Thread(target=self.listenToWeather, args=(client, adress))
                thread.start()
                thread.join()
                break
         except:
            print("error")
            break
        sock.close()
        time.sleep(1)

    # Creer un nombre de thread fini pour parler avec House(Process) via socket via la methode "listentoClient"
    # Il va synchoniser seulement 3 thread avec Semaphore qui parle ,les autres doivent attendre
    # Mettre une periode du temps pour parler avec client ,ici settimeout=5
    def controllerHome(self):
       self.sema = t.BoundedSemaphore(3)
       lock = t.Lock()
       sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
       port =4999
       sock.bind((self.host, port))
       sock.listen(5)

       while True:
           self.sema.acquire()
           try:
             client, adress = sock.accept()
             sock.settimeout(5)

             #self.lock.acquire()
             thread=t.Thread(target=self.listenToClient, args=(client,adress,lock))

             time.sleep(0.1)
             thread.start()
             thread.join()

           except  :
               break
           finally:
               self.sema.release()
       sock.close()
    #Exchange les donnee avec le Climat(Process)
    def listenToWeather(self,client,adress):
        while True:
            try:
                dataByte =client.recv(1024)
                data=dataByte.decode('utf-8')
                #print("Received : " + data)
                if data:
                    value=data.split()
                    self.weather = float(value[1])
                    msg1="ok"
                    client.send(msg1.encode('utf-8'))
                    break
                else:
                   err = "Payment -1"
                   client.send(err.encode('utf-8'))
                   break
            except:
                client.close()
                break
        client.close()

    # Exchange les donnee avec le House(Process)
    # Utiliser Lock pour chaque thread accede au valeur commune(stock ,buy ,sell,argent)
    def listenToClient(self,client,adress,lock):
        self.EnergyPrice()
        while True:

            try:
                dataByte =client.recv(1024)
                data=dataByte.decode('utf-8')

                #print("Received : " + data)

                if data :

                    value=data.split()
                    if "v" in value:# Home Vendre
                        msg = "Market buy "+ str(value[2])+" energy from Home " +str(value[0])
                        affichage(msg)
                        energy =int(value[2])
                        payment=self.Payment(energy)
                        #print("Payment :" +str(payment))
                        if Marche.__argent > payment:
                          msg1="Payment "+str(payment)
                          client.send(msg1.encode('utf-8'))

                          lock.acquire()
                          Marche.__argent=float(Marche.__argent)-payment
                          self.argent=Marche.__argent
                          Marche.__stock=Marche.__stock + energy
                          self.stock=Marche.__stock
                          Marche.__bought=Marche.__bought + energy
                          self.bought=Marche.__bought
                          #print("Send complete")
                          break
                        else:
                          err="Payment -1"
                          client.send(err.encode('utf-8'))


                    elif "a" in value:#Home Acheter

                        energy =int(value[2])
                        require=self.PricetoBuy(energy)
                        #print("Require :" +str(require))
                        if Marche.__stock==0:
                            break
                        if Marche.__stock >= energy:
                          msg2 ="Require " +str(require) + " " +str(energy)
                          msg = "Market sell  " + str(value[2]) + " energy to Home " + str(value[0])
                          affichage(msg)
                        else:
                            msg2="-1"
                        client.send(msg2.encode('utf-8'))

                        #print("Send complete")
                        receiveByte =client.recv(1024)
                        receive =receiveByte.decode('utf-8')

                        #print("Received : " + receive)
                        if receive !="-1":

                         lock.acquire()
                         Marche.__argent=float(Marche.__argent) + float(receive)
                         self.argent = Marche.__argent
                         Marche.__sold=Marche.__sold + energy
                         self.sold=Marche.__sold
                         Marche.__stock=Marche.__stock - energy
                         self.stock = Marche.__stock
                        break

                else:
                    #print("Bye")
                    break
            except:

                client.close()
                break

        lock.release()
        client.close()


    #Calculer l'argent pour que la Marche achete l' energie des Maison
    def Payment(self,energy):
        if Marche.__price>2:
         facteur =2
        else:
         facteur =1.2
        return round(facteur*(energy),2)

    # Calculer l'argent pour que la Maison achete l' energie de la Marche
    def PricetoBuy(self,energy):

        return round(Marche.__price*(energy),2)
    # Calcule Le prix de l'energie
    def EnergyPrice(self):
        attenuation = 0.08
        Marche.__price = float(Marche.__price)*attenuation + 0.002 *(self.weather + float(Marche.__bought + Marche.__sold)) + 0.02*self.facteur
        self.price=Marche.__price
        self.weather = 0
        self.facteur = 0
        return round(Marche.__price,2)
    """Ces 2 fonctions la pour communiquer Le Marche avec Le facteur externe (d'enfant processus) via signal"""
    def Facteur(self,event):
        event.wait()
        #print("this is facteur", os.getpid())
        try:
            value = rd.randint(-100, 100)/100.00
            if value<0:
                msg="Decresing tax of transport : "
            else:
                msg= "Price of fuel increasing  : "
            affichage(msg + str(value))
            self.queue.put(value)

        except KeyboardInterrupt:

            print("got KeyboardInterrupt")
        #print("'a_task' is at end")


    def Calcul(self ):
        event=Event()
        p = Process(target=self.Facteur, args=(event,))
        p.start()
        event.set()
        time.sleep(3)
        try:
            os.kill(p.pid, signal.SIGTERM)
        except:
            pass
        self.facteur =self.queue.get()
    #Remettre le valeur initial pour les nouveaux testes
    def reset(self):
         Marche__stock = 1000
         Marche__argent = 1000
         Marche__sold = 0
         Marche__bought = 0
         Marche__price = 2

"""Fonction generale pour demarche ,recoit un signal d l horlore pour commence"""
def signa(queue,event):
    value=queue.get()
    event.wait()
    #Attende le signal event et le signal de l'horlorge pour continuer
    if value==0:
        host = ""
        server = Marche(host, 8000)
        server.Calcul()
        msg = "Market( " + " Stock :" + str(server.stock) + " ;Sell : " + str(server.sold) + " ;Buy :" + str(server.bought) + " ;Money : " + str(server.argent) +" )"
        affichage(msg)

        if server.weather==0:
          server.controllerWeather()
          msg="Factor weather : " +str(server.weather)
          affichage(msg)
          msg2= "Facteur internal :" +str(server.facteur)
          affichage(msg2)
        server.controllerHome()


        msg="Market( " + " Stock :" +str(server.stock) +" ;Sell : " +str(server.sold)+ " ;Buy :" +str(server.bought) +" ;Money : "+ str(server.argent)+" )"
        affichage(msg)
        msg1="Energy Price :" +str(server.price)
        affichage(msg1)
        server.facteur = 0
        server.weather = 0
        queue.task_done()

"""Fonction pour afficher"""
def affichage(msg):
    f = open("project_Energy.txt", 'a')
    f.write( msg + '\n')
    f.close()

"""Tous au desus est pour tester seulement ce processus"""
"""if __name__ == '__main__':
    host=""
    port=8000
    server = Marche(host, port)
    """