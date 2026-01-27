"""
Debug script to check if cascade simulation is working
"""

import sys
import traceback

try:
    print("Testing imports...")
    from logic import MatchThreeLogic, Position
    from evaluator import MoveEvaluator
    print("✓ Imports OK")
    
    print("\nTesting cascade simulation...")
    logic = MatchThreeLogic(8, 8)
    
    # Simple test board
    board = [
        ["RED", "RED", "RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE"],
        ["BLUE", "GREEN", "YELLOW", "RED", "BLUE", "GREEN", "YELLOW", "RED"],
        ["GREEN", "YELLOW", "RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE"],
        ["YELLOW", "RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE", "GREEN"],
        ["RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE", "GREEN", "YELLOW"],
        ["BLUE", "GREEN", "YELLOW", "RED", "BLUE", "GREEN", "YELLOW", "RED"],
        ["GREEN", "YELLOW", "RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE"],
        ["YELLOW", "RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE", "GREEN"],
    ]
    
    print("✓ Board created")
    
    # Find moves
    print("\nFinding moves...")
    moves = logic.find_valid_moves(board)
    print(f"✓ Found {len(moves)} moves")
    
    if not moves:
        print("✗ No moves found - this might be the problem!")
        sys.exit(1)
    
    # Test cascade simulation
    print("\nTesting cascade simulation on first move...")
    test_move = moves[0]
    board_copy = [row[:] for row in board]
    logic.swap_gems(board_copy, test_move.from_pos, test_move.to_pos)
    
    cascade_result = logic.simulate_cascade(board_copy, test_move.matches)
    print(f"✓ Cascade simulation OK")
    print(f"  Depth: {cascade_result['cascade_depth']}")
    print(f"  Gems removed: {cascade_result['total_gems_removed']}")
    
    # Test evaluator
    print("\nTesting evaluator...")
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
            "RED": 70,
            "BLUE": 80,
            "GREEN": 60,
            "YELLOW": 100,
        }
    }
    evaluator = MoveEvaluator(scoring_rules)
    print("✓ Evaluator created")
    
    # Test scoring without cascade
    print("\nTesting scoring WITHOUT cascade simulation...")
    score1 = evaluator.score_move(test_move, board, logic, use_cascade_simulation=False)
    print(f"✓ Score (no cascade): {score1}")
    
    # Test scoring with cascade
    print("\nTesting scoring WITH cascade simulation...")
    score2 = evaluator.score_move(test_move, board, logic, use_cascade_simulation=True)
    print(f"✓ Score (with cascade): {score2}")
    
    # Test get_best_move with time limit
    print("\nTesting get_best_move with time limit...")
    best_move, best_score = evaluator.get_best_move(moves, board, logic, max_time=0.5)
    print(f"✓ Best move found with score: {best_score}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nIf bot is stopping, the problem is elsewhere.")
    print("Check:")
    print("1. Is game_automation enabled? Check state_manager")
    print("2. Is board being read correctly?")
    print("3. Any errors in console when bot runs?")
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ ERROR FOUND!")
    print("="*60)
    print(f"\nError: {e}")
    print("\nTraceback:")
    traceback.print_exc()
    print("\n" + "="*60)
    print("This is likely why the bot stops!")
    sys.exit(1)
