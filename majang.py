import pygame as pg
import random as r

pg.init()
screen = pg.display.set_mode((1080, 640))
pg.display.set_caption('役満麻雀')
icon = pg.image.load('./img/majang_icon.png')
pg.display.set_icon(icon)
clock = pg.time.Clock()
small_font = pg.font.Font('./fonts/DotGothic16-Regular.ttf',36)
middle_font = pg.font.Font('./fonts/DotGothic16-Regular.ttf',72)
large_font = pg.font.Font('./fonts/DotGothic16-Regular.ttf',144)

class TileSheet:
    def __init__(self, image_path):
        self.sheet = pg.image.load(image_path).convert_alpha()
        self.tile_width = 64
        self.tile_height = 96
    
    def get_tile(self, tile_code):
        
        x = tile_code % 9 * self.tile_width
        y = tile_code // 9 * self.tile_height
        
        tile_surface = pg.Surface((self.tile_width, self.tile_height), pg.SRCALPHA)
        tile_surface.blit(self.sheet, (0, 0), (x, y, self.tile_width, self.tile_height))
        
        return tile_surface

tile_sheet = TileSheet('./img/majang_tiles.png')

class Tile:
    def __init__(self, tile_code, x, y, tile_sheet):
        self.tile_code = tile_code
        self.number = tile_code % 9 + 1
        self.suit = tile_code // 9 + 1
        self.tile_tuple = (self.number,self.suit)
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y

        self.hovered = False
        self.image = tile_sheet.get_tile(tile_code)
    
    def draw(self, screen):
        y_hover = 0
        
        if self.hovered:
            y_hover = -15
        else:
            y_hover = 0
        screen.blit(self.image, (self.x, self.y + y_hover))

    def clicked(self, mouse_pos):
        self.tile_rect = pg.Rect(self.x, self.y, 64, 96)
        if self.tile_rect.collidepoint(mouse_pos):
            print("clicked")
            return True
        else:
            return False
    
    def hover(self, mouse_pos):
        self.tile_rect = pg.Rect(self.x, self.y, 64, 96)
        if self.tile_rect.collidepoint(mouse_pos):
            self.hovered = True
        else:
            self.hovered = False

    def move(self):
        diff_x = self.target_x - self.x
        diff_y = self.target_y - self.y
        
        # 少しずつ移動（30%ずつ近づく）
        self.x += diff_x * 0.3
        self.y += diff_y * 0.3
        
        # ほぼ到達したら、きっちり目標位置にする
        if abs(diff_x) < 0.5:
            self.x = self.target_x
        if abs(diff_y) < 0.5:
            self.y = self.target_y

