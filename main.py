import os
import time
import random
import msvcrt

DEBUG = False

grid = []
grid_upgrade = 1
money = 100000
population = 0
pop_house = 3
max_population = 0
happiness = 0
energy = 0
energy_req = 0
water = 0
water_req = 0
shops = 0
industries = 0

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def addGrid(grid):
    for i in range(10):
        row = []
        for e in range(20):
            row.append(0)
        grid.append(row)
        
def progressBar(val,valMax, max=10):
    if val > valMax:
        val = valMax
    if valMax == 0:
        ratio = 0
    else:
        ratio = val/valMax
    barra = int(ratio * max)
    rimanente = max - barra
    return "[" + "█"*barra + " "*rimanente + "]"
        
def printGrid(grid, happiness=happiness):
    global conta
    clear()

    # 0 = vuoto
    # 1 = casa
    # 2 = negozio
    # 3 = industria
    # 4 = gen. acqua
    # 5 = gen. energia
    # 6 = scuola
    # 7 = ospedale
    # 8 = vigile del fuoco
    # 9 = polizia
    
    conta = 0
    print("    A B C D E F G H I J K L M N O P Q R S T")
    for row in grid:
        if conta < 10:
            print(f"0{conta} ", end="")
        else:
            print(f"{conta} ", end="")
        conta += 1
        for cell in row:
            if cell == 0:
                print(" ☐", end="")
            elif cell == 1:
                print("🏠", end="")
            elif cell == 2:
                print("🏠", end="")
            elif cell == 3:
                print("🏭", end="")
            elif cell == 4:
                print("💧", end="")
            elif cell == 5:
                print("⚡", end="")
            elif cell == 6:
                print("🏫", end="")
            elif cell == 7:
                print("🏥", end="")
            elif cell == 8:
                print("🚒", end="")
            elif cell == 9:
                print("🚓", end="")
        print()
    print("--------------------------------------------")
    print(f"            Upgrade Grid: {50000 * grid_upgrade}$")
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"┃ Soldi: \t {money}$ (+{income}$) ")
    print(f"┃ Popolazione: \t {progressBar(population, max_population)} {population}/{max_population}")
    print(f"┃ Felicità: \t {progressBar(happiness, 10)} {happiness}/10")
    print(f"┃ Energia: \t {progressBar(energy, energy_req)} {energy}/{energy_req}")
    print(f"┃ Acqua: \t {progressBar(water, water_req)} {water}/{water_req}")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print("      Premi 'Invio' per aprire il menu.")
        
        
def printSimpleGrid(grid):
    global conta
    clear()

    # 0 = vuoto
    # 1 = casa
    # 2 = negozio
    # 3 = industria
    # 4 = gen. acqua
    # 5 = gen. energia
    # 6 = scuola
    # 7 = ospedale
    # 8 = vigile del fuoco
    # 9 = polizia
    
    conta = 0
    print("    A B C D E F G H I J K L M N O P Q R S T")
    for row in grid:
        if conta < 10:
            print(f"0{conta} ", end="")
        else:
            print(f"{conta} ", end="")
        conta += 1
        for cell in row:
            if cell == 0:
                print(" ☐", end="")
            elif cell == 1:
                print("🏠", end="")
            elif cell == 2:
                print("🛍️", end="")
            elif cell == 3:
                print("🏭", end="")
            elif cell == 4:
                print("💧", end="")
            elif cell == 5:
                print("⚡", end="")
            elif cell == 6:
                print("🏫", end="")
            elif cell == 7:
                print("🏥", end="")
            elif cell == 8:
                print("🚒", end="")
            elif cell == 9:
                print("🚓", end="")
        print()
    print()
        
def buyMore_Grid(grid, money):
    global grid_upgrade
    cost = 50000 * grid_upgrade
    if money >= cost:
        addGrid(grid)
        money -= cost
        grid_upgrade += 1
    return money

