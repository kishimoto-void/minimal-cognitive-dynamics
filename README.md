1. プロジェクトの目的

This project investigates how minimal cognitive dynamics (Void → Imprint → Meaning → Gate → Action)
can produce:

- Policy formation
- Behavioral fixation
- Oscillatory cognition (stability vs exploration trade-off)
2. コア構造

Core loop:

Void → Phase Error → Imprint → Meaning → Gate → Action
そして重要な補足：

No explicit reward model.
No external optimizer.
Behavior emerges from internal state dynamics.

3. 発見①：固定化現象（STANDARD Gate）
4. Finding 1: Confidence-driven collapse

When Gate Confidence increases monotonically:

- Exploration decreases
- Entropy decreases
- Imprint increases (behavioral fixation)

Result:
→ System converges to a single dominant action
4. 発見②：SELF-DESTRUCTメカニズム
Finding 2: Self-destructive confidence restores exploration

When high confidence induces anomaly behavior:

- Exploration increases
- Entropy increases
- Imprint decreases

Result:
→ System enters oscillatory regime instead of collapse
5. 最重要発見

Key Insight:

Confidence is not a measure of belief strength,
but a control parameter that determines system phase:

- High confidence + strict gate → fixed-point attractor
- High confidence + self-disruption → limit-cycle oscillation
6. 振動の本質
Oscillation emerges when:

positive_feedback ≈ negative_feedback (slightly asymmetric)

This produces:

- stable entropy
- persistent exploration
- non-collapsing policy dynamics
7. 実験結果
Results (5 seeds, 600 turns):

STANDARD:
- Exploration: 5.5%
- Entropy: 1.66
- Behavior: collapse to single action

SELF-DESTRUCT:
- Exploration: 10.8%
- Entropy: 1.81
- Behavior: oscillatory regime
8. 解釈
Interpretation:

The system exhibits two phases:

1. Cognitive Closure (fixed policy)
2. Cognitive Oscillation (adaptive exploration)

Transition is controlled by Gate dynamics, not reward.
9. 限界

Limitations:

- Single-agent system
- No external environment feedback diversity
- Simplified Gate mechanism
- No long-term memory decay model
10. 次のステップ
Future work:

- Energy-minimal oscillation point analysis
- Dynamic confidence attractor model
- Hierarchical Gate phase coupling
- Multi-agent interaction system

- python simulate_cognition.py