class Hand:
    def __init__(self, tile_sheet):
        self.tiles = []
        self.tile_sheet = tile_sheet
        self.tile_width = 68
        self.start_x = 30
        self.y = 500
        self.margin = 10
        self.tsumo_tile = None
    
    def shuffle(self):
        self.tiles = []
        tile_code_list = []
        for i in range(13):
            tile_code = r.randint(0, 33)
            tile_code_list.append(tile_code)

        tile_code_list.sort()

        for i, selected_code in enumerate(tile_code_list):
            x = self.start_x + i * self.tile_width + self.margin
            tile = Tile(selected_code, x, self.y, self.tile_sheet)
            self.tiles.append(tile)

    def tsumo(self):
        tile_code = r.randint(0, 33)
        self.tsumo_tile = Tile(tile_code, self.start_x + 930, self.y, self.tile_sheet)

    def swap(self,swaped_tile):
        self.tsumo_tile = swaped_tile
        self.tsumo_tile.target_y = self.y
        self.tsumo_tile.target_x = self.start_x + 930

    def draw(self, screen):
        for tile in self.tiles:
            tile.draw(screen)
        if self.tsumo_tile:
            self.tsumo_tile.draw(screen)

    def clicked(self, mouse_pos):
        # 手牌をチェック
        for i, tile in enumerate(self.tiles):
            if tile.clicked(mouse_pos):
                discarded_tile = self.tiles.pop(i)  # ★捨てた牌を保存
                self.tiles.append(self.tsumo_tile)
                self.rearrange()
                self.tsumo_tile = None  # ★忘れずにクリア
                print(f"手牌の{i+1}番目を捨てた")
                return discarded_tile  # ★捨てた牌を返す
        
        # ツモ牌をチェック
        if self.tsumo_tile and self.tsumo_tile.clicked(mouse_pos):
            discarded_tile = self.tsumo_tile  # ★捨てた牌を保存
            self.tsumo_tile = None
            print("ツモ牌を捨てた")
            return discarded_tile  # ★捨てた牌を返す
        
        return None  # ★何も捨てていない

    def agari(self,tsumo_tile,agari):
        yaku_list = []
        tile_list = []
        kotsu_list = []
        syuntsu_list = []
        jantou_list = []
        tuple_list = []

        agari_hand = self.tiles.copy()

        for tile in agari_hand:
            tuple_list.append(tile.tile_tuple)
        tuple_list.append(tsumo_tile)
        print(tuple_list)

        all_number = [tile[0] for tile in tuple_list]
        tile_list = list(set(tuple_list))
        number_list = list(set(all_number))
        suit_list = list(set([tile[1] for tile in tuple_list]))
        print(number_list)

        if all(tile in tuple_list for tile in [(1,1),(9,1),(1,2),(9,2),(1,3),(9,3),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4)]):
            if len(tile_list) == 13:
                yaku_list.append(("国士無双",4))
                print(tile_list)
                print("国士無双確定！")
                print(f"役：{yaku_list}")
                return [magnification[1] for magnification in yaku_list]
            else:
                return 0
            
        for i,jantou in enumerate(tile_list):
            remain_tile = tuple_list.copy()
            tile_count = remain_tile.count(jantou)
            kotsu = []
            syuntsu = []
            
            print(f"--- 試行 {i}: 雀頭候補 {jantou} ---")
            
            if tile_count >= 2:
                
                for j in range(2):
                    remain_tile.remove(jantou)
                print(f"雀頭除去後: {remain_tile}")
                
                is_removed = True
                while is_removed:
                    is_removed = False
                    for tile in list(set(remain_tile)):
                        quantity = remain_tile.count(tile)
                        if quantity >= 3:
                            kotsu.append(tile)
                            for k in range(3):
                                remain_tile.remove(tile)
                            print(f"刻子 {tile} 除去後: {remain_tile}")
                            is_removed = True
                            break
                
                is_removed = True
                while is_removed:
                    is_removed = False
                    for tile in sorted(set(remain_tile)):
                        number, suit = tile
                        if (number+1, suit) in remain_tile and (number+2, suit) in remain_tile:
                            syuntsu.append(((number, number+1, number+2), suit))
                            for k in range(3):
                                remain_tile.remove((number+k, suit))
                            print(f"順子 {number}-{number+1}-{number+2} ({suit}) 除去後: {remain_tile}")
                            is_removed = True
                            break
                
                print(f"最終残り: {remain_tile}")
                print(f"刻子: {kotsu}, 順子: {syuntsu}")
                
                if len(remain_tile) == 0:
                    print("面子確定")
                    kotsu_list.append(kotsu)
                    syuntsu_list.append(syuntsu)
                    jantou_list.append(jantou)
                print()

        sev_toitsu = True
        for i,tile in enumerate(tile_list):
            if tuple_list.count(tile) % 2 == 0:
                continue
            else:
                sev_toitsu = False
                break
        if sev_toitsu == True:
            kotsu_list.append([])
            syuntsu_list.append([])
            jantou_list.append(())

        if agari:
            wait_tile = self.check_tenpai()

        for i, kotsu in enumerate(kotsu_list):
            for j, syuntsu in enumerate(syuntsu_list):
                if len(kotsu) == 4:
                    yaku_list.append(("四暗刻",1))
                if all(tile in [(2,2),(3,2),(4,2),(6,2),(8,2),(6,4)] for tile in tuple_list):
                    yaku_list.append(("緑一色",3))
                if all(tile in kotsu for tile in [(5,4),(6,4),(7,4)]):
                    yaku_list.append(("大三元",2))
                if suit_list == [4]:
                    yaku_list.append(("字一色",1))
                if jantou in [(1,4),(2,4),(3,4),(4,4)]:
                    wind_list = [(1,4),(2,4),(3,4),(4,4)]
                    wind_list.remove(jantou)
                    if all(wind in kotsu for wind in wind_list):
                        yaku_list.append(("小四喜",2))
                if all(wind in kotsu for wind in [(1,4),(2,4),(3,4),(4,4)]):
                    yaku_list.append(("大四喜",3))
                if all(number in [1,9] for number in number_list):
                    yaku_list.append(("清老頭",2))
                if len(suit_list) == 1:
                    if all_number.count(1) >= 3 and all_number.count(9) >= 3:
                        if len(number_list) == 9:
                            yaku_list.append(("九蓮宝燈",4))
                if len(tile_list) == 1:
                    yaku_list.append(("万象統一",4))

        yaku_list = list(set(yaku_list))
        for i in range(len(yaku_list)):
            print(yaku_list[i])
        print(f"役：{yaku_list}")
        print(jantou_list)
        if yaku_list == []:
            return 0
        else:
            return yaku_list
    
    def check_tenpai(self):
        wait_tile = []
        tuple_list = []

        agari_hand = self.tiles.copy()

        for tile in agari_hand:
            tuple_list.append(tile.tile_tuple)
        print(tuple_list)

        tuple_list = list(set(tuple_list))
        test_list = tuple_list.copy()

        for number,suit in tuple_list:
            if suit != 4:
                if number > 1:
                    test_list.append((number-1,suit))
                if number < 9:
                    test_list.append((number+1,suit))
                
        wait_list = list(set(test_list))
            
        for test_tsumo in wait_list:
            if self.agari(test_tsumo,False):
                wait_tile.append(test_tsumo)
        
        if wait_list == []:
            print("聴牌ではありません")
            print(f'testing:{test_list}')
            print(wait_list)
        else:
            print(test_list)
            print(f"聴牌！待ち牌: {wait_tile}")
            print(wait_list)
        
        return wait_tile

    def rearrange(self):
        """牌の位置を再配置"""
        self.tiles.sort(key=lambda t: t.tile_code)
        for i, tile in enumerate(self.tiles):
            tile.target_x = self.start_x + i * self.tile_width + self.margin

    def move(self):
        for tile in self.tiles:
            tile.move()

    def hover(self, mouse_pos):
        for tile in self.tiles:
            tile.hover(mouse_pos)
        if self.tsumo_tile:  # ★Noneチェック
            self.tsumo_tile.hover(mouse_pos)

