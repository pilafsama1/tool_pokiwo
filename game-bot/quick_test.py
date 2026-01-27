"""
Quick test to verify bot components are working
"""

print("="*60)
print("TESTING BOT COMPONENTS")
print("="*60)

# Test 1: Config loading
print("\n1. Testing config...")
try:
    import yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"   ✓ Config loaded")
    print(f"   - cascade_simulation: {config.get('calculation', {}).get('use_cascade_simulation')}")
    print(f"   - max_time: {config.get('calculation', {}).get('max_calculation_time')}")
    print(f"   - game_automation: {config.get('game_automation', {}).get('enabled')}")
except Exception as e:
    print(f"   ✗ Config error: {e}")
    exit(1)

# Test 2: Imports
print("\n2. Testing imports...")
try:
    from logic import MatchThreeLogic
    from evaluator import MoveEvaluator
    from capture import ScreenCapture
    from board_reader_color import BoardReaderColor
    from controller import MouseController
    from game_state_manager import GameStateManager, GameState
    print("   ✓ All imports OK")
except Exception as e:
    print(f"   ✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Component creation
print("\n3. Testing component creation...")
try:
    logic = MatchThreeLogic(8, 8)
    evaluator = MoveEvaluator(config['scoring'])
    print("   ✓ Logic and evaluator created")
except Exception as e:
    print(f"   ✗ Component error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Cascade simulation
print("\n4. Testing cascade simulation...")
try:
    test_board = [["RED"] * 8 for _ in range(8)]
    test_board[0] = ["RED", "RED", "RED", "BLUE", "GREEN", "YELLOW", "RED", "BLUE"]
    
    moves = logic.find_valid_moves(test_board)
    if moves:
        test_move = moves[0]
        board_copy = [row[:] for row in test_board]
        logic.swap_gems(board_copy, test_move.from_pos, test_move.to_pos)
        result = logic.simulate_cascade(board_copy, test_move.matches)
        print(f"   ✓ Cascade simulation works")
        print(f"   - Depth: {result['cascade_depth']}")
        print(f"   - Gems: {result['total_gems_removed']}")
    else:
        print("   ⚠ No moves found (board might be stable)")
except Exception as e:
    print(f"   ✗ Cascade error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Scoring with cascade
print("\n5. Testing scoring...")
try:
    if moves:
        score1 = evaluator.score_move(moves[0], test_board, logic, use_cascade_simulation=False)
        score2 = evaluator.score_move(moves[0], test_board, logic, use_cascade_simulation=True)
        print(f"   ✓ Scoring works")
        print(f"   - Without cascade: {score1}")
        print(f"   - With cascade: {score2}")
        print(f"   - Difference: {score2 - score1}")
except Exception as e:
    print(f"   ✗ Scoring error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 6: Get best move
print("\n6. Testing get_best_move...")
try:
    if moves:
        import time
        start = time.time()
        best_move, best_score = evaluator.get_best_move(moves, test_board, logic, max_time=0.5)
        elapsed = time.time() - start
        print(f"   ✓ get_best_move works")
        print(f"   - Time: {elapsed:.3f}s")
        print(f"   - Score: {best_score}")
        print(f"   - Within time limit: {elapsed <= 0.6}")  # Allow 0.1s buffer
except Exception as e:
    print(f"   ✗ get_best_move error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nBot should work correctly now.")
print("\nIf bot still stops, check:")
print("1. Game window coordinates are correct")
print("2. Board is being read correctly (color detection)")
print("3. No errors in console when running")
print("4. Game automation state detection")
