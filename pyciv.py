#PyCiv by Timothy Fisher-Taylor, */4/20 - */4/20

import pygame as pg
import random as r

#the basics
pg.init()#silly command

pixel_size = 8

ui_colour = (225,185,225)
tech_colour = (20,0,20)

game_width,game_height = 1280-24,640
board_width,board_height = 960,640
tile_size = 64
board_tile_width,board_tile_height = int(board_width/tile_size),int(board_height/tile_size)
ui_size = game_width-board_width

game_screen = pg.display.set_mode((game_width,game_height))
game_screen.fill((255,255,255))
pg.display.update()

pg.display.set_caption("PyCiv")

#config
fog_active = True#True
start_population = 3#3

score = 0#0
food = 30#30?
wood = 0#0
stone = 0#0
knowledge = 0#0

city_max_size = 0#0 (smallest city is 0); change to 0 once techs are added properly
city_true_max_size = 3#determines the maximum POSSIBLE city size, not the maximum allowed size (which is city_max_size)
population_max_density = 6#6 per tile is best
ship_max_density = 2#2

disaster_base_chance = 1250#~1500; 1 in this is the base disaster chance, though it rapidly increases 
disaster_peaks_at = 100#when the chance for disaster reaches its highest 'resting' point; should be around 5% of above
disaster_counter_speed = 0.5
turn_counter = 0
disaster_counter = 0

city_food_cost = 3

wonder_cost = 25

available_wonders = []#starts as none
#The Babbling Gardens - Cultivation
#The Monument to the Sky - Philosophy 
#The Golden Mausoleum - Architecture
#The Watcher Over the Seas - Navigation


help_width = 480
help_min_height = 48
help_text_size = 16
text_indent = '  '

def help_text_split(text):

    new_text = text.split('|')

    for i in range(len(new_text)):
        if i != 0:
            
            new_text[i] = text_indent + new_text[i]

    return new_text


def help_me(pos,tech_tree_open=False,disaster=False,starvation=False):

    x = pos[0]
    y = pos[1]

    help_text = []

    help_text_colour = (0,0,0)
    
    help_colour = (185,235,200)

    help_corner = [pos[0],pos[1]]

    if x > game_width/2:
        help_corner = [x-help_width,y]


    if tech_tree_open:

        for z in techs:

            if pg.Rect(techs[z].image.rect).collidepoint(pos):#if this one is clicked

                for c in help_text_split(techs[z].image.description):
                    help_text.append(c) 
                
                break

            
    elif x > ui_size:#if on board

        mouse_tile = find_mouse_tile(pos)
        tile = tiles[mouse_tile[0]][mouse_tile[1]]
        
        if tile.fog:

            help_text.append("Fog: Move a person here to see what is hidden.")

        else:#if not fog, disallows gaining hidden information through help feature 

            for z in help_text_split(terrain_descriptions[tile.terrain]):
                help_text.append(z)

            if tile.terrain == 'forest' and 'treetops' not in tile.features:

                help_text.append(f"{text_indent}The trees will return shortly.")
            
            if tile.population > 0:

                for z in help_text_split("Person: Performs one action and eats one food per round.|Groups of people will grow by one person per round."):
                    help_text.append(z)
                    
            if tile.city_level != None:

                for z in help_text_split(f"City {tile.city_level+1}: A centre of your civilisation. Provides knowledge and stability,|but costs {(tile.city_level+1)*(3-int(technologies['medicine'].unlocked))} food per turn."):
                    help_text.append(z)

            for f in tile.features:

                if 'city' in f or f == 'treetops':
                    pass

                else:
                    for z in help_text_split(feature_descriptions[f]):
                        help_text.append(z)
        
    elif pg.Rect(stage_corner,stage_size).collidepoint(pos):

        if disaster:
            for z in help_text_split(disaster_descriptions[disaster]):
                help_text.append(z)
            
        else:
            if stage_img == action_img:
                for z in help_text_split("Take action!|Click on your people to move them,|or on the action buttons above."):
                    help_text.append(z)

            elif stage_img == starve_img:
                for z in help_text_split("Your people starve!|Click on a person or city to starve it.|Continue until your food total isn't red."):
                    help_text.append(z)


    else:#if in ui

        for z in images:

            if pg.Rect(images[z].rect).collidepoint(pos):#if this one is clicked

                for c in help_text_split(images[z].description):
                    help_text.append(c) 
                
                break



    #constructs the text box

    if help_text:
        help_height = (help_text_size*len(help_text))+(2*pixel_size)
        if help_height < help_min_height:
            help_height = help_min_height
            

        while help_corner[1] + help_height > game_height:
            help_corner[1] -= pixel_size#ensures text box doesn't go below the screen
            
        help_size = (help_width,help_height)

        help_rect = (help_corner,help_size)

        pg.draw.rect(game_screen,help_colour,help_rect)

        iter_ = 0
        for x in help_text:
            print_text(x,(pixel_size+help_corner[0],help_corner[1]+(iter_*help_text_size)+pixel_size),help_text_colour,help_text_size)
            iter_ += 1

        pg.display.update(help_rect)

        

        helping = True
        while helping:
            for event in pg.event.get():

                if event.type == pg.QUIT:

                    pg.quit()

                elif event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEMOTION:

                    helping = False

        if tech_tree_open:
            draw_tech_tree()

            find_ui(tech_open=True)
            
        else:
            find_ui()
            find_board()

            if disaster:
                for z in disaster_tiles:
                    if not (fog_active and tiles[z[0]][z[1]].fog):
                        tiles[z[0]][z[1]].overlay(True)
            elif starvation:
                for z in populated_tiles:
                    tiles[z[0]][z[1]].overlay(True)
                for z in city_tiles:
                    if  tiles[z[0]][z[1]].population == 0:
                        tiles[z[0]][z[1]].overlay(True)



def hesitate(reason=(False,None)):#waits for the player to click next turn or press enter

    waiting = True
    while waiting:
        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()

            elif event.type == pg.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if pg.Rect(images['next_turn'].rect).collidepoint(event.pos):

                        waiting = False

                elif event.button == 3:
                    
                    if reason[0] == 'disaster':
                        help_me(event.pos,disaster=reason[1])

                    else:
                        help_me()

            elif event.type == pg.KEYDOWN:

                if event.key == pg.K_RETURN:
                    
                    waiting = False


def find_mouse_tile(pos):#turns mouse pos into tile coords; returns False if the mouse is not on the board

    if pos[0] >= ui_size:
        
        x = pos[0] - ui_size
        x = int((x - x%tile_size)/tile_size)

        y = pos[1]
        y = int((y - y%tile_size)/tile_size)

        return (x,y)

    else:
        return False
    

#defines text stuff

def print_text(text,location,colour,size):
    text_font = pg.font.Font('freesansbold.ttf',size)#yuck font is 'freesansbold.ttf'
    ready_text = text_font.render(text,True,colour)
    game_screen.blit(ready_text,location)


#tiles
fog = pg.transform.scale(pg.image.load(r'art\tiles\fog.png'),(tile_size,tile_size))

tile_images = []
tile_ints = {'grass':0,'forest':1,'rocks':2,'water':3,'desert':4}
terrain_descriptions = {
                    'grass':"Grassland: Cities are built on grasslands.|Occasionally grows grain.",
                    'forest':"Forest: Grows berries at a decent rate and provides wood.|Wood-cutting requires three people.",
                    'rocks':"Rocks: Provides stone. Mining requires six people.",
                    'water':"Water: Provides fish, but requires technology to traverse.",
                    'desert':"Desert: A useless wasteland."}

for x in ['grass','forest','rocks','water','desert']:
    tile_images.append(pg.transform.scale(pg.image.load(f'art\\tiles\\{x}.png'),(tile_size,tile_size)))

tile_feature_images = []

feature_descriptions = {
                    'grain':"Grain: Provides 1-6 food if gathered.",
                    'berries':"Berries: Provides 2-12 food if gathered.",
                    'fish':"Fish: Provides 3-18 food if gathered.",
                    'farm':"Farm: Grows crops every round.",
                    'crops':"Crops: Provides 3-6 food if gathered.",
                    'mine':"Mine: The rocks will not disappear when mined.",
                    'sawmill':"Sawmill: One worker can fell this forest, and the trees will|regrow faster.",
                    'garden':"An irrigated spire covered in lush gardens.",
                    'monument':"A monument dedicated to the heavens.",
                    'watcher':"A colossal bronze statue.",
                    'mausoleum':"A shining tomb, masterfully gilded and engraved.",
                    }
    