class Trash:
    def __init__(self, tile_sheet):
        self.tiles = []
        self.tile_sheet = tile_sheet
        self.tile_width = 68
        self.start_x = 40  # 捨て牌エリアの開始位置
        self.y = 350
        self.tiles_per_row = 12  # 1行に6枚
    
    def add_tile(self, tile):
        """牌を捨て牌に追加（Tileオブジェクトをそのまま受け取る）"""
        # 位置を更新
        tile.target_y = self.y
        tile.hovered = False
        
        self.tiles.append(tile)
        if len(self.tiles) == 12:
            del self.tiles[0]
        self.rearrange()

    def draw(self, screen):
        """捨て牌を描画"""
        for tile in self.tiles:
            tile.draw(screen)

    def clicked(self, mouse_pos):
        # 手牌をチェック
        for i, tile in enumerate(self.tiles):
            if tile.clicked(mouse_pos):
                discarded_tile = self.tiles.pop(i)  # ★捨てた牌を保存
                print("ツモ牌を捨てた")
                return discarded_tile   # ★捨てた牌を返す
            
        return None

    def rearrange(self):
        for i, tile in enumerate(self.tiles):
            tile.target_x = self.start_x + i * self.tile_width

    def hover(self, mouse_pos):
        for tile in self.tiles:
            tile.hover(mouse_pos)

    def move(self):
        for tile in self.tiles:
            tile.move()

