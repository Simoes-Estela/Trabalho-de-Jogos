import math
import random
import pygame
from enum import Enum, auto

pygame.init()

LARGURA, ALTURA = 900, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sobrevivente - Survivor Shooter")
RELOGIO = pygame.time.Clock()

FONTE = pygame.font.SysFont("arial", 22)
FONTE_GRANDE = pygame.font.SysFont("arial", 48, bold=True)
FONTE_PEQUENA = pygame.font.SysFont("arial", 16)

PRETO = (15, 18, 28)
BRANCO = (240, 242, 250)
CINZA = (95, 105, 125)
VERDE = (70, 210, 125)
VERMELHO = (235, 75, 85)
AMARELO = (250, 210, 80)
AZUL = (75, 160, 245)
ROXO = (175, 110, 235)


EVT_CRIAR_INIMIGO = pygame.USEREVENT + 1
EVT_INIMIGO_MORTO = pygame.USEREVENT + 2
EVT_JOGADOR_DANIFICADO = pygame.USEREVENT + 3
EVT_COLETAR_POWERUP = pygame.USEREVENT + 4


class EstadoJogador(Enum):
    NORMAL = auto()
    INVENCIVEL = auto()
    POWERUP = auto()
    MORTO = auto()

class EstadoInimigo(Enum):
    APROXIMANDO = auto()
    ATORDOADO = auto()
    MORTO = auto()


class Projetil:
    def __init__(self, x, y, destino, dano=1):
        self.pos = pygame.Vector2(x, y)
        direcao = pygame.Vector2(destino) - self.pos
        if direcao.length_squared() == 0:
            direcao = pygame.Vector2(1, 0)
        self.vel = direcao.normalize() * 570
        self.raio = 5
        self.dano = dano
        self.ativo = True

    def atualizar(self, dt):
        self.pos += self.vel * dt
        if (self.pos.x < -20 or self.pos.x > LARGURA + 20 or
                self.pos.y < -20 or self.pos.y > ALTURA + 20):
            self.ativo = False

    def desenhar(self, tela):
        pygame.draw.circle(tela, AMARELO, (int(self.pos.x), int(self.pos.y)), self.raio)


