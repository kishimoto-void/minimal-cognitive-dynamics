import random
import math
from collections import Counter
from itertools import combinations, product

# ==============================================================================
# クラス定数・文明の制約
# ==============================================================================
COMPLEXITY_PENALTY = 0.08
ANOMALY_SEVERITY = 0.85     
MAX_MEMORY_SLOTS = 6
INITIAL_BUDGET = 50.0
HISTORICAL_DECAY = 0.94

ANOMALY_THRESHOLD = 3.0
ANOMALY_GAIN = 6.0
ANOMALY_DECAY = 0.92
MEMORY_WINDOW = 40 

OPERATOR_COMPLEXITY = {
    "OR": 0.00, "AND": 0.02, "NOT": 0.05, "XOR": 0.08,
    "NAND": 0.14, "XNOR": 0.16
}

OPERATOR_DISTANCE = {
    "OR":   {"OR": 0, "AND": 1, "XOR": 2, "NOT": 2, "NAND": 2, "XNOR": 3},
    "AND":  {"OR": 1, "AND": 0, "XOR": 2, "NOT": 3, "NAND": 2, "XNOR": 2},
    "XOR":  {"OR": 2, "AND": 2, "XOR": 0, "NOT": 3, "NAND": 3, "XNOR": 1},
    "NOT":  {"OR": 2, "AND": 3, "XOR": 3, "NOT": 0, "NAND": 1, "XNOR": 2},
    "NAND": {"OR": 2, "AND": 2, "XOR": 3, "NOT": 1, "NAND": 0, "XNOR": 2},
    "XNOR": {"OR": 3, "AND": 2, "XOR": 1, "NOT": 2, "NAND": 2, "XNOR": 0},
}


# ==============================================================================
# 確率的・非線形相転移宇宙
# ==============================================================================
class AutomutatingUniverse:
    def __init__(self):
        self.registry = [
            {"name": "matter_alpha", "color": "red", "shape": "ball", "speed": "fast", "energy": "high", "temperature": "hot"},
            {"name": "matter_beta", "color": "blue", "shape": "box", "speed": "slow", "energy": "low", "temperature": "cold"},
        ]
        self.experimental_stress = 0.0
        self.current_law_combo = ("energy", "speed")
        self.current_law_operator = "AND"
        
        self.all_attributes = ["color", "shape", "speed", "energy"]
        self.all_operators = ["AND", "OR", "XOR"] 
        self.last_experiment_signature = None

    def unlock_operator_in_nature(self, op):
        if op not in self.all_operators:
            self.all_operators.append(op)

    def apply_stress_and_check_mutation(self, blueprint):
        base_stress = random.gammavariate(alpha=2.5, beta=1.3)
        
        sig = (blueprint.get("color"), blueprint.get("shape"))
        if sig == self.last_experiment_signature:
            base_stress *= 2.2 
        self.last_experiment_signature = sig

        self.experimental_stress += base_stress
        dynamic_threshold = 42.0 + random.uniform(-4.0, 4.0)
        
        if self.experimental_stress >= dynamic_threshold:
            self.experimental_stress = 0.0
            
            next_r = random.choice([1, 2, 3])
            all_possible_combos = [tuple(sorted(list(c))) for c in combinations(self.all_attributes, next_r)]
            self.current_law_combo = random.choice(all_possible_combos)
            
            next_ops = [op for op in self.all_operators if op != self.current_law_operator]
            if next_ops:
                self.current_law_operator = random.choice(next_ops)
            return True
        return False

    def manifest_matter(self, blueprint):
        key_bits = []
        for attr in self.current_law_combo:
            bit = 1 if blueprint[attr] in ["high", "fast", "red", "ball"] else 0
            key_bits.append(bit)
            
        op = self.current_law_operator
        if op == "AND": is_hot = all(key_bits) if key_bits else False
        elif op == "OR": is_hot = any(key_bits) if key_bits else False
        elif op == "XOR": is_hot = (sum(key_bits) == 1) if key_bits else False
        elif op == "NOT": is_hot = not any(key_bits) if key_bits else True
        elif op == "NAND": is_hot = not all(key_bits) if key_bits else True
        elif op == "XNOR": is_hot = (sum(key_bits) != 1) if key_bits else True
        else: is_hot = False
            
        new_obj = blueprint.copy()
        new_obj["name"] = f"quantum_matter_{random.randint(1000,9999)}"
        new_obj["temperature"] = "hot" if is_hot else "cold"
        self.registry.append(new_obj)
        return new_obj


