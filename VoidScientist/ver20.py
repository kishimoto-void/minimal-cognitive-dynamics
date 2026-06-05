import random
import math
import numpy as np
import matplotlib
# ヘッドレス環境（CUI環境）での動作を保証するためAggバックエンドを明示的に指定
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Set, Optional

# ==========================================
# SYSTEM PARAMETERS & CONFIGURATION
# ==========================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# 生態系・数理物理パラメータ
L_0 = 25.0          # 基礎寿命
ALPHA = 1.2         # 環境ストレス感度
BETA = 1.8          # 適応報酬係数
GAMMA = 2.0         # 淘汰圧係数
MAX_CAPACITY = 15   # 環境キャパシティ (K)

AVAILABLE_CAUSES = ["Alpha", "Beta", "Gamma", "Void"]
OPERATOR_HIERARCHY = ["AND", "OR", "XOR", "NAND", "XNOR"]


# ==========================================
# DATA CORE: INDIVIDUAL THEORY MODEL
# ==========================================
@dataclass
class Theory:
    causes: Tuple[str, ...]
    operator: str
    fitness: float = 1.0
    age: int = 1
    parent_paradigm: str = "VoidGenesis"
    # 瞬間的な確率ノイズを排し、頑健性を追跡するための履歴バッファ
    fitness_history: List[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.fitness_history:
            self.fitness_history = [self.fitness]

    def update_fitness(self, raw_fitness: float):
        """慣性を持たせた適応度の更新（学習と慣性の再現）"""
        self.fitness = 0.6 * self.fitness + 0.4 * raw_fitness
        self.fitness_history.append(self.fitness)
        if len(self.fitness_history) > 5:
            self.fitness_history.pop(0)

    @property
    def stability_penalty(self) -> float:
        """過去の適応度の移動分散を計算。バタつきが大きい『ギャンブラー理論』にペナルティを与える"""
        if len(self.fitness_history) < 2:
            return 0.0
        variance = float(np.var(self.fitness_history))
        return variance * 1.5

    def genome(self) -> Tuple[Tuple[str, ...], str]:
        return (self.causes, self.operator)


# ==========================================
# LOGIC CORE: PARITY EVALUATOR
# ==========================================
class LogicalOperator:
    @staticmethod
    def evaluate(op: str, bits: List[bool]) -> bool:
        """多入力における厳密な論理評価とパリティチェック"""
        if not bits: 
            return False
        
        if op in ["AND", "NAND"]:
            res = all(bits)
            return not res if op == "NAND" else res
        
        if op == "OR":
            return any(bits)
            
        if op == "XOR":
            # 多入力XORの標準定義（Trueの数が奇数個であればTrue）
            return sum(1 for b in bits if b) % 2 == 1
            
        if op == "XNOR":
            # XORの完全な否定（Trueの数が偶数個であればTrue：一貫性バグの修正）
            return sum(1 for b in bits if b) % 2 == 0
            
        return False

    @staticmethod
    def complexity(op: str) -> float:
        """上位概念演算子ほど高い報酬係数（進化のインセンティブ）を持つ"""
        return {"AND": 1.0, "OR": 1.0, "XOR": 1.5, "NAND": 2.0, "XNOR": 2.5}.get(op, 1.0)


# ==========================================
# ADVANCED METABOLISM & KNOWLEDGE SYSTEMS
# ==========================================
class ConceptAxioms:
    """成果ベースの概念アンロック機構"""
    def __init__(self):
        self.unlocked_operators: Set[str] = {"AND", "OR"}
        self.operator_success_streaks: Dict[str, int] = {op: 0 for op in OPERATOR_HIERARCHY}

    def track_achievements(self, population: List[Theory], current_stress: float):
        # 【修正】最低限の環境流動性（ストレス）条件を 0.1 -> 0.06 に緩和
        if current_stress < 0.06:
            return

        # 現在エコシステムが扱える最高位の演算子を特定
        highest_active_op = "AND"
        for op in OPERATOR_HIERARCHY:
            if op in self.unlocked_operators:
                highest_active_op = op

        # 必要となる適応度閾値は 1.15
        success = any(t.operator == highest_active_op and t.fitness > 1.15 for t in population)
        
        if success:
            self.operator_success_streaks[highest_active_op] += 1
        else:
            self.operator_success_streaks[highest_active_op] = max(0, self.operator_success_streaks[highest_active_op] - 1)

        # 次の上位演算子のインデックスを取得
        current_index = OPERATOR_HIERARCHY.index(highest_active_op)
        if current_index + 1 < len(OPERATOR_HIERARCHY):
            next_op = OPERATOR_HIERARCHY[current_index + 1]
            
            # 必要連続成功回数は 4回
            if self.operator_success_streaks[highest_active_op] >= 4:
                self.unlocked_operators.add(next_op)
                print(f"💡 [CONCEPT UNLOCKED] 成果により新しい論理公理が発見されました: {next_op} (Streak: {self.operator_success_streaks[highest_active_op]})")
                self.operator_success_streaks[highest_active_op] = 0


class GhostArchetypeSystem:
    """死骸知識をクラスタ化し『幽霊原型（時代精神）』として結晶化する機構"""
    def __init__(self):
        # 3要素構造を一貫して維持: (causes, operator, weight)
        self.raw_ghosts: List[Tuple[Tuple[str, ...], str, float]] = []

    def inject_death(self, theory: Theory, stress: float):
        # 適応度が高く、かつ安定打率を残して死んだ個体ほど、亡霊としての発言力が強まる
        weight = (theory.fitness / (1.0 + theory.stability_penalty)) * (1.0 + stress)
        self.raw_ghosts.append((theory.causes, theory.operator, weight))

    def decay_and_crystallize(self) -> Optional[Tuple[Tuple[str, ...], str, float]]:
        # 記憶の風化率（減衰係数）は 0.83
        self.raw_ghosts = [(c, o, w * 0.83) for c, o, w in self.raw_ghosts if w * 0.83 > 0.05]
        if not self.raw_ghosts:
            return None

        # 同一ゲノム構造（原因プールと演算子のペア）ごとに重量を集計
        archetype_map: Dict[Tuple[Tuple[str, ...], str], float] = {}
        for causes, op, w in self.raw_ghosts:
            archetype_map[(causes, op)] = archetype_map.get((causes, op), 0.0) + w

        # 最も蓄積重量の多いゲノムを「幽霊原型（Archetype）」として選出
        best_genome = max(archetype_map, key=archetype_map.get)
        total_crystallized_weight = archetype_map[best_genome]
        
        return (best_genome[0], best_genome[1], total_crystallized_weight)


# ==========================================
# MAIN ECOSYSTEM SIMULATOR
# ==========================================
class AxiomaticUniverse:
    def __init__(self):
        self.generation = 0
        self.void_gap = 0.15
        self.environmental_stress = 0.15
        self.current_paradigm = "VoidGenesis"
        
        self.theories: List[Theory] = []
        self.axioms = ConceptAxioms()
        self.ghost_system = GhostArchetypeSystem()
        
        # 統計トラッキング用バッファ
        self.history_pop_size = []
        self.history_void_gap = []
        self.history_archetype_weight = []
        self.history_op_ratios = {op: [] for op in OPERATOR_HIERARCHY}

        # 初期創世世代のシード生成 (AND理論から開始)
        for _ in range(6):
            causes = tuple(random.sample(AVAILABLE_CAUSES, random.randint(1, 2)))
            self.theories.append(Theory(causes=causes, operator="AND"))

    def step_generation(self):
        self.generation += 1
        
        # --- 0. 環境流動と適応度の多サンプル評価 ---
        for t in self.theories:
            t.age += 1
            success = 0
            # 評価サンプル数を15に増やし、確率の偶発的なブレ（運要素）を抑制
            for _ in range(15):
                env = {c: random.choice([True, False]) for c in AVAILABLE_CAUSES}
                inputs = [env[c] for c in t.causes]
                pred = LogicalOperator.evaluate(t.operator, inputs)
                actual = random.random() < self.void_gap
                if pred == actual: 
                    success += 1
            
            raw_fit = (success / 15.0) * LogicalOperator.complexity(t.operator)
            t.update_fitness(raw_fit)

        # --- ① 破壊フェーズ (Death) ---
        survivors = []
        for t in self.theories:
            # 安定性ペナルティを反映した実質適応度で寿命 L(t) を動的計算
            effective_fitness = t.fitness - t.stability_penalty
            d_env = (self.void_gap + self.environmental_stress) / 2.0
            le = L_0 * math.exp(-ALPHA * d_env) * (1.0 + BETA * effective_fitness)
            le = max(1.0, le)

            # シグモイド関数による滑らかな淘汰圧
            x = (t.age / le) + GAMMA * (1.0 - effective_fitness)
            p_death = 1.0 / (1.0 + math.exp(-(x - 2.5)))

            if random.random() < p_death:
                self.ghost_system.inject_death(t, self.environmental_stress)
            else:
                survivors.append(t)
        self.theories = survivors

        # 幽霊原型の結晶化状態を取得
        crystallized = self.ghost_system.decay_and_crystallize()
        archetype_weight = crystallized[2] if crystallized else 0.0

        # --- ② 生成フェーズ (Birth) ---
        # キャパシティ制限（K=15）と出生数を完全に同期させ、無駄な即時削除を根逐
        free_space = MAX_CAPACITY - len(self.theories)
        birth_count = 0
        if free_space > 0:
            # 出生数算定係数は強化版 (0.65, 5.0) を維持
            birth_potential = math.floor(free_space * 0.65 + 5.0 * self.void_gap)
            birth_count = min(free_space, max(0, birth_potential))

        for _ in range(birth_count):
            if len(self.theories) >= 2 and random.random() < 0.7:
                # 遺伝交叉：両親の持つすべての原因プール（遺伝子）をブレンドして子へ受け継ぐ
                p1, p2 = random.sample(self.theories, 2)
                combined_pool = list(set(p1.causes + p2.causes))
                sample_size = min(len(combined_pool), random.randint(1, 3))
                c_causes = tuple(random.sample(combined_pool, sample_size))
                
                c_op = random.choice(list(self.axioms.unlocked_operators))
                self.theories.append(Theory(causes=c_causes, operator=c_op, parent_paradigm=self.current_paradigm))
            else:
                # 新規自然発生
                c_causes = (random.choice(AVAILABLE_CAUSES),)
                c_op = random.choice(list(self.axioms.unlocked_operators))
                self.theories.append(Theory(causes=c_causes, operator=c_op, parent_paradigm=self.current_paradigm))

        # --- ③ 更新・成果チェック・パラダイムシフト ---
        self.axioms.track_achievements(self.theories, self.environmental_stress)

        # 【修正】パラダイムシフト閾値を 4.2 -> 3.5 に引き下げ
        if crystallized and archetype_weight > 3.5 and self.void_gap > 0.18:
            arch_causes, arch_op, _ = crystallized
            self.current_paradigm = f"Paradigm_{self.generation}"
            
            # 歴史を断絶させない慣性引き継ぎ型ソフト・リセット
            self.void_gap = 0.4 * self.void_gap + 0.05
            self.environmental_stress = 0.4 * self.environmental_stress + 0.05
            
            # 亡霊たちの集合知の結晶から「革命的理論」を現世へ具現化
            revolutionary = Theory(
                causes=arch_causes, 
                operator=arch_op, 
                fitness=1.6, 
                parent_paradigm=self.current_paradigm
            )
            self.theories.append(revolutionary)
            print(f"💥 [PARADIGM SHIFT] Gen {self.generation:03d} | Archetype Weight: {archetype_weight:.2f} | New Era: {self.current_paradigm} -> {arch_causes} via {arch_op}")

        # 宇宙側（環境）のエントロピー硬直フィードバック
        ops_present = set(t.operator for t in self.theories)
        if len(ops_present) <= 1:
            # 生態系が1つのドグマ（演算子）に染まりきると環境が激化して退屈を破壊する
            self.void_gap = min(0.6, self.void_gap + 0.05)
            self.environmental_stress = min(0.5, self.environmental_stress + 0.04)
        else:
            # 【修正】多様性が維持されている時期の Void Gap 低下速度を -0.011 -> -0.008 に減速
            self.void_gap = max(0.02, self.void_gap - 0.008)
            self.environmental_stress = max(0.05, self.environmental_stress - 0.01)

        # 各種統計データのトラッキング記録
        total_pop = max(1, len(self.theories))
        self.history_pop_size.append(total_pop)
        self.history_void_gap.append(self.void_gap)
        self.history_archetype_weight.append(archetype_weight)
        
        op_counts = {op: 0 for op in OPERATOR_HIERARCHY}
        for t in self.theories:
            if t.operator in op_counts: 
                op_counts[t.operator] += 1
        for op in OPERATOR_HIERARCHY:
            self.history_op_ratios[op].append(op_counts[op] / total_pop)

        if self.generation % 10 == 0:
            print(f"Gen {self.generation:03d} | Pop: {len(self.theories):02d}/{MAX_CAPACITY} | VoidGap: {self.void_gap:.3f} | ArchetypeWeight: {archetype_weight:.2f} | Unlocked: {list(self.axioms.unlocked_operators)}")


# ==========================================
# EXECUTION & DEEP ANALYTICS PLOT SAVE
# ==========================================
if __name__ == "__main__":
    TOTAL_GENERATIONS = 200
    print(f"--- Starting Stage 20.2: Axiomatic Universe Simulation ({TOTAL_GENERATIONS} Generations) ---")
    universe = AxiomaticUniverse()
    
    for _ in range(TOTAL_GENERATIONS):
        universe.step_generation()
        
    # 可視化処理の構築
    fig, axes = plt.subplots(3, 1, figsize=(11, 13), sharex=True)
    gens = range(1, TOTAL_GENERATIONS + 1)
    
    # パネル1: 人口動態
    axes[0].plot(gens, universe.history_pop_size, color="royalblue", linewidth=2.5, label="Ecosystem Active Population (N)")
    axes[0].axhline(y=MAX_CAPACITY, color="gray", linestyle="--", alpha=0.6, label="Carrying Capacity Bound (K=15)")
    axes[0].set_title("Ecosystem Population Dynamics & Dynamic Equilibrium", fontsize=12, fontweight='bold')
    axes[0].set_ylabel("Individuals (Count)", fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="upper left")
    
    # パネル2: 宇宙のエントロピー流動 vs 死骸結晶化重量の相関
    axes[1].plot(gens, universe.history_void_gap, color="crimson", linewidth=2.2, label="Void Gap (Cosmic Fluidity Press)")
    axes[1].plot(gens, universe.history_archetype_weight, color="gold", linewidth=1.8, linestyle="-.", label="Crystallized Archetype Weight (Ghost Impact)")
    # 【修正】グラフ上の閾値ラインも 4.2 -> 3.5 に変更
    axes[1].axhline(y=3.5, color="orange", linestyle=":", linewidth=1.5, label="Shift Threshold Trigger (3.5)")
    axes[1].set_title("Cosmic Fluidity vs Ghost Archetype Weight Dynamics", fontsize=12, fontweight='bold')
    axes[1].set_ylabel("Metric Scale", fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="upper left")
    
    # パネル3: 成果ベース解禁に伴う論理公理（演算子）の世代遷移スタックプロット
    y_data = [universe.history_op_ratios[op] for op in OPERATOR_HIERARCHY]
    axes[2].stackplot(gens, y_data, labels=OPERATOR_HIERARCHY, colors=['#4c72b0', '#55a868', '#c44e52', '#8172b3', '#ccb974'], alpha=0.85)
    axes[2].set_title("Succession of Logical Axioms via Achievement-based Unlocking", fontsize=12, fontweight='bold')
    axes[2].set_xlabel("Generations (Time Steps)", fontsize=10)
    axes[2].set_ylabel("Composition Ratio", fontsize=10)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(loc="upper left")
    
    plt.tight_layout()
    
    output_filename = "stage20_2_final_universe.png"
    plt.savefig(output_filename, dpi=150)
    print(f"\n Simulation completed successfully.")
    print(f"↳ Deep analytics graph generated and saved to: [ {output_filename} ]")
