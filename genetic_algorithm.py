import random
import pygame
from pygame.locals import *
import os

pressure=3
mutation_chance = 0.3

#game constants
SCREENRECT     = Rect(0, 0, 640, 480)
LONG_INDIVIDUO = 30
NPOPULATION    = 20
MIN_IND        = -64
MAX_IND        = 64
NOBSTACULOS    = 8

class Obstaculo(pygame.sprite.Sprite):
    images = []
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(x=x,y=y)

class Player(pygame.sprite.Sprite):
    speed = 16
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self,self.container)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        
    def move(self,movx):
        self.rect.move_ip(movx,-self.speed)
    

class  Explosion(pygame.sprite.Sprite):
    defaultlife = 2
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0: self.kill()


class Genetic():
    def __init__(self,long_individuo,npopulation,min_ind,max_ind):
        self.long_individuo = long_individuo
        self.npopulation = npopulation
        self.min_ind = min_ind
        self.max_ind  = max_ind
        self.population  = self.gen_population()
        
    def gen_individuo(self):
        return [ random.randint(self.min_ind,self.max_ind) for gen in range(self.long_individuo) ]

    def gen_population(self):
        return [ self.gen_individuo() for ind in range(self.npopulation) ]

    def selection_and_reproduction(self,puntuados): #Se le envian la poblacion y su respectivo fitness
        
        puntuados = [i[1] for i in sorted(puntuados)] #Ordena de mayor a menor fitness y se almacena la poblacion ordenada en una lista
        population = puntuados
    
        selected =  puntuados[(len(puntuados)-pressure):] #Esta linea selecciona los 'n' individuos del final, donde n viene dado por 'pressure'
    
        #Se mezcla el material genetico para crear nuevos individuos
        for i in range(len(population)-pressure):
            padre = random.sample(selected, 2) #Se eligen dos padres al azar
            punto = random.randint(1,self.long_individuo-1) #Se elige un punto para hacer el intercambio
            
            population[i][:punto] = padre[0][:punto] #Se mezcla el material genetico de los padres en cada nuevo individuo
            population[i][punto:] = padre[1][punto:]
    
        return population #El array 'population' tiene ahora una nueva poblacion de

    def mutation(self,population):
        for i in range(len(population)-pressure):
            if random.random() <= mutation_chance: #Cada individuo de la poblacion (menos los padres) tienen una probabilidad de mutar
                punto = random.randint(0,self.long_individuo-1) #Se elgie un punto al azar
                nuevo_valor = random.randint(self.min_ind,self.max_ind) #y un nuevo valor para este punto
    
                #Es importante mirar que el nuevo valor no sea igual al viejo
                while nuevo_valor == population[i][punto]:
                    nuevo_valor = random.randint(self.min_ind,self.max_ind)
                #Se aplica la mutacion
                population[i][punto] = nuevo_valor
        return population


#print("Poblacion Inicial:\n%s"%(population)) #Se muestra la poblacion inicia
#Se evoluciona la poblacion

#print(population)
#print([ get_fitness(ind) for ind in population ])
#print(gen_population())
#print(tournament(population))

def load_image(file):
    file = os.path.join(os.path.split(os.path.abspath(__file__))[0],"data",file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load the image "%s" %s'%(file,pygame.get_error()))
    return surface.convert()

def main():
    #variables AG
    genetic_algorithm = Genetic(LONG_INDIVIDUO,NPOPULATION,MIN_IND,MAX_IND)
    population = genetic_algorithm.gen_population()#Inicializar una poblacion

    #print("Fitness Despues de entrenar")
    #print("Poblacion Final:\n%s"%(population)) #Se muestra la poblacion Final
    #print([ get_fitness(ind) for ind in population])
    #initialize pygame 

    pygame.init()
    #set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    #load images
    img = load_image("alien2.png")
    Player.images = [img]

    img = load_image("brick.png")
    Obstaculo.images = [img]


    img = load_image('explosion1.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]

    bgdtile = load_image('background.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()
    clock = pygame.time.Clock()
    all = pygame.sprite.RenderUpdates()
    obstaculos = pygame.sprite.Group()

    Player.container = all
    Obstaculo.containers = all,obstaculos
    Explosion.containers = all
    player = Player()
    fitness = 60
    puntation = []
    #Generar obstaculos aleatorios
    
    [Obstaculo( random.randint(0,SCREENRECT.w-Obstaculo.images[0].get_width()), y*(Obstaculo.images[0].get_height()))  for y in range(NOBSTACULOS)]
    
    for x in range(100):
        for ind in population:
            for gen in ind:
                player.move(gen)
                for obs  in pygame.sprite.spritecollide(player, obstaculos, 0):
                    fitness -= 2  
                    Explosion(player)

                if not SCREENRECT.contains(player.rect):
                    fitness -= 2
                clock.tick(40)
                all.update()
                all.clear(screen,background)
                dirty = all.draw(screen)
                pygame.display.update(dirty)
                for event in pygame.event.get():
                    if event.type == QUIT or \
                        (event.type == KEYDOWN and event.key == K_ESCAPE):
                            return
            print(fitness)
            puntation.append((fitness, ind)) #Calcula el fitness de cada individuo, y lo guarda en pares ordenados de la forma (5 , [1,2,1,1,4,1,8,9,4,1])
            
            #Iniciar los parametros para el siguiente individuo
            player = Player()
            fitness = 60
        
        population = genetic_algorithm.selection_and_reproduction(puntation) #Envio la poblacion con su fitness
        population = genetic_algorithm.mutation(population)
        puntation.clear()     

    pygame.quit()
    pygame.time.wait(1000)


if __name__ == "__main__": main()