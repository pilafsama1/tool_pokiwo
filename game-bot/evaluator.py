"""
Move Evaluator Module
Scores and ranks possible moves based on various criteria
"""

from typing import List, Dict
from logic import Move, Match, Position, MatchThreeLogic


class MoveEvaluator:
    """Evaluates and scores moves"""
    
    def __init__(self, scoring_rules: Dict[str, int]):
        """
        Initialize move evaluator
        
        Args:
            scoring_rules: Dictionary of scoring rules
                - gem_removed: points per gem removed
                - unlock_tile: bonus for unlocking locked tiles
                - combo_bonus: bonus for combos (multiple matches)
                - special_gem: bonus for creating special gems
                - match_4: bonus for 4-gem matches
                - match_5: bonus for 5+ gem matches
                - gem_priority: priority scores for each gem type
        """
        self.rules = scoring_rules
        self.gem_priority = scoring_rules.get('gem_priority', {})
    
    def get_gem_points(self, gem_type: str) -> int:
        """
        Lấy điểm số của từng loại gem
        
        Args:
            gem_type: Loại gem (YELLOW_STAR, GREEN, RED, BLUE, etc.)
            
        Returns:
            Điểm số của gem đó
        """
        gem_points = {
            "YELLOW_STAR": 70,  # Gem vàng: 70 điểm (ưu tiên rất cao)
            "GREEN": 15,         # Gem xanh lá: 15 điểm
            "RED": 14,           # Gem đỏ: 14 điểm
            "BLUE": 13,          # Gem xanh dương: 13 điểm
        }
        return gem_points.get(gem_type, 10)  # Các gem khác: 10 điểm
    
    def _simulate_cascade_multiple_runs(self, move: Move, board: List[List[str]], 
                                       logic: MatchThreeLogic, num_simulations: int = 5,
                                       max_depth: int = 15) -> int:
        """
        Mô phỏng cascade nhiều lần với random spawn để tính điểm chính xác
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            num_simulations: Số lần chạy simulation (càng nhiều càng chính xác)
            max_depth: Số cấp cascade tối đa
            
        Returns:
            Điểm cascade trung bình từ tất cả các lần chạy
        """
        total_score = 0
        
        for sim_run in range(num_simulations):
            # Tạo bản sao board cho mỗi lần chạy
            board_copy = [row[:] for row in board]
            logic.swap_gems(board_copy, move.from_pos, move.to_pos)
            
            # Mô phỏng cascade với random spawn
            cascade_result = logic.simulate_cascade(
                board_copy, 
                move.matches, 
                max_iterations=max_depth,
                spawn_gems=True  # Bật random spawn
            )
            
            # Tính điểm từ cascade (bỏ chain đầu tiên)
            cascade_chains = cascade_result.get('cascade_chains', [])
            run_score = 0
            
            for chain_index in range(1, len(cascade_chains)):
                matches_in_chain = cascade_chains[chain_index]
                
                for match in matches_in_chain:
                    gem_type = match.gem_type
                    gem_count = len(match.positions)
                    
                    # Tính điểm theo loại gem
                    gem_point = self.get_gem_points(gem_type)
                    run_score += gem_count * gem_point
            
            total_score += run_score
        
        # Trả về điểm trung bình
        return total_score // num_simulations if num_simulations > 0 else 0
    
    def score_move(self, move: Move, board: List[List[str]], 
                   logic: MatchThreeLogic, use_cascade_simulation: bool = True) -> int:
        """
        Calculate score based on gems collected with cascade simulation
        - Normal gems: 10 points each
        - Yellow gems (YELLOW_STAR): 25 points each
        - Cascade combo: additional gems from chain reactions
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            use_cascade_simulation: If True, simulate cascade for accurate scoring
            
        Returns:
            Score for the move (total gems collected × points)
        """
        score = 0
        
        # ================================================================
        # BƯỚC 1: Tính điểm từ gems ăn được ngay lập tức (immediate match)
        # ================================================================
        for match in move.matches:
            for pos in match.positions:
                gem_type = board[pos.row][pos.col]
                
                # Tính điểm theo loại gem: YELLOW_STAR=35, GREEN=15, RED=14, BLUE=13, khác=10
                score += self.get_gem_points(gem_type)
        
        # ================================================================
        # BƯỚC 2: Mô phỏng cascade để tính điểm combo
        # ================================================================
        if use_cascade_simulation:
            cascade_result = self._calculate_cascade_gems_collected(move, board, logic)
            score += cascade_result
        
        return score
    
    def _calculate_unlock_bonus(self, move: Move, board: List[List[str]]) -> int:
        """
        Calculate bonus for unlocking tiles
        
        Args:
            move: Move to evaluate
            board: Current board state
            
        Returns:
            Number of locked tiles that would be unlocked
        """
        unlocked = 0
        affected_positions = set()
        
        for match in move.matches:
            affected_positions.update(match.positions)
        
        # Check if any affected positions are locked or adjacent to locked tiles
        for pos in affected_positions:
            # Check neighbors for locked tiles
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pos.row + dr, pos.col + dc
                if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                    if board[nr][nc] == "LOCKED":
                        unlocked += 1
        
        return unlocked
    
    def _calculate_position_bonus(self, move: Move, logic: MatchThreeLogic) -> int:
        """
        Calculate bonus based on move position (prefer center)
        
        Args:
            move: Move to evaluate
            logic: MatchThreeLogic instance
            
        Returns:
            Position bonus score
        """
        # Calculate distance from center
        center_row = logic.rows / 2
        center_col = logic.cols / 2
        
        # Average position of affected gems
        total_dist = 0
        count = 0
        
        for match in move.matches:
            for pos in match.positions:
                dist = abs(pos.row - center_row) + abs(pos.col - center_col)
                total_dist += dist
                count += 1
        
        if count == 0:
            return 0
        
        avg_dist = total_dist / count
        max_dist = logic.rows + logic.cols
        
        # Convert to bonus (closer to center = higher bonus)
        bonus = int((1 - (avg_dist / max_dist)) * 10)
        return max(0, bonus)
    
    def _calculate_chain_potential(self, move: Move, board: List[List[str]], 
                                   logic: MatchThreeLogic) -> int:
        """
        Estimate potential for chain reactions
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            
        Returns:
            Chain potential bonus
        """
        # Simple heuristic: count gems of the same type near the match
        chain_potential = 0
        affected_positions = set()
        
        for match in move.matches:
            affected_positions.update(match.positions)
            gem_type = match.gem_type
            
            # Check area around the match for same gems
            for pos in match.positions:
                for dr in [-2, -1, 0, 1, 2]:
                    for dc in [-2, -1, 0, 1, 2]:
                        if dr == 0 and dc == 0:
                            continue
                        
                        nr, nc = pos.row + dr, pos.col + dc
                        check_pos = Position(nr, nc)
                        
                        if (logic.is_valid_position(check_pos) and 
                            check_pos not in affected_positions):
                            if board[nr][nc] == gem_type:
                                chain_potential += 1
        
        return min(chain_potential, 20)  # Cap at 20
    
    def _calculate_cascade_bonus_simple(self, move: Move, board: List[List[str]]) -> int:
        """
        Simple CASCADE STRATEGY: Prefer moves at bottom rows (gravity creates chain reactions)
        Moves at the bottom are more likely to cause gems to fall and create new matches
        
        Args:
            move: Move to evaluate
            board: Current board state
            
        Returns:
            Cascade bonus (higher for bottom rows)
        """
        total_row = 0
        count = 0
        
        for match in move.matches:
            for pos in match.positions:
                total_row += pos.row
                count += 1
        
        if count == 0:
            return 0
        
        avg_row = total_row / count
        board_height = len(board)
        
        # Bottom rows get higher bonus (row 7 gets 50 points, row 0 gets 0)
        cascade_bonus = int((avg_row / board_height) * 50)
        
        return cascade_bonus
    
    
    def _calculate_cascade_gems_collected(self, move: Move, board: List[List[str]], 
                                         logic: MatchThreeLogic) -> int:
        """
        Mô phỏng cascade và tính điểm từ tất cả gems ăn được trong chuỗi phản ứng
        DEPRECATED: Dùng _simulate_cascade_multiple_runs để chính xác hơn
        
        Hàm này giữ lại để tương thích với code cũ (score_move với use_cascade_simulation)
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            
        Returns:
            Total points from cascade gems (không tính gems ban đầu)
        """
        # Dùng hàm mới với 1 lần simulation (nhanh hơn)
        return self._simulate_cascade_multiple_runs(move, board, logic, num_simulations=1, max_depth=10)
    
    def _calculate_dynamic_priority_bonus(self, move: Move, board: List[List[str]], 
                                         logic) -> int:
        """
        Dynamic gem priority based on board scarcity
        Rare gems get higher priority (removing rare gems creates more chaos)
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            
        Returns:
            Dynamic priority bonus
        """
        # Get board distribution
        distribution = logic.get_board_gem_distribution(board)
        total_gems = sum(distribution.values())
        
        if total_gems == 0:
            return 0
        
        priority_bonus = 0
        
        # Calculate scarcity bonus for each gem in matches
        for match in move.matches:
            gem_type = match.gem_type
            gem_count = distribution.get(gem_type, 0)
            
            # Scarcity ratio: fewer gems = higher bonus
            scarcity_ratio = 1.0 - (gem_count / total_gems)
            
            # Base priority from config
            base_priority = self.gem_priority.get(gem_type, 0)
            
            # Dynamic bonus: combine base priority with scarcity
            dynamic_value = base_priority + (scarcity_ratio * self.rules.get("scarcity_multiplier", 50))
            
            # Add bonus for each gem in the match
            priority_bonus += int(dynamic_value * len(match.positions))
        
        return priority_bonus
    
    def _calculate_setup_bonus(self, move: Move, board: List[List[str]], 
                               logic: MatchThreeLogic) -> int:
        """
        SETUP STRATEGY: Bonus for moves that create potential for special gems
        Check if move creates a board state with 3 gems in a row (ready for match-4)
        or 4 gems in a row (ready for match-5)
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            
        Returns:
            Setup bonus for potential special gems
        """
        setup_bonus = 0
        
        # Simulate board after this move (simplified)
        # Count how many "almost matches" (2 gems in a row) exist near the move
        affected_positions = set()
        for match in move.matches:
            affected_positions.update(match.positions)
        
        # Check surrounding area for potential setups
        for pos in affected_positions:
            # Check horizontal and vertical lines
            for direction in [(0, 1), (1, 0)]:  # right, down
                dr, dc = direction
                
                # Count consecutive empty or movable positions
                consecutive = 0
                for i in range(1, 4):
                    nr, nc = pos.row + (dr * i), pos.col + (dc * i)
                    check_pos = Position(nr, nc)
                    
                    if not logic.is_valid_position(check_pos):
                        break
                    
                    # Check if position will be empty after move or has matching gem
                    if check_pos in affected_positions:
                        consecutive += 1
                    elif board[nr][nc] not in ["LOCKED", "EMPTY"]:
                        consecutive += 1
                    else:
                        break
                
                # Bonus for creating potential match-4 or match-5 setups
                if consecutive >= 2:
                    setup_bonus += 15
                if consecutive >= 3:
                    setup_bonus += 30
        
        return min(setup_bonus, 60)  # Cap at 60
    
    def _calculate_edge_bonus(self, move: Move) -> int:
        """
        CORNER/EDGE STRATEGY: Prefer corners and edges
        Edge moves tend to be more stable and create predictable cascades
        
        Args:
            move: Move to evaluate
            
        Returns:
            Edge bonus (higher for corners and edges)
        """
        edge_bonus = 0
        corner_count = 0
        edge_count = 0
        
        board_size = 8  # 8x8 board
        
        for match in move.matches:
            for pos in match.positions:
                # Check if corner
                if (pos.row == 0 or pos.row == board_size - 1) and \
                   (pos.col == 0 or pos.col == board_size - 1):
                    corner_count += 1
                # Check if edge
                elif pos.row == 0 or pos.row == board_size - 1 or \
                     pos.col == 0 or pos.col == board_size - 1:
                    edge_count += 1
        
        # Corners get more bonus than regular edges
        edge_bonus = (corner_count * 20) + (edge_count * 10)
        
        return min(edge_bonus, 40)  # Cap at 40
    
    def evaluate_moves(self, moves: List[Move], board: List[List[str]], 
                      logic: MatchThreeLogic, use_beam_search: bool = True,
                      max_time: float = 3.0) -> List[tuple]:
        """
        Evaluate và rank moves với multi-stage filtering (3 pha)
        Tối ưu cho độ chính xác cao với thời gian < 3s
        
        Args:
            moves: List of possible moves
            board: Current board state
            logic: MatchThreeLogic instance
            use_beam_search: Use multi-stage filtering
            max_time: Maximum time in seconds (default 3.0s)
            
        Returns:
            List of (move, score) tuples, sorted by score (descending)
        """
        import time as time_module
        start_time = time_module.time()
        
        if not moves:
            return []
        
        # Nếu số moves ít, đánh giá trực tiếp với cascade đầy đủ
        if len(moves) <= 15:
            if self.rules.get('verbose', False):
                print(f"📊 Ít moves ({len(moves)}), eval trực tiếp với cascade đầy đủ...")
            
            scored_moves = []
            for move in moves:
                if time_module.time() - start_time > max_time:
                    break
                # Cascade với 7 lần simulation (tối ưu tốc độ)
                score = self._evaluate_move_with_accurate_cascade(move, board, logic, num_sims=7)
                scored_moves.append((move, score))
            
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            elapsed = time_module.time() - start_time
            if self.rules.get('verbose', False):
                print(f"✓ Hoàn thành trong {elapsed:.2f}s")
            return scored_moves
        
        # ============================================================
        # MULTI-STAGE FILTERING cho nhiều moves
        # ============================================================
        
        # PHASE 1: Quick Filter - Loại bỏ moves rõ ràng tệ
        # Chỉ tính immediate score + bonus gems vàng
        # ============================================================
        phase1_start = time_module.time()
        quick_scores = []
        
        for move in moves:
            score = 0
            yellow_count = 0
            
            # Tính điểm immediate
            for match in move.matches:
                for pos in match.positions:
                    gem_type = board[pos.row][pos.col]
                    score += self.get_gem_points(gem_type)
                    
                    if gem_type == "YELLOW_STAR":
                        yellow_count += 1
            
            # Bonus đặc biệt cho gems vàng (ưu tiên cao)
            score += yellow_count * 20  # Thêm 20 điểm/gem vàng
            
            quick_scores.append((move, score))
        
        quick_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Lấy top 50 moves (hoặc 50%)
        phase1_width = min(max(int(len(moves) * 0.5), 30), 50)
        phase1_candidates = quick_scores[:phase1_width]
        
        phase1_time = time_module.time() - phase1_start
        if self.rules.get('verbose', False):
            print(f"✓ Phase 1: {len(moves)} → {len(phase1_candidates)} moves ({phase1_time:.2f}s)")
        
        # ============================================================
        # PHASE 2: Medium Eval - Cascade với 5 lần simulation
        # ============================================================
        phase2_start = time_module.time()
        medium_scores = []
        
        for move, _ in phase1_candidates:
            if time_module.time() - start_time > max_time * 0.7:  # 70% thời gian
                break
            
            # Cascade với 3 lần simulation (tối ưu tốc độ)
            score = self._evaluate_move_with_accurate_cascade(move, board, logic, num_sims=3)
            medium_scores.append((move, score))
        
        medium_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Lấy top 20 moves
        phase2_width = min(20, len(medium_scores))
        phase2_candidates = medium_scores[:phase2_width]
        
        phase2_time = time_module.time() - phase2_start
        if self.rules.get('verbose', False):
            print(f"✓ Phase 2: {len(phase1_candidates)} → {len(phase2_candidates)} moves ({phase2_time:.2f}s)")
        
        # ============================================================
        # PHASE 3: Deep Eval - Cascade với 10 lần simulation
        # ============================================================
        phase3_start = time_module.time()
        deep_scores = []
        
        for move, _ in phase2_candidates:
            if time_module.time() - start_time > max_time:
                break
            
            # Cascade với 7 lần simulation (chính xác & nhanh)
            score = self._evaluate_move_with_accurate_cascade(move, board, logic, num_sims=7)
            deep_scores.append((move, score))
        
        deep_scores.sort(key=lambda x: x[1], reverse=True)
        
        phase3_time = time_module.time() - phase3_start
        total_time = time_module.time() - start_time
        
        if self.rules.get('verbose', False):
            print(f"✓ Phase 3: {len(phase2_candidates)} → {len(deep_scores)} moves ({phase3_time:.2f}s)")
            print(f"🎯 TỔNG THỜI GIAN: {total_time:.2f}s")
        
        # Thêm các moves còn lại với điểm từ phase 2 hoặc phase 1
        # Dùng list comprehension thay vì set vì Move không hashable
        deep_scored_moves = [m for m, _ in deep_scores]
        remaining = []
        
        # Thêm từ phase 2
        for m, s in medium_scores:
            if m not in deep_scored_moves:
                remaining.append((m, s))
        
        # Thêm từ phase 1 (loại bỏ những moves đã có trong deep_scores và medium_scores)
        all_evaluated_moves = deep_scored_moves + [m for m, _ in remaining]
        for m, s in quick_scores:
            if m not in all_evaluated_moves:
                remaining.append((m, s))
        
        return deep_scores + remaining
    
    def _evaluate_move_with_accurate_cascade(self, move: Move, board: List[List[str]], 
                                            logic: MatchThreeLogic, num_sims: int = 5) -> int:
        """
        Đánh giá move với cascade simulation chính xác
        
        Args:
            move: Move to evaluate
            board: Current board state
            logic: MatchThreeLogic instance
            num_sims: Số lần simulation
            
        Returns:
            Total score
        """
        score = 0
        
        # Điểm immediate
        for match in move.matches:
            for pos in match.positions:
                gem_type = board[pos.row][pos.col]
                score += self.get_gem_points(gem_type)
        
        # Điểm cascade (với random spawn)
        cascade_score = self._simulate_cascade_multiple_runs(move, board, logic, num_sims, max_depth=15)
        score += cascade_score
        
        return score
    
    def get_best_move(self, moves: List[Move], board: List[List[str]], 
                     logic: MatchThreeLogic, max_time: float = 3.0) -> tuple:
        """
        Get the best move with time limit
        
        Args:
            moves: List of possible moves
            board: Current board state
            logic: MatchThreeLogic instance
            max_time: Maximum time in seconds (default 3.0s)
            
        Returns:
            Tuple of (best_move, score) or (None, 0) if no moves
        """
        if not moves:
            return (None, 0)
        
        scored_moves = self.evaluate_moves(moves, board, logic, 
                                          use_beam_search=True, 
                                          max_time=max_time)
        return scored_moves[0] if scored_moves else (None, 0)
    
    def get_top_n_moves(self, moves: List[Move], board: List[List[str]], 
                       logic: MatchThreeLogic, n: int = 5) -> List[tuple]:
        """
        Get top N moves
        
        Args:
            moves: List of possible moves
            board: Current board state
            logic: MatchThreeLogic instance
            n: Number of top moves to return
            
        Returns:
            List of top (move, score) tuples
        """
        scored_moves = self.evaluate_moves(moves, board, logic)
        return scored_moves[:n]
    
    def explain_score(self, move: Move, board: List[List[str]], 
                     logic: MatchThreeLogic, show_cascade: bool = True) -> Dict[str, int]:
        """
        Get detailed score breakdown for a move
        Simplified version: counts gems collected with cascade simulation
        
        Args:
            move: Move to explain
            board: Current board state
            logic: MatchThreeLogic instance
            show_cascade: Include cascade simulation details
            
        Returns:
            Dictionary with score breakdown
        """
        breakdown = {}
        
        # ================================================================
        # BƯỚC 1: Gems từ match ban đầu
        # ================================================================
        immediate_score = 0
        immediate_gems = 0
        yellow_gems = 0
        other_gems = 0
        
        for match in move.matches:
            for pos in match.positions:
                gem_type = board[pos.row][pos.col]
                immediate_gems += 1
                
                # Tính điểm theo loại gem: YELLOW_STAR=35, GREEN=15, RED=14, BLUE=13, khác=10
                gem_point = self.get_gem_points(gem_type)
                immediate_score += gem_point
                
                if gem_type == "YELLOW_STAR":
                    yellow_gems += 1
                else:
                    other_gems += 1
        
        breakdown["immediate_gems"] = immediate_gems
        breakdown["immediate_yellow"] = yellow_gems
        breakdown["immediate_other"] = other_gems
        breakdown["immediate_score"] = immediate_score
        
        # ================================================================
        # BƯỚC 2: Cascade simulation
        # ================================================================
        if show_cascade:
            board_copy = [row[:] for row in board]
            logic.swap_gems(board_copy, move.from_pos, move.to_pos)
            cascade_result = logic.simulate_cascade(board_copy, move.matches, max_iterations=10)
            
            # Tính gems từ cascade (bỏ chain đầu tiên)
            cascade_chains = cascade_result.get('cascade_chains', [])
            cascade_score = 0
            cascade_gems = 0
            cascade_yellow = 0
            cascade_other = 0
            
            for chain_index in range(1, len(cascade_chains)):
                matches_in_chain = cascade_chains[chain_index]
                
                for match in matches_in_chain:
                    gem_type = match.gem_type
                    gem_count = len(match.positions)
                    cascade_gems += gem_count
                    
                    # Tính điểm theo loại gem: YELLOW_STAR=35, GREEN=15, RED=14, BLUE=13, khác=10
                    gem_point = self.get_gem_points(gem_type)
                    cascade_score += gem_count * gem_point
                    
                    if gem_type == "YELLOW_STAR":
                        cascade_yellow += gem_count
                    else:
                        cascade_other += gem_count
            
            breakdown["cascade_depth"] = max(0, cascade_result.get('cascade_depth', 0) - 1)
            breakdown["cascade_matches"] = max(0, cascade_result.get('total_matches', 0) - len(move.matches))
            breakdown["cascade_gems"] = cascade_gems
            breakdown["cascade_yellow"] = cascade_yellow
            breakdown["cascade_other"] = cascade_other
            breakdown["cascade_score"] = cascade_score
        else:
            breakdown["cascade_depth"] = 0
            breakdown["cascade_gems"] = 0
            breakdown["cascade_score"] = 0
        
        # ================================================================
        # TỔNG KẾT
        # ================================================================
        breakdown["total_gems"] = immediate_gems + breakdown.get("cascade_gems", 0)
        breakdown["total_yellow"] = yellow_gems + breakdown.get("cascade_yellow", 0)
        breakdown["total_other"] = other_gems + breakdown.get("cascade_other", 0)
        breakdown["total_score"] = immediate_score + breakdown.get("cascade_score", 0)
        
        return breakdown
        
        # Setup bonus
        breakdown["setup_score"] = self._calculate_setup_bonus(move, board, logic)
        
        # Edge bonus
        breakdown["edge_score"] = self._calculate_edge_bonus(move)
        
        # Chain potential
        breakdown["chain_score"] = self._calculate_chain_potential(move, board, logic)
        
        # Total
        breakdown["total_score"] = sum([
            breakdown["gems_score"],
            breakdown["combo_score"],
            breakdown["special_score"],
            breakdown["cascade_score"],
            breakdown["unlock_score"],
            breakdown["priority_score"],
            breakdown["setup_score"],
            breakdown["edge_score"],
            breakdown["position_score"],
            breakdown["chain_score"]
        ])
        
        return breakdown