def calcHappiness():
    global happiness, grid, energy, energy_req, water, water_req, population

    score = 10

    # Energia: calcolo semplice della penalità
    if energy_req > 0 and energy < energy_req:
        shortage = (energy_req - energy) / energy_req
        penalty = int(shortage * 5) + 1
        score = score - penalty

    # Acqua: stessa cosa per l'acqua
    if water_req > 0 and water < water_req:
        shortage = (water_req - water) / water_req
        penalty = int(shortage * 5) + 1
        score = score - penalty

    # Controllo servizi essenziali uno per uno
    has_school = False
    has_hospital = False
    has_fire = False
    has_police = False

    for row in grid:
        for cell in row:
            if cell == 6:
                has_school = True
            if cell == 7:
                has_hospital = True
            if cell == 8:
                has_fire = True
            if cell == 9:
                has_police = True

    # Penalità per ogni servizio mancante
    if not has_school:
        score = score - 1
    if not has_hospital:
        score = score - 1
    if not has_fire:
        score = score - 1
    if not has_police:
        score = score - 1

    # Bonus se energia e acqua soddisfatte e tutti i servizi ci sono
    if energy >= energy_req and water >= water_req and has_school and has_hospital and has_fire and has_police:
        score = score + 1

    # Limita tra 0 e 10
    if score < 0:
        score = 0
    if score > 10:
        score = 10

    happiness = score
    return happiness

def calcEnergy():
    global energy, grid, max_population, energy_req, shops, industries
    energy_req = max_population // 3
    energy_req += shops 
    energy_req += industries * 2
    energy = 0
    for row in grid:
        for cell in row:
            if cell == 5:
                energy += 25
    return energy

def calcWater():
    global water, grid, max_population, water_req, shops, industries
    water_req = max_population // 3
    water_req += shops 
    water_req += industries * 2
    water = 0
    for row in grid:
        for cell in row:
            if cell == 4:
                water += 25
    return water

"""
def calcPopulation():
    global population, grid, pop_house
    population = 0
    for row in grid:
        for cell in row:
            if cell == 2:
                population += pop_house  # ogni casa supporta 'pop_house' persone
    return population
"""
def calcPopulation():
    """
    ogni volta che viene chiamata questa funzione, la popolazione potrebbe aumentare o diminuire in base alla felicità, 
    la popolazione non cambia sempre ad ogni chiamata, ma c'è una probabilità del 10% che cambi. 
    """
    
    global population, grid, pop_house, max_population, happiness, shops, industries
    # Calcola la popolazione massima basata sulle case
    max_population = 0
    for row in grid:
        for cell in row:
            if cell == 1:
                max_population += pop_house  # ogni casa supporta 'pop_house' persone
            if cell == 2:
                max_population += pop_house // 2  # ogni negozio supporta metà della popolazione di una casa
            if cell == 3:
                max_population += pop_house // 3  # ogni industria supporta un terzo della popolazione di una casa
    # Solo il 30% di probabilità di cambiare la popolazione
    rnd = random.random()
    if rnd <= 0.3:
        if happiness == 7 and rnd <= 0.1:
            increase = int(max_population * 0.05)
            if increase < 1:
                increase = 1
            population += increase
        elif happiness == 8 and rnd <= 0.2:
            increase = int(max_population * 0.05)
            if increase < 1:
                increase = 1
            population += increase
        elif happiness >= 9 and rnd <= 0.3:
            increase = int(max_population * 0.05)
            if increase < 1:
                increase = 1
            population += increase
        elif happiness <= 4:
            # Diminuisce la popolazione del 5% della capacità massima
            decrease = int(max_population * 0.05)
            if decrease < 1:
                decrease = 1
            population -= decrease

        # Assicurati che la popolazione non superi la capacità massima o scenda sotto zero
        if population > max_population:
            population = max_population
        if population < 0:
            population = 0
               
    return population

history = []

def getMoney():
    global money, income
    income = 0
    rnd = random.random()
    if rnd <= 0.25:
        income = int(population * 0.3 + shops * 0.5 + industries * 0.8) * 10
        money += income