class Inimigo:
    def __init__(self, x, y, onda):
        self.pos = pygame.Vector2(x, y)
        self.raio = random.randint(15, 21)
        self.vida = 2 if onda >= 3 and random.random() < 0.25 else 1
        self.velocidade = random.randint(75, 105) + onda * 4
        self.estado = EstadoInimigo.APROXIMANDO
        self.tempo_atordoado = 0
        self.ativo = True

    def atualizar(self, dt, jogador):
        if self.estado == EstadoInimigo.MORTO:
            return

        if self.estado == EstadoInimigo.ATORDOADO:
            self.tempo_atordoado -= dt
            if self.tempo_atordoado <= 0:
                self.estado = EstadoInimigo.APROXIMANDO
            return

        direcao = jogador.pos - self.pos
        if direcao.length_squared() > 0:
            self.pos += direcao.normalize() * self.velocidade * dt

    def receber_tiro(self, dano):
        if self.estado == EstadoInimigo.MORTO:
            return False
        self.vida -= dano
        if self.vida <= 0:
            self.estado = EstadoInimigo.MORTO
            self.ativo = False
            return True
        self.estado = EstadoInimigo.ATORDOADO
        self.tempo_atordoado = 0.35
        return False

    def desenhar(self, tela):
        if self.estado == EstadoInimigo.MORTO:
            return
        cor = ROXO if self.estado == EstadoInimigo.ATORDOADO else VERMELHO
        pygame.draw.circle(tela, cor, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(tela, (255, 180, 180), (int(self.pos.x - 6), int(self.pos.y - 4)), 3)
        pygame.draw.circle(tela, (255, 180, 180), (int(self.pos.x + 6), int(self.pos.y - 4)), 3)


class PowerUp:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.raio = 12
        self.ativo = True

    def desenhar(self, tela):
        pygame.draw.circle(tela, AZUL, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.line(tela, BRANCO, (self.pos.x - 6, self.pos.y),
                         (self.pos.x + 6, self.pos.y), 3)
        pygame.draw.line(tela, BRANCO, (self.pos.x, self.pos.y - 6),
                         (self.pos.x, self.pos.y + 6), 3)


class Jogador:
    def __init__(self):
        self.pos = pygame.Vector2(LARGURA / 2, ALTURA / 2)
        self.raio = 17
        self.velocidade = 260
        self.vida_maxima = 5
        self.vida = self.vida_maxima
        self.estado = EstadoJogador.NORMAL
        self.tempo_invencivel = 0
        self.tempo_powerup = 0
        self.intervalo_tiro = 0.22
        self.tempo_tiro = 0

    def atualizar(self, dt, teclas):
        movimento = pygame.Vector2(0, 0)
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            movimento.y -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            movimento.y += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            movimento.x -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            movimento.x += 1

        if movimento.length_squared() > 0:
            self.pos += movimento.normalize() * self.velocidade * dt

        self.pos.x = max(self.raio, min(LARGURA - self.raio, self.pos.x))
        self.pos.y = max(self.raio, min(ALTURA - self.raio, self.pos.y))

        self.tempo_tiro = max(0, self.tempo_tiro - dt)

        if self.estado == EstadoJogador.INVENCIVEL:
            self.tempo_invencivel -= dt
            if self.tempo_invencivel <= 0:
                self.estado = EstadoJogador.NORMAL
        elif self.estado == EstadoJogador.POWERUP:
            self.tempo_powerup -= dt
            if self.tempo_powerup <= 0:
                self.estado = EstadoJogador.NORMAL

    def pode_atirar(self):
        return self.tempo_tiro <= 0 and self.estado != EstadoJogador.MORTO

    def atirar(self, destino):
        if not self.pode_atirar():
            return None
        dano = 2 if self.estado == EstadoJogador.POWERUP else 1
        self.tempo_tiro = self.intervalo_tiro * (0.55 if dano == 2 else 1)
        return Projetil(self.pos.x, self.pos.y, destino, dano)

    def receber_dano(self):
        if self.estado in (EstadoJogador.INVENCIVEL, EstadoJogador.POWERUP,
                           EstadoJogador.MORTO):
            return False
        self.vida -= 1
        if self.vida <= 0:
            self.estado = EstadoJogador.MORTO
        else:
            self.estado = EstadoJogador.INVENCIVEL
            self.tempo_invencivel = 1.25
        return True

    def pegar_powerup(self):
        self.estado = EstadoJogador.POWERUP
        self.tempo_powerup = 6.0

    def desenhar(self, tela):
        if self.estado == EstadoJogador.INVENCIVEL and int(pygame.time.get_ticks() / 100) % 2 == 0:
            return
        cor = AMARELO if self.estado == EstadoJogador.POWERUP else VERDE
        pygame.draw.circle(tela, cor, (int(self.pos.x), int(self.pos.y)), self.raio)
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        direcao = mouse - self.pos
        if direcao.length_squared() > 0:
            ponta = self.pos + direcao.normalize() * 27
            pygame.draw.line(tela, BRANCO, self.pos, ponta, 5)


class Jogo:
    def __init__(self):
        self.rodando = True
        self.reiniciar()

    def reiniciar(self):
        self.jogador = Jogador()
        self.inimigos = []
        self.projeteis = []
        self.powerups = []
        self.pontuacao = 0
        self.onda = 1
        self.tempo_onda = 0
        self.tempo_spawn = 0
        self.game_over = False
        self.eventos_pendentes = []

    def criar_inimigo(self):
        lado = random.randint(0, 3)
        if lado == 0:
            x, y = random.randint(0, LARGURA), -25
        elif lado == 1:
            x, y = random.randint(0, LARGURA), ALTURA + 25
        elif lado == 2:
            x, y = -25, random.randint(0, ALTURA)
        else:
            x, y = LARGURA + 25, random.randint(0, ALTURA)
        self.inimigos.append(Inimigo(x, y, self.onda))

    def processar_evento_jogo(self, evento):
        if evento.type == EVT_CRIAR_INIMIGO:
            self.criar_inimigo()
        elif evento.type == EVT_INIMIGO_MORTO:
            self.pontuacao += 10
            if random.random() < 0.13:
                origem = evento.posicao
                self.powerups.append(PowerUp(origem[0], origem[1]))
        elif evento.type == EVT_JOGADOR_DANIFICADO:
            self.jogador.receber_dano()
        elif evento.type == EVT_COLETAR_POWERUP:
            self.jogador.pegar_powerup()

    def atualizar(self, dt):
        if self.game_over:
            return

        teclas = pygame.key.get_pressed()
        self.jogador.atualizar(dt, teclas)

        self.tempo_onda += dt
        if self.tempo_onda >= 18:
            self.onda += 1
            self.tempo_onda = 0

        self.tempo_spawn += dt
        intervalo_spawn = max(0.38, 1.35 - self.onda * 0.07)
        if self.tempo_spawn >= intervalo_spawn:
            self.tempo_spawn = 0
            pygame.event.post(pygame.event.Event(EVT_CRIAR_INIMIGO))

        for projetil in self.projeteis:
            projetil.atualizar(dt)
        self.projeteis = [p for p in self.projeteis if p.ativo]

        # serve para atualiza os inimigos e verifica se tem colisões colisões.
        for inimigo in self.inimigos:
            inimigo.atualizar(dt, self.jogador)

            if inimigo.estado != EstadoInimigo.MORTO:
                distancia = inimigo.pos.distance_to(self.jogador.pos)
                if distancia < inimigo.raio + self.jogador.raio:
                    pygame.event.post(pygame.event.Event(EVT_JOGADOR_DANIFICADO))
                    # Afasta o inimigo para evitar vários danos no mesmo instante.
                    direcao = inimigo.pos - self.jogador.pos
                    if direcao.length_squared() > 0:
                        inimigo.pos += direcao.normalize() * 35

                for projetil in self.projeteis:
                    if projetil.ativo and inimigo.pos.distance_to(projetil.pos) < inimigo.raio + projetil.raio:
                        projetil.ativo = False
                        morreu = inimigo.receber_tiro(projetil.dano)
                        if morreu:
                            pygame.event.post(pygame.event.Event(
                                EVT_INIMIGO_MORTO,
                                posicao=(inimigo.pos.x, inimigo.pos.y)
                            ))
                        break

        self.inimigos = [i for i in self.inimigos if i.ativo]
        self.projeteis = [p for p in self.projeteis if p.ativo]

        # Coleta de power-ups.
        for item in self.powerups:
            if item.ativo and item.pos.distance_to(self.jogador.pos) < item.raio + self.jogador.raio:
                item.ativo = False
                pygame.event.post(pygame.event.Event(EVT_COLETAR_POWERUP))
        self.powerups = [p for p in self.powerups if p.ativo]

        if self.jogador.estado == EstadoJogador.MORTO:
            self.game_over = True

    def desenhar_hud(self):
        pygame.draw.rect(TELA, (30, 35, 50), (0, 0, LARGURA, 54))
        texto = FONTE.render(f"Vida: {self.jogador.vida}/{self.jogador.vida_maxima}", True, BRANCO)
        TELA.blit(texto, (18, 14))
        texto = FONTE.render(f"Pontos: {self.pontuacao}", True, AMARELO)
        TELA.blit(texto, (220, 14))
        texto = FONTE.render(f"Onda: {self.onda}", True, BRANCO)
        TELA.blit(texto, (410, 14))
        texto = FONTE.render(f"Inimigos: {len(self.inimigos)}", True, VERMELHO)
        TELA.blit(texto, (560, 14))

        if self.jogador.estado == EstadoJogador.POWERUP:
            status = f"POWER-UP: {self.jogador.tempo_powerup:.1f}s"
            TELA.blit(FONTE_PEQUENA.render(status, True, AZUL), (750, 19))

    def desenhar(self):
        TELA.fill(PRETO)

        # Grade discreta para dar referência espacial.
        for x in range(0, LARGURA, 40):
            pygame.draw.line(TELA, (25, 30, 43), (x, 54), (x, ALTURA))
        for y in range(54, ALTURA, 40):
            pygame.draw.line(TELA, (25, 30, 43), (0, y), (LARGURA, y))

        for item in self.powerups:
            item.desenhar(TELA)
        for projetil in self.projeteis:
            projetil.desenhar(TELA)
        for inimigo in self.inimigos:
            inimigo.desenhar(TELA)
        self.jogador.desenhar(TELA)

        self.desenhar_hud()

        if self.game_over:
            escurecer = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            escurecer.fill((0, 0, 0, 180))
            TELA.blit(escurecer, (0, 0))
            titulo = FONTE_GRANDE.render("GAME OVER", True, VERMELHO)
            TELA.blit(titulo, titulo.get_rect(center=(LARGURA / 2, ALTURA / 2 - 45)))
            resultado = FONTE.render(f"Pontuação: {self.pontuacao}", True, BRANCO)
            TELA.blit(resultado, resultado.get_rect(center=(LARGURA / 2, ALTURA / 2 + 10)))
            dica = FONTE.render("Pressione ESPACO para jogar novamente", True, BRANCO)
            TELA.blit(dica, dica.get_rect(center=(LARGURA / 2, ALTURA / 2 + 55)))

        pygame.display.flip()

    def executar(self):
        while self.rodando:
            dt = min(RELOGIO.tick(60) / 1000, 0.04)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.rodando = False
                    if evento.key == pygame.K_SPACE and self.game_over:
                        self.reiniciar()

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if not self.game_over:
                        tiro = self.jogador.atirar(evento.pos)
                        if tiro:
                            self.projeteis.append(tiro)

                if evento.type in (EVT_CRIAR_INIMIGO, EVT_INIMIGO_MORTO,
                                   EVT_JOGADOR_DANIFICADO, EVT_COLETAR_POWERUP):
                    self.processar_evento_jogo(evento)

            self.atualizar(dt)
            self.desenhar()

        pygame.quit()


if __name__ == "__main__":
    Jogo().executar()
