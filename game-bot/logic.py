"""
Match-3 Logic Module
Detects valid moves and matches on the board
"""

from typing import List, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum
import random


class Direction(Enum):
    """Direction for swapping gems"""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass
class Position:
    """Represents a position on the board"""
    row: int
    col: int
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def __repr__(self):
        return f"({self.row}, {self.col})"


@dataclass
class Match:
    """Represents a match on the board"""
    positions: List[Position]
    gem_type: str
    length: int
    direction: str  # "horizontal" or "vertical"
    
    def __repr__(self):
        return f"Match({self.gem_type}, {self.length}, {self.direction})"


@dataclass
class Move:
    """Represents a possible move"""
    from_pos: Position
    to_pos: Position
    direction: Direction
    matches: List[Match]
    
    def __repr__(self):
        return f"Move({self.from_pos} -> {self.to_pos}, {len(self.matches)} matches)"


class MatchThreeLogic:
    """Handles match-3 game logic"""
    
    def __init__(self, rows: int, cols: int):
        """
        Initialize logic handler
        
        Args:
            rows: Number of rows on the board
            cols: Number of columns on the board
        """
        self.rows = rows
        self.cols = cols
        
        # Danh sách các loại gems có thể spawn (dùng cho cascade simulation)
        self.gem_types = [
            "BLUE_LIGHTNING",
            "GREEN_HEART", 
            "ORANGE_SUN",
            "PURPLE_MOON",
            "RED_FIRE",
            "YELLOW_STAR",
            "RED_HEART",
            "GRAY_YINYANG"
        ]
    
    def is_valid_position(self, pos: Position) -> bool:
        """Check if position is within board bounds"""
        return 0 <= pos.row < self.rows and 0 <= pos.col < self.cols
    
    def get_neighbors(self, pos: Position) -> List[Tuple[Position, Direction]]:
        """
        Get valid neighboring positions
        
        Args:
            pos: Current position
            
        Returns:
            List of (neighbor_position, direction) tuples
        """
        neighbors = []
        
        for direction in Direction:
            dr, dc = direction.value
            neighbor = Position(pos.row + dr, pos.col + dc)
            
            if self.is_valid_position(neighbor):
                neighbors.append((neighbor, direction))
        
        return neighbors
    
    def swap_gems(self, board: List[List[str]], pos1: Position, pos2: Position):
        """
        Swap two gems on the board (in-place)
        
        Args:
            board: Game board
            pos1: First position
            pos2: Second position
        """
        board[pos1.row][pos1.col], board[pos2.row][pos2.col] = \
            board[pos2.row][pos2.col], board[pos1.row][pos1.col]
    
    def find_matches_at_position(self, board: List[List[str]], pos: Position) -> List[Match]:
        """
        Find all matches that include the given position
        
        Args:
            board: Game board
            pos: Position to check
            
        Returns:
            List of Match objects
        """
        gem_type = board[pos.row][pos.col]
        
        # Ignore special cells
        if gem_type in ["EMPTY", "LOCKED", "UNKNOWN"]:
            return []
        
        matches = []
        
        # Check horizontal match
        h_positions = [pos]
        
        # Check left
        col = pos.col - 1
        while col >= 0 and board[pos.row][col] == gem_type:
            h_positions.append(Position(pos.row, col))
            col -= 1
        
        # Check right
        col = pos.col + 1
        while col < self.cols and board[pos.row][col] == gem_type:
            h_positions.append(Position(pos.row, col))
            col += 1
        
        # Add horizontal match if >= 3
        if len(h_positions) >= 3:
            matches.append(Match(
                positions=sorted(h_positions, key=lambda p: p.col),
                gem_type=gem_type,
                length=len(h_positions),
                direction="horizontal"
            ))
        
        # Check vertical match
        v_positions = [pos]
        
        # Check up
        row = pos.row - 1
        while row >= 0 and board[row][pos.col] == gem_type:
            v_positions.append(Position(row, pos.col))
            row -= 1
        
        # Check down
        row = pos.row + 1
        while row < self.rows and board[row][pos.col] == gem_type:
            v_positions.append(Position(row, pos.col))
            row += 1
        
        # Add vertical match if >= 3
        if len(v_positions) >= 3:
            matches.append(Match(
                positions=sorted(v_positions, key=lambda p: p.row),
                gem_type=gem_type,
                length=len(v_positions),
                direction="vertical"
            ))
        
        return matches
    
    def find_all_matches(self, board: List[List[str]]) -> List[Match]:
        """
        Find all matches on the current board
        
        Args:
            board: Game board
            
        Returns:
            List of all Match objects
        """
        all_matches = []
        processed_positions = set()
        
        for row in range(self.rows):
            for col in range(self.cols):
                pos = Position(row, col)
                
                if pos in processed_positions:
                    continue
                
                matches = self.find_matches_at_position(board, pos)
                
                for match in matches:
                    all_matches.append(match)
                    processed_positions.update(match.positions)
        
        return all_matches
    
    def find_valid_moves(self, board: List[List[str]]) -> List[Move]:
        """
        Find all valid moves on the board
        
        Args:
            board: Game board
            
        Returns:
            List of valid Move objects
        """
        valid_moves = []
        
        # Try every possible swap
        for row in range(self.rows):
            for col in range(self.cols):
                pos = Position(row, col)
                gem_type = board[row][col]
                
                # Skip special cells
                if gem_type in ["EMPTY", "LOCKED", "UNKNOWN"]:
                    continue
                
                # Try swapping with each neighbor
                neighbors = self.get_neighbors(pos)
                
                for neighbor_pos, direction in neighbors:
                    neighbor_gem = board[neighbor_pos.row][neighbor_pos.col]
                    
                    # Skip special cells
                    if neighbor_gem in ["EMPTY", "LOCKED", "UNKNOWN"]:
                        continue
                    
                    # Make a copy of the board
                    board_copy = [row[:] for row in board]
                    
                    # Perform swap
                    self.swap_gems(board_copy, pos, neighbor_pos)
                    
                    # Check for matches
                    matches_at_from = self.find_matches_at_position(board_copy, pos)
                    matches_at_to = self.find_matches_at_position(board_copy, neighbor_pos)
                    
                    # Combine matches (remove duplicates)
                    all_matches = matches_at_from + matches_at_to
                    unique_matches = []
                    seen_positions = set()
                    
                    for match in all_matches:
                        match_key = frozenset(match.positions)
                        if match_key not in seen_positions:
                            unique_matches.append(match)
                            seen_positions.add(match_key)
                    
                    # If valid move, add it
                    if unique_matches:
                        move = Move(
                            from_pos=pos,
                            to_pos=neighbor_pos,
                            direction=direction,
                            matches=unique_matches
                        )
                        valid_moves.append(move)
        
        return valid_moves
    
    def get_affected_gems(self, matches: List[Match]) -> Set[Position]:
        """
        Get all gem positions affected by matches
        
        Args:
            matches: List of Match objects
            
        Returns:
            Set of Position objects
        """
        affected = set()
        for match in matches:
            affected.update(match.positions)
        return affected
    
    def count_total_gems_removed(self, matches: List[Match]) -> int:
        """
        Count total unique gems removed by matches
        
        Args:
            matches: List of Match objects
            
        Returns:
            Number of gems removed
        """
        return len(self.get_affected_gems(matches))
    
    def detect_special_matches(self, match: Match) -> str:
        """
        Detect if a match creates special gems
        
        Args:
            match: Match object
            
        Returns:
            Type of special gem ("match_4", "match_5", "t_shape", "l_shape", or "none")
        """
        if match.length == 4:
            return "match_4"
        elif match.length >= 5:
            return "match_5"
        else:
            return "none"
    
    def simulate_gravity(self, board: List[List[str]], removed_positions: Set[Position]) -> List[List[str]]:
        """
        Simulate gravity after gems are removed
        Gems fall down to fill empty spaces
        
        Args:
            board: Current board state
            removed_positions: Set of positions where gems were removed
            
        Returns:
            New board state after gravity
        """
        # Create a copy of the board
        new_board = [row[:] for row in board]
        
        # Mark removed positions as EMPTY
        for pos in removed_positions:
            new_board[pos.row][pos.col] = "EMPTY"
        
        # Apply gravity column by column
        for col in range(self.cols):
            # Collect non-empty gems from bottom to top
            gems = []
            for row in range(self.rows - 1, -1, -1):
                gem = new_board[row][col]
                if gem not in ["EMPTY", "LOCKED"]:
                    gems.append(gem)
            
            # Place gems back from bottom
            row = self.rows - 1
            for gem in gems:
                new_board[row][col] = gem
                row -= 1
            
            # Fill remaining with EMPTY (will be refilled with random gems in real game)
            while row >= 0:
                new_board[row][col] = "EMPTY"
                row -= 1
        
        return new_board
    
    def spawn_random_gems(self, board: List[List[str]]) -> List[List[str]]:
        """
        Spawn random gems vào các vị trí EMPTY
        Được dùng trong cascade simulation để mô phỏng gems rơi từ trên xuống
        
        Args:
            board: Board state có các vị trí EMPTY
            
        Returns:
            Board state với EMPTY được fill bằng random gems
        """
        new_board = [row[:] for row in board]
        
        for row in range(self.rows):
            for col in range(self.cols):
                if new_board[row][col] == "EMPTY":
                    # Random spawn một gem từ danh sách gem types
                    new_board[row][col] = random.choice(self.gem_types)
        
        return new_board
    
    def simulate_cascade(self, board: List[List[str]], initial_matches: List[Match], 
                        max_iterations: int = 5, spawn_gems: bool = False) -> dict:
        """
        Simulate cascade effects after a move
        Apply gravity and find new matches repeatedly until stable
        
        Args:
            board: Board state after initial move
            initial_matches: Matches from the initial move
            max_iterations: Maximum cascade iterations to prevent infinite loop
            spawn_gems: If True, spawn random gems into EMPTY spaces (more accurate)
            
        Returns:
            Dictionary with cascade statistics:
            - total_gems_removed: Total gems removed across all cascades
            - total_matches: Total number of matches (including cascades)
            - cascade_depth: How many cascade levels occurred
            - cascade_chains: List of matches at each cascade level
        """
        result = {
            'total_gems_removed': 0,
            'total_matches': 0,
            'cascade_depth': 0,
            'cascade_chains': []
        }
        
        current_board = [row[:] for row in board]
        current_matches = initial_matches
        
        for iteration in range(max_iterations):
            if not current_matches:
                break
            
            # Count gems removed in this iteration
            removed_positions = self.get_affected_gems(current_matches)
            result['total_gems_removed'] += len(removed_positions)
            result['total_matches'] += len(current_matches)
            result['cascade_chains'].append(current_matches)
            result['cascade_depth'] += 1
            
            # Apply gravity
            current_board = self.simulate_gravity(current_board, removed_positions)
            
            # Spawn random gems vào EMPTY (nếu bật)
            if spawn_gems:
                current_board = self.spawn_random_gems(current_board)
            
            # Find new matches after gravity (and spawn)
            current_matches = self.find_all_matches(current_board)
            
            # Nếu không spawn gems, lọc bỏ matches có EMPTY
            if not spawn_gems:
                current_matches = [
                    match for match in current_matches 
                    if not any(current_board[pos.row][pos.col] == "EMPTY" for pos in match.positions)
                ]
            
            # If no new matches, cascade ends
            if not current_matches:
                break
        
        return result
    
    def count_gem_type_on_board(self, board: List[List[str]], gem_type: str) -> int:
        """
        Count how many gems of a specific type are on the board
        
        Args:
            board: Game board
            gem_type: Type of gem to count
            
        Returns:
            Count of gems
        """
        count = 0
        for row in board:
            for gem in row:
                if gem == gem_type:
                    count += 1
        return count
    
    def get_board_gem_distribution(self, board: List[List[str]]) -> dict:
        """
        Get distribution of gem types on board
        
        Args:
            board: Game board
            
        Returns:
            Dictionary mapping gem_type -> count
        """
        distribution = {}
        for row in board:
            for gem in row:
                if gem not in ["EMPTY", "LOCKED", "UNKNOWN"]:
                    distribution[gem] = distribution.get(gem, 0) + 1
        return distribution


if __name__ == "__main__":
    # Test the logic module
    print("Testing match-3 logic...")
    
    # Create test board
    test_board = [
        ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
        ["BLUE", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE", "RED"],
        ["GREEN", "GREEN", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE"],
        ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
        ["BLUE", "RED", "RED", "RED", "RED", "GREEN", "BLUE", "RED"],  # Horizontal match
        ["GREEN", "GREEN", "BLUE", "GREEN", "RED", "RED", "GREEN", "BLUE"],
        ["RED", "BLUE", "GREEN", "RED", "BLUE", "GREEN", "RED", "BLUE"],
        ["BLUE", "RED", "BLUE", "GREEN", "RED", "GREEN", "BLUE", "RED"],
    ]
    
    logic = MatchThreeLogic(rows=8, cols=8)
    
    # Find matches on current board
    matches = logic.find_all_matches(test_board)
    print(f"\nFound {len(matches)} matches on the board:")
    for match in matches:
        print(f"  {match}")
    
    # Find valid moves
    moves = logic.find_valid_moves(test_board)
    print(f"\nFound {len(moves)} valid moves")
    if moves:
        print("First 5 moves:")
        for move in moves[:5]:
            print(f"  {move}")
