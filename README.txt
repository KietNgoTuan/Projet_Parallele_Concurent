*********** PROJET ENERGY_MARKET***********
+)Author:NGO TUAN KIET
+)Projet pour le but d'appliquer la programmation parallele et concurrente en Python
+)Explication de la conception :
   -,Les Maisons parlent entre eux via queue ,il met la demande d'energie dans un queue commun,et transfers directement l'energie via leur queue
     Elles recoivent le facteur Climat par Mempoire Partage via Environnement qui parle avec Le climat(Process) via socket
     Elles traitent le consommation et la production selon ce facteur 
     Elles communiquent apres avec la Marche via socket
   -,La Marche communique avec Le facteur externe via signal pour recuperer le facteur different (Decresing tax of transport ou Price of fuel increasing )
     Elle parle avec Le Climat via socket et recupere le facteur climat
     Elle calcule le cout d energie
     Elle parle avec les maisons et leur exchange via socket avec un nouveau port et multhithread,chaque thread s'occupe 1 maisons(Seulement 3 threads disponible en meme temp)
     Elle sauvegarde le valeur du stock ,vente ,achat,argent,le prix d'energie
   -,Le Climat recupere le facteur climat avec Le Climat parametre par La memoire partage 
     Il le traite selon temperature(-10*C,35*C) et climat(pluie,neige,normal,soleil,ou catastrophe)
     Il le renvoie a l'Environnement du Home via socket
     Il le renvoie a la Marche via socket 
   -,La Horlorge envoie le signal(stop) aux autres processus grace un queue de tache(JoinableQueue) chaque fois
     Elle redonne quand tous les processus sont finis (task_done)
     
 
+)Instruction :****Attention:Changer l adress IP (host) avec celui de vous pour communiquer TCP****
  -,Lancez le fichier Horlorge.py 
  _,Observer dans le fichier project_Energy.txt qui indique Le climat et le facteur externe au debut
    Apres il affiche les etats initiales des maisons
    puis ,les exchanges entre les maisons
    puis, l'etat initial de la marche
    puis ,Les exchanges entre la marche et les maisons
    puis ,il affiche les etats actuels des maisons et de la marche et du prix d'energie
    enfin ,il termine et indique le jour 