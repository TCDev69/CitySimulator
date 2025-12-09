import flet as ft
import random
import time
from threading import Thread
import json

# Variabili globali
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
moneyMed = 0
history = []
income = 0
game_running = False

# Emoji per gli edifici
BUILD_ICONS = {
    0: "☐",
    1: "🏠",
    2: "🛍️",
    3: "🏭",
    4: "💧",
    5: "⚡",
    6: "🏫",
    7: "🏥",
    8: "🚒",
    9: "🚓"
}

BUILD_NAMES = {
    0: "Vuoto",
    1: "Casa",
    2: "Negozio",
    3: "Industria",
    4: "Generatore Acqua",
    5: "Generatore Energia",
    6: "Scuola",
    7: "Ospedale",
    8: "Vigile del Fuoco",
    9: "Polizia"
}

def load():
    global grid, money, population, pop_house, max_population, happiness
    global energy, energy_req, water, water_req, shops, industries
    global moneyMed, history, income, grid_upgrade

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
    global moneyMed, history, income, grid_upgrade

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
        "grid_upgrade": grid_upgrade
    }

    with open("savegame.json", "w") as f:
        json.dump(data, f)       
        print("Game saved.") 

def addGrid(grid):
    for i in range(10):
        row = []
        for e in range(20):
            row.append(0)
        grid.append(row)

def progressBar(val, valMax, max=10):
    if val > valMax:
        val = valMax
    if valMax == 0:
        ratio = 0
    else:
        ratio = val / valMax
    barra = int(ratio * max)
    rimanente = max - barra
    return "[" + "█" * barra + " " * rimanente + "]"

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

    # Servizi
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

    if not has_school:
        score = score - 1
    if not has_hospital:
        score = score - 1
    if not has_fire:
        score = score - 1
    if not has_police:
        score = score - 1

    if energy >= energy_req and water >= water_req and has_school and has_hospital and has_fire and has_police:
        score = score + 1

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

def calcPopulation():
    global population, grid, pop_house, max_population, happiness, shops, industries
    max_population = 0
    for row in grid:
        for cell in row:
            if cell == 1:
                max_population += pop_house
            if cell == 2:
                max_population += pop_house // 2
            if cell == 3:
                max_population += pop_house // 3

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

        if population > max_population:
            population = max_population
        if population < 0:
            population = 0

    return population

def getMoney():
    global money, income, moneyMed, population, shops, industries, history
    income = 0
    s = 0
    rnd = random.random()
    if rnd <= 0.25:
        income = int(population * 0.3 + shops * 0.5 + industries * 0.8) * 10
        money += income
    history.append(income)
    if len(history) > 10:
        history.pop(0)
        for i in range(len(history) - 1):
            s += history[i]
        moneyMed = s // len(history)

def buyMore_Grid(grid, money):
    global grid_upgrade
    cost = 50000 * grid_upgrade
    if money >= cost:
        addGrid(grid)
        money -= cost
        grid_upgrade += 1
    return money

def main(page: ft.Page):
    global game_running, grid, money, population, shops, industries, grid_upgrade
    
    page.title = "City Simulator"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 1050
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
        global moneyMed, history, income, grid_upgrade
        
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
        
        addGrid(grid)
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
    def show_message(message):
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Notifica"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        page.dialog = dialog
        dialog.open = True
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
        stats_text.value = f"""
💰 Soldi: {money}$ (+{moneyMed}$/s)
👥 Popolazione: {progressBar(population, max_population)} {population}/{max_population}
😊 Felicità: {progressBar(happiness, 10)} {happiness}/10
⚡ Energia: {progressBar(energy, energy_req)} {energy}/{energy_req}
💧 Acqua: {progressBar(water, water_req)} {water}/{water_req}
📊 Upgrade Grid: {50000 * grid_upgrade}$
"""
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
        
        if money < 1000 and selected_building["type"] != 0:
            show_message("Fondi insufficienti!")
            return
        
        old_cell = grid[row][col]
        
        # Aggiorna contatori
        if old_cell == 2:
            shops -= 1
        elif old_cell == 3:
            industries -= 1
        
        if selected_building["type"] == 2:
            shops += 1
        elif selected_building["type"] == 3:
            industries += 1
        
        grid[row][col] = selected_building["type"]
        
        if selected_building["type"] != 0:
            money -= 1000
        elif old_cell != 0:
            money -= 100  # Costo di demolizione
        
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
            update_stats()
            time.sleep(0.5)
    
    # Statistiche
    stats_text = ft.Text(
        "",
        size=14,
        font_family="Consolas",
        weight=ft.FontWeight.BOLD
    )
    
    # Pannello edifici
    building_buttons = []
    building_panel = ft.Column(spacing=5)
    
    for i in range(10):
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
                            ft.Divider(),
                            ft.Text("Edifici", size=18, weight=ft.FontWeight.BOLD),
                            selected_text,
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