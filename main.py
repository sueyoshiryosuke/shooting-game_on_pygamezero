import os
import random
import pgzrun

# ウィンドウの位置を設定（スクリーン中央に配置）
os.environ['SDL_VIDEO_CENTERED'] = '1'

# 画面サイズ
WIDTH = 600
HEIGHT = 900

# プレイヤーの初期設定
player = Actor('player', (200, 800))  # プレイヤー画像を 'player.png' に置き換え

# 敵のリスト
enemies = [Actor('enemy', (random.randint(0, WIDTH), 100))]  # 初期敵は1体

# 弾のリスト
bullets = []

# 星のリストを作成（星50個。幅と高さをランダムに設定）
stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "width": random.randint(1, 2), "height": random.randint(1, 2)} for _ in range(50)]

# 星が下に動く速度を管理する変数。数字が増えると星の動きが速くなる。
star_speed = 2  # 初期速度

# スコアを初期化
score = 0

# ゲームオーバーフラグ
game_over = False

# 敵の左右移動用フラグ
enemy_directions = [random.choice([-1, 1])]

# 追加された敵の数を追跡
added_enemies = 0

# ゲームの更新処理
def update():
    global game_over, score, added_enemies, star_speed

    if game_over:
        return  # ゲームオーバー時は何もしない

    # 星の移動
    for star in stars:
        star["y"] += star_speed  # 星の移動速度を反映
        if star["y"] > HEIGHT:  # 画面下に到達したら再び上部に戻る
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)  # ランダムなX座標

    # プレイヤーの移動
    if keyboard.left and player.x > 0:
        player.x -= 5
    if keyboard.right and player.x < WIDTH:
        player.x += 5

    # 弾の移動
    for bullet in bullets:
        bullet['y'] -= 10
        if bullet['y'] < 0:
            bullets.remove(bullet)

    # 敵の移動
    for i, enemy in enumerate(enemies):
        enemy.y += 2
        if enemy.y > HEIGHT:  # 下に到達したら上部に戻る
            enemy.y = 0
            enemy.x = random.randint(0, WIDTH)

        # 左右移動
        enemy.x += enemy_directions[i] * 3
        if enemy.x <= 0 or enemy.x >= WIDTH:  # 画面端で方向を反転
            enemy_directions[i] *= -1

        # ランダムに左右を反転
        if random.random() < 0.02:  # 一定の確率で反転
            enemy_directions[i] *= -1

        # プレイヤーと敵の衝突判定
        if player.colliderect(enemy):
            sounds.crash.play()  # 衝突時の効果音を再生
            game_over = True

    # 弾と敵の衝突判定
    for bullet in bullets:
        for i, enemy in enumerate(enemies):
            if enemy.colliderect(Rect((bullet['x'], bullet['y']), (5, 10))):
                bullets.remove(bullet)
                enemy.y = 0  # 敵を上部に戻す
                enemy.x = random.randint(0, WIDTH)
                enemy_directions[i] = random.choice([-1, 1])  # ランダムな移動方向に変更
                score += 1  # スコア加算

                # 敵を倒したときの音
                sounds.hit.play()
                break

    # 敵を増やす（3体倒すごとに1体追加。敵の数の上限あり）
    # スコアから計算される段階が上がったら敵を追加
    if score // 3 > added_enemies and added_enemies < 15 :
        new_enemy = Actor('enemy', (random.randint(0, WIDTH), 0))  # 新しい敵を追加
        enemies.append(new_enemy)
        enemy_directions.append(random.choice([-1, 1]))  # 新しい敵の移動方向を追加
        added_enemies += 1  # 追加された敵の数を更新
        
        # 敵が増えるたびに星の速度を上げる（速度上限あり）
        if star_speed < added_enemies:
            star_speed += 1

# 弾を発射する処理を関数に分離
def fire_bullet():
    if not game_over:  # ゲームオーバー中は発射しない
        bullets.append({'x': player.x, 'y': player.y - 20})  # 弾を追加
        sounds.shoot.play()  # 弾発射音を再生

# ゲームの描画処理
def draw():
    screen.clear()

    # 星を描画
    # 3色（白、赤、青）で、ランダムなサイズのピクセルで描画
    for star in stars:
        color = random.choice([(255, 255, 255), (255, 200, 200), (200, 200, 255)])
        screen.draw.filled_rect(Rect((star["x"], star["y"]), (star["width"], star["height"])), color)  # ランダムなサイズで描画

    if game_over:
        # ゲームオーバー画面
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
        screen.draw.text(f"SCORE: {score}", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color="white")
        sounds.bgm.stop()  # ゲームオーバー時にBGMを停止
    else:
        # ゲーム画面
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            screen.draw.filled_rect(Rect((bullet['x'], bullet['y']), (5, 10)), 'cyan')

        # スコア表示（左上）
        screen.draw.text(f"SCORE: {score}", topleft=(10, 10), fontsize=30, color="white")

# 自動発射のタイマーを設定
clock.schedule_interval(fire_bullet, 0.25)  # 何秒ごとに弾を発射するか

# 効果音の音量設定
sounds.shoot.set_volume(0.3)  # 弾の発射音
sounds.hit.set_volume(0.2)    # 敵を倒した音
sounds.crash.set_volume(0.3)  # ゲームオーバー音

# BGMの音量調整と再生
sounds.bgm.set_volume(0.1)  # 音量を設定
sounds.bgm.play(-1)  # -1はループ再生を意味します

# Pygame Zeroのメインループを開始
pgzrun.go()
