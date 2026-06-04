import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# =========================
# シミュレーション設定
# =========================
T = 600
confidence = 0.5
entropy = 0.5
imprint = 0.5

c_history = []
e_history = []
i_history = []  # Imprintも記録

# =========================
# ダイナミクス
# =========================
def step(conf, ent, imp):
    success_signal = np.tanh(imp - ent)
    noise = np.random.normal(0, 0.02)
    
    # Confidence更新
    conf = conf + 0.05 * success_signal - 0.03 * ent + noise
    conf = np.clip(conf, 0, 1)
    
    # Entropy更新（自己破壊機構付き）
    anomaly = (conf > 0.72) * np.random.rand() * 0.12
    ent = ent + 0.04 * (1 - conf) + anomaly - 0.02 * ent
    ent = np.clip(ent, 0, 1)
    
    # Imprint更新
    imp = imp + 0.03 * conf - 0.02 * ent
    imp = np.clip(imp, 0, 1)
    
    return conf, ent, imp

# =========================
# 実行
# =========================
conf, ent, imp = confidence, entropy, imprint

for _ in range(T):
    c_history.append(conf)
    e_history.append(ent)
    i_history.append(imp)
    conf, ent, imp = step(conf, ent, imp)

# =========================
# アニメーション作成
# =========================
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel("Confidence", fontsize=12)
ax.set_ylabel("Entropy", fontsize=12)
ax.set_title("Minimal Cognitive Dynamics\n(Confidence - Entropy Phase Space)", fontsize=14)
ax.grid(True, alpha=0.3)

# 軌跡と現在点
line, = ax.plot([], [], lw=2, color='blue', alpha=0.7, label='Trajectory')
point, = ax.plot([], [], 'ro', markersize=6, label='Current State')

# Imprintの強さを色で表現するための準備
scat = ax.scatter([], [], c=[], cmap='viridis', s=30, alpha=0.6)

ax.legend()

def update(frame):
    # 軌跡
    line.set_data(c_history[:frame], e_history[:frame])
    
    # 現在位置
    point.set_data([c_history[frame]], [e_history[frame]])
    
    # Imprintの強さを色で表示
    colors = i_history[:frame]
    if len(colors) > 0:
        scat.set_offsets(np.c_[c_history[:frame], e_history[:frame]])
        scat.set_array(np.array(colors))
    
    return line, point, scat

ani = FuncAnimation(
    fig, 
    update, 
    frames=len(c_history), 
    interval=20, 
    blit=True
)

# =========================
# GIF保存
# =========================
writer = PillowWriter(fps=30)
ani.save("cognitive_phase_space.gif", writer=writer)

plt.close()
print("✅ GIFを保存しました: cognitive_phase_space.gif")
print(f"   フレーム数: {T}  |  所要時間: 約 {T/30:.1f}秒")
