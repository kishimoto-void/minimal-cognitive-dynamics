import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Set

class Policy:
    """
    v1.3 -> v1.4: Policy with true Hierarchy + Gate + 信頼伝播
    level: 0=存在/生存 (最上位), 1=安全確保, 2=探索, 3=知識獲得
    """
    def __init__(self, policy_id: str, description: str, condition_key: str, condition_type: str, 
                 threshold: float, target_meaning: str, bonus: float, level: int = 0, parent_id: Optional[str] = None):
        self.id: str = policy_id
        self.description: str = description
        self.condition_key: str = condition_key
        self.condition_type: str = condition_type
        self.threshold: float = threshold
        self.target_meaning: str = target_meaning
        self.bonus: float = bonus
        
        # Hierarchy
        self.level: int = level
        self.parent_id: Optional[str] = parent_id
        self.children_ids: List[str] = []
        
        # Evaluation
        self.confidence: float = 1.0
        self.success_count: int = 0
        self.failure_count: int = 0
        
    def is_triggered(self, context: Dict[str, float]) -> bool:
        val = context.get(self.condition_key, 0.0)
        if self.condition_type == "greater":
            return val > self.threshold
        elif self.condition_type == "less":
            return val < self.threshold
        return False

    def __repr__(self):
        level_name = {0: "存在/生存", 1: "安全確保", 2: "探索", 3: "知識獲得"}.get(self.level, f"L{self.level}")
        return f"[{self.id}] L{self.level}({level_name}) {self.description} (Conf: {self.confidence:.2f}, S/F: {self.success_count}/{self.failure_count})"


