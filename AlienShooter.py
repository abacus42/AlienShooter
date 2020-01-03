from Sprites import *
import random
import os
import numpy


class Status:
    def __init__(self):
        self.reset()
    def reset(self):
        self.kills = 0
        self.lives = 3
        self.level = 1
        self.DifficultyVectors = [(0.8,0.1,0.1),(0.6, 0.2, 0.2), (0.4, 0.3, 0.3), (0.2, 0.4, 0.4), (0.2, 0.2, 0.6), (0.1, 0.1, 0.8)]
        self.DifficultyVector = self.DifficultyVectors[1]
    def levelUp(self):
        self.level += 1
        if self.level-1 >= len(self.DifficultyVectors):
            self.DifficultyVector = self.DifficultyVectors[level]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("AlienShooter")
        self.clock = pygame.time.Clock()
        self.screenWidth = 1100
        self.screenHeight = 900
        statusBarHeight = 30
        self.showMenu = True
        self.status = Status()

        self.font = pygame.freetype.SysFont("Alegreya Sans",72)
        self.menu, rect = self.font.render("Klick to Start New Game", (0,113,156))

        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        backgroundImage = self.loadImage("space.jpg")
        backgroundImage = pygame.transform.scale(backgroundImage, (self.screenWidth, self.screenHeight))
        alienImage = self.loadImage("alien.png")
        alienImage = pygame.transform.scale(alienImage, (100, 70))
        alienMediumImage = self.loadImage("alien_medium.png")
        alienMediumImage = pygame.transform.scale(alienMediumImage, (100, 70))
        alienHardImage = self.loadImage("alien_hard.png")
        alienHardImage = pygame.transform.scale(alienHardImage, (100, 70))
        self.alienImages = [alienImage, alienMediumImage, alienHardImage]
        self.missileImage = self.loadImage("missile.png")
        shooterImage = self.loadImage("shooter.png")
        heartImage = self.loadImage("heart.png")
        bombImage = self.loadImage("bomb.png")
        snowflakeImage = self.loadImage("snowflake.png")
        snailImage = self.loadImage("snail.png")
        shooterFrozenImage = self.loadImage("shooter_frozen.png")
        self.dropImages = [bombImage, heartImage, snowflakeImage, snailImage]
        self.background = Background(backgroundImage, (0,0))
        self.shooter = Shooter(shooterImage, shooterFrozenImage, (int(self.screenWidth/2), self.screenHeight-statusBarHeight))
        self.statusBar = StatusBar((0, self.screenHeight-statusBarHeight),(self.screenWidth,statusBarHeight), self.status)
        self.explosionImages = []
        self.statusBarSprite = pygame.sprite.RenderPlain(self.statusBar)
        self.shooterSprite = pygame.sprite.RenderPlain(self.shooter)
        self.missileSprites = pygame.sprite.RenderPlain()
        self.alienSprites = pygame.sprite.RenderPlain()
        self.ExplosionSprites = pygame.sprite.RenderPlain()
        self.DropSprites = pygame.sprite.RenderPlain()
        for i in range(1,21):
            self.explosionImages.append(self.loadImage("explosion/explosion"+str(i)+".png"))

    def startNewGame(self):
        self.resetGame()
        self.ExplosionSprites.empty()
        self.showMenu = False
        self.status.reset()

    def resetGame(self):
        self.missileSprites.empty()
        self.alienSprites.empty()
        self.DropSprites.empty()
        self.addAlienRow(0)

    def addAlienRow(self, y):
        image_width = self.alienImages[0].get_rect().width
        for i in range(0, (self.screen.get_rect().width//image_width)):
            # randomly choose number of lives of each alien
            lives = numpy.random.choice([1,2,3], p=self.status.DifficultyVector)
            self.alienSprites.add(Alien(self.alienImages[lives-1], (i*image_width, y), lives))

    def loadImage(self, name):
        fullname = os.path.join('Images', name)
        try:
            image = pygame.image.load(fullname)
        except:
            print("Could not load picture: "+ fullname)
            raise SystemExit
        image = image.convert()
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def handleEvent(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_l]:
                    self.shooter.moveRight()
                if event.key in [pygame.K_LEFT, pygame.K_a, pygame.K_j]:
                    self.shooter.moveLeft()
                if event.key == pygame.K_SPACE:
                    self.missileSprites.add(Missile(self.missileImage, self.shooter.rect.midtop))
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT,pygame.K_RIGHT, pygame.K_d, pygame.K_a, pygame.K_l, pygame.K_j]:
                self.shooter.stopMoving()
        if self.showMenu and event.type == pygame.MOUSEBUTTONUP:
            self.startNewGame()

    def loop(self):
        self.missileSprites.update()
        self.shooter.update()
        self.alienSprites.update()
        self.ExplosionSprites.update()
        self.DropSprites.update()
        if not pygame.sprite.spritecollideany(AlienArea(self.screen.get_rect().width, 60), self.alienSprites):
            self.addAlienRow(-1*self.alienImages[0].get_rect().height)
        for missile in self.missileSprites:
            for alien in self.alienSprites:
                if pygame.sprite.collide_rect(alien, missile):
                    missile.kill()
                    # alien.hit() returns True if the alien is killed
                    if alien.hit():
                        self.status.kills +=1
                        self.ExplosionSprites.add(Explosion(alien.getLocation(), self.explosionImages))
                        # drop someting (life, bomb, etc.) with certain probability
                        if random.randint(1, 10) == 10:
                            n = random.randint(0, len(self.dropImages)-1)
                            self.DropSprites.add(Drop(self.dropImages[n], alien.getLocation(), DropTypes(n)))
        for drop in self.DropSprites:
            if pygame.sprite.collide_rect(drop, self.statusBar):
                drop.kill()
            if pygame.sprite.collide_rect(drop, self.shooter):
                if drop.dropType == DropTypes.BOMB:
                    self.status.lives -= 1
                    self.ExplosionSprites.add(Explosion(drop.getLocation(), self.explosionImages))
                if drop.dropType == DropTypes.LIFE:
                    self.status.lives += 1
                if drop.dropType == DropTypes.FREEZE:
                    self.shooter.freeze()
                if drop.dropType == DropTypes.SLOW:
                    self.shooter.slow()
                drop.kill()
        for alien in self.alienSprites:
            if pygame.sprite.collide_rect(alien, self.statusBar) or pygame.sprite.collide_rect(alien, self.shooter):
                self.ExplosionSprites.add(Explosion(alien.getLocation(), self.explosionImages))
                self.status.lives -= 1
                self.resetGame()
                break
        # increase level every 40 kills
        if self.status.level*40 - self.status.kills <= 0:
            self.status.levelUp()
        if self.status.lives == 0:
            self.showMenu = True

    def renderGame(self):
        if self.showMenu:
            self.screen.blit(self.menu, self.menu.get_rect(center=(self.screenWidth//2, self.screenHeight//2)))
        else:
            self.screen.fill([255, 255, 255])
            self.screen.blit(self.background.image, self.background.rect)
            self.missileSprites.draw(self.screen)
            self.shooterSprite.draw(self.screen)
            self.alienSprites.draw(self.screen)
            self.DropSprites.draw(self.screen)
            self.ExplosionSprites.draw(self.screen)
            self.statusBar.draw(self.screen)
        pygame.display.flip()

    def execute(self):
        self.running = True
        while self.running:
            self.clock.tick(50)
            for event in pygame.event.get():
                self.handleEvent(event)
            self.loop()
            self.renderGame()

def main():
    game = Game()
    game.execute()

if __name__ == '__main__': main()
