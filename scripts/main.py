from bs4 import BeautifulSoup
import requests as rq
import re

error = list()

mainUrl = 'https://www.myfooddiary.com'
directory = '/foods/brands'
url = f'{mainUrl}{directory}'

r = rq.get(url)
status = r.status_code 

# Check for coonextion status to go on
if status != 200:
    print("Respuesta desconocida")
    quit()

soup = BeautifulSoup(r.content, 'html.parser')

# Brand lists

brandsConteiner = soup.find("div", id="BrandListHldr") # Main container

brandMenuLinks = list() #Link list to all brands menus

for a in brandsConteiner.find_all("a"):
    link = f'{a["href"]}'
    brandMenuLinks.append({"brand":a.text , "href":link}) 
    #Por ahora lo voy a hacer asi pero mas delante con todos los datos tengo que hacer un diccionario por marca
    
# Iteration trought brands. The objetive is to get menu items.
for i in brandMenuLinks[:
    link = f'{mainUrl}{i["href"]}'
    r = rq.get(link)
    status = r.status_code
    soup = BeautifulSoup(r.content, 'html.parser')
    menuTable = soup.find("table", class_="FoodListTable")
    # Chequeo que la tabla como la busque exista
    if not menuTable == None:
        menuTable = menuTable.tbody
    else:
        error.append({"error":"No menuTable", "desc":"Error mientas buscaba la tabla con el menu"})
        continue
    menu = menuTable.find_all("tr")
    # Tomo todas las filas de la tabla, cada fila es un item en el menu
    if len(menu) > 0:
        menuItems = list()
        for p in menu:
            row = p.find("td", class_="FoodRowLt")
            if row == None:
                continue
            itemUrl = row.a["href"]
            itemName = row.a.span.next_sibling
            idP = row.a["id"]
            menuItems.append({"idp":idP, "itemName":itemName, "href":itemUrl})  
    i.update({"menu":menuItems}) # Actualizacion de los datos en el diccionario

# Next step get Nutritions facts
for i in brandMenuLinks:
    # There I set a dictionary for each item on the menu wich will contain the nutritional data
    # la informacion nutricional tambien va a ser una lista de diccionarios
    for item in i["menu"]:
        # -> CONEXION al item
        url = f'{mainUrl}{item["href"]}'
        r = rq.get(url)
        # Chequeo de status
        if r.status_code != 200:
            error.append({"error":f'Estado {r.status_code}', "desc":"Error mientas buscaba informacion nutricional"})
            continue
        # FIN CONEXION <-
        # -> INSTANCIA OBJETO SOUP
        soup = BeautifulSoup(r.content, "html.parser")
        # Aqui estan todos los datos
        foodLabel = soup.find("div", id="FoodLabelHldr")
# <---- Empiza la extraccion de los datos ----->
        netCarbs = foodLabel.find("div", id="nf_net_carbs_hldr").extract()
        calories = foodLabel.find("div",id="nf_cal_hldr").extract()
        if not netCarbs == None:
            try:
                netCarbs = [int(s) for s in netCarbs.text.split() if s.isdigit()][0]
            except :
                netCarbs = f'Fail {netCarbs}'
        else:
            netCarbs = "Not available"
        if not calories == None:
            try:
                calories = [int(s) for s in calories.text.split() if s.isdigit()][0]
            except :
                calories = f'Fail {calories}'
        # <- Salvo primeros datos -->
        #item.update({"nFacts":{"calories":calories, "netCarbs":netCarbs}})
# <- end -->
# <- Next -->
        # Los divs de interes tinenen un id con el siguiente formato
        patt = "nf_((?!amount)(?!dv_note)(?!daily))[a-zA-Z_]*"
        # Lista de todos los divs con los datos
        nfContainers = foodLabel.find_all("div", id=re.compile(patt))
        # Loop de elementos dentro del conetenedor de informacion nutricional
        nutrients = list()
        for nf in nfContainers:
            # Lista de tags en el contenedor
            tagsInNfC = nf.find_all(True) 
            if len(tagsInNfC):
                nutrients.append(nFactData(nf))
            else:
                continue
        item.update({"nFacts":{"calories":calories, "netCarbs":netCarbs, "facts":nutrients}})
# <- end -->                        