wonder_types = {'forest':'garden','grass':'monument','rocks':'mausoleum','water':'watcher'}

feature_ints = {'treetops':0,'grain':1,'berries':2,'fish':3,'city0':4,'city1':5,'city2':6,'city3':7,'farm':8,'crops':9,'mine':10,'sawmill':11,'garden':12,'monument':13,'watcher':14,'mausoleum':15}
for x in feature_ints:
    tile_feature_images.append(pg.transform.scale(pg.image.load(f'art\\features\\{x}.png'),(tile_size,tile_size)))

building_types = ('farm','crops','mine','sawmill',)
wonder_tiles = []

def find_feature_key(x):
    return feature_ints[x]


def protrude(place,iter_,terrain,size_num):#should be done several times
    new_place = place[:]
    new_place[r.randint(0,1)] += r.choice([-1,1])
    if not (0 <= new_place[0] < board_tile_width and 0 <= new_place[1] < board_tile_height):
        return
    tiles[new_place[0]][new_place[1]].terrain = terrain
    if r.randint(1,16) <= size_num/2**iter_: protrude(new_place,iter_+1,terrain,size_num)


class Tile:

    def __init__(self,terrain,x,y,features,population,active_population,city_level,fog):

        self.terrain = terrain#a key for tile_images
        self.x = x
        self.y = y
        self.features = features#a list of integers corresponding to things in tile_feature_images
        self.population = population#an integer noting the population
        self.active_population = active_population#an integer noting the active population
        self.city_level = city_level#an integer noting the city level (None is no city; 0 is 1st level, etc)
        self.fog = fog#whether there is fog


    def find(self,full=False):
        tile_location = (ui_size+(tile_size*self.x),tile_size*self.y)
        
        game_screen.blit(tile_images[tile_ints[self.terrain]],tile_location)

        self.features.sort(key=find_feature_key)
        #add items on tile here
        for z in self.features:
            game_screen.blit(tile_feature_images[feature_ints[z]],(ui_size+(tile_size*self.x),tile_size*self.y))
        
        active_people = self.active_population
        pop_img = (person_img,inactive_person_img)
        if self.terrain == 'water':
            pop_img = (ship_img,inactive_ship_img)
            
        for k in range(self.population):
            stack = 0
            while k > 2:
                k -= 3
                stack += 1
                    
            if self.terrain != 'water':
                person_location = (pixel_size+tile_location[0]+(k*2*pixel_size),(2*pixel_size)+tile_location[1]+(stack*3*pixel_size))
            else:                
                person_location = (pixel_size+tile_location[0]+(k*pixel_size),(pixel_size)+tile_location[1]+(k*pixel_size*3))

            if active_people:
                active_people -= 1
                game_screen.blit(pop_img[0],person_location)
            else:
                game_screen.blit(pop_img[1],person_location)
                

        if fog_active and self.fog:
            game_screen.blit(fog,(ui_size+(tile_size*self.x),tile_size*self.y))

        if not full: pg.display.update((ui_size+(tile_size*self.x),tile_size*self.y),(tile_size,tile_size))

        
    def decrease_population(self,change=1,active=True):

        if self.population > 0:
            
            if change > self.population:
                self.population = change

            self.population -= change
            if active:
                self.active_population -= change
            else:
                if self.active_population > self.population:
                    self.active_population = self.population
            
            if (self.x,self.y) in populated_tiles and self.population == 0:
                populated_tiles.remove((self.x,self.y))
        

    def increase_population(self,change=1,active=False):

        self.population += change

        if active: self.active_population += change
        
        if (self.x,self.y) not in populated_tiles and self.population > 0:
            populated_tiles.append((self.x,self.y))
            

    def reduce_city(self,change=1):
        global knowledge

        for i in range(change):

            if self.city_level != None:

                self.features.remove('city'+str(self.city_level))
                knowledge -= self.city_level+1
                self.city_level -= 1


                if self.city_level == -1:
                    city_tiles.remove((self.x,self.y))
                    self.city_level = None

                    if techs['writing'].unlocked:
                        knowledge -= 1


    def build_city(self,change=1):
        global wood,stone,food,knowledge

        for j in range(change):

            if self.city_level == None:
                
                self.city_level = 0
                self.features.append('city0')
                
                if 'grain' in self.features: self.features.remove('grain')
                city_tiles.append((self.x,self.y))
                
                self.decrease_population(city_costs[0][0],True)
                wood -= city_costs[0][1]
                stone -= city_costs[0][2]

                knowledge += 1

                if techs['writing'].unlocked:
                    knowledge += 1

            elif self.city_level < city_max_size:

                self.city_level += 1
                self.features.append('city' + str(self.city_level))
                
                self.decrease_population(city_costs[self.city_level][0],True)
                wood -= city_costs[self.city_level][1]
                stone -= city_costs[self.city_level][2]

                knowledge += self.city_level+1
                
                
            
    def overlay(self,red=False):

        overlay_type = tile_overlay
        if red: overlay_type = tile_red_overlay
        game_screen.blit(overlay_type, (ui_size+(self.x*tile_size), self.y*tile_size))
        pg.display.update((ui_size+(self.x*tile_size),self.y*tile_size),(tile_size,tile_size))


def find_board():#draws the board
    for x in range(board_tile_width):
        for y in range(board_tile_height):
            tiles[x][y].find(True)
    pg.display.update((ui_size,0),(board_width,game_height))


#img class
class Image:

    def __init__(self, image, corner, size, description):

        self.image = image
        self.corner = corner
        self.size = size

        self.description = description

        self.rect = (corner,size)


    def draw(self):

        game_screen.blit(self.image,self.rect)


#civ-type things

person_img = pg.transform.scale(pg.image.load(r'art\civ\person.png'),(pixel_size,2*pixel_size))
inactive_person_img = pg.transform.scale(pg.image.load(r'art\civ\inactive_person.png'),(pixel_size,2*pixel_size))

ship_img = pg.transform.scale(pg.image.load(r'art\civ\ship.png'),(4*pixel_size,3*pixel_size))
inactive_ship_img = pg.transform.scale(pg.image.load(r'art\civ\inactive_ship.png'),(4*pixel_size,3*pixel_size))

city_costs = [[6,2,0],[6,3,1],[6,4,3],[6,5,6]]

populated_tiles = []
city_tiles = []#tiles with population/a city


#ui definitions

images = {}

img_names = ('next_turn','crown','food','wood','stone','knowledge','gather','fell','mine','check','build_city','build_production','build_wonder','technology')

img_desc = ("Click this to enter the next phase of the game.",
            "Score: Try to maximise this by developing your civilisation.|Cities and technologies provide points per turn based on|their level in the following pattern: 1, 3, 6, 10.",
            "Food: The most important resource.|Every round, each person eats one food,|and each city consumes thrice its level in food.",
            "Wood: Used to build cities and unlock technologies.",
            "Stone: Used for advanced cities and technologies.",
            "Knowledge: Used to unlock new technologies.|Gaining knowledge requires you to build or upgrade cities.",
            "Gather: Used to gain food from grain, fish, and berries.",
            "Fell Trees: Three people chop a forest down for one wood.",
            "Mine Stone: Six people mine one stone from rocks.",
            "Check Population: Highlights all active population.",
            "Build City: Six people can build or upgrade a city.|New cities cost two wood.|Level two cities cost three wood and one stone.|Level three cities cost four wood and three stone.|Level four cities cost five wood and six stone.",
            "Build Production: For building farms, sawmills, and mines.|Farms need agriculture and cost two wood.|They are built on fields of grain.|Sawmills need forestry and cost one wood and one stone.|They are built on forests and make woodcutting easier.|Mines need minig and cost one wood and one stone.|They are built on rocks to make the rocks persistent.",
            "Build Wonder: Wonders cost six population, 25 wood and|25 stone. Each requires a different tier three technology|and can be built only once. Wonders are worth 50 points per turn.|The Monument to the Sky is built on grassland.|The Babbling Gardens is built in forest.|The Golden Mausoleum is built on rocks.|The Watcher Over the Seas goes in water.",
            "Technology: Opens the technology screen."
          )