# ==============================================================================
# 自己修正型メタ認知科学文明エージェント (Phase 16.2 - 排他等価分派修正版)
# ==============================================================================
class VoidScientist:
    def __init__(self):
        self.observations = []
        self.domain_space = {
            "color": ["red", "blue", "grey", "green"],
            "shape": ["ball", "box", "stone"],
            "speed": ["fast", "slow"],
            "energy": ["high", "low"]
        }
        self.attributes = list(self.domain_space.keys())
        self.target_attribute = "temperature"
        
        self.experiment_gap = 0.0
        self.certainty_gap = 0.0
        self.history_gap = 0.0
        self.meta_history_gap = 0.0
        self.void_gap = 20.0
        self.anomaly_pressure = 0.0
        
        self.discovered_operators = ["OR", "AND", "XOR", "NOT"]
        self.has_invented_nand = False
        self.has_invented_xnor = False
        
        self.max_theory_slots = 5
        self.complexity_penalty_modifier = 1.0
        self.max_logical_r = 2 
        
        self.candidate_theories = []
        self.civilization_memory = []
        
        self.meta_laws = {"preferred_operators": [], "extinction_patterns": []}
        
        self.predicted_universe_stress = 0.0
        self.catastrophe_warning_flag = False
        self.recent_anomalies_timeline = []

        self.experiment_budget = INITIAL_BUDGET
        self.last_predictions = {}
        self.last_actual = None
        self.optimal_experiment_blueprint = None

    def calculate_jaccard(self, set_a, set_b):
        union = len(set_a | set_b)
        if union == 0: return 1.0
        return len(set_a & set_b) / union

    def find_best_parent(self, child_combo, child_op):
        if not self.candidate_theories:
            return "VoidGenesis"
        
        best_parent_name = "VoidGenesis"
        min_distance = 99.0
        
        child_set = set(child_combo)
        for theory in self.candidate_theories:
            attr_dist = 1.0 - self.calculate_jaccard(child_set, set(theory["causes"]))
            op_dist = OPERATOR_DISTANCE.get(child_op, {}).get(theory["operator"], 2.0)
            
            total_dist = attr_dist * 2.0 + op_dist * 0.5
            if total_dist < min_distance:
                min_distance = total_dist
                best_parent_name = theory["name"]
                
        return best_parent_name

    def analyze(self, world_system):
        current_prediction_error_flag = False
        if self.candidate_theories and self.last_predictions and (self.last_actual is not None):
            top_name = self.candidate_theories[0]["name"]
            if self.last_predictions.get(top_name) != self.last_actual:
                current_prediction_error_flag = True

        if current_prediction_error_flag:
            self.anomaly_pressure += ANOMALY_GAIN
            self.recent_anomalies_timeline.append(1.0)
        else:
            self.recent_anomalies_timeline.append(0.0)
        
        self.anomaly_pressure *= ANOMALY_DECAY
        if len(self.recent_anomalies_timeline) > 15:
            self.recent_anomalies_timeline.pop(0)

        anomaly_density = sum(self.recent_anomalies_timeline) / max(1, len(self.recent_anomalies_timeline))
        self.predicted_universe_stress = (anomaly_density * 30.0) + (self.anomaly_pressure * 2.5)
        self.catastrophe_warning_flag = (self.predicted_universe_stress > 25.0)

        recent_obs = self.observations[-MEMORY_WINDOW:] if self.observations else []

        # 数学概念・次元拡張の判定
        if self.void_gap > 17.0 and self.anomaly_pressure > 3.0 and len(recent_obs) >= 5:
            max_possible_explanation = 0.0
            for r in range(1, self.max_logical_r + 1):
                for combo in combinations(self.attributes, r):
                    for op in self.discovered_operators:
                        conflicts = 0
                        for obj in recent_obs:
                            key_bits = [1 if obj[attr] in ["high", "fast", "red", "ball"] else 0 for attr in combo]
                            if op == "AND": s = "hot" if all(key_bits) else "cold"
                            elif op == "OR": s = "hot" if any(key_bits) else "cold"
                            elif op == "XOR": s = "hot" if (sum(key_bits) == 1) else "cold"
                            elif op == "NOT": s = "hot" if not any(key_bits) else "cold"
                            elif op == "NAND": s = "hot" if not all(key_bits) else "cold"
                            elif op == "XNOR": s = "hot" if (sum(key_bits) != 1) else "cold"
                            else: s = "cold"
                            if s != obj[self.target_attribute]: conflicts += 1
                        acc = 1.0 - (conflicts / len(recent_obs))
                        if acc > max_possible_explanation: max_possible_explanation = acc

            if max_possible_explanation < 0.82:
                if self.max_logical_r < 3:
                    self.max_logical_r = 3
                    print(f"\n🧠【認識のパラダイムシフト】次元の壁を超越。文明は『3変数高階階層認知』(r=3) を獲得しました。")
                else:
                    dead_ops = [g["operator"] for g in self.civilization_memory if g["death_reason"] == "prediction_failure"]
                    op_counts = Counter(dead_ops)
                    
                    if (op_counts["AND"] + op_counts["OR"] >= op_counts["XOR"]) and not self.has_invented_nand:
                        self.discovered_operators.append("NAND")
                        self.has_invented_nand = True
                        self.max_theory_slots += 3               
                        self.complexity_penalty_modifier *= 0.6  
                        world_system.unlock_operator_in_nature("NAND")
                        print("\n🚨【数学の爆発】新言語 『NAND』 創発。スロット枠が拡張され、概念記述コストが40%デフレしました！")
                    elif not self.has_invented_xnor:
                        self.discovered_operators.append("XNOR")
                        self.has_invented_xnor = True
                        self.max_theory_slots += 3
                        self.complexity_penalty_modifier *= 0.6
                        world_system.unlock_operator_in_nature("XNOR")
                        print("\n🚨【数学の爆発】新言語 『XNOR』 創発。スロット枠が拡張され、概念記述コストが40%デフレしました！")

        # 予測成功・失敗の集計と、ドグマ分裂の執行
        if self.observations and self.last_predictions and (self.last_actual is not None):
            active_theories = []
            schism_candidates = [] 

            for theory in self.candidate_theories:
                t_name = theory["name"]
                pred = self.last_predictions.get(t_name)
                
                theory["age"] += 1
                if pred == self.last_actual:
                    theory["success"] += 1
                    theory["explanatory_power"] += 1.0
                    theory["confidence"] = min(1.0, theory["confidence"] + 0.05)
                else:
                    theory["fail"] += 1
                    weight = 1.0 + math.log(1.0 + theory["explanatory_power"])
                    shattering_damage = (ANOMALY_SEVERITY * (1.0 + theory["confidence"])) / weight
                    
                    if theory["explanatory_power"] > 8.0 and self.void_gap > 16.0 and not self.catastrophe_warning_flag:
                        shattering_damage *= 0.12 
                        theory["is_dogma"] = True
                    else:
                        theory["is_dogma"] = False

                    if self.catastrophe_warning_flag:
                        shattering_damage *= 1.8
                    
                    theory["confidence"] -= shattering_damage
                
                total_trials = theory["success"] + theory["fail"]
                theory["predictive_accuracy"] = theory["success"] / total_trials if total_trials > 0 else 0.0
                
                if theory["confidence"] > 0.88 and self.void_gap > 16.0 and len(theory["causes"]) < self.max_logical_r:
                    schism_candidates.append(theory)

                if theory["confidence"] >= 0.15:
                    active_theories.append(theory)
                else:
                    death_reason = "law_shift" if current_prediction_error_flag else "prediction_failure"
                    self.civilization_memory.append({
                        "name": theory["name"], "causes": theory["causes"], "operator": theory["operator"],
                        "rules": theory["rules"], "explanatory_power": theory["explanatory_power"],
                        "success": theory["success"], "historical_weight": 1.0, "death_reason": death_reason,
                        "parent_paradigm": theory.get("parent_paradigm"), 
                        "birth_conditions": {
                            "universe_law_combo": world_system.current_law_combo, 
                            "universe_law_operator": world_system.current_law_operator,
                            "obs_count": len(self.observations)
                        }
                    })
                    
                    if len(self.civilization_memory) >= 3:
                        dead_ops = [g["operator"] for g in self.civilization_memory]
                        self.meta_laws["extinction_patterns"] = [Counter(dead_ops).most_common(1)[0][0]]
                    
                    if len(self.civilization_memory) > MAX_MEMORY_SLOTS:
                        self.civilization_memory.pop(0)
            
            # ドグマ分裂の肉体化
            for parent_theory in schism_candidates:
                if len(active_theories) >= self.max_theory_slots: break
                
                schism_type = random.choice([1, 2])
                new_cause = parent_theory["causes"]
                new_op = parent_theory["operator"]
                faction_name = "VoidFaction"
                
                # --- 【バグ修正】排他的な if-elif 制御構造への完全修正 ---
                if schism_type == 1:
                    unused_attrs = [a for a in self.attributes if a not in parent_theory["causes"]]
                    if unused_attrs:
                        new_cause = tuple(sorted(list(parent_theory["causes"]) + [random.choice(unused_attrs)]))
                        new_op = parent_theory["operator"]
                        faction_name = f"Conservative:{parent_theory['name']}+{new_cause[-1]}"
                    else:
                        schism_type = 2  # 属性に空きがない場合は改革派へフォールバック
                        
                if schism_type == 2:
                    new_cause = parent_theory["causes"]
                    available_ops = [op for op in self.discovered_operators if op != parent_theory["operator"]]
                    available_ops.sort(key=lambda o: OPERATOR_DISTANCE.get(parent_theory["operator"], {}).get(o, 2))
                    new_op = available_ops[0] if available_ops else parent_theory["operator"]
                    faction_name = f"Reform:{parent_theory['name']}[->{new_op}]"

                if not any(t["name"] == faction_name for t in active_theories):
                    print(f"🌲【ドグマ分裂（Schism）】支配学派 '{parent_theory['name']}' が内部対立により決裂！ 新分派 '{faction_name}' が誕生しました。")
                    active_theories.append({
                        "name": faction_name, "causes": new_cause, "operator": new_op,
                        "effect": self.target_attribute, "rules": {new_cause: new_op},
                        "predictive_accuracy": parent_theory["predictive_accuracy"],
                        "confidence": parent_theory["confidence"] * 0.75, 
                        "explanatory_power": parent_theory["explanatory_power"] * 0.5,
                        "age": 1, "success": 1, "fail": 0, "is_dogma": False,
                        "parent_paradigm": parent_theory["name"], 
                        "birth_conditions": parent_theory["birth_conditions"]
                    })

            self.candidate_theories = active_theories

        for ghost in self.civilization_memory:
            ghost["historical_weight"] *= HISTORICAL_DECAY

        if self.anomaly_pressure > ANOMALY_THRESHOLD or not self.candidate_theories:
            self._spawn_counter_theories(world_system)
            self.anomaly_pressure = 0.0
            
        self.candidate_theories.sort(key=lambda x: (x["confidence"], x["explanatory_power"]), reverse=True)

        # 内部ストレス（Void Gap）計算
        self.certainty_gap = 0.0
        if self.candidate_theories:
            top_theory = self.candidate_theories[0]
            if top_theory["confidence"] > 0.80:
                self.certainty_gap = (top_theory["confidence"] - 0.80) * 12.0
            theory_gap_val = max(0.0, 10.0 - (top_theory["confidence"] * 10.0))
        else:
            theory_gap_val = 10.0

        self.history_gap = 0.0
        self.meta_history_gap = 0.0
        
        if self.civilization_memory and self.candidate_theories:
            top_theory = self.candidate_theories[0]
            top_causes_set = set(top_theory["causes"])
            hist_sum, meta_sum, weight_sum = 0.0, 0.0, 0.0
            
            for ghost in self.civilization_memory:
                ghost_causes_set = set(ghost["causes"])
                w = ghost["historical_weight"]
                weight_sum += w
                
                subsumption_rate = self.calculate_jaccard(top_causes_set, ghost_causes_set)
                hist_sum += (ghost["explanatory_power"] * (1.0 - subsumption_rate) * 0.4) * w
                
                op_dist = OPERATOR_DISTANCE.get(top_theory["operator"], {}).get(ghost["operator"], 2.0)
                ghost_birth_combo = set(ghost["birth_conditions"]["universe_law_combo"])
                ghost_past_adaptability = self.calculate_jaccard(ghost_causes_set, ghost_birth_combo)
                
                meta_sum += (ghost_past_adaptability * (1.0 - subsumption_rate) * (1.0 + op_dist * 1.5) * 4.5) * w
                
            if weight_sum > 0:
                self.history_gap = hist_sum / weight_sum
                self.meta_history_gap = meta_sum / weight_sum

        prediction_error_val = 6.0 if current_prediction_error_flag else 0.0
        catastrophe_stress = 5.0 if self.catastrophe_warning_flag else 0.0
        
        self.void_gap = theory_gap_val + prediction_error_val + self.experiment_gap + self.certainty_gap + self.history_gap + self.meta_history_gap + catastrophe_stress

    def _spawn_counter_theories(self, world_system):
        recent_obs = self.observations[-MEMORY_WINDOW:]
        if len(recent_obs) < 2: return
        
        existing_combos = {(t["causes"], t["operator"]) for t in self.candidate_theories}
        scored_candidates = []

        for r in range(1, self.max_logical_r + 1):
            for combo in combinations(self.attributes, r):
                for op in self.discovered_operators:
                    if (combo, op) not in existing_combos:
                        conflicts = 0
                        for obj in recent_obs:
                            key_bits = [1 if obj[attr] in ["high", "fast", "red", "ball"] else 0 for attr in combo]
                            
                            if op == "AND": logical_state = "hot" if all(key_bits) else "cold"
                            elif op == "OR": logical_state = "hot" if any(key_bits) else "cold"
                            elif op == "XOR": logical_state = "hot" if (sum(key_bits) == 1) else "cold"
                            elif op == "NOT": logical_state = "hot" if not any(key_bits) else "cold"
                            elif op == "NAND": logical_state = "hot" if not all(key_bits) else "cold"
                            elif op == "XNOR": logical_state = "hot" if (sum(key_bits) != 1) else "cold"
                                
                            if logical_state != obj[self.target_attribute]:
                                conflicts += 1
                                
                        explanation_score = 1.0 - (conflicts / len(recent_obs))
                        
                        subsumption_bonus = 0.0
                        combo_set = set(combo)
                        for ghost in self.civilization_memory:
                            subsumption_bonus += self.calculate_jaccard(combo_set, set(ghost["causes"])) * ghost["historical_weight"] * 0.05

                        dimension_penalty = len(combo) * COMPLEXITY_PENALTY * self.complexity_penalty_modifier
                        op_penalty = OPERATOR_COMPLEXITY.get(op, 0.0) * self.complexity_penalty_modifier
                        
                        meta_bonus = 0.0
                        if op in self.meta_laws["extinction_patterns"]:
                            meta_bonus -= 0.15 
                        
                        final_score = max(0.0, explanation_score - dimension_penalty - op_penalty + subsumption_bonus + meta_bonus)
                        scored_candidates.append((final_score, combo, op, explanation_score))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        for score, combo, op, exp_accuracy in scored_candidates:
            if len(self.candidate_theories) >= self.max_theory_slots: break
            if score <= 0.05: continue
            
            assigned_parent = self.find_best_parent(combo, op)
            
            self.candidate_theories.append({
                "name": f"Paradigm:({'+'.join(combo)}|{op})",
                "causes": combo, "operator": op, "effect": self.target_attribute, "rules": {combo: op},
                "predictive_accuracy": exp_accuracy,
                "confidence": min(1.0, score),
                "explanatory_power": float(len(recent_obs)),
                "age": 1, "success": len(recent_obs), "fail": 0,
                "is_dogma": False,
                "parent_paradigm": assigned_parent,  
                "birth_conditions": {
                    "universe_law_combo": world_system.current_law_combo, 
                    "universe_law_operator": world_system.current_law_operator,
                    "obs_count": len(self.observations)
                }
            })

    def formulate_experiment_demand(self):
        best_cost = 1.0 
        if not self.candidate_theories:
            self.experiment_gap = 0.0
            self.optimal_experiment_blueprint = {"color": "red", "shape": "ball", "speed": "fast", "energy": "high"}
            return

        best_blueprint = None
        max_collapse_utility = -999.0
        saved_collapse_gap = 0.0

        keys = self.domain_space.keys()
        values = self.domain_space.values()
        
        for combo in product(*values):
            virtual_obj = dict(zip(keys, combo))
            collapse_if_hot = 0.0
            collapse_if_cold = 0.0
            
            for theory in self.candidate_theories:
                key_bits = [1 if virtual_obj[attr] in ["high", "fast", "red", "ball"] else 0 for attr in theory["causes"]]
                op = theory["operator"]
                if op == "AND": pred = "hot" if all(key_bits) else "cold"
                elif op == "OR": pred = "hot" if any(key_bits) else "cold"
                elif op == "XOR": pred = "hot" if (sum(key_bits) == 1) else "cold"
                elif op == "NOT": pred = "hot" if not any(key_bits) else "cold"
                elif op == "NAND": pred = "hot" if not all(key_bits) else "cold"
                elif op == "XNOR": pred = "hot" if (sum(key_bits) != 1) else "cold"
                else: pred = "cold"
                
                if pred == "cold": collapse_if_hot += theory["confidence"]
                else: collapse_if_cold += theory["confidence"]
            
            expected_theory_collapse = min(collapse_if_hot, collapse_if_cold)

            cost = 1.0
            if virtual_obj["color"] == "green": cost += 3.0
            if virtual_obj["shape"] == "stone": cost += 1.5
            feasibility = 1.0 / cost

            utility = expected_theory_collapse * feasibility

            if utility > max_collapse_utility:
                max_collapse_utility = utility
                best_blueprint = virtual_obj
                best_cost = cost
                saved_collapse_gap = expected_theory_collapse

        self.experiment_budget = max(0.0, self.experiment_budget - (best_cost * 0.25))
        self.experiment_budget = min(INITIAL_BUDGET, self.experiment_budget + 0.6)

        self.experiment_gap = saved_collapse_gap
        self.optimal_experiment_blueprint = best_blueprint

    def execute_and_predict(self, world_system):
        target_obj = world_system.manifest_matter(self.optimal_experiment_blueprint)
        
        self.last_predictions = {}
        for theory in self.candidate_theories:
            key_bits = [1 if target_obj[attr] in ["high", "fast", "red", "ball"] else 0 for attr in theory["causes"]]
            op = theory["operator"]
            if op == "AND": pred = "hot" if all(key_bits) else "cold"
            elif op == "OR": pred = "hot" if any(key_bits) else "cold"
            elif op == "XOR": pred = "hot" if (sum(key_bits) == 1) else "cold"
            elif op == "NOT": pred = "hot" if not any(key_bits) else "cold"
            elif op == "NAND": pred = "hot" if not all(key_bits) else "cold"
            elif op == "XNOR": pred = "hot" if (sum(key_bits) != 1) else "cold"
            else: pred = "cold"
            self.last_predictions[theory["name"]] = pred

        self.last_actual = target_obj[self.target_attribute]
        self.observations.append(target_obj)
        return target_obj

    def run_cognition_cycle(self, world_system):
        self.analyze(world_system)
        self.formulate_experiment_demand()
        target = self.execute_and_predict(world_system)
        mutated = world_system.apply_stress_and_check_mutation(self.optimal_experiment_blueprint)
        return target, mutated


