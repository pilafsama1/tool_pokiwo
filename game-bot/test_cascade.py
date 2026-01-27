"""
Test cascade simulation improvements
"""

from logic import MatchThreeLogic, Position, Move, Match, Direction
from evaluator import MoveEvaluator

# Test board with potential cascades
test_board = [
    ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
    ["BLUE", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE", "RED"],
    ["GREEN", "GREEN", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE"],
    ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
    ["BLUE", "RED", "RED", "RED", "RED", "GREEN", "BLUE", "RED"],  # Match-5!
    ["GREEN", "GREEN", "BLUE", "GREEN", "RED", "RED", "GREEN", "BLUE"],
    ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
    ["BLUE", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE", "RED"],
]

print("="*60)
print("TESTING CASCADE SIMULATION IMPROVEMENTS")
print("="*60)

# Initialize
logic = MatchThreeLogic(rows=8, cols=8)
scoring_rules = {
    "gem_removed": 10,
    "combo_bonus": 30,
    "combo_multiplier": 1.5,
    "match_4": 100,
    "match_5": 300,
    "cascade_chain_bonus": 80,
    "cascade_gem_bonus": 25,
    "cascade_match_bonus": 60,
    "scarcity_multiplier": 50,
    "gem_priority": {
        "YELLOW": 100,
        "BLUE": 80,
        "RED": 70,
        "GREEN": 60,
    }
}
evaluator = MoveEvaluator(scoring_rules)

# Find moves
print("\n1. Finding valid moves...")
moves = logic.find_valid_moves(test_board)
print(f"   Found {len(moves)} valid moves")

# Test cascade simulation on a specific move
if moves:
    print("\n2. Testing cascade simulation...")
    test_move = moves[0]
    
    # Create board after move
    board_copy = [row[:] for row in test_board]
    logic.swap_gems(board_copy, test_move.from_pos, test_move.to_pos)
    
    # Simulate cascade
    cascade_result = logic.simulate_cascade(board_copy, test_move.matches)
    
    print(f"   Cascade depth: {cascade_result['cascade_depth']}")
    print(f"   Total gems removed: {cascade_result['total_gems_removed']}")
    print(f"   Total matches: {cascade_result['total_matches']}")

# Test beam search evaluation
print("\n3. Testing beam search evaluation...")
print("   Quick mode (0.1s)...")
import time
start = time.time()
scored_quick = evaluator.evaluate_moves(moves[:50] if len(moves) > 50 else moves, 
                                       test_board, logic, 
                                       use_beam_search=True, 
                                       max_time=0.1)
time_quick = time.time() - start
print(f"   Time: {time_quick:.3f}s, Evaluated: {len(scored_quick)} moves")

print("\n   Deep mode (0.5s)...")
start = time.time()
scored_deep = evaluator.evaluate_moves(moves[:50] if len(moves) > 50 else moves, 
                                      test_board, logic, 
                                      use_beam_search=True, 
                                      max_time=0.5)
time_deep = time.time() - start
print(f"   Time: {time_deep:.3f}s, Evaluated: {len(scored_deep)} moves")

# Get best move with new system
print("\n4. Getting best move with cascade simulation...")
start = time.time()
best_move, best_score = evaluator.get_best_move(moves, test_board, logic, max_time=0.5)
eval_time = time.time() - start

print(f"   Evaluation time: {eval_time:.3f}s")
print(f"   Best move score: {best_score}")
print(f"   From: {best_move.from_pos} -> To: {best_move.to_pos}")
print(f"   Immediate matches: {len(best_move.matches)}")

# Show detailed breakdown
print("\n5. Score breakdown:")
breakdown = evaluator.explain_score(best_move, test_board, logic, show_cascade=True)
for key, value in breakdown.items():
    if isinstance(value, (int, float)) and value > 0:
        print(f"   {key:20s}: {value}")

print("\n" + "="*60)
print("COMPARISON WITH OLD SYSTEM")
print("="*60)

# Compare with old simple cascade
print("\nOld scoring (no simulation):")
old_score = evaluator.score_move(best_move, test_board, logic, use_cascade_simulation=False)
print(f"   Score: {old_score}")

print("\nNew scoring (with simulation):")
new_score = evaluator.score_move(best_move, test_board, logic, use_cascade_simulation=True)
print(f"   Score: {new_score}")
print(f"   Improvement: {new_score - old_score} points ({((new_score - old_score) / max(old_score, 1) * 100):.1f}%)")

print("\n" + "="*60)
print("TEST COMPLETED!")
print("="*60)
