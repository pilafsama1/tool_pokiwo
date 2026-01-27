import sys
sys.path.insert(0, r"d:\slim\Tool game\toolautopokiwo\game-bot")

try:
    print("Importing logic...")
    from logic import MatchThreeLogic
    print("OK")
    
    print("Importing evaluator...")
    from evaluator import MoveEvaluator
    print("OK")
    
    print("Testing cascade simulation...")
    logic = MatchThreeLogic(8, 8)
    
    # Test simulate_gravity
    board = [["RED"] * 8 for _ in range(8)]
    board[4][3] = "EMPTY"
    
    from logic import Position
    removed = {Position(4, 3)}
    new_board = logic.simulate_gravity(board, removed)
    print(f"Gravity test: {new_board[4][3]}")
    
    print("\nAll tests passed!")
    
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
