""" MA3.py

Student: Malva Jindanet Åberg
Mail: malva.jindanet-aberg.1343@student.uu.se 
Reviewed by:
Date reviewed:

"""
import random
import matplotlib.pyplot as plt
import math as m
import concurrent.futures as future
from statistics import mean 
from time import perf_counter as pc
from numba import njit

# Exc1
def approximate_pi(n):
    # n is the number of points
    # Write your code here

    def random_n_koord(n):
        x = [] #lista som sparar x-koord.
        y = [] #lista som sparar y-koord.
        for i in range(n): #n är antalet punkter, och för varje punkt ska en koord. skapas 
            #för varje punkt skapas 2 koordinater
            x.append(random.random())
            y.append(random.random())
        return (x,y) #returnerar hela listorna 
    x, y = random_n_koord(n) #x, y kommer då innehålla koordinaterna
    n_c = 0 #punkter som ligger i cirkeln
    for i in range(n): #för varje punkt
        if (x[i]**2 +y[i]**2)**0.5 <= 1: #kontrollera avståndet till origo och om det är mindre än 1 lägg till i n_c
            n_c +=1
    pi = 4 *(n_c/n)
    return pi

# Exc2, approximation
def sphere_volume(n, d): 
    # n is the number of points
    # d is the number of dimensions of the sphere
    # koordinat = [random.random() for i in range (d)] #skapar d-antal random koordinater
    
    punkter_med_koordinater =[[random.random() for i in range (d)] for j in range(n)] #n-antal punkter med d-antal random koordinater
    listade_n_c = list(filter(None,map((lambda punkt:(sum(koord**2 for koord in punkt))**0.5 <=1), punkter_med_koordinater)))
    # lista (filter (None,..) behåller bara det som är True från map)
    # map(funktion,listan som gås igenom) 
    #funktionen är att beräkna om avståndet för varje punkt <=1
    #avståndet beräknas genom att ta roten av (summan av varje koordinat^2 i en punkt)
    n_c = len(listade_n_c) #antal punkter innanför sfären


    volym = (2**d)*(n_c/n)
# Punkterna slumpas mellan 0-1 i alla dimensioner
#n_c/n uppskattar volymen av sfärens del där koordinaterna är pos.
# vill undersöka den del där alla koordinater är positiva, varje koordinat kan ha 2 tecken
# med d-koordinater finns alltså 2^d teckenkombinationer och då även 2^d lika stora delar 
#multiplikation med (2**d) ger en uppskattning av hela sfärensvolym
    return volym

#Exc2, real value
def hypersphere_exact(n, d):
    # n is the number of points
    # d is the number of dimensions of the sphere 

    täljare = (m.pi)**(d/2)
    nämnare = m.gamma(d/2 +1)
    volym = täljare/nämnare
    return volym

#skriva ut:
# print (f' (n,d) = (100000, 2), min approximation: {sphere_volume(100000, 2)}, den exakta : {hypersphere_exact(100000, 2)}')
# print (f' (n,d) = (100000, 11), min approximation: {sphere_volume(100000, 11)}, den exakta : {hypersphere_exact(100000, 11)}')


#Exc3: numba version
@njit
def sphere_volume_numba(n:int, d:int)->float:
    # n is the number of points
    # d is the number of dimensions of the sphere
    #np is the number of processes
    punkter_med_koordinater =[[random.random() for i in range (d)] for j in range(n)] #n-antal punkter med d-antal random koordinater
    #listade_n_c = list(filter(None,map((lambda punkt:(sum(koord**2 for koord in punkt))**0.5 <=1), punkter_med_koordinater)))
    listade_n_c =[]
    for punkt in punkter_med_koordinater:
        # avstånd = [sum(koord**2 for koord in punkt)**0.5]
        summa = 0 
        for koord in punkt:
            summa += koord**2
        avstånd = summa**0.5
        if avstånd <= 1:
            listade_n_c.append(avstånd)
    n_c = len(listade_n_c) 
    volym = (2**d)*(n_c/n)
    return volym

#Exc4: parallel code - parallelize actual computations by splitting data
def for_varje_process (process_antal_punkter, d): #hjälpfunktion
    punkter_med_koordinater =[[random.random() for i in range (d)] for j in range(process_antal_punkter)] 
    listade_n_c_per_process = list(filter(None,map((lambda punkt:(sum(koord**2 for koord in punkt))**0.5 <=1), punkter_med_koordinater)))
    n_c_per_process = len(listade_n_c_per_process) #antal punkter innanför sfären
    return n_c_per_process

def sphere_volume_parallel(n, d, np=10):
    # n is the number of points
    # d is the number of dimensions of the sphere
    # np is the number of processes
    processer = [] # alla processer måste sparas i en lista för att alla ska kunna sättas samman sen
    resultat_from_processer =[]
    process_antal_punkter = n//np
    

    with future.ProcessPoolExecutor() as ex:
        for _ in range (np):
            p = ex.submit(for_varje_process, process_antal_punkter, d) #metod som vill användas är hjälpfunktionen, med de argument som behövs
            processer.append(p) #för varje gång en process körts så ska det sparas i en lista 
  
        for p in processer:
            r = p.result()
            resultat_from_processer.append(r)
    
    n_c = sum(resultat_from_processer) #summerar alla 10 prcessers antal n_c:n
    volym = (2**d)*(n_c/n)

    return volym
    
def main():
    # Exc1
    dots = [1000, 10000, 100000]
    for n in dots:
        approximate_pi(n)

    # Exc2
    n = 100000
    d = 2
    sphere_volume(n, d)
    print(f"Actual volume of {d} dimentional sphere = {hypersphere_exact(n,d)}")

    n = 100000
    d = 11
    sphere_volume(n, d)
    print(f"Actual volume of {d} dimentional sphere = {hypersphere_exact(n,d)}")

    # Exc3
    n = 1000000
    d = 11
    start = pc()
    sphere_volume(n, d)
    stop = pc()
    print(f"Exc3: Sequential time of {d} and {n}: {stop-start}")
    print("What is numba time?")

    # Exc4
    n = 1000000
    d = 11
    start = pc()
    sphere_volume(n, d)
    stop = pc()
    print(f"Exc4: Sequential time of {d} and {n}: {stop-start}")
    start = pc()
    sphere_volume_parallel (n,d,np=10)
    stop = pc()
    print("What is parallel time?")
    print(f"Exc4: Parallel time of {d} and {n}: {stop-start}")

    
    

if __name__ == '__main__':
	main()
