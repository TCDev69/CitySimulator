import flet as ft
import random
import time
from threading import Thread
import json

# Variabili globali
grid = []
history = []
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
moneyMed = 0
income = 0
demand_house = 0
demand_shop = 0
demand_industry = 0
tax_rate = 10  # percentuale tasse
game_running = False

# Emoji per gli edifici
BUILD_ICONS = {
    0: "☐",
    1: "🛣️",  # Strada
    2: "🏠",
    3: "🛍️",
    4: "🏭",
    5: "💧",
    6: "⚡",
    7: "🏫",
    8: "🏥",
    9: "🚒",
    10: "🚓"
}

BUILD_NAMES = {
    0: "Vuoto",
    1: "Strada",
    2: "Casa",
    3: "Negozio",
    4: "Industria",
    5: "Generatore Acqua",
    6: "Generatore Energia",
    7: "Scuola",
    8: "Ospedale",
    9: "Vigile del Fuoco",
    10: "Polizia"
}

BUILD_COSTS = {
    0: "-100",   # demolizione
    1: "-300",   # strada
    2: "-1000",
    3: "-1500",
    4: "-2000",
    5: "-5000",
    6: "-5000",
    7: "-8000",
    8: "-8000",
    9: "-8000",
    10: "-8000"
}

def load():
    global grid, money, population, pop_house, max_population, happiness
    global energy, energy_req, water, water_req, shops, industries
    global moneyMed, history, income, grid_upgrade, tax_rate

    try:
        with open("savegame.json", "r") as f:
            data = json.load(f)
            grid = data["grid"]
            money = data["money"]
            population = data["population"]
            pop_house = data["pop_house"]
            max_population = data["max_population"]
            happiness = data["happiness"]
            energy = data["energy"]
            energy_req = data["energy_req"]
            water = data["water"]
            water_req = data["water_req"]
            shops = data["shops"]
            industries = data["industries"]
            moneyMed = data["moneyMed"]
            history = data["history"]
            income = data["income"]
            grid_upgrade = data["grid_upgrade"]
            tax_rate = data.get("tax_rate", 10)
            recount_structures()
    except FileNotFoundError:
        data = json.load(f)
        grid = data["grid"]
        money = data["money"]
        population = data["population"]
        pop_house = data["pop_house"]
        max_population = data["max_population"]
        happiness = data["happiness"]
        energy = data["energy"]
        energy_req = data["energy_req"]
        water = data["water"]
        water_req = data["water_req"]
        shops = data["shops"]
        industries = data["industries"]
        moneyMed = data["moneyMed"]
        history = data["history"]
        income = data["income"]
        grid_upgrade = data["grid_upgrade"]
        
def save(e=None):
    global grid, money, population, pop_house, max_population, happiness
    global energy, energy_req, water, water_req, shops, industries
    global moneyMed, history, income, grid_upgrade, tax_rate

    data = {
        "grid": grid,
        "money": money,
        "population": population,
        "pop_house": pop_house,
        "max_population": max_population,
        "happiness": happiness,
        "energy": energy,
        "energy_req": energy_req,
        "water": water,
        "water_req": water_req,
        "shops": shops,
        "industries": industries,
        "moneyMed": moneyMed,
        "history": history,
        "income": income,
        "grid_upgrade": grid_upgrade,
        "tax_rate": tax_rate
    }

    with open("savegame.json", "w") as f:
        json.dump(data, f)       
        print("Game saved.") 


def recount_structures():
    """Ricalcola negozi e industrie in base alla griglia corrente."""
    global shops, industries
    shops = 0
    industries = 0
    for row in grid:
        for cell in row:
            if cell == 3:
                shops += 1
            elif cell == 4:
                industries += 1

def addGrid(grid):
    for i in range(10):
        row = []
        for e in range(20):
            row.append(0)
        grid.append(row)