act_names = ('gather','fell','mine','check','build_city','build_production','build_wonder','technology')
action_size = (64,64)


#action grid: x,y
action_count = (4,2)

#border
border_size = pixel_size
border_img_base = pg.image.load(r'art\ui\border.png')
border_img = [pg.transform.scale(border_img_base,(ui_size,border_size)),pg.transform.scale(border_img_base,(border_size,game_height)),pg.transform.scale(border_img_base,(border_size,border_size+(64*action_count[1])))]


resource_icon_size = (56,48)

img_y = [border_size+pixel_size]
for i in range(4):#calculates the y values for the resource icons
    img_y.append(img_y[-1]+resource_icon_size[1]+(2*pixel_size))



#actions I think
act_x = [border_size]
for i in range(action_count[0]):
    act_x.append(act_x[-1]+action_size[0]+border_size)

act_y = [640-128-(64*action_count[1])]
for i in range(action_count[1]):
    act_y.append(act_y[-1]+action_size[1]+border_size)


for x in ((img_names[0], (0,640-64),(ui_size,64), img_desc[0]),
          (img_names[1], (border_size*2,img_y[0]), resource_icon_size, img_desc[1]),
          (img_names[2], (border_size*2,img_y[1]), resource_icon_size, img_desc[2]),
          (img_names[3], (border_size*2,img_y[2]), resource_icon_size, img_desc[3]),
          (img_names[4], (border_size*2,img_y[3]), resource_icon_size, img_desc[4]),
          (img_names[5], (border_size*2,img_y[4]), resource_icon_size, img_desc[5]),
          (img_names[6], (act_x[0],act_y[0]), action_size, img_desc[6]),
          (img_names[7], (act_x[1],act_y[0]), action_size, img_desc[7]),
          (img_names[8], (act_x[2],act_y[0]), action_size, img_desc[8]),
          (img_names[9], (act_x[3],act_y[0]), action_size, img_desc[9]),
          (img_names[10], (act_x[0],act_y[1]), action_size, img_desc[10]),
          (img_names[11], (act_x[1],act_y[1]), action_size, img_desc[11]),
          (img_names[12], (act_x[2],act_y[1]), action_size, img_desc[12]),
          (img_names[13], (act_x[3],act_y[1]), action_size, img_desc[13]),
          ):

    img = pg.transform.scale(pg.image.load(f'art\\ui\\{x[0]}.png'),x[2])
    
    images[x[0]] = Image(img,x[1],x[2],x[3])

#rectangle containing all the action icons
action_rect = ((act_x[0],act_y[0]),(ui_size,((action_count[1]-1)*border_size)+(action_count[1]*action_size[1])))


#misc
tile_overlay = pg.transform.scale(pg.image.load(r'art\ui\overlay.png'),(tile_size,tile_size))
tile_red_overlay = pg.transform.scale(pg.image.load(r'art\ui\red_overlay.png'),(tile_size,tile_size))
action_overlay = pg.transform.scale(pg.image.load(r'art\ui\overlay.png'),action_size)

#hardcoded values I guess; at least the reasoning is kinda clear
stage_corner = (0,640-64-56)#this contains the border and therefore can begin on the edge
stage_size = (ui_size,64)

action_img = pg.transform.scale(pg.image.load(r'art\ui\action.png'),stage_size)
starve_img = pg.transform.scale(pg.image.load(r'art\ui\starve.png'),stage_size)

stage_img = action_img


#disasters

disasters = {}
disaster_list = ('meteor','earthquake','drought','flood','plague','heresy','civil_war')

disaster_descriptions = {'meteor':"A meteor falls from the heavens, destroying all civilisation|in a 3x3 area and damaging the terrain.",
                        'earthquake':"The ground shakes, ravaging a fissure of the landscape!|Damages cities and destroys all population in cities.|One population dies in tiles out of cities.",
                        'drought':"An immense drought withers food sources and desertifies the land.",
                        'flood':"A terrifying flood covers an area with water.|Each tile has a one-third chance of flooding,|being completely replaced by water.",
                        'plague':"Every city has a chance equal to its size in four to become|plagued, which reduces its level by one and kills|one population per tile within two tiles, diagonals included.",
                        'heresy':"Many random populated tiles form heretical beliefs.|Cities lose one size, and one population dies.",
                        'civil_war':"An area is consumed in destructive civil war!|Cities lose a random amount of size, and population dies randomly."}

for i in disaster_list:    
    disasters[i] = pg.transform.scale(pg.image.load(f'art\\disasters\\{i}.png'),stage_size)


def find_ui(area=((0,0),(ui_size,board_height)),tech_open=False):#draws the ui

    #background
    pg.draw.rect(game_screen,(ui_colour),((0,0),(ui_size,game_height)))


    #main drawing
    for x in img_names:
        images[x].draw()

    if tech_open:
        game_screen.blit(action_overlay,images['technology'].corner)


    #resource quantities    
    print_text(str(score),(images['crown'].corner[0]+images['crown'].size[0]+10,images['crown'].corner[1]),(0,0,0),48)

    food_text_colour = (0,0,0)
    if food < 0: food_text_colour = (155,0,0)
    print_text(str(food),(images['food'].corner[0]+images['food'].size[0]+10,images['food'].corner[1]),food_text_colour,48)

    print_text(str(wood),(images['wood'].corner[0]+images['wood'].size[0]+10,images['wood'].corner[1]),(0,0,0),48)

    print_text(str(stone),(images['stone'].corner[0]+images['stone'].size[0]+10,images['stone'].corner[1]),(0,0,0),48)

    knowledge_text_colour = (0,0,0)
    if knowledge < 0: knowledge_text_colour = (155,0,0)
    print_text(str(knowledge),(images['knowledge'].corner[0]+images['knowledge'].size[0]+10,images['knowledge'].corner[1]),knowledge_text_colour,48)


    #misc
    game_screen.blit(stage_img,stage_corner)


    #border
    #main border
    game_screen.blit(border_img[0],(0,0))
    game_screen.blit(border_img[0],(0,game_height-border_size))
    game_screen.blit(border_img[1],(0,0))
    game_screen.blit(border_img[1],(ui_size-border_size,0))

    #actions border
    for i in range(action_count[0]-1):
        game_screen.blit(border_img[2],((i+1)*(border_size+64),640-128-(64*action_count[1])))
    for i in range(action_count[1]):
        game_screen.blit(border_img[0],(0,640-120-((i+1)*(border_size+64))))

    pg.display.update(area)
    
#technology

    
class Tech:

    def __init__(self, tech, image, unlocked, cost, prereqs):

        self.tech = tech
        self.image = image
        self.unlocked = unlocked
        self.cost = cost
        self.prereqs = prereqs


    def overlay(self,red=False):

        overlay_type = tech_overlay
        if red: overlay_type = tech_red_overlay

        game_screen.blit(overlay_type,self.image.corner)
        pg.display.update(self.image.rect)


    def find_img(self,full=True):
        global wood,stone,knowledge

        add = False
        
        game_screen.blit(tech_border,(self.image.corner[0]-border_size,self.image.corner[1]-border_size))        
        self.image.draw()

        if self.unlocked:
            pass

        #if resource requirements are met; also add prereqs

        else:

            res_num = 0#resource number; number of previous resource images drawn
            res_y = 0
            for i in range(len(self.cost)):#draws resource costs
                for j in range(self.cost[i]):
                    game_screen.blit(mini_resources[i],(self.image.corner[0]+(res_num*24),self.image.corner[1]+self.image.size[1]+16+(res_y*(mini_resource_size[1]+pixel_size))))
                    res_num += 1
                    if res_num % 3 == 0:
                        res_y += 1
                        res_num -= 3


            prereq_check = True
            for z in self.prereqs:
                if not techs[z].unlocked:
                    prereq_check = False
            
            if prereq_check and wood >= self.cost[0] and stone >= self.cost[1] and knowledge >= self.cost[2]:

                self.overlay()

                add = True

            else:

               self.overlay(True)

        if not full:

            pg.display.update(self.image.rect)

        return add


    def discover(self):
        global wood,stone,knowledge,available_wonders,city_costs

        wood -= self.cost[0]
        stone -= self.cost[1]
        knowledge -= self.cost[2]

        self.unlocked = True

        if self.tech in ('masonry','law','architecture'):
            global city_max_size
            city_max_size += 1

            if self.tech == 'architecture':
                available_wonders.append('mausoleum')

        elif self.tech == 'navigation':
            available_wonders.append('watcher')

        elif self.tech == 'writing':
            knowledge += len(city_tiles)

        elif self.tech == 'irrigation':
            feature_descriptions['crops'] = "Crops: Provides 2-6 food if gathered.",

        elif self.tech == 'cultivation':
            available_wonders.append('garden')

        elif self.tech == 'medicine':
            global city_food_cost
            city_food_cost = 2

        elif self.tech == 'engineering':

            for i in range(len(city_costs)):

                city_costs[i][1] -= 1
                city_costs[i][2] -= 1
                if city_costs[i][2] < 0: city_costs[i][2] = 1

        elif self.tech in ('religion','mysticism'):

            for c in city_costs:
                c[0] -= 1
                if self.tech == 'mysticism':
                    c[0] -= 1

        elif self.tech == 'philosophy':
            available_wonders.append('monument')

        elif self.tech == 'mathematics':
            global techs
            
            for z in techs:
                if not techs[z].unlocked:

                    if techs[z].cost[0] >= techs[z].cost[1]:
                        techs[z].cost[0] -= 1

                    else:
                        techs[z].cost[1] -= 1
                    