def box(scelte, divisore="*", separatore="-", preZero=False, startZero=False, startNum=True):
    righe = []
    if startNum:
        n = 0
        if not startZero:
            n=1
        if preZero:
            for scelta in scelte:
                righe.append(f"{divisore} {n:02d} {separatore} {scelta} ")
                n += 1
        else:
            for scelta in scelte:
                righe.append(f"{divisore} {n:2d} {separatore} {scelta} ")
                n += 1
    else:
        for scelta in scelte:
            righe.append(f"{divisore} {scelta} ")

    lmax=0
    for riga in righe:
        if lmax < len(riga):
            lmax = len(riga)
    bordo = divisore * (lmax+1)
    print(bordo)
    for riga in righe:
        print(riga + " "*int(lmax-len(riga))+ divisore)
    print(bordo)

def menu():
    global grid, money, shops, industries
    clear()

    options = ("Costruisci", "Migliora Griglia ", "Esci")
    box(options, divisore="#", separatore="-", startZero=False, startNum=True)
    err = True
    while err:
        scelta = input(">> Seleziona un'opzione: (1-3) ")
        if scelta == "1":
            clear()
            while err:
                printSimpleGrid(grid)
                print("Costruisci cosa? (Costo: 1000$ per ogni costruzione,\nrimpiazza l'elemento precedente)")
                options = ("Vuoto", "Casa", "Negozio", "Industria", "Generatore Acqua", "Generatore Energia", "Scuola", "Ospedale", "Vigile del Fuoco", "Polizia")
                box(options, divisore="#", separatore="-", startZero=True, startNum=True)
                scelta = input(">> Seleziona un'opzione: (0-9) ")
                corr = ("0","1","2","3","4","5","6","7","8","9")
                chars = ("A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T")
                if scelta in corr:
                    while err:
                        x_coord = input(">> Inserisci coordinata X (A-T): ").upper()
                        if x_coord in chars:
                            x_index = chars.index(x_coord)
                            while err:
                                y_coord = input(f">> Inserisci coordinata Y (0-{conta-1}): ")
                                if y_coord.isdigit() and y_coord >= '0' and int(y_coord) < conta:
                                    if scelta == "2":
                                        shops += 1
                                    elif scelta == "3":
                                        industries += 1
                                    elif scelta == "0":
                                        if grid[int(y_coord)][x_index] == 2:
                                            shops -= 1
                                        elif grid[int(y_coord)][x_index] == 3:
                                            industries -= 1
                                    updategrid(grid, (int(y_coord), x_index), int(scelta), money)     
                                    err = False
        elif scelta == "2":
            money = buyMore_Grid(grid, money)
            print("Miglioramento Griglia in corso...")
            err = False
        elif scelta == "3":
            err = False
        else:
            print("Scelta non valida. Riprova.")

def updategrid(grid, coord, valore, money):
        x = coord[0]
        y = coord[1]
        grid[x][y] = valore
        return money - 1000  

def debug(grid):
    # Ensure we update the module-level values used elsewhere
    global population, energy_req, water_req, happiness, energy, water, money
    addGrid(grid)
    printGrid(grid)
   
    for i in range(10):
        money = updategrid(grid, (0, i), i+1, money)
        money = updategrid(grid, (i, 0), i+1, money)
        money = updategrid(grid, (i, i+1), 2, money)
        money = updategrid(grid, (i, i), 1, money)
    
    printGrid(grid)
    
    #money = buyMore_Grid(grid, money)
    population = 15
    # Recalculate global happiness based on globals
    calcHappiness()
    # aggiorna i requisiti dopo aver cambiato la popolazione, ricalcola e stampa
    
    calcPopulation()
    calcEnergy()
    calcWater()
    calcHappiness()
    printGrid(grid, happiness)
    
def play():
    global money, population, shops, industries
    addGrid(grid)
    
    run = True
    while run:
        clear()
        calcEnergy()
        calcWater()
        calcPopulation()
        calcHappiness()
        getMoney()
        printGrid(grid, happiness)
        # Se c'è un tasto premuto
        if msvcrt.kbhit() and msvcrt.getch() == b'\r':
            menu()
        time.sleep(.5)
        
if DEBUG:
    debug(grid)
else:
    play()