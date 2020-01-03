import pygame
import pygame.freetype
import random
import os
import numpy
from enum import Enum

class AlienArea(pygame.sprite.Sprite):
    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, width, height)


class Alien(pygame.sprite.Sprite):
    def __init__(self, image, location, lives):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = location
        self.lives = lives

    def getLocation(self):
        return(self.rect.left, self.rect.top)

    def update(self):
        self.rect = self.rect.move(0, 1)

    def hit(self):
        self.lives -= 1
        if self.lives == 0:
            self.kill()
            return True
        return False


class DropTypes(Enum):
    BOMB = 0
    LIFE = 1
    FREEZE = 2
    SLOW = 3

class Drop(pygame.sprite.Sprite):
    def __init__(self, image, location, dropType):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = location
        self.dropType = dropType

    def getLocation(self):
        return(self.rect.left, self.rect.top)

    def update(self):
        self.rect = self.rect.move(0, 15)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, location, explosionImages):
        pygame.sprite.Sprite.__init__(self)
        self.rect = explosionImages[1].get_rect()
        self.explosionImages = explosionImages
        self.image = explosionImages[0]
        self.rect.left, self.rect.top = location
        self.counter = 1

    def update(self):
        if self.counter == len(self.explosionImages):
            self.kill()
        else:
            self.image = self.explosionImages[self.counter]
            self.counter += 1


class Missile(pygame.sprite.Sprite):
    def __init__(self, image, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect = self.rect.move(location[0]-int(self.rect.width/2), location[1])

    def update(self):
        if self.rect.midbottom[1] <= 0:
            self.kill()
        self.rect = self.rect.move(0, -11)


class Shooter(pygame.sprite.Sprite):
    def __init__(self, image, frozenImage, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.defaultImage = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = (location[0]-int(self.rect.width/2), location[1]-self.rect.height)
        self.area = pygame.display.get_surface().get_rect()
        self.speed = 0
        self.freezeCounter = 0
        self.slowCounter = 0
        self.frozenImage = frozenImage

    def update(self):
        if self.rect.right > self.area.right and self.speed > 0:
            self.speed = 0
        if self.rect.left < self.area.left and self.speed < 0:
            self.speed = 0
        if self.freezeCounter == 0:
            self.rect = self.rect.move(self.speed, 0)
        if self.slowCounter > 0:
            self.slowCounter -= 1
            # speed up movement to default if "slow" ends
            if self.slowCounter == 0:
                self.speed *= 10
        if self.freezeCounter > 0:
            self.freezeCounter -= 1
            if self.freezeCounter == 0:
                self.image = self.defaultImage

    def freeze(self):
        self.stopMoving()
        self.freezeCounter = 80
        self.image = self.frozenImage

    def slow(self):
        self.stopMoving()
        self.slowCounter = 100

    def stopMoving(self):
        self.speed = 0

    def moveRight(self):
        if self.slowCounter > 0:
            self.speed = 1
        else:
            self.speed = 10

    def moveLeft(self):
        if self.slowCounter > 0:
            self.speed = -1
        else:
            self.speed = -10


class Background(pygame.sprite.Sprite):
    def __init__(self, image, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

class StatusBar(pygame.sprite.Sprite):
    def __init__(self, location, rect, status):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(location, rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.font = pygame.freetype.SysFont("Alegreya Sans",24)
        self.status = status
    def draw(self, screen):
        self.image.fill((0,113,156))
        self.font.render_to(self.image, (5,5), "Enemies Destroyed: "+str(self.status.kills), fgcolor=(0, 0, 0))
        self.font.render_to(self.image, (300,5), "Lives: "+str(self.status.lives), fgcolor=(0, 0, 0))
        self.font.render_to(self.image, (450,5), "Level: "+str(self.status.level), fgcolor=(0, 0, 0))
        screen.blit(self.image, self.rect)


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