tech_grid = (7,3)#is a grid yeah gaming

tech_size = (64,64)

tech_buffer_size = (64,96)

tech_x = [ui_size+tech_size[0]]
for i in range(tech_grid[0]):
    tech_x.append(tech_x[-1] + (2*tech_buffer_size[0]))

tech_y = [tech_size[1]-(3*pixel_size)]
for i in range(tech_grid[1]):
    tech_y.append(tech_y[-1] + (2*tech_buffer_size[1]))


tech_overlay = pg.transform.scale(pg.image.load(r'art\ui\overlay.png'),tech_size)
tech_red_overlay = pg.transform.scale(pg.image.load(r'art\ui\red_overlay.png'),tech_size)
tech_border = pg.transform.scale(pg.image.load(r'art\ui\tech_border.png'),(tech_size[0]+(2*border_size),tech_size[1]+(2*border_size)))

techs = {}


mini_resources = []
mini_resource_size = (16,32)
for z in ('mini_wood','mini_stone','mini_knowledge'):
    mini_resources.append(pg.transform.scale(pg.image.load(f'art\\civ\\{z}.png'),mini_resource_size))

#name, cost (wood, stone, knowledge), location, prerequisites (list of names),description
for tech in (('cartography', [0,0,1], (5,0), (), "Cartography: Your people can now map the world's terrain.|The fog no longer reappears when people move away."),
            ('writing', [2,0,2], (5,1), ('cartography',), "Writing: Every city provides one extra knowledge."),
            ('law', [1,2,4], (5,2), ('cartography','writing'), "Law: The maximum city size is increased by one.|Heresy and civil war are less damaging to cities."),
            ('fishing', [1,0,1], (3,0), (), "Fishing: Your people can gather sail onto the shore and|gather fish, but cannot move across water tiles."),
            ('sailing', [2,1,2], (3,1), ('fishing',), "Sailing: Your people can traverse water."),
            ('navigation', [2,2,3], (3,2), ('fishing','sailing'), "Navigation: Ships enter non-coastal water tiles for free.|Unlocks the Watcher Over the Seas."),
            ('agriculture', [1,1,1], (0,0), (), "Agriculture: For two wood, you can convert grain into a farm.|Farms provide grain every round."),
            ('wheel', [3,0,2], (0,1), ('agriculture',), "The Wheel: Population on grassland can continue moving if the|tile which it enters is already occupied."),
            ('irrigation', [3,3,3], (0,2), ('agriculture','wheel'), "Irrigation: Farms produce 1-4 extra food each round.|Droughts and floods are less likely to replace tiles."),
            ('forestry', [1,0,1], (1,0), (), "Forestry: For one wood and stone, you can build a sawmill.|Forests with sawmills are regrown faster and require only|one worker to fell."),
            ('medicine', [2,0,3], (1,1), ('forestry',), "Medcine: Cities consume only two food per level.|Plagues are half as likely to affect any given city."),
            ('cultivation', [4,1,4], (1,2), ('forestry','medicine'), "Cultivation: Sawmills regrow forests immediately.|Grain, fish, and berries appear more often.|Unlocks the Babbling Gardens."),
            ('mining', [0,1,1], (2,0), (), "Mining: For one wood and stone, you can build a mine.|Four people with a mine can acquire stone."),
            ('metallurgy', [1,2,2], (2,1), ('mining',), "Metallurgy: Forests are felled with two people and rocks are|mined with four people."),
            ('engineering', [2,4,3], (2,2), ('mining','metallurgy'), "Engineering: Building and upgrading cities requires|one fewer stone and wood.|Floods can only reduce cities by one level.|Earthquakes are less damaging to cities and buildings."),
            ('masonry', [0,1,1], (4,0), (), "Masonry: The maximum city size is increased by one."),
            ('mathematics', [2,2,2], (4,1), ('masonry',), "Mathematics: The cost of every technology is reduced by|one wood or stone, whichever is used in a greater quantity."),
            ('architecture', [3,2,3], (4,2), ('masonry','mathematics'), "Architecture: The maximum city size is increased by one.|Earthquakes are less damaging to cities.|Unlocks the Golden Mausoleum."),
            ('mysticism', [0,0,1], (6,0), (), "Mysticism: Building and upgrading cities only requires|four people."),
            ('religion', [1,2,2], (6,1), ('mysticism',), "Religion: Upgrading cities requires three people.|Civil wars and heresy affect fewer tiles."),
            ('philosophy', [1,1,6], (6,2), ('mysticism','religion'), "Philosophy: Knowledge is worth one point per turn.|Heresy has no effect.|Unlocks the Monument to the Sky."),
             ):

    img = pg.transform.scale(pg.image.load(f'art\\civ\\tech\\{tech[0]}.png'),tech_size)

    x = tech_x[tech[2][0]]
    y = tech_y[tech[2][1]]

    img = Image(img,(x,y),tech_size,tech[4])


    techs[tech[0]] = Tech(tech[0],img,False,tech[1],tech[3])
    #adds Tech object to techs dictionary



def draw_tech_tree():
    #background
    pg.draw.rect(game_screen,tech_colour,((ui_size,0),(board_width,board_height)))

    #techs
    possible_techs = []
    for i in techs:

        if techs[i].find_img():
            possible_techs.append(techs[i])                              

    pg.display.update()

    return possible_techs


def use_tech_tree():
    global wood,stone,knowledge

    possible_techs = draw_tech_tree()
    #tech loop
    tech_tree = True
    while tech_tree:
        
        for event in pg.event.get():
            
            if event.type == pg.QUIT:

                pg.quit()

            elif event.type == pg.MOUSEBUTTONDOWN:

                if event.button == 3:

                    help_me(event.pos,tech_tree_open=True)

                elif event.button == 1:

                    if pg.Rect(images['technology'].rect).collidepoint(event.pos):

                        tech_tree = False


                    elif event.pos[0] > ui_size:

                        for tech in possible_techs:

                            if pg.Rect(tech.image.rect).collidepoint(event.pos):#if valid tech is clicked

                                tech.discover()
                                possible_techs = draw_tech_tree()
                                find_ui()

                                game_screen.blit(action_overlay,images['technology'].corner)
                                pg.display.update(images['technology'].rect)
                             

#title

print_text('PyCiv',(320,80),(0,0,0),200)
game_screen.blit(pg.transform.scale(pg.image.load(r'art\title\start.png'),(80,80)),(600,320))
pg.display.update()

title = True
while title:
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            pg.quit()

        elif event.type == pg.MOUSEBUTTONDOWN:

            if event.button == 1:
                if pg.Rect((600,320),(80,80)).collidepoint(event.pos):
                    title = False
            

game_screen.fill((255,255,255))
print_text('Loading...',(440,240),(0,0,0),80)
pg.display.update()


#main tile generation
tiles = []
for x in range(board_tile_width):
    tiles.append([])
    for y in range(board_tile_height):
        rand = r.randint(1,11)
        if rand <= 7:
            new = 'grass'
        elif rand <= 10:
            new = 'forest'
        elif rand <= 11:
            new = 'rocks'
        elif rand <= 13:#does not occur, neither do deserts
            new = 'water'
            
        tiles[-1].append(Tile(new,x,y,[],0,0,None,fog_active))

