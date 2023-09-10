"""
This class is responsible for storing all the information about the current state of a chess game. It will 
also be responsible for determining the valid moves at the current state. Additonally, it will keep a move log.
"""

class GameState():
    def __init__(self):
        #possibly look to implement num.py to improve efficiency
        #board is a 8x8 2d list, each element has 2 characters
        #1st character: color of piece, 2nd character: type of piece, King, Queen, Rook, Knight, Bishop, Pawn
        #"--" represents an empty space with no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 
        'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}        

        #whos turn is it
        self.whiteToMove = True

        #previous moves done
        self.moveLog = []

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible

    '''
    takes a move as a parameter and executes it. (won't work for castling, pawn promotion, and en-passant
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove

        #update kings location if move
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if(len(self.moveLog) != 0): #make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #switch turn back

            #update King's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsandChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move King
                moves = self.getAllPossibleMoves()
                #to block a check, you must move a piece into one of the squares between the enemy piece and King
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = []#squares that pieces can move to 
                #if knight, must capture knight or move King, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to piece end checks
                            break
                #get rid of any moves that don't block check or move King
                for i in range(len(moves)-1, -1, -1): #go through backwards when youa re removing from a list as iterations
                    if moves[i].pieceMoved[1] != "K": #move doesn't move King so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesn't block check or capture pieces
                            moves.remove(moves[i])
            else: #double check, King has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        
        
        return moves
        '''
        # 1) generate all the possible moves
        moves = self.getAllPossibleMoves()

        # 2) for each move, make the move
        for i in range((len(moves) - 1), -1, -1): #when removing from a list, go backwards through the list
            self.makeMove(moves[i])

            # 3) generate all opponents moves
            # 4) for each of your opponents moves, see if they attack your King
            self.whiteToMove = not self.whiteToMove #switch turn back
            if self.inCheck():
                 # 5) if they do attack your King, it is not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove 
            self.undoMove()
        if len(moves) == 0: #either checkmate or stalemate
            if self.inCheck():
                checkMate = True
            else:
                staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves
        '''
        

    def checkForPinsandChecks(self):
        pins = [] #squares wheere the allied pinned [piece is and direction pinned from
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from King for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possibilities here in this complex conditional
                        #1.) orthogonally away from King and piece is a rook
                        #2.) diagonally away from King and piece is a bishop
                        #3.) 1 square  away diagonally from King and piece is a pawn
                        #4.) any direction and piece is a queen
                        #5.) any direction 1 square away and piece is a king (this is necessary to prevent
                        # a King move to a square controlled by another King)
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: #friendly piece not applying check
                            break
                else:
                    break #off the board
        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N": #enemy Knight attacking King
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    '''
    Determine if the the current player is under Check
    
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else: 
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    '''
    '''
    Determine if the enemy can attack square r, c
    
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponents turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch the turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under Attack
                return True
        return False

    '''
    
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) #calls appropriate move function based on pieces
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these to a list
    '''
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                        moves.append(Move((r,c), (r-2,c), self.board))
            #captures
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r,c), (r-1, c-1), self.board))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r-1,c+1), self.board))
        
        else: #black pawn moves
            if self.board[r+1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c), (r+1,c), self.board))
                    if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                        moves.append(Move((r,c), (r+2,c), self.board))

            #captures
            if c-1 >= 0: #captures to the left
                if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r,c), (r+1,c-1), self.board))
            if c+1 <= 7: #captures to the right
                if self.board[r+1][c+1][0] == 'w': #enemy piece to capture
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r,c), (r+1,c+1), self.board))



    '''
    Get all the rook moves for the pawn located at row, col and add these to a list
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #cannot remove queen from pin on rook moves, ony remove on bishop moves
                    self.pins.remove(self.pins[i])
                    break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions: 
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #empty space valid
                            moves.append(Move((r, c),(endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                    else: #friendly piece invalid
                        break
                else: #off the board
                    break
    
    '''
    Get all the knight moves for the pawn located at row, col and add these to a list
    '''
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #not an ally (either empty or enemy piece)
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    '''
    Get all the bishop moves for the pawn located at row, col and add these to a list
    '''
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #four diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range (1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy Piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off the board
                    break

    '''
    Get all the Queen moves for the pawn located at row, col and add these to a list
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves( r, c, moves)

    '''
    Get all the King moves for the pawn located at row, col and add these to a list
    '''
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0 ,1)
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #on the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not an ally piece (either empty or enemy)
                    #place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsandChecks()
                    if not inCheck: 
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    #place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
                    




class Move():
    # maps key to values 
    # key : value

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}

    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantPossible = ()):
        self.startRow = startSq[0]
        self.startCol = startSq[1]

        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]

        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        #enpassant
        self.isEnpassantMove = self.pieceMoved[1] == 'p' and ((self.endRow, self.endCol) == enpassantPossible)


        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if (isinstance(other, Move)):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        #can improve to make more like actual/real chess game notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]