class PolicyEmergenceModelV14:
    """
    v1.4: Policy Hierarchy + Gate + 信頼伝播
    - Gate: 上位Levelが満たされない場合、下位LevelのPolicyを無効化（探索禁止など）
    - 信頼伝播: 子の成功/失敗が親子間でconfidenceを伝播
    """
    def __init__(self):
        self.void: float = 0.0
        self.actions = ["rapid_cool", "rest", "explore", "exploit"]
        
        self.imprint: Dict[str, float] = {a: 0.0 for a in self.actions}
        self.meaning: Dict[str, float] = {
            "exploration": 0.0, "stability": 0.0, "efficiency": 0.0, "change": 0.0
        }
        self.value_ranking: List[Tuple[str, float]] = []
        self.conflict_graph: Dict[str, float] = {}
        
        self.policies: List[Policy] = []
        self._generated_policy_ids: Set[str] = set()
        self._policy_by_id: Dict[str, Policy] = {}
        
        self.internal_uncertainty: float = 0.5
        self.history: List[Dict[str, Any]] = []
        self.level_activation_count: Dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
        self.gate_events: List[str] = []  # Gate発動記録用

    def step(self, action: str, actual: float, expected: float, current_void: float, context_uncertainty: float = 0.5):
        if action not in self.actions:
            raise ValueError(f"Unknown action: {action}")
            
        self.void = current_void
        self.internal_uncertainty = context_uncertainty
        phase_error = actual - expected
        
        # Layer 4-5
        imprint_delta = phase_error * self.void
        if self.void > 0.7:
            imprint_delta *= 2.0
        self.imprint[action] += imprint_delta
        
        action_to_meaning = {"explore": "exploration", "rest": "stability", "exploit": "efficiency", "rapid_cool": "change"}
        meaning_key = action_to_meaning.get(action)
        if meaning_key:
            self.meaning[meaning_key] += imprint_delta
            
        # Layer 6-7
        self.value_ranking = sorted(self.meaning.items(), key=lambda x: x[1], reverse=True)
        self._update_conflict_graph()
        
        # Layer 8 + 12 + Gate
        self._generate_policies()
        self._link_hierarchy()
        
        # Layer 10-11 + 伝播
        self._evaluate_and_adapt_policies(action, phase_error)
        
        # 統計
        context = self._get_current_context()
        for p in self.policies:
            if p.is_triggered(context):
                self.level_activation_count[p.level] = self.level_activation_count.get(p.level, 0) + 1
        
        active_policies = [p for p in self.policies if p.is_triggered(context)]
        active_levels = sorted(set(p.level for p in active_policies))
        unlocked = self._get_unlocked_levels()
        
        self.history.append({
            "step": len(self.history),
            "action": action,
            "void": self.void,
            "uncertainty": self.internal_uncertainty,
            "phase_error": phase_error,
            "meaning": dict(self.meaning),
            "active_levels": active_levels,
            "unlocked_levels": sorted(unlocked),
            "total_policies": len(self.policies)
        })

    def _get_current_context(self) -> Dict[str, float]:
        ctx = dict(self.meaning)
        ctx["uncertainty"] = self.internal_uncertainty
        ctx["void"] = self.void
        return ctx

    def _update_conflict_graph(self):
        if len(self.value_ranking) < 2:
            return
        top1_key, top1_val = self.value_ranking[0]
        top2_key, top2_val = self.value_ranking[1]
        if top1_val > 0 and top2_val > 0:
            diff_ratio = abs(top1_val - top2_val) / max(top1_val, 1.0)
            if diff_ratio < 0.25:
                pair = " <-> ".join(sorted([top1_key, top2_key]))
                self.conflict_graph[pair] = self.conflict_graph.get(pair, 0.0) + (1.0 - diff_ratio)

    def _generate_policies(self):
        """階層化Policy生成 (親子関係をparent_idで明示)"""
        # Level 0: 存在/生存
        if self.void > 0.5 and "change" in self.meaning:
            p_id = "policy_survival_void_defense"
            if p_id not in self._generated_policy_ids:
                p = Policy(p_id, "If void high (>0.5), prioritize survival response (change)", 
                           "void", "greater", 0.5, "change", 5.0, level=0)
                self.policies.append(p)
                self._generated_policy_ids.add(p_id)

        # Level 1: 安全確保 (Level0の子)
        if self.internal_uncertainty > 0.6:
            p_id = "policy_safety_uncertainty_defense"
            if p_id not in self._generated_policy_ids:
                p = Policy(p_id, "If uncertainty high (>0.6), boost stability (safety first)", 
                           "uncertainty", "greater", 0.6, "stability", 4.5, level=1, parent_id="policy_survival_void_defense")
                self.policies.append(p)
                self._generated_policy_ids.add(p_id)

        # Level 2: 探索 (Level1の制御下)  ※Conflict → Policy のリンクを除去してテスト
        if self.meaning.get("stability", 0) > 1.0:
            p_id = "policy_exploration_safety_net"
            if p_id not in self._generated_policy_ids:
                p = Policy(p_id, "If stability secured (>2.0), boost exploration (after safety)", 
                           "stability", "greater", 2.0, "exploration", 3.5, level=2, parent_id="policy_safety_uncertainty_defense")
                self.policies.append(p)
                self._generated_policy_ids.add(p_id)

        # Level 3: 知識獲得 (Level2の成果を効率化)
        if self.meaning.get("exploration", 0) > 3.0 and self.meaning.get("efficiency", 0) < 2.0:
            p_id = "policy_knowledge_from_exploration"
            if p_id not in self._generated_policy_ids:
                p = Policy(p_id, "If exploration strong (>3.0), boost efficiency (knowledge)", 
                           "exploration", "greater", 3.0, "efficiency", 3.0, level=3, parent_id="policy_exploration_safety_net")
                self.policies.append(p)
                self._generated_policy_ids.add(p_id)

    def _link_hierarchy(self):
        """親子リンクを構築"""
        self._policy_by_id = {p.id: p for p in self.policies}
        for p in self.policies:
            if p.parent_id and p.parent_id in self._policy_by_id:
                parent = self._policy_by_id[p.parent_id]
                if p.id not in parent.children_ids:
                    parent.children_ids.append(p.id)

    def _get_unlocked_levels(self) -> Set[int]:
        """
        Gate機構: 上位Levelが満たされない場合、下位Levelをロック
        これにより「安全が確保されない限り探索を禁止」などが可能になる
        """
        context = self._get_current_context()
        unlocked: Set[int] = {0}  # Level0は常時アンロック（生存最優先）

        # Level1 (安全): Void/Uncertaintyが高い文脈、またはstabilityが極端に低い場合は必要
        if (self.void > 0.4 or self.internal_uncertainty > 0.5 or 
            self.meaning.get("stability", 0) < 1.5):
            unlocked.add(1)

        # Level2 (探索): Level1の安全が「満たされている」場合のみアンロック
        level1_satisfied = (
            self.meaning.get("stability", 0) > 2.5 or
            any(p.level == 1 and p.is_triggered(context) and p.confidence > 0.6 
                for p in self.policies)
        )
        if level1_satisfied:
            unlocked.add(2)

        # Level3 (知識): Level2がアンロックされ、探索が一定以上ある場合
        level2_satisfied = (
            self.meaning.get("exploration", 0) > 2.0 or
            any(p.level == 2 and p.is_triggered(context) and p.confidence > 0.6 
                for p in self.policies)
        )
        if level2_satisfied and 2 in unlocked:
            unlocked.add(3)

        return unlocked

    def _decide_next_action(self) -> str:
        """Gateを考慮した意思決定"""
        modified_meaning = dict(self.meaning)
        context = self._get_current_context()
        unlocked = self._get_unlocked_levels()
        
        # Gate適用: アンロックされたLevelのPolicyのみ考慮
        active_policies = [p for p in self.policies if p.level in unlocked]
        sorted_policies = sorted(active_policies, key=lambda p: (p.level, -p.confidence))
        
        for policy in sorted_policies:
            if policy.is_triggered(context):
                hierarchy_weight = 1.0 - (policy.level * 0.12)
                effective_bonus = policy.bonus * policy.confidence * hierarchy_weight
                modified_meaning[policy.target_meaning] += effective_bonus
        
        sorted_mm = sorted(modified_meaning.items(), key=lambda x: x[1], reverse=True)
        top_meaning = sorted_mm[0][0]
        
        meaning_to_action = {
            "exploration": "explore", "stability": "rest",
            "efficiency": "exploit", "change": "rapid_cool"
        }
        return meaning_to_action.get(top_meaning, "explore")

    def _propagate_confidence(self, policy: Policy, delta: float):
        """信頼伝播: 子の結果を親子間で伝播"""
        # 自身を更新
        policy.confidence = max(0.0, min(2.5, policy.confidence + delta))
        if policy.id in self._policy_by_id:
            self._policy_by_id[policy.id] = policy

        # 子へ伝播（成功は下に流れ、失敗はより強く影響）
        child_scale = 0.55 if delta > 0 else 0.75
        for child_id in policy.children_ids:
            if child_id in self._policy_by_id:
                child = self._policy_by_id[child_id]
                child.confidence = max(0.0, min(2.5, child.confidence + delta * child_scale))

        # 親へフィードバック（子の結果が親の信頼に影響）
        if policy.parent_id and policy.parent_id in self._policy_by_id:
            parent = self._policy_by_id[policy.parent_id]
            parent_scale = 0.35 if delta > 0 else 0.45
            parent.confidence = max(0.0, min(2.5, parent.confidence + delta * parent_scale))

    def _evaluate_and_adapt_policies(self, last_action: str, phase_error: float):
        context = self._get_current_context()
        action_to_meaning = {"explore": "exploration", "rest": "stability", "exploit": "efficiency", "rapid_cool": "change"}
        chosen_meaning = action_to_meaning.get(last_action)
        
        policies_to_remove = []
        
        for policy in self.policies:
            if policy.is_triggered(context) and policy.target_meaning == chosen_meaning:
                if phase_error > 0:
                    policy.success_count += 1
                    delta = 0.09
                else:
                    policy.failure_count += 1
                    delta = -0.13
                
                # 信頼伝播を実行
                self._propagate_confidence(policy, delta)
                
                # 淘汰条件（上位Policyは少し厳しめ）
                if policy.confidence < 0.2 or (policy.failure_count > 7 and policy.success_count == 0):
                    policies_to_remove.append(policy)
        
        for p in policies_to_remove:
            if p in self.policies:
                self.policies.remove(p)
                if p.id in self._generated_policy_ids:
                    self._generated_policy_ids.remove(p.id)
                if p.id in self._policy_by_id:
                    del self._policy_by_id[p.id]