#mini oceans

for i in range(r.randint(2,4)):
    place = [r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1)]

    tiles[place[0]][place[1]].terrain = 'water'
    
    for j in range(4): protrude(place,0,'water',1024)


#rivers
for l in range(r.randint(2,4)):#river count

    start = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

    i = 0
    j = 0
    river = [r.randint(0,1)]

    if start[0] < board_tile_width/2: river.append(1)
    else: river.append(-1)
    if start[1] < board_tile_height/2: river.append(1)
    else: river.append(-1)

    
    for k in range(r.randint(15,20)):#river size

        if river[0] == 1:
            if r.randint(1,4) != 1: i += river[1]
            else: j += river[2]
        else:
            if r.randint(1,4) != 1: j += river[2]
            else: i += river[1]

        if 0 <= start[0]+i < board_tile_width and 0 <= start[1]+j < board_tile_height:

            tiles[start[0]+i][start[1]+j].terrain = 'water'

        else:
            break


    

for x in range(board_tile_width):#adds features
    for y in range(board_tile_height):

        if tiles[x][y].terrain == 'grass':
            
            if r.randint(1,3) == 1: tiles[x][y].features.append('grain')

        elif tiles[x][y].terrain == 'forest':

            tiles[x][y].features.append('treetops')

            if r.randint(1,3) != 1: tiles[x][y].features.append('berries')

        elif tiles[x][y].terrain == 'water':

            if r.randint(1,20) == 1:

                tiles[x][y].features.append('fish')

#        elif tiles[x][y].terrain == 'rocks':

#        elif tiles[x][y].terrain == 'water':



#picks a start location
begin = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))
while tiles[begin[0]][begin[1]].terrain != 'grass':#must start on grass
    begin = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

tiles[begin[0]][begin[1]].population = start_population
tiles[begin[0]][begin[1]].active_population = start_population
tiles[begin[0]][begin[1]].fog = False

populated_tiles.append((begin[0],begin[1]))

for i in ((0,1),(1,0)):#clears fog
    for j in (-1,1):
        if 0 <= begin[0]+(j*i[0]) < board_tile_width and 0 <= begin[1]+(j*i[1]) < board_tile_height:
            tiles[begin[0]+(j*i[0])][begin[1]+(j*i[1])].fog = False


find_ui()
find_board()
pg.display.update()

