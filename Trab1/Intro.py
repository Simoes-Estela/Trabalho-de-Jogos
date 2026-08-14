# Inicialização
import pygame 
import random
pygame.init()
pygame.font.init()



font = font = pygame.font.Font(None, 50)
Nome = "Estela"
rect =  (300, 100, 160, 40)

random.seed(Nome)
x, y =  330, 105

print(y)

# Cria a janela
WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

#loop
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        # Desenha
        screen.fill((40, 30, 30))
        pygame.draw.rect(screen, (200,0,255), rect)
        screen.blit(font.render(Nome, True, (0,0,0)), (x, y))
        pygame.display.flip()
