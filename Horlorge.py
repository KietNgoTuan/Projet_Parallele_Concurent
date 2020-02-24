from multiprocessing import Process ,Event,JoinableQueue
import threading as t
import time
import Weather as w
import Market as mk
import Home as h

"""Envoie le stop pour que les prosees """
class Clock(Process):
    #Ce prosessus a un queue rejoint et un signal a envoyer
      def __init__(self):
          super().__init__()
          self.queue=JoinableQueue()
          self.signal=0
      #Metre le signal dans son queue
      def sendsignal(self):
           self.queue.put(self.signal)
           self.queue.put(self.signal)
           self.queue.put(self.signal)


if __name__ == '__main__':
 """Lancer le projet ,envoyer le queue de tache pour les autres processus"""
 event = Event()
 clock = Clock()
 #Remettre le valeur pour les nouveaux testes
 mk.Marche("", 8000).reset()
 f = open("project_Energy.txt", 'w')
 f.write("")
 """Mettre une boucle for pour test en 5 fois ,
 peut faire avec une boucle infine dans une periode du temps"""
 for i in range(5):
    clock.sendsignal()
    cl=clock.queue
    f = open("project_Energy.txt", 'a')
    f.write("Day " + str(i + 1) + "\n")
    f.write("********************" + "\n")
    thread1 = t.Thread(target=w.signa, args=(cl,event))
    thread2 = t.Thread(target=h.signa, args=(cl,event))
    thread3 = t.Thread(target=mk.signa, args=(cl, event))
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()
    cl.join()
    print(i+1)
    time.sleep(0.7)
    event.clear()