if __name__ == "__main__":
    # Test the evaluator
    print("Testing move evaluator...")
    
    from logic import MatchThreeLogic, Position, Move, Match, Direction
    
    # Create test scenario
    test_board = [
        ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
        ["BLUE", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE", "RED"],
        ["GREEN", "GREEN", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE"],
        ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
        ["BLUE", "RED", "RED", "RED", "RED", "GREEN", "BLUE", "RED"],
        ["GREEN", "GREEN", "BLUE", "GREEN", "RED", "RED", "GREEN", "BLUE"],
        ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
        ["BLUE", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE", "RED"],
    ]
    
    logic = MatchThreeLogic(rows=8, cols=8)
    
    scoring_rules = {
        "gem_removed": 10,
        "unlock_tile": 20,
        "combo_bonus": 30,
        "special_gem": 50,
        "match_4": 40,
        "match_5": 100
    }
    
    evaluator = MoveEvaluator(scoring_rules)
    
    # Find and evaluate moves
    moves = logic.find_valid_moves(test_board)
    print(f"Found {len(moves)} valid moves")
    
    if moves:
        best_move, best_score = evaluator.get_best_move(moves, test_board, logic)
        print(f"\nBest move: {best_move}")
        print(f"Score: {best_score}")
        
        # Get score breakdown
        breakdown = evaluator.explain_score(best_move, test_board, logic)
        print("\nScore breakdown:")
        for key, value in breakdown.items():
            print(f"  {key}: {value}")
