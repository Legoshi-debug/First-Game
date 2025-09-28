import pygame, sys, os, random, asyncio

import math #for da star

pygame.init()
pygame.mixer.init() 

async def main():
    #music
    jump_sound = None
    win_sound = None
    hit_sound = None

    # safely load sounds
    if os.path.exists("sounds/jump.wav"):
        jump_sound = pygame.mixer.Sound("sounds/jump.wav")
    if os.path.exists("sounds/win.wav"):
        win_sound = pygame.mixer.Sound("sounds/win.wav")
    if os.path.exists("sounds/hit.wav"):
        hit_sound = pygame.mixer.Sound("sounds/hit.wav")

    # screen
    WIDTH, HEIGHT = 1200, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Loss Of Limbs")
    clock = pygame.time.Clock()
    FPS = 60

    # colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 100, 200)  # darker blue
    RED = (255, 150, 180)  # lighter pink
    FAKE_COLOR = (50, 50, 50)

    # fonts for screen
    title_font = pygame.font.SysFont(None, 90)
    button_font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    # how player jumps, size etc 
    player_size = 40
    start_x, start_y = 50, HEIGHT - 50 - player_size
    player_x, player_y = start_x, start_y
    player_vel_y = 0
    gravity = 0.95
    jump_strength = -18
    speed = 6
    on_ground = True
    jump_buffer = 0

    leg_segments = 8
    jumps_left = leg_segments * 2

    # platform definition (we'll make multiple levels)
    level_1 = [
        pygame.Rect(0, HEIGHT-40, start_x + player_size*2, 20),
        pygame.Rect(200, 560, 60, 20),
        pygame.Rect(320, 520, 60, 20),
        pygame.Rect(440, 560, 60, 20),
        pygame.Rect(560, 500, 60, 20),
        pygame.Rect(680, 460, 60, 20),
        pygame.Rect(800, 500, 60, 20),
        pygame.Rect(920, 440, 60, 20),
        pygame.Rect(1040, 480, 60, 20),
        pygame.Rect(1160, 420, 60, 20),
        pygame.Rect(1300, 460, 60, 20),
        pygame.Rect(1400, 400, 60, 20),
        pygame.Rect(1560, 420, 60, 20),
        pygame.Rect(1680, 460, 60, 20),
        pygame.Rect(1800, 300, 60, 20),
        pygame.Rect(1960, 340, 60, 20),
        pygame.Rect(2130, 390, 60, 20),
        pygame.Rect(2220, 440, 60, 20),
        pygame.Rect(2300, 480, 60, 20),
    ]

    # level 2 platforms
    level_2 = [
        pygame.Rect(0, HEIGHT-40, start_x + player_size*2, 20),
        pygame.Rect(200, 560, 60, 20),
        ("fake", pygame.Rect(320, 520, 60, 20)),
        pygame.Rect(440, 560, 60, 20),
        pygame.Rect(560, 500, 60, 20),
        ("fake", pygame.Rect(680, 460, 60, 20)),
        pygame.Rect(800, 500, 60, 20),
        pygame.Rect(920, 440, 60, 20),
        pygame.Rect(1040, 480, 60, 20),
        ("fake", pygame.Rect(1160, 420, 60, 20)),
        pygame.Rect(1280, 460, 60, 20),
        pygame.Rect(1400, 400, 60, 20),
        ("fake", pygame.Rect(1560, 420, 60, 20)),
        pygame.Rect(1680, 460, 60, 20),
        pygame.Rect(1800, 300, 60, 20),
        ("fake", pygame.Rect(1960, 340, 60, 20)),
        pygame.Rect(2130, 390, 60, 20),
        pygame.Rect(2260, 440, 60, 20),
        ("fake", pygame.Rect(2400, 480, 60, 20)),
    ]

    level_3 = [
        pygame.Rect(0, HEIGHT-40, start_x + player_size*2, 20),
        pygame.Rect(200, 560, 60, 20),
        ("fake", pygame.Rect(320, 520, 60, 20)),
        pygame.Rect(440, 560, 60, 20),
        pygame.Rect(560, 500, 60, 20),
        ("fake", pygame.Rect(680, 460, 60, 20)),
        ("fake",pygame.Rect(800, 500, 60, 20)),
        pygame.Rect(920, 440, 60, 20),
        pygame.Rect(1040, 480, 60, 20),
        ("fake", pygame.Rect(1160, 420, 60, 20)),
        pygame.Rect(1280, 460, 60, 20),
        ("fake", pygame.Rect(1400, 400, 60, 20)),
        ("fake", pygame.Rect(1560, 420, 60, 20)),
        pygame.Rect(1680, 460, 60, 20),
        pygame.Rect(1800, 300, 60, 20),
        ("fake", pygame.Rect(1960, 340, 60, 20)),
        pygame.Rect(2130, 390, 60, 20),
        ("fake",pygame.Rect(2260, 440, 60, 20)),
        ("fake", pygame.Rect(2400, 480, 60, 20)),
        pygame.Rect(2600, 520, 60, 20),
    ]

    levels = [level_1, level_2, level_3]
    current_level_index = 0
    platforms = levels[current_level_index]

    collapsed = set()  # tracks disappeared fake platforms

    # la camera
    def last_platform_rect(plats):
        last = plats[-1]
        if isinstance(last, tuple):
            return last[1]
        return last

    last_platform = last_platform_rect(platforms)
    goal = pygame.Rect(last_platform.x + 50, last_platform.y - 80, 120, 100)  # bigger goal at the end
    camera_x = 0

    # gpt says you need it
    player_image = None
    if os.path.exists("player.png"):
        player_image = pygame.image.load("player.png").convert_alpha()
        player_image = pygame.transform.scale(player_image, (player_size, player_size))

    # the end
    goal_image = None
    if os.path.exists("victory.jpeg"):
        goal_image = pygame.image.load("victory.jpeg").convert()
        goal_image = pygame.transform.scale(goal_image, (goal.width, goal.height))

    # game states
    START, PLAYING, WIN, LOSE = "start","playing","win","lose"
    game_state = START

    # random functions that are needed
    def draw_text_center(text, font, color, x, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)
        return rect

    # button for title screen
    def draw_button(text, font, x, y):
        surf = font.render(text, True, BLACK)
        rect = surf.get_rect(center=(x, y))
        btn = pygame.Rect(rect.left-12, rect.top-8, rect.width+24, rect.height+16)
        pygame.draw.rect(screen, WHITE, btn, border_radius=6)
        screen.blit(surf, rect)
        return btn

    # how the player works, keeping camera on them, leggssssss
    def draw_player():
        rect = pygame.Rect(player_x-camera_x, player_y, player_size, player_size)
        if player_image:
            screen.blit(player_image, rect)
        else:
            pygame.draw.rect(screen, (0, 100, 255), rect)

        # draw legs
        for i in range(max(2, leg_segments)):  # always draw at least 2 leg segments
            seg_y = player_y + player_size + i*4
            pygame.draw.rect(screen, (255, 150, 200), (rect.left+8, seg_y, 10, 3))
            pygame.draw.rect(screen, (255, 150, 200), (rect.right-18, seg_y, 10, 3))

    # finish line
    def draw_goal():
        gx = goal.x - camera_x
        gy = goal.y
        if goal_image:
            screen.blit(goal_image, (gx, gy))
        else:
            pygame.draw.rect(screen, BLUE, (gx, gy, goal.width, goal.height))

    def load_level(index):
        global platforms, last_platform, goal
        platforms = levels[index]
        last_platform = last_platform_rect(platforms)
        goal = pygame.Rect(last_platform.x + 50, last_platform.y - 80, 120, 100)

    def reset_level():
        global player_x, player_y, player_vel_y, jumps_left, leg_segments, on_ground, camera_x, collapsed
        player_x, player_y = start_x, start_y
        player_vel_y = 0
        leg_segments = 8
        jumps_left = leg_segments * 2
        on_ground = True
        camera_x = 0
        collapsed = set()

    # one main loop
    running = True
    play_btn = home_btn = again_btn = next_btn = None

    while running:
        dt = clock.tick(FPS)
        screen.fill(BLACK)

        # game stats/screens
        if game_state==START:
            draw_text_center("The Loss Of Limbs", title_font, WHITE, WIDTH//2, HEIGHT//3)
            play_btn = draw_button("Play Game", button_font, WIDTH//2, HEIGHT//2)
            draw_text_center("<--    --> to move   •   SPACE to jump", small_font, WHITE, WIDTH//2, HEIGHT//2+60)
        
        if levels == level_3:
            if game_state==WIN: 
                print("The END")

        elif game_state==PLAYING:
            camera_x = max(0, player_x - WIDTH//3)
            # draw platforms
            for p in platforms:
                if isinstance(p, tuple): kind, rect = p
                else: kind, rect = "solid", p
                if id(rect) in collapsed: continue
                color = WHITE if kind=="solid" else FAKE_COLOR
                pygame.draw.rect(screen, color, (rect.x-camera_x, rect.y, rect.width, rect.height))
            draw_goal()
            draw_player()
            draw_text_center(f"Jumps left: {jumps_left}", small_font, WHITE, 120, 20) #jumps left
        
            # show level number
            draw_text_center(f"Level {current_level_index+1}", small_font, WHITE, WIDTH-100, 20)

        elif game_state==WIN:
            draw_text_center("You Won", title_font, WHITE, WIDTH//2, HEIGHT//3)
            draw_text_center("you kept your limbs", small_font, WHITE, WIDTH//2, HEIGHT//2)
            home_btn = draw_button("Home", button_font, WIDTH//2-140, HEIGHT//2+100)
            next_btn = draw_button("Next Level", button_font, WIDTH//2, HEIGHT//2+100)
            again_btn = draw_button("Try Again", button_font, WIDTH//2+140, HEIGHT//2+100)

        elif game_state==LOSE:
            draw_text_center("Defeat", title_font, WHITE, WIDTH//2, HEIGHT//3)
            draw_text_center("you lost your legs", small_font, WHITE, WIDTH//2, HEIGHT//2)
            home_btn = draw_button("Home", button_font, WIDTH//2-100, HEIGHT//2+100)
            again_btn = draw_button("Try Again", button_font, WIDTH//2+100, HEIGHT//2+100)

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                mx, my = event.pos
                # from START -> PLAYING
                if game_state==START and play_btn and play_btn.collidepoint(mx, my):
                    game_state = PLAYING
                    current_level_index = 0
                    load_level(current_level_index)
                    reset_level()

                # WIN/LOSE buttons
                elif game_state==WIN:
                    if home_btn and home_btn.collidepoint(mx, my):
                        game_state = START
                    elif next_btn and next_btn.collidepoint(mx, my):
                        # advance level
                        current_level_index = (current_level_index + 1) % len(levels)
                        load_level(current_level_index)
                        reset_level()
                        game_state = PLAYING
                    elif again_btn and again_btn.collidepoint(mx, my):
                        load_level(current_level_index)
                        reset_level()
                        game_state = PLAYING

                elif game_state==LOSE:
                    if home_btn and home_btn.collidepoint(mx, my):
                        game_state = START
                    elif again_btn and again_btn.collidepoint(mx, my):
                        load_level(current_level_index)
                        reset_level()
                        game_state = PLAYING

            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    jump_buffer = 6
                if event.key==pygame.K_ESCAPE:
                    running = False

        # gameplay logic
        if game_state==PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player_x -= speed
            if keys[pygame.K_RIGHT]: player_x += speed

            player_vel_y += gravity
            player_y += player_vel_y
            on_ground = False
            rect = pygame.Rect(player_x, player_y, player_size, player_size)

            # platforms collision + fake collapse
            for p in platforms:
                if isinstance(p, tuple): kind, plat = p
                else: kind, plat = "solid", p
                if id(plat) in collapsed: continue
                
                if rect.colliderect(plat) and player_vel_y >= 0 and (player_y + player_size) - plat.top < 25:
                    # place player on top
                    player_y = plat.top - player_size
                    player_vel_y = 0
                    on_ground = True
                    if kind == "fake":
                        if hit_sound:  # play hit only if file exists
                            hit_sound.play()
                        collapsed.add(id(plat))

            # jumping pyshics and leg loss
            if jump_buffer > 0:
            
                if on_ground and jumps_left > 0:
                    player_vel_y = jump_strength
                    jumps_left -= 1
                    
                    if jumps_left % 2 == 0:
                        leg_segments = max(2, leg_segments - 1)
                    jump_buffer = 0
                    on_ground = False
                    if jump_sound:  # safe play jump
                        jump_sound.play()
                else:
                
                    jump_buffer -= 1

            # falling off world
            if player_y > HEIGHT + 300:
                # penalty for falling
                jumps_left -= 2  
                leg_segments = max(0, leg_segments - 1)
                if hit_sound:
                    hit_sound.play()
                if jumps_left <= 0 or leg_segments <= 0:
                    leg_segments = 0
                    game_state = LOSE
                else:
                    player_x, player_y = start_x, start_y
                    player_vel_y = 0

            # win condition
            if rect.colliderect(goal) and leg_segments > 0:
                if win_sound:
                    win_sound.play()
                game_state = WIN

            # lose if no legs
            if leg_segments <= 0:
                game_state = LOSE

        pygame.display.flip()
        await asyncio.sleep(0)
asyncio.run(main())