game = True
while game:

    turn_done = False

    for event in pg.event.get():

        if event.type == pg.QUIT:
            pg.quit()


        elif event.type == pg.MOUSEBUTTONDOWN:

            if event.button == 3:

                help_me(event.pos)

            elif event.button == 1:

                if event.pos[0] <= ui_size:
                   
                    if pg.Rect(images['next_turn'].rect).collidepoint(event.pos):
                        turn_done = True

                    elif pg.Rect(action_rect).collidepoint(event.pos):#actions

                        action_type = ''
                        for z in act_names:
                            
                            if pg.Rect(images[z].rect).collidepoint(event.pos):
                                action_type = z
                                break

                        if action_type == 'check':

                            for z in populated_tiles:

                                if tiles[z[0]][z[1]].active_population > 0:
                                    tiles[z[0]][z[1]].overlay()      

                            game_screen.blit(action_overlay,images['check'].corner)
                            pg.display.update(images['check'].rect)

                            checking = True
                            while checking:

                                for event_ in pg.event.get():

                                    if event_.type == pg.QUIT:
                                        pg.quit()

                                    elif event_.type == pg.MOUSEBUTTONDOWN:

                                        if event.button == 1:
                                            checking = False


                        elif action_type == 'technology':

                            game_screen.blit(action_overlay,images['technology'].corner)
                            pg.display.update(images['technology'].rect)

                            use_tech_tree()

                            find_board()
                            find_ui()#(images['technology'],action_size))


                        elif action_type in ['gather','fell','mine','build_city','build_production','build_wonder']:

                            game_screen.blit(action_overlay,images[action_type].corner)
                            pg.display.update(images[action_type].rect)

                            possible_tiles = []

                            for z in populated_tiles:
                                
                                tile = tiles[z[0]][z[1]]
                                
                                if tile.active_population >= 1:
                                    
                                    if action_type == 'gather' and ('grain' in tile.features or 'berries' in tile.features or 'fish' in tile.features or 'crops' in tile.features):
                                        possible_tiles.append(z)

                                    elif action_type == 'fell' and 'treetops' in tile.features and ('sawmill' in tile.features or tile.active_population >= 3 - int(techs['metallurgy'].unlocked)):
                                        possible_tiles.append(z)

                                    elif action_type == 'mine' and tile.terrain == 'rocks' and tile.active_population >= 6 - (2*int(techs['metallurgy'].unlocked)):
                                        possible_tiles.append(z)

                                    elif action_type == 'build_wonder':

                                        if (tile.active_population == 6 or tile.active_population == 2 and tile.terrain == 'water') and wood >= wonder_cost and stone >= wonder_cost and wonder_types[tile.terrain] in available_wonders:
                                            possible_tiles.append(z)
                                            
                                    elif action_type == 'build_production':

                                        free_tile = True

                                        for f in building_types:
                                            if f in tile.features:
                                                free_tile = False

                                        if free_tile:

                                            if tile.terrain == 'grass':

                                                if 'grain' in tile.features and wood >= 2 and techs['agriculture'].unlocked:

                                                    possible_tiles.append(z)

                                            elif tile.terrain == 'forest':

                                                if wood >= 1 and stone >= 1 and techs['forestry'].unlocked:

                                                    possible_tiles.append(z)

                                            elif tile.terrain == 'rocks':

                                                if wood >= 1 and stone >= 1 and techs['mining'].unlocked:

                                                    possible_tiles.append(z)

                                    elif action_type == 'build_city' and tile.terrain == 'grass':

                                        free_tile = True

                                        for f in building_types:
                                            if f in tile.features:
                                                free_tile = False

                                        if free_tile and tile.city_level != city_max_size:

                                            if tile.city_level == None:
                                                new = 0
                                            else:
                                                new = tile.city_level + 1

                                            if city_costs[new][0] <= tile.active_population and city_costs[new][1] <= wood and city_costs[new][2] <= stone:#checks resources available

                                                possible_tiles.append(z)


                            for z in possible_tiles:

                                tiles[z[0]][z[1]].overlay()
                                                    

                            acting = True
                            while acting:
                                
                                for event_ in pg.event.get():
                                    
                                    if event_.type == pg.MOUSEBUTTONDOWN:

                                        if event_.button == 1:

                                            acting = True#this bit allows the player to hold shift to continue acting
                                            if not pg.key.get_pressed()[pg.K_LSHIFT]:
                                            
                                                acting = False
                                                

                                            mouse_tile = find_mouse_tile(event_.pos)
                                            if mouse_tile:

                                                x = mouse_tile[0]
                                                y = mouse_tile[1]

                                                if mouse_tile in possible_tiles:

                                                    tile = tiles[x][y]

                                                    if action_type == 'gather':
                                                        
                                                        if 'grain' in tile.features: #if grain
                                                            
                                                            food += r.randint(1,6)
                                                            tile.active_population -= 1
                                                            tile.features.remove('grain')
                                                            tile.find()

                                                        elif 'berries' in tile.features:#if berries

                                                            food += r.randint(1,6)+r.randint(1,6)
                                                            tile.active_population -= 1
                                                            tile.features.remove('berries')
                                                            tile.find()

                                                        elif 'fish' in tile.features:

                                                            food += r.randint(1,6)+r.randint(1,6)+r.randint(1,6)
                                                            tile.active_population -= 1
                                                            tile.features.remove('fish')
                                                            tile.find()
                                                        
                                                        elif 'crops' in tile.features:

                                                            food += r.randint(3,6)
                                                            if techs['irrigation'].unlocked: food += r.randint(1,4)
                                                            tile.active_population -= 1
                                                            tile.features.remove('crops')
                                                            tile.find()

                                                        find_ui((images['food'].corner,(ui_size,images['food'].size[1])))


                                                    elif action_type == 'fell' and 'treetops' in tile.features:

                                                        wood += 1

                                                        manpower = 3
                                                        if 'sawmill' in tile.features:
                                                            manpower -= 2
                                                        elif techs['metallurgy'].unlocked:
                                                            manpower -= 1
                                                        
                                                        tile.active_population -= manpower
                                                        tile.features.remove('treetops')
                                                        if 'berries' in tile.features: tile.features.remove('berries')
                                                        tile.find()

                                                        find_ui((images['wood'].corner,(ui_size,images['wood'].size[1])))
                                                            

                                                    elif action_type == 'mine' and tile.terrain == 'rocks':

                                                        manpower = 6
                                                        
                                                        if techs['metallurgy'].unlocked:
                                                            manpower -= 2


                                                        if tile.active_population >= manpower:

                                                            stone += 1

                                                            tile.active_population -= manpower

                                                            if 'mine' not in tile.features:
                                                                tile.terrain = 'grass'#rocks are go
                                                                
                                                            tile.find()

                                                            find_ui((images['stone'].corner,(ui_size,images['stone'].size[1])))
                                                        

                                                    elif action_type == 'build_wonder':

                                                        tile.decrease_population(tile.population)

                                                        wood -= wonder_cost
                                                        stone -= wonder_cost

                                                        tile.features.append(wonder_types[tile.terrain])
                                                        wonder_tiles.append((x,y))
                                                        available_wonders.remove(wonder_types[tile.terrain])

                                                        for f in ('berries','fish','grain'):
                                                            if f in tile.features: tile.features.remove(f)

                                                            
                                                        for z in ('wood','stone'):
                                                            find_ui((images[z].corner,(ui_size,images[z].size[1])))

                                                        tile.find()


                                                    elif action_type == 'build_production':

                                                        if tile.terrain == 'grass':#farm

                                                            wood -= 2
                                                            tile.active_population -= 1
                                                            tile.features.remove('grain')
                                                            tile.features.append('farm')

                                                        if tile.terrain == 'forest':#sawmill

                                                            wood -= 1
                                                            stone -= 1
                                                            tile.active_population -= 1
                                                            if 'berries' in tiles[x][y].features: tile.features.remove('berries')
                                                            tile.features.append('sawmill')

                                                        if tile.terrain == 'rocks':#mine

                                                            wood -= 1
                                                            stone -= 1
                                                            tile.active_population -= 1
                                                            tile.features.append('mine')

                                                        for z in ('food','wood','stone'):
                                                            find_ui((images[z].corner,(ui_size,images[z].size[1])))
                                                            
                                                        tile.find()
                                                        


                                                    elif action_type == 'build_city':
                                                    
                                                        if tile.city_level == None:
                                                            new = 0
                                                        else:
                                                            new = tile.city_level + 1
                                                                
                                                        if city_costs[new][0] <= tile.active_population and city_costs[new][1] <= wood and city_costs[new][2] <= stone:#checks resources available

                                                            tile.build_city()
                                                            tile.find()

                                                            for z in ('wood','stone','knowledge'):
                                                                find_ui((images[z].corner,(ui_size,images[z].size[1])))
       

                            find_ui()
                        

                elif event.pos[0] > ui_size:#if the mouse is in the board

                    #this part checks for population
                    mouse_tile = find_mouse_tile(event.pos)
                    x = mouse_tile[0]
                    y = mouse_tile[1]
                                        
                    if tiles[x][y].active_population:#this part does the action (currently just movement); it checks active people only

                        possible_tiles = []
                        
                        #finds possible places to move
                        for a in ((0,1),(1,0)):
                            for b in (-1,1):

                                new = (x+(a[0]*b),y+(a[1]*b))

                                if not (-1 in new or new[0] == board_tile_width or new[1] == board_tile_height):#cannot leave board

                                    if techs['fishing'].unlocked or techs['sailing'].unlocked or tiles[new[0]][new[1]].terrain != 'water':#cannot enter water without tech
                                    
                                        if (tiles[new[0]][new[1]].terrain != 'water' and tiles[new[0]][new[1]].population < population_max_density) or (tiles[new[0]][new[1]].terrain == 'water' and tiles[new[0]][new[1]].population < ship_max_density):#cannot enter tiles with 6+ population/2+ if water

                                            fishing_check = True
                                            if tiles[new[0]][new[1]].terrain == 'water' and not techs['sailing'].unlocked:#if fishing

                                                fishing_check = False

                                                for i in ((0,1),(1,0)):
                                                    for j in (-1,1):

                                                        if not fishing_check:

                                                            if 0 <= new[0]+(i[0]*j) < board_tile_width and 0 <= new[1]+(i[1]*j) < board_tile_height:
                                                                if tiles[new[0]+(i[0]*j)][new[1]+(i[1]*j)].terrain != 'water':
                                                                    fishing_check = True
                                                
                                            if fishing_check: possible_tiles.append(new)

                        for z in possible_tiles:

                            tiles[z[0]][z[1]].overlay()
                            

                        moving = True
                        while moving:

                            for event_ in pg.event.get():

                                if event_.type == pg.MOUSEBUTTONDOWN:
                                    
                                    full_move = False#this bit allows the player to hold shift to move all people in a tile
                                    if pg.key.get_pressed()[pg.K_LSHIFT]:
                                    
                                        full_move = True


                                    if event_.button == 1:

                                        moving = False#clicking somewhere invalid ends the movemetn thing

                                        mouse_tile = find_mouse_tile(event_.pos)

                                        if mouse_tile:

                                            if mouse_tile in possible_tiles:#checks if pos is legal
                                                
                                                dest_x = mouse_tile[0]
                                                dest_y = mouse_tile[1]


                                                #enacts the move

                                                change = 1

                                                if full_move and tiles[x][y].terrain != 'water':#cannot full move in water
                                                    change = min(tiles[x][y].active_population,population_max_density - tiles[dest_x][dest_y].population)

                                                remains_active = False

                                                if techs['navigation'].unlocked and tiles[x][y].terrain == 'water' and tiles[dest_x][dest_y].terrain == 'water':
                                                    remains_active = True

                                                    for i in ((0,1),(1,0)):
                                                        for j in (-1,1):

                                                            if 0 <= dest_x+(j*i[0]) < board_tile_width and 0 <= dest_y+(j*i[1]) < board_tile_height:

                                                                if tiles[dest_x+(j*i[0])][dest_y+(j*i[1])].terrain != 'water':

                                                                    remains_active = False

                                                elif techs['wheel'].unlocked and tiles[dest_x][dest_y].population and tiles[x][y].terrain == 'grass' and tiles[dest_x][dest_y].terrain == 'grass':
                                                    remains_active = True
                                                
                                                tiles[x][y].decrease_population(change,True)
                                                tiles[dest_x][dest_y].increase_population(change,remains_active)
                                                
                                                for i in ((0,1),(1,0)):
                                                    for j in (-1,1):#fog remover

                                                        new = (dest_x+(i[0]*j),dest_y+(i[1]*j))

                                                        if not (-1 in new or new[0] == board_tile_width or new[1] == board_tile_height):#cannot leave board

                                                            tiles[new[0]][new[1]].fog = False
                                                            

        elif event.type == pg.KEYDOWN:

            if event.key == pg.K_RETURN:
                turn_done = True


    if turn_done:
        turn_counter += 1
        
        census = 0

        for z in populated_tiles:
            census += tiles[z[0]][z[1]].population
        
        if food == 0:
            
            stage_img = starve_img
            pg.display.set_caption("PyCiv - Starving!")
            game = False
            
        else:
        
            food -= census

            for z in city_tiles:

                food -= city_food_cost*(tiles[z[0]][z[1]].city_level+1)#cites cost 3 food per level, or 2 with medicine
            
            if food < 0:
                stage_img = starve_img
                pg.display.set_caption("PyCiv - Starving!")
            
            find_ui()


            starving = False
            if food < 0:
                starving = True
                for z in populated_tiles:

                    tiles[z[0]][z[1]].overlay(True)
                    
                for z in city_tiles:

                    if z not in populated_tiles:#cannot overlay same tile twice
    
                        tiles[z[0]][z[1]].overlay(True)

                    
            while starving:#starvation; click on people to kill them

                for event_ in pg.event.get():

                    if event_.type == pg.QUIT:

                        pg.quit()

                    elif event_.type == pg.KEYDOWN:

                        if event_.key == pg.K_RETURN and food >= 0:
                            starving = False
                            

                    elif event_.type == pg.MOUSEBUTTONDOWN:

                        if event_.button == 3:

                            help_me(event_.pos,starvation=True)

                        elif event_.button == 1:

                            full_starve = False#this bit allows the player to hold shift to starve all people in a tile
                            if pg.key.get_pressed()[pg.K_LSHIFT]:
                            
                                full_starve = True

                            mouse_tile = find_mouse_tile(event_.pos)

                            if mouse_tile:
                                x = mouse_tile[0]
                                y = mouse_tile[1]

                                if ((x,y) in populated_tiles or (x,y) in city_tiles) and food < 0:

                                    if (x,y) in populated_tiles:

                                        deaths = 1
                                        if full_starve:
                                            deaths = tiles[x][y].population

                                        for i in range(deaths):

                                            tiles[x][y].decrease_population(1,False)
                                            
                                            food += 1
                                            census -= 1

                                            if food >= 0:
                                                break

                                    elif (x,y) in city_tiles:

                                        tiles[x][y].reduce_city(1)

                                        food += city_food_cost

                                    find_ui()
                                    tiles[x][y].find()
                                    
                                    if (x,y) in populated_tiles or (x,y) in city_tiles:
                                        tiles[x][y].overlay(True)

                                    if census == 0 and not city_tiles:#should be unnecessary, but checks for game end nonetheless
                                        game = False
                                        starving = False


                                if food >= 0:

                                    find_board()

                            elif pg.Rect(images['next_turn'].rect).collidepoint(event_.pos) and food >= 0: 
                                starving = False

            
        
        #disaster
        if r.randint(1,disaster_base_chance) >= min(turn_counter,disaster_peaks_at)*disaster_counter:#no disaster
            disaster_counter += disaster_counter_speed
            
        else:#do disaster

            disaster_counter = 0
            
            disaster = r.choice(disaster_list)

            stage_img = disasters[disaster]
            pg.display.set_caption(f"PyCiv - {disaster[0].upper()+disaster[1:]}!")
            
            disaster_tiles = []

            disaster_seen = False
            if not fog_active: disaster_seen = True

            if disaster == 'meteor':

                start = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

                for i in (-1,0,1):
                    for j in (-1,0,1):

                        if 0 <= start[0]+i < board_tile_width and 0 <= start[1]+j < board_tile_height and (start[0]+i,start[1]+j) not in wonder_tiles:

                            disaster_tiles.append((start[0]+i,start[1]+j))

                            if not disaster_seen:
                                if not tiles[start[0]+i][start[1]+j].fog:
                                    disaster_seen = True

                
                if disaster_seen:                    
                    find_ui()

                    for z in disaster_tiles:
                        if not (fog_active and tiles[z[0]][z[1]].fog):
                            tiles[z[0]][z[1]].overlay(True)
                    
                    hesitate(('disaster','meteor'))
            
                for z in disaster_tiles:#the effects occur

                    tile = tiles[z[0]][z[1]]

                    if not (fog_active and tile.fog):

                        tile.overlay(True)

                    tile.decrease_population(population_max_density)
                    tile.reduce_city(city_true_max_size)#destroys all population and cities

                    for f in tile.features:#removes grain, berries, fish, treetops
                        tile.features.remove(f)

                    if tile.terrain == 'forest':#may level forests to grasslands
                        if r.randint(1,3) == 1:
                            tile.terrain = 'grass'

                    if tile.terrain == 'grass':#may crumble grasslands to rocks; slim chance of forest to grass to rocks
                        if r.randint(1,3) == 1:
                            tile.terrain = 'rocks'

                    if r.randint(1,4) == 1:
                        tile.terrain = 'desert'
                            

            elif disaster == 'earthquake':

                for l in range(r.randint(1,4)):#creates 1-4 fissures

                    start = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

                    i = 0
                    j = 0
                    fissure = [r.randint(0,1)]

                    if start[0] < board_tile_width/2: fissure.append(1)
                    else: fissure.append(-1)
                    if start[1] < board_tile_height/2: fissure.append(1)
                    else: fissure.append(-1)
                    
                    for k in range(r.randint(7,14)):

                        if fissure[0] == 1:
                            if r.randint(1,4) != 1: i += fissure[1]
                            else: j += fissure[2]
                        else:
                            if r.randint(1,4) != 1: j += fissure[2]
                            else: i += fissure[1]

                        if 0 <= start[0]+i < board_tile_width and 0 <= start[1]+j < board_tile_height and (start[0]+i,start[1]+j) not in wonder_tiles:

                            if (start[0]+i,start[1]+j) not in disaster_tiles:
                                disaster_tiles.append((start[0]+i,start[1]+j))

                            if not disaster_seen:
                                if not tiles[start[0]+i][start[1]+j].fog:
                                    disaster_seen = True

                
                if disaster_seen:                    
                    find_ui()

                    for z in disaster_tiles:
                        if not (fog_active and tiles[z[0]][z[1]].fog):
                            tiles[z[0]][z[1]].overlay(True)
                    
                    hesitate(('disaster','earthquake'))
            
                for z in disaster_tiles:#the effects occur

                    tile = tiles[z[0]][z[1]]

                    if not (fog_active and tile.fog):

                        tile.overlay(True)

                    if tile.city_level != None: tile.decrease_population(population_max_density)
                    else: tile.decrease_population(1,False)
                    
                    max_dam = 3
                    
                    for t in ('engineering','architecture'):
                        if techs[t].unlocked:
                            max_dam -= 1
                        
                    city_dam = r.randint(0,max_dam)  
                    tile.reduce_city(city_dam)#kills 1 population, or all if there is a city; cities are damaged; also destroys buildsings

                    for f in building_types:
                        if f in tile.features and not (techs['engineering'].unlocked and r.randint(0,1)):
                            tile.features.remove(f)

                    if tile.terrain == 'grass' and tile.city_level == None:#may shake grass to rocks
                        if r.randint(1,3) == 1:
                            if 'grain' in tile.features: tile.features.remove('grain')
                            tile.terrain = 'rocks'
                        

            elif disaster == 'drought':

                start = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

                pos_lists = [[],[]]

                for i in range(2):
                    for j in (-1,1):
                        
                        size = r.randint(1,2)
                        for k in range(size):
                            k += 1
                            if j == -1:
                                k = size+1-k
                            pos_lists[i].append(j*k)

                        if j == -1:
                            pos_lists[i].append(0)


                for i in (pos_lists[0]):
                    for j in (pos_lists[1]):

                        if 0 <= start[0]+i < board_tile_width and 0 <= start[1]+j < board_tile_height and (start[0]+i,start[1]+j) not in wonder_tiles:

                            disaster_tiles.append((start[0]+i,start[1]+j))

                            if not disaster_seen:
                                if not tiles[start[0]+i][start[1]+j].fog:
                                    disaster_seen = True

                
                if disaster_seen:                    
                    find_ui()

                    for z in disaster_tiles:
                        if not (fog_active and tiles[z[0]][z[1]].fog):
                            tiles[z[0]][z[1]].overlay(True)
                    
                    hesitate(('disaster','drought'))
            
                for z in disaster_tiles:#the effects occur

                    tile = tiles[z[0]][z[1]]

                    for f in ('grain','berries','fish','crops'):
                        if f in tile.features:
                            tile.features.remove(f)

                    chance = 5
                    
                    if techs['irrigation'].unlocked:
                        chance += 2
                    
                    if r.randint(1,5) == 1 and tile.terrain != 'water':
                        if tile.city_level != None: tile.reduce_city(city_true_max_size)
                        tile.features = []
                        tile.terrain = 'desert'

                        
            elif disaster == 'flood':

                start = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

                pos_lists = [[],[]]

                for i in range(2):
                    for j in (-1,1):
                        
                        size = r.randint(1,2)
                        for k in range(size):
                            k += 1
                            if j == -1:
                                k = size+1-k
                            pos_lists[i].append(j*k)

                        if j == -1:
                            pos_lists[i].append(0)


                for i in (pos_lists[0]):
                    for j in (pos_lists[1]):

                        if 0 <= start[0]+i < board_tile_width and 0 <= start[1]+j < board_tile_height and (start[0]+i,start[1]+j) not in wonder_tiles:

                            disaster_tiles.append((start[0]+i,start[1]+j))

                            if not disaster_seen:
                                if not tiles[start[0]+i][start[1]+j].fog:
                                    disaster_seen = True

                
                if disaster_seen:                    
                    find_ui()

                    for z in disaster_tiles:
                        if not (fog_active and tiles[z[0]][z[1]].fog):
                            tiles[z[0]][z[1]].overlay(True)
                    
                    hesitate(('disaster','flood'))
            
                for z in disaster_tiles:#the effects occur

                    tile = tiles[z[0]][z[1]]

                    chance = 3

                    if techs['irrigation'].unlocked:
                        chance += 1

                    if r.randint(1,chance) == 1 and tile.terrain != 'water':
                        
                        if tile.city_level != None:
                            if techs['engineering'].unlocked:
                                tile.reduce_city(1)

                            else:
                                tile.reduce_city(city_true_max_size)
                                
                        if tile.city_level == None:#if the city got gobbled
                            tile.decrease_population(population_max_density)
                            tile.features = []
                            tile.terrain = 'water'
                            if r.randint(1,6) == 1:
                                tile.features.append('fish')
                            

            elif disaster == 'plague':

                for z in city_tiles:

                    chance = 4

                    if techs['medicine'].unlocked:
                        chance = 8

                    if r.randint(1,4) <= tiles[z[0]][z[1]].city_level+1:

                        disaster_seen = True

                        disaster_tiles.append(z)

                        for i in (-2,-1,0,1,2):
                            for j in (-2,-1,0,1,2):
                                if 0 <= z[0]+i < board_tile_width and 0 <= z[1]+j < board_tile_height:
                                    if (z[0]+i,z[1]+j) not in wonder_tiles and (z[0]+i,z[1]+j) not in disaster_tiles:

                                        disaster_tiles.append((z[0]+i,z[1]+j))

                
                if disaster_seen:                    
                    find_ui()

                    for z in disaster_tiles:
                        if not (fog_active and tiles[z[0]][z[1]].fog):
                            tiles[z[0]][z[1]].overlay(True)
                    
                    hesitate(('disaster','plague'))
            
                for z in disaster_tiles:#the effects occur

                    tile = tiles[z[0]][z[1]]

                    if tile.city_level != None:
                        tile.decrease_population(tile.city_level+1,False)
                        tile.reduce_city(1)

                    else:
                        tile.decrease_population(1,False)


            elif disaster == 'heresy':

                if not techs['philosophy'].unlocked:#philosophy cancels the event

                    chance = 5

                    if techs['religion'].unlocked:
                        chance += 3

                    for x in range(board_tile_width):
                        for y in range(board_tile_height):

                            if ((x,y) in city_tiles or (x,y) in populated_tiles) and r.randint(1,chance) == 1 and (x,y) not in wonder_tiles:
                                disaster_seen = True
                                disaster_tiles.append((x,y))
                                
                    
                    if disaster_seen:                    
                        find_ui()

                        for z in disaster_tiles:
                            if not (fog_active and tiles[z[0]][z[1]].fog):
                                tiles[z[0]][z[1]].overlay(True)
                        
                        hesitate(('disaster','heresy'))
                
                    for z in disaster_tiles:#the effects occur

                        tile = tiles[z[0]][z[1]]

                        if tile.city_level != None:
                            tile.decrease_population(tile.city_level+1,False)

                            if r.randint(1,2) == 1 or not techs['law'].unlocked:
                                tile.reduce_city(1)

                        if tile.population:
                            tile.decrease_population(1,False)

                        
                  
            elif disaster == 'civil_war':

                start = (r.randint(0,board_tile_width-1),r.randint(0,board_tile_height-1))

                pos_lists = [[],[]]

                for i in range(2):
                    for j in (-1,1):
                        
                        size = r.randint(1,2)

                        if r.randint(0,2) and techs['religion'].unlocked and size == 2:
                            size = 1#religion makes area smaller
                        
                        for k in range(size):
                            k += 1
                            if j == -1:
                                k = size+1-k
                            pos_lists[i].append(j*k)

                        if j == -1:
                            pos_lists[i].append(0)


                for i in (pos_lists[0]):
                    for j in (pos_lists[1]):

                        if 0 <= start[0]+i < board_tile_width and 0 <= start[1]+j < board_tile_height and (start[0]+i,start[1]+j) not in wonder_tiles:

                            disaster_tiles.append((start[0]+i,start[1]+j))

                            if not disaster_seen:
                                if not tiles[start[0]+i][start[1]+j].fog:
                                    disaster_seen = True

                                    
                if disaster_seen:                    
                    find_ui()

                    for z in disaster_tiles:
                        if not (fog_active and tiles[z[0]][z[1]].fog):
                            tiles[z[0]][z[1]].overlay(True)
                    
                    hesitate(('disaster','civil_war'))
            
                for z in disaster_tiles:#the effects occur

                    tile = tiles[z[0]][z[1]]

                    if tile.city_level != None:
                        tile.decrease_population(tile.city_level+1,False)
                        
                        max_dam = tile.city_level+1
                        min_dam = 1
                        if techs['law'].unlocked:
                            max_dam -= 1
                            min_dam -= 1
                            
                        tile.reduce_city(r.randint(min_dam,max_dam))
                    

                    if tile.population:
                        tile.decrease_population(r.randint(1,tile.population),False)
                  

            if disaster_seen:
                find_ui()
                find_board()
                #hesitate(('disaster',disaster))

                    
        for x in range(board_tile_width):#performs things on each tile
            for y in range(board_tile_height):

                tile = tiles[x][y]

                tile.active_population = tile.population#refreshes population
                if tile.population > 1 and tile.terrain != 'water':
                    tile.population = min(tile.population+1,population_max_density)#grouped population grows by 1, to a maximum of 6
                
                
                if tile.population > 0 and (x,y) not in populated_tiles:
                    populated_tiles.append((x,y))

                elif tile.population == 0 and (x,y) in populated_tiles:
                    populated_tiles.remove((x,y))
                    

                if tile.terrain == 'grass':#if grass

                    if tile.city_level != None:
                        pass

                    elif 'farm' in tile.features:
                        if 'crops' not in tile.features:
                            tile.features.append('crops')
                    
                    elif 'monument' not in tile.features and 'grain' not in tile.features and r.randint(1,35-(10*int(techs['cultivation'].unlocked))) == 1:#adds grain
                        tile.features.append('grain')

                elif tile.terrain == 'forest':#if forest

                    if 'treetops' not in tile.features:

                        chance = 5

                        if 'sawmill' in tile.features:
                            chance -= 2
                            if techs['cultivation'].unlocked:
                                chance -= 2

                        if r.randint(1,chance) == 1:#regrows treetops
                            tile.features.append('treetops')

                    elif 'sawmill' not in tile.features and 'garden' not in tile.features and 'berries' not in tile.features and r.randint(1,7-(2*int(techs['cultivation'].unlocked))) == 1:#adds berries
                          tile.features.append('berries')
                          

                elif tile.terrain == 'water':

                    if 'fish' not in tile.features:

                        if 'watcher' not in tile.features and r.randint(1,42-(12*int(techs['cultivation'].unlocked))) == 1:#fish reappear
                            tile.features.append('fish')


                if not (techs['cartography'].unlocked or tile.fog):#this part makes the fog return

                    if not ((x,y) in populated_tiles or (x,y) in city_tiles):#if tile lacks population and a city

                        unseen_test = True
                        for i in ((0,1),(1,0)):
                            for j in (-1,1):

                                if (x+(j*i[0]),y+(j*i[1])) in populated_tiles or (x+(j*i[0]),y+(j*i[1])) in city_tiles:#if tile has city/population
                                    unseen_test = False

                        if unseen_test:#the fog returns...
                            tile.fog = True


        #scoring
        for z in techs:

            if techs[z].unlocked:

                score += (1,3,6)[len(techs[z].prereqs)]

        for z in city_tiles:

            score += (1,3,6,10)[tiles[z[0]][z[1]].city_level]

        if techs['philosophy'].unlocked:

            score += knowledge#love of knowledge

        score += 50*len(wonder_tiles)#wonders are 50 points each


        if not populated_tiles and not city_tiles:#everyone is dead
            game = False
        
        #actual end of turn/round
        stage_img = action_img
        pg.display.set_caption("PyCiv")
                
        turn_done = False


                                    

    find_ui()
    find_board()

            
#add losing screen
#or maybe victory somehow?
pg.quit()