class Button:
    def __init__(self, x, y, button_x, button_y, button_sheet):
        self.x = x
        self.y = y
        self.button_width = 192
        self.button_height = 96
        
        sheet = pg.image.load(button_sheet).convert_alpha()
        btn_x = (button_x-1) * self.button_width
        btn_y = (button_y-1) * self.button_height
        
        self.image = pg.Surface((self.button_width, self.button_height), pg.SRCALPHA)
        self.image.blit(sheet, (0,0), (btn_x, btn_y, self.button_width, self.button_height))
        self.image_original = self.image.copy()

        self.rect = pg.Rect(x, y, self.button_width, self.button_height)
        self.hovered = False
    
    def draw(self, screen):
        if self.hovered:
            self.image = self.image_original.copy()
            self.image.fill((100, 100, 100), special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.image = self.image_original.copy()
        
        screen.blit(self.image, (self.x, self.y))
    
    def hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class timer():
    def __init__(self):
        self.x = 850
        self.y = 30
        self.flame = 0
        self.min = 0
        self.sec = 0
        
    def update(self):
        if self.flame == 60:
            self.flame = 0
            if self.sec == 0:
                self.min -= 1
                self.sec = 59
            else:
                self.sec -= 1
        self.flame += 1

        if self.min == 0 and self.sec == 0:
            return True
        return False

    def time_extend(self,magnification):
        time_plus = 5*magnification
        self.sec += time_plus
        while self.sec >= 60:
            self.min += 1
            self.sec -= 60
        screen.blit(middle_font.render(f'+{time_plus}', True, (255, 200, 0)), (self.x, self.y-35))

    def draw(self,screen):
        if self.sec >= 10:
            screen.blit(middle_font.render(f'{self.min}:{self.sec}', True, (255, 200, 0)), (self.x, self.y))
        else:
            screen.blit(middle_font.render(f'{self.min}:0{self.sec}', True, (255, 200, 0)), (self.x, self.y))

class score_counter():
    def __init__(self):
        self.x = 1000
        self.y = 100
        self.score = 0

    def scored(self,score):
        self.score = score

    def draw(self,screen):
        score_text = middle_font.render((f'{self.score}点'), True, (255, 255, 255))
        text_width = score_text.get_width()
        position_x = self.x - text_width
        screen.blit(score_text,(position_x,self.y))

class bonus_container():
    def __init__(self,bonus):
        self.x = 50
        self.y = 200
        self.bonus = bonus

    def update(self,bonus):
        self.bonus = bonus

    def draw(self,screen):
        screen.blit(small_font.render(('追加得点'), True, (255, 255, 255)),(self.x,self.y))
        screen.blit(middle_font.render((self.bonus), True, (255, 200, 0)),(self.x,self.y+35))

class yaku_container():
    def __init__(self,yaku_name_list,magnification,score_plus,complete):
        self.yaku_name_list = yaku_name_list
        self.magnification = magnification
        self.score_plus = score_plus
        self.x = 380
        self.y = 40
        self.color = (255,255,255)
        self.flame = 0
        self.interval = 20
        self.line = 0
        self.draw_yaku = []
        self.complete = complete

    def update(self):
        if not self.complete:
            if self.flame == self.interval * (len(self.yaku_name_list)+4):
                self.complete = True
                return

            if self.flame >= self.interval * len(self.yaku_name_list):
                self.flame += 1
                return

            if self.flame == 0 + self.line * self.interval:
                self.draw_yaku.append(self.yaku_name_list[self.line])
                self.line += 1
            self.flame += 1

    def draw(self,screen):
        if not self.complete:
            for i,yaku_name in enumerate(self.draw_yaku):
                yaku_text = small_font.render(yaku_name, True, self.color)
                screen.blit(yaku_text, (self.x, self.y + i*35))
            if self.line >= len(self.yaku_name_list):
                if self.magnification == 1:
                    screen.blit(small_font.render(f'役満 {self.score_plus}点', True, self.color), (self.x, self.y + (self.line+1)*35))
                elif self.magnification > 1:
                    screen.blit(small_font.render(f'{self.magnification}倍役満 {self.score_plus}点', True, self.color), (self.x, self.y + (self.line+1)*35))
                else:
                    screen.blit(small_font.render(f'{self.score_plus}点', True, self.color), (self.x, self.y + (self.line+1)*35))

class signal():
    def __init__(self,text):
        self.text = large_font.render(text,True,(255,200,0))
        self.x = 400
        self.y = 100

    def sign(self,screen):
        screen.blit(self.text,(self.x,self.y))

class wait():
    def __init__(self,time):
        self.complete = False
        self.flame = 0
        self.wait_time = time / 1000 * 60

    def updete(self):
        if self.flame == self.wait_time:
            return True
        else:
            self.flame += 1
            return False

class small_text():
    def __init__(self,text,y,color):
        self.y = y
        self.text = small_font.render(text, True, color)
        self.x = ((screen.get_width() - self.text.get_width()) // 2 )

    def draw(self,screen):
        screen.blit(self.text, (self.x, self.y))

class middle_text():
    def __init__(self,text,y,color):
        self.y = y
        self.text = middle_font.render(text, True, color)
        self.x = ((screen.get_width() - self.text.get_width()) // 2 )

    def draw(self,screen):
        screen.blit(self.text, (self.x, self.y))

class large_text():
    def __init__(self,text,y,color):
        self.y = y
        self.text = large_font.render(text, True, color)
        self.x = ((screen.get_width() - self.text.get_width()) // 2 )

    def draw(self,screen):
        screen.blit(self.text, (self.x, self.y))

def result(screen,score):
    end_flag = False
    color_white = (255,255,255)
    color_yellow = (255,200,0)
    result_text = small_text('結果発表',200,color_white)
    score_text = middle_text(f'{score}点', 235, color_yellow)
    restart_button = Button(240, 400, 1, 2, './img/buttons.png')
    end_button = Button(660, 400, 2, 1, './img/buttons.png')
    while not end_flag:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 000
            elif event.type == pg.MOUSEBUTTONDOWN:
                click_pos = event.pos
                if restart_button.clicked(click_pos):
                    screen.fill((0, 100, 0))
                    end_stile = majang()
                    if end_stile == 000:
                        end_flag = True
                elif end_button.clicked(click_pos):
                    main()
                    return 000
        mouse_pos = pg.mouse.get_pos()
        restart_button.hover(mouse_pos)
        end_button.hover(mouse_pos)
        screen.fill((0, 100, 0))
        result_text.draw(screen)
        score_text.draw(screen)
        restart_button.draw(screen)
        end_button.draw(screen)
        pg.display.update()
        clock.tick(60)
    return end_stile

def majang():
    start_signal = signal('開局')
    my_hand = Hand(tile_sheet)
    my_trash = Trash(tile_sheet)
    my_hand.shuffle()
    my_hand.tsumo()
    tsumo_button = Button(830, 350, 2, 2, './img/buttons.png')
    end_flag = False
    score = 0
    bonus_list = ["四暗刻","字一色","緑一色","大三元","小四喜","大四喜","清老頭","九蓮宝燈","国士無双"]
    bonus = r.choice(bonus_list)
    time_text = timer()
    score_text = score_counter()
    bonus_text = bonus_container(bonus)
    yaku_text = yaku_container([],0,0,True)
    screen.fill((0, 100, 0))
    my_hand.draw(screen)
    tsumo_button.draw(screen)
    start_signal.sign(screen)
    pg.display.update()
    sign_wait = wait(1500)

    while not sign_wait.updete():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 000
        clock.tick(60)

    while not end_flag:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 000
            elif event.type == pg.MOUSEBUTTONDOWN:
                click_pos = event.pos

                discarded_tile = my_hand.clicked(click_pos)
                if discarded_tile:
                    my_trash.add_tile(discarded_tile)
                    my_hand.tsumo()

                else:
                    discarded_tile = my_trash.clicked(click_pos)
                    if discarded_tile:
                        tsumo_tile = my_hand.tsumo_tile
                        my_trash.add_tile(tsumo_tile)
                        my_hand.swap(discarded_tile)

                    elif tsumo_button.clicked(click_pos):
                        yaku_list = my_hand.agari(my_hand.tsumo_tile.tile_tuple,True)
                        if yaku_list != 0:
                            yaku_name_list = [yaku_tuple[0] for yaku_tuple in yaku_list]
                            magnification_list = [yaku_tuple[1] for yaku_tuple in yaku_list]                                
                            magnification = sum(magnification_list)
                            if bonus in yaku_name_list:
                                magnification += 1
                                yaku_name_list.append("追加得点")
                            score_plus = 32000*magnification
                            time_text.time_extend(magnification)
                            print(magnification)
                            print(score_plus)
                            yaku_text = yaku_container(yaku_name_list,magnification,score_plus,False)
                            bonus = r.choice(bonus_list)
                            bonus_text.update(bonus)
                            my_hand.shuffle()
                            my_hand.tsumo()
                        else:
                            magnification = 0
                            yaku_name_list = ['誤ツモ...']
                            score_plus = -32000
                            yaku_text = yaku_container(yaku_name_list,magnification,score_plus,False)
                            print(score)
                        score += score_plus
                        score_text.scored(score)
                        
                        # 描画
        mouse_pos = pg.mouse.get_pos()
        my_hand.hover(mouse_pos)
        my_trash.hover(mouse_pos)
        tsumo_button.hover(mouse_pos)
        screen.fill((0, 100, 0))
        my_hand.move()
        my_hand.tsumo_tile.move()
        my_trash.move()
        if time_text.update():
            end_flag = True
        yaku_text.update()
        my_hand.draw(screen)
        my_trash.draw(screen)
        tsumo_button.draw(screen)
        time_text.draw(screen)
        score_text.draw(screen)
        bonus_text.draw(screen)
        yaku_text.draw(screen)
        pg.display.update()
        clock.tick(60)

    end_signal = signal('終局')
    end_signal.sign(screen)
    pg.display.update()
    sign_wait = wait(1500)
    while not sign_wait.updete():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 000
        clock.tick(60)
    end_stile = result(screen,score)
    return end_stile

def main():
    game_end_flag = False
    start_button = Button(240, 400, 1, 1, './img/buttons.png')
    end_button = Button(660, 400, 2, 1, './img/buttons.png')
    title = large_text('役満麻雀',150,(255,255,255))
    while not game_end_flag:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_end_flag = True
                end_stile = 000
            elif event.type == pg.MOUSEBUTTONDOWN:
                click_pos = event.pos
                if start_button.clicked(click_pos):
                    end_stile = majang()
                    if end_stile == 000:
                        game_end_flag = True
                elif end_button.clicked(click_pos):
                    game_end_flag = True
                    end_stile = 100

        mouse_pos = pg.mouse.get_pos()
        start_button.hover(mouse_pos)
        end_button.hover(mouse_pos)
        screen.fill((0, 100, 0))
        title.draw(screen)
        start_button.draw(screen)
        end_button.draw(screen)
        pg.display.update()
        clock.tick(60)

    return end_stile

if __name__ == "__main__":
    code = main()

pg.quit()