def calcHappiness():
    global happiness, grid, energy, energy_req, water, water_req, population

    score = 10

    # Energia
    if energy_req > 0 and energy < energy_req:
        shortage = (energy_req - energy) / energy_req
        penalty = int(shortage * 5) + 1
        score = score - penalty

    # Acqua
    if water_req > 0 and water < water_req:
        shortage = (water_req - water) / water_req
        penalty = int(shortage * 5) + 1
        score = score - penalty
        
    if tax_rate > 20:
        score -= 2
    elif tax_rate > 10:
        score -= 1
    elif tax_rate < 5:
        score += 1        

    # Servizi pubblici
    school_count = 0
    hospital_count = 0
    fire_count = 0
    police_count = 0

    for row in grid:
        for cell in row:
            if cell == 7:
                school_count += 1
            if cell == 8:
                hospital_count += 1
            if cell == 9:
                fire_count += 1
            if cell == 10:
                police_count += 1

    service_capacity = 50
    min_capacity = min(
        school_count * service_capacity if school_count > 0 else 0,
        hospital_count * service_capacity if hospital_count > 0 else 0,
        fire_count * service_capacity if fire_count > 0 else 0,
        police_count * service_capacity if police_count > 0 else 0
    )

    # Penalità se manca almeno un servizio
    if school_count == 0 or hospital_count == 0 or fire_count == 0 or police_count == 0:
        score -= 2  # penalità maggiore se manca almeno uno

    # Penalità se la popolazione supera la capacità minima
    if population > min_capacity and min_capacity > 0:
        score -= 2

    # Bonus se tutto ok
    if (
        energy >= energy_req and water >= water_req and
        school_count > 0 and hospital_count > 0 and fire_count > 0 and police_count > 0 and
        population <= min_capacity
    ):
        score += 1

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
            if cell == 6:
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
            if cell == 5:
                water += 25
    return water

def calcDemand():
    global demand_house, demand_shop, demand_industry, population, shops, industries, happiness, max_population

    # Domanda case: cresce se la popolazione è vicina alla capacità massima
    if max_population == 0:
        demand_house = 100
    else:
        ratio = population / max_population if max_population > 0 else 0
        demand_house = int((ratio * 100) + (happiness - 5) * 5)
        demand_house = max(0, min(demand_house, 100))

    # Domanda negozi: cresce se ci sono molte case e pochi negozi
    demand_shop = max(0, min(100, int((population / (shops + 1)) * 2)))
    # Domanda industrie: cresce se ci sono molti negozi e poche industrie
    demand_industry = max(0, min(100, int((shops / (industries + 1)) * 2)))

def calcPopulation():
    global population, grid, pop_house, max_population, happiness, shops, industries
    max_population = 0
    for row in grid:
        for cell in row:
            if cell == 2:
                max_population += pop_house
            if cell == 3:
                max_population += pop_house // 2
            if cell == 4:
                max_population += pop_house // 3

    # Calcolo capacità servizi pubblici
    school_count = 0
    hospital_count = 0
    fire_count = 0
    police_count = 0
    for row in grid:
        for cell in row:
            if cell == 7:
                school_count += 1
            if cell == 8:
                hospital_count += 1
            if cell == 9:
                fire_count += 1
            if cell == 10:
                police_count += 1
    service_capacity = 50
    min_capacity = min(
        school_count * service_capacity if school_count > 0 else 0,
        hospital_count * service_capacity if hospital_count > 0 else 0,
        fire_count * service_capacity if fire_count > 0 else 0,
        police_count * service_capacity if police_count > 0 else 0
    )

    # La popolazione non può superare la capacità minima dei servizi pubblici
    if min_capacity == 0:
        population = 0
    elif population > min_capacity:
        population = min_capacity

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
            decrease = int(max_population * 0.05)
            if decrease < 1:
                decrease = 1
            population -= decrease

        # Limite massimo popolazione
        if population > max_population:
            population = max_population
        # Limite servizi pubblici
        if min_capacity > 0 and population > min_capacity:
            population = min_capacity
        if population < 0:
            population = 0

    return population

