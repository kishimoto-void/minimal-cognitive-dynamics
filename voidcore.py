import random

class VoidCore:
    def __init__(self,
                 v_init=0.5,
                 s_init=0.5,
                 eta=0.05,
                 v_min=0.1,
                 v_max=1.0):

        # 状態変数
        self.V = v_init  # 欠損
        self.S = s_init  # 内部状態

        # パラメータ（固定）
        self.eta = eta
        self.v_min = v_min
        self.v_max = v_max

    def step(self):
        """
        最小ループ：
        V → A → S → V
        """

        # --- ① 行動A（欠損に基づく微小更新） ---
        A = self.V - self.S  # ズレそのものを駆動力にする

        # ノイズ（完全安定化防止）
        A += random.uniform(-0.01, 0.01)

        # --- ② 状態更新S ---
        self.S += self.eta * A

        # 変化制限（暴走防止）
        self.S = self._clip(self.S, 0.0, 1.0)

        # --- ③ 欠損更新V ---
        # 「完全一致しない」構造を維持
        self.V += self.eta * (self.S - self.V)

        # 欠損帯域制御（死と爆発を防ぐ）
        self.V = self._clip(self.V, self.v_min, self.v_max)

        return self.V, self.S, A

    def _clip(self, x, low, high):
        return max(low, min(high, x))


# ======================
# 実行テスト
# ======================
if __name__ == "__main__":
    core = VoidCore()

    for t in range(100):
        V, S, A = core.step()
        print(f"t={t:03d} V={V:.3f} S={S:.3f} A={A:.3f}")