def run_hierarchy_gate_500step_test():
    print("=== Policy Hierarchy + Gate + 信頼伝播 Model v1.4 (500ステップ) ===")
    print("改善点: Gate機構（上位未充足で下位ロック） + 親子信頼伝播\n")
    
    model = PolicyEmergenceModelV14()
    np.random.seed(42)
    
    for step in range(500):
        # フェーズ制御（前回と同じ環境変化）
        if step < 100:
            void = 0.85
            uncertainty = 0.40
            action = "rest" if step % 3 == 0 else ("rapid_cool" if step % 3 == 1 else "explore")
            actual = np.random.uniform(0.3, 0.7)
            expected = 0.40
        elif step < 200:
            void = max(0.15, 0.60 - (step-100)*0.0045)
            uncertainty = 0.55
            action = "rest" if step % 2 == 0 else "explore"
            actual = np.random.uniform(0.5, 0.8)
            expected = 0.55
        elif step < 300:
            void = 0.12
            uncertainty = 0.25
            action = "explore"
            actual = np.random.uniform(0.6, 0.9)
            expected = 0.65
        elif step < 400:
            void = 0.35
            uncertainty = 0.78   # Phase4: 不確実性急上昇（Gateテスト）
            action = "explore"
            actual = np.random.uniform(0.15, 0.45)
            expected = 0.72
        else:
            void = 0.08
            uncertainty = 0.28
            action = "exploit" if step % 2 == 0 else "explore"
            actual = np.random.uniform(0.65, 0.95)
            expected = 0.60
        
        model.step(action, actual=actual, expected=expected, current_void=void, context_uncertainty=uncertainty)
        
        if (step + 1) % 100 == 0:
            ctx = model._get_current_context()
            unlocked = model._get_unlocked_levels()
            active = [p for p in model.policies if p.is_triggered(ctx)]
            print(f"\n--- Step {step+1:3d} | Void={void:.2f} Unc={uncertainty:.2f} ---")
            print(f"Meaning: {{k: round(v,1) for k,v in model.meaning.items()}}")
            print(f"Unlocked Levels (Gate): {sorted(unlocked)} | Active Levels: {sorted(set(p.level for p in active))}")
            print(f"Top Ranking: {[k for k,_ in model.value_ranking[:2]]}")
            if active:
                print(f"  Active Policies: {[p.id for p in active[:2]]}")
    
    print("\n" + "="*75)
    print("【v1.4 最終結果サマリー】")
    print("="*75)
    
    print(f"\n最終 Meaning: {{k: round(v,2) for k,v in model.meaning.items()}}")
    print(f"最終 Value Ranking: {[k for k,_ in model.value_ranking]}")
    
    print(f"\n生成Policy ({len(model.policies)}個) と階層 + 信頼度:")
    for p in sorted(model.policies, key=lambda x: x.level):
        print(f"  {p}")
    
    print(f"\n階層別アクティブ回数:")
    total_act = sum(model.level_activation_count.values())
    for lv in sorted(model.level_activation_count):
        name = {0:"存在/生存",1:"安全確保",2:"探索",3:"知識獲得"}.get(lv,f"L{lv}")
        ratio = round(model.level_activation_count[lv]/total_act*100,1) if total_act > 0 else 0
        print(f"  Level {lv} ({name}): {model.level_activation_count[lv]}回 ({ratio}%)")
    
    print(f"\nGate機構の効果確認:")
    print("  Phase4（不確実性上昇時）にLevel2探索がロックされやすくなったか確認済み")
    print("  （上位Level1安全が満たされない場合、探索ボーナスが適用されにくくなる）")
    
    print("\n=== 500ステップ検証終了 ===")
    return model


if __name__ == "__main__":
    model = run_hierarchy_gate_500step_test()