def getMoney():
    global money, income, moneyMed, population, shops, industries, history, tax_rate
    # Reddito base da popolazione e attività
    taxable = int(population * 1.2 + shops * 4 + industries * 6)
    income = int(taxable * (tax_rate / 100))
    money += income
    history.append(income)
    if len(history) > 10:
        history.pop(0)
    moneyMed = sum(history) // len(history) if history else 0

def buyMore_Grid(grid, money):
    global grid_upgrade
    cost = 50000 * grid_upgrade
    if money >= cost:
        addGrid(grid)
        money -= cost
        grid_upgrade += 1
    return money

def nearRoad(row, col):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1), (-1,-1),(-1,1),(1,-1),(1,1)]:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] == 1:  # strada
                return True
    return False

def all_roads_connected(grid):
    # Trova tutte le posizioni delle strade
    road_positions = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == 1]
    if not road_positions:
        return True  # Nessuna strada, consideriamo valido

    # BFS per trovare tutte le strade collegate partendo dalla prima
    visited = set()
    queue = [road_positions[0]]
    while queue:
        r, c = queue.pop(0)
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == 1 and (nr, nc) not in visited:
                    queue.append((nr, nc))
    # Se tutte le strade sono state visitate, sono collegate
    return len(visited) == len(road_positions)

def road_components(grid):
    """Conta le componenti connesse di strade (id 1) con 4-neighbors."""
    road_positions = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == 1]
    visited = set()
    comps = 0

    for start in road_positions:
        if start in visited:
            continue
        comps += 1
        stack = [start]
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 1 and (nr, nc) not in visited:
                    stack.append((nr, nc))
    return comps