# ==============================================================================
# 【完全単体執行】 Phase 16.2 稼働
# ==============================================================================
print("===== Phase 16.2: 『排他等価分派・系譜的科学文明シミュレーター』 =====\n")

universe = AutomutatingUniverse()
agent = VoidScientist()

for i in range(2):
    agent.observations.append(universe.registry[i])

total_mutations = 0
for generation in range(1, 301):
    realized_matter, mutated = agent.run_cognition_cycle(universe)
    if mutated:
        total_mutations += 1
    
    if generation % 30 == 0 or mutated:
        mut_status = f"💥 [宇宙相転移発動！ 通算:{total_mutations}回目]" if mutated else "  [定常科学流動]"
        
        if agent.candidate_theories:
            top_theory = agent.candidate_theories[0]
            top_name = top_theory["name"]
            confidence = round(top_theory["confidence"], 2)
            dogma_status = "【🔥正統ドグマ】" if top_theory.get("is_dogma", False) else ""
            parent_link = top_theory.get("parent_paradigm", "None")
            
            cause_jaccard = agent.calculate_jaccard(set(universe.current_law_combo), set(top_theory["causes"]))
            op_accuracy = 1.0 if top_theory["operator"] == universe.current_law_operator else 0.40
            pred_acc = top_theory.get("predictive_accuracy", 1.0)
            true_alignment = (cause_jaccard * 0.6 + pred_acc * 0.4) * op_accuracy
        else:
            top_name = "None"
            confidence = 0.0
            dogma_status = ""
            parent_link = "None"
            true_alignment = 0.0
            
        warn_status = "⚠️ [終末予震アラート]" if agent.catastrophe_warning_flag else "✅ [環境平穏]"
        
        print(f"Gen {generation:03d} | {mut_status} 宇宙の真理: {universe.current_law_combo} ({len(universe.current_law_combo)}属性) | 【{universe.current_law_operator}宇宙】")
        print(f"        >> 👑筆頭学説: {top_name:<45} [確信: {confidence}] {dogma_status}")
        print(f"        >> 🔗 学派系譜（親リンク）: {parent_link}")
        print(f"        >> 🎯 真理アライメント: {round(true_alignment, 2)} | 歴史の忌避演算子: {agent.meta_laws['extinction_patterns']}")
        print(f"        >> 📡 終末予測負荷: {round(agent.predicted_universe_stress, 1)}/42.0 -> {warn_status}")
        print(f"        >> ⚙️ 認知次元: {agent.max_logical_r}次元 | 保持学説数: {len(agent.candidate_theories)}/{agent.max_theory_slots}個 | 語彙空間: {agent.discovered_operators}")
        print(f"        >> 🏛️ 文明内部ストレス (Void Gap): {round(agent.void_gap, 2)}")
        print("-" * 150)