def main(page: ft.Page):
    global game_running, grid, money, population, shops, industries, grid_upgrade
    
    page.title = "City Simulator"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 1050 + page.padding
    page.window.height = 700
    page.window.maximizable = False
    page.window.resizable = False
    
    # Variabile per il tipo di edificio selezionato
    selected_building = {"type": 0}
    
    def window_event(e):
        if e.data == "close":
            if game_running:
                save(e)
            page.window.destroy()
            
    page.window.prevent_close = True
    page.window.on_event = window_event
    
    # Funzione per iniziare nuova partita
    def new_game(e):
        global grid, money, population, pop_house, max_population, happiness
        global energy, energy_req, water, water_req, shops, industries
        global moneyMed, history, income, grid_upgrade, tax_rate
        
        grid = []
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
        moneyMed = 0
        history = []
        income = 0
        grid_upgrade = 1
        tax_rate = 10

        addGrid(grid)
        grid[0][0] = 1  # Inizia con una strada
        show_game_screen()
    
    # Funzione per caricare partita
    def load_game(e):
        global grid
        try:
            load()
            if not grid:
                addGrid(grid)
            show_game_screen()
        except FileNotFoundError:
            show_message("Nessun salvataggio trovato!")
        except Exception as ex:
            show_message(f"Errore nel caricamento: {str(ex)}")
    
    # Funzione per mostrare messaggi
    def show_message(message: str):
        page.open(ft.SnackBar(ft.Text(f"⚠️ {message}",weight=ft.FontWeight.BOLD)))
        page.update()
    
    # Homepage
    def show_homepage():
        page.controls.clear()
        
        homepage = ft.Column(
            [
                ft.Container(height=50),
                ft.Text(
                    "🏙️ CITY SIMULATOR 🏙️",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.ElevatedButton(
                                "🎮 Nuova Partita",
                                icon=ft.Icons.ADD_CIRCLE,
                                on_click=new_game,
                                width=300,
                                height=60,
                                style=ft.ButtonStyle(
                                    text_style=ft.TextStyle(size=20)
                                )
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "💾 Carica Partita",
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=load_game,
                                width=300,
                                height=60,
                                style=ft.ButtonStyle(
                                    text_style=ft.TextStyle(size=20)
                                )
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "❌ Esci",
                                icon=ft.Icons.EXIT_TO_APP,
                                on_click=lambda e: page.window.close(),
                                width=300,
                                height=60,
                                style=ft.ButtonStyle(
                                    text_style=ft.TextStyle(size=20)
                                )
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.Container(height=50),
                ft.Text(
                    "Costruisci la tua città ideale!",
                    size=16,
                    italic=True,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
        
        page.add(homepage)
        page.update()
    
    # Funzione per aggiornare le statistiche
    def update_stats():
        textUpgrade_grid = 50000 * grid_upgrade
        textUpgrade_grid = '{:,}'.format(textUpgrade_grid).replace(',', '.')
        textMoney = '{:,}'.format(money).replace(',', '.')
        stats_text.value = f"""
💰 Soldi: {textMoney}$ (+{moneyMed}$/s)
📊 Upgrade Grid: {textUpgrade_grid}$
💸 Tasse: {tax_rate}%
            """

        # Aggiorna le progress bar
        pop_bar.value = population / max_population if max_population > 0 else 0
        pop_label.value = f"👥 Popolazione: {population}/{max_population}"

        happiness_bar.value = happiness / 10 if happiness > 0 else 0
        happiness_label.value = f"😊 Felicità: {happiness}/10"

        energy_bar.value = energy / energy_req if energy_req > 0 else 0
        energy_label.value = f"⚡ Energia: {energy}/{energy_req}"

        water_bar.value = water / water_req if water_req > 0 else 0
        water_label.value = f"💧 Acqua: {water}/{water_req}"

        # Servizi pubblici
        school_count = 0
        hospital_count = 0
        fire_count = 0
        police_count = 0
        for row in grid:
            for cell in row:
                if cell == 7:
                    school_count += 1
                if cell == 8:
                    hospital_count += 1
                if cell == 9:
                    fire_count += 1
                if cell == 10:
                    police_count += 1
        service_capacity = 50
        min_capacity = min(
            school_count * service_capacity if school_count > 0 else 0,
            hospital_count * service_capacity if hospital_count > 0 else 0,
            fire_count * service_capacity if fire_count > 0 else 0,
            police_count * service_capacity if police_count > 0 else 0
        )
        services_label.value = f"Servizi Pubblici: {population}/{min_capacity if min_capacity > 0 else 'N/A'}"
        services_bar.value = population / min_capacity if min_capacity > 0 else 0

        tax_label.value = f"Tasse: {tax_rate}%"
        tax_slider.value = tax_rate

        calcDemand()
        demand_text.value = (
            f"Domanda:\n"
            f"🏠 Case: {demand_house}\n"
            f"🛍️ Negozi: {demand_shop}\n"
            f"🏭 Industrie: {demand_industry}"
        )
            
        page.update()
        
    # Funzione per aggiornare la griglia visuale
    def update_grid_display():
        grid_container.controls.clear()
        
        # Header con le lettere
        header_row = ft.Row([ft.Text("  ", size=12, width=30)], spacing=2)
        for i in range(20):
            header_row.controls.append(
                ft.Text(chr(65 + i), size=12, width=30, text_align=ft.TextAlign.CENTER)
            )
        grid_container.controls.append(header_row)
        
        # Righe della griglia
        for idx, row in enumerate(grid):
            row_container = ft.Row(spacing=2)
            row_container.controls.append(
                ft.Text(f"{idx:02d}", size=12, width=30, text_align=ft.TextAlign.CENTER)
            )
            
            for col_idx, cell in enumerate(row):
                def make_cell_click(r, c):
                    def click(e):
                        place_building(r, c)
                    return click
                
                cell_button = ft.Container(
                    content=ft.Text(BUILD_ICONS[cell], size=20),
                    width=30,
                    height=30,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.BLUE_GREY_900,
                    border_radius=3,
                    on_click=make_cell_click(idx, col_idx)
                )
                row_container.controls.append(cell_button)
            
            grid_container.controls.append(row_container)
        
        page.update()
    
    # Funzione per piazzare un edificio
    def place_building(row, col):
        global money, shops, industries, grid

        build_type = selected_building["type"]

        # Se non è vuoto o strada, deve essere vicino a una strada
        if build_type != 0 and build_type != 1 and not nearRoad(row, col):
            show_message("Puoi costruire solo vicino a una strada!")
            return

        # Se è una strada, verifica che non crei un nuovo pezzo isolato
        if build_type == 1:
            old_cell = grid[row][col]
            comps_before = road_components(grid)
            # Simula la posa
            grid[row][col] = 1
            comps_after = road_components(grid)
            # Se aumenta il numero di componenti (e non era zero), la nuova strada è isolata
            if comps_before > 0 and comps_after > comps_before:
                grid[row][col] = old_cell  # ripristina
                show_message("Le strade devono restare collegate (niente tratti isolati).")
                return
            # ripristina, verrà assegnato più sotto
            grid[row][col] = old_cell
        elif build_type != 0:
            if money < abs(int(BUILD_COSTS[build_type])):
                show_message("Fondi insufficienti!")
                return

        old_cell = grid[row][col]

        # Aggiorna contatori rimuovendo il precedente
        if old_cell == 3:
            shops -= 1
        elif old_cell == 4:
            industries -= 1

        # Aggiorna contatori aggiungendo il nuovo
        if build_type == 3:
            shops += 1
        elif build_type == 4:
            industries += 1

        grid[row][col] = build_type

        if build_type != 0 and build_type != 1:
            money -= int(BUILD_COSTS[build_type])
        elif build_type == 1:
            money -= 300
        elif build_type == 0 and old_cell != 0:
            money -= 100  # demolizione

        update_grid_display()
        update_stats()
    
    # Funzione per upgrade della griglia
    def upgrade_grid_click(e):
        global money, grid_upgrade
        cost = 50000 * grid_upgrade
        if money >= cost:
            money = buyMore_Grid(grid, money)
            update_grid_display()
            update_stats()
            show_message(f"Griglia espansa! Nuovo costo: {50000 * grid_upgrade}$")
        else:
            show_message(f"Fondi insufficienti! Servono {cost}$")
    
    # Funzione per tornare al menu
    def backMenu(e):
        global game_running
        save()
        game_running = False
        show_homepage()
    
    # Funzione di selezione edificio
    def select_building(building_type):
        def click(e):
            selected_building["type"] = building_type
            for i, btn in enumerate(building_buttons):
                if i == building_type:
                    btn.bgcolor = ft.Colors.BLUE_700
                else:
                    btn.bgcolor = ft.Colors.BLUE_GREY_800
            page.update()
            selected_text.value = f"Selezionato: {BUILD_NAMES[building_type]}"
            selected_cost.value = f"Costo: {BUILD_COSTS[building_type]}$"
            page.update()
        return click
    
    # Game loop
    def game_loop():
        while game_running:
            calcEnergy()
            calcWater()
            calcPopulation()
            calcHappiness()
            getMoney()
            calcDemand()
            update_stats()
            time.sleep(0.5)
    
    # Statistiche
    stats_text = ft.Text(
        "",
        size=14,
        font_family="Consolas",
        weight=ft.FontWeight.BOLD
    )
    
    # Progress bars per le statistiche
    pop_label = ft.Text("👥 Popolazione: 0/0", size=12)
    pop_bar = ft.ProgressBar(value=0, width=250, color=ft.Colors.BLUE, bgcolor=ft.Colors.BLUE_GREY_800)
    
    happiness_label = ft.Text("😊 Felicità: 0/10", size=12)
    happiness_bar = ft.ProgressBar(value=0, width=250, color=ft.Colors.GREEN, bgcolor=ft.Colors.BLUE_GREY_800)
    
    energy_label = ft.Text("⚡ Energia: 0/0", size=12)
    energy_bar = ft.ProgressBar(value=0, width=250, color=ft.Colors.YELLOW, bgcolor=ft.Colors.BLUE_GREY_800)
    
    water_label = ft.Text("💧 Acqua: 0/0", size=12)
    water_bar = ft.ProgressBar(value=0, width=250, color=ft.Colors.CYAN, bgcolor=ft.Colors.BLUE_GREY_800)
    
    services_label = ft.Text("Servizi Pubblici: 0/0", size=12)
    services_bar = ft.ProgressBar(value=0, width=250, color=ft.Colors.PURPLE, bgcolor=ft.Colors.BLUE_GREY_800)

    tax_label = ft.Text(f"Tasse: {tax_rate}%", size=12)

    def update_tax(e):
        global tax_rate
        tax_rate = int(e.control.value)
        tax_label.value = f"Tasse: {tax_rate}%"
        page.update()

    tax_slider = ft.Slider(min=0, max=30, divisions=30, value=tax_rate, on_change=update_tax)

    # Pannello edifici
    building_buttons = []
    building_panel = ft.Column(spacing=5)
    
    for i in range(11):  # ora da 0 a 10
        btn = ft.Container(
            content=ft.Row([
                ft.Text(BUILD_ICONS[i], size=20),
                ft.Text(BUILD_NAMES[i], size=12)
            ]),
            padding=10,
            bgcolor=ft.Colors.BLUE_GREY_800 if i != 0 else ft.Colors.BLUE_700,
            border_radius=5,
            on_click=select_building(i)
        )
        building_buttons.append(btn)
        building_panel.controls.append(btn)
    
    selected_text = ft.Text(f"Selezionato: {BUILD_NAMES[0]}", size=12, weight=ft.FontWeight.BOLD)
    selected_cost = ft.Text(f"Costo: {BUILD_COSTS[0]}$", size=12)
    
    demand_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
    
    # Pulsante upgrade
    upgrade_button = ft.ElevatedButton(
        "Espandi Griglia",
        icon=ft.Icons.ADD_CIRCLE,
        on_click=upgrade_grid_click
    )
    
    # Pulsante menu
    menu_button = ft.ElevatedButton(
        "Menu Principale",
        icon=ft.Icons.HOME,
        on_click=backMenu
    )
    
    # Pulsante salva
    save_button = ft.ElevatedButton(
        "Salva Partita",
        icon=ft.Icons.SAVE,
        on_click=save
    )
    
    # Container griglia
    grid_container = ft.Column(
        spacing=2,
        scroll=ft.ScrollMode.AUTO,
        height=600
    )
    
    # Mostra schermata di gioco
    def show_game_screen():
        global game_running
        page.controls.clear()
        
        # Layout principale
        page.add(
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("City Simulator", size=24, weight=ft.FontWeight.BOLD),
                            stats_text,
                            pop_label,
                            pop_bar,
                            happiness_label,
                            happiness_bar,
                            energy_label,
                            energy_bar,
                            water_label,
                            water_bar,
                            services_label,
                            services_bar,
                            tax_label,
                            tax_slider,
                            ft.Divider(),
                            demand_text,
                            ft.Divider(),
                            ft.Text("Edifici", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                selected_text,
                                selected_cost
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            building_panel,
                            ft.Divider(),
                            upgrade_button,
                            save_button,
                            menu_button
                        ],
                        width=300,
                        scroll=ft.ScrollMode.AUTO
                    ),
                    ft.VerticalDivider(),
                    ft.Container(
                        content=grid_container,
                        expand=True
                    )
                ],
                expand=True
            )
        )
        
        # Update iniziale
        update_grid_display()
        update_stats()
        
        # Avvia game loop
        game_running = True
        thread = Thread(target=game_loop, daemon=True)
        thread.start()
    
    # Mostra homepage all'avvio
    show_homepage()

ft.app(target=main)