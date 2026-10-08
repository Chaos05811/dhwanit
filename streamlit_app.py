import random
import streamlit as st


WIN_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]

X_COLOR = "#e74c3c"
O_COLOR = "#3498db"
LINE_COLOR = "#888888"


# ---------- Game ----------

def new_game():
    st.session_state.board = [""] * 9
    st.session_state.winner = None
    st.session_state.winning_line = ()
    st.session_state.draw = False


def check_result(board):
    for line in WIN_LINES:
        a, b, c = line

        if board[a] and board[a] == board[b] == board[c]:
            return board[a], line

    return None, ()


def minimax(board, player):
    winner, _ = check_result(board)

    if winner:
        return 1 if winner == "O" else -1

    empty = [i for i, cell in enumerate(board) if not cell]

    if not empty:
        return 0

    scores = []

    for i in empty:
        board[i] = player
        next_player = "X" if player == "O" else "O"
        scores.append(minimax(board, next_player))
        board[i] = ""

    return max(scores) if player == "O" else min(scores)


def bot_move(board, difficulty):
    empty = [i for i, cell in enumerate(board) if not cell]

    if difficulty == "Easy":
        return random.choice(empty)

    best_score = -2
    best_moves = []

    for i in empty:
        board[i] = "O"
        score = minimax(board, "X")
        board[i] = ""

        if score > best_score:
            best_score = score
            best_moves = [i]
        elif score == best_score:
            best_moves.append(i)

    return random.choice(best_moves)


def update_game():
    state = st.session_state

    state.winner, state.winning_line = check_result(state.board)

    if not state.winner and all(state.board):
        state.draw = True


def play(index):
    state = st.session_state

    if state.board[index] or state.winner or state.draw:
        return

    state.board[index] = "X"
    update_game()

    if not state.winner and not state.draw:
        move = bot_move(state.board, state.difficulty)
        state.board[move] = "O"
        update_game()


# ---------- Frontend ----------

def board_css(state):
    css = f"""
    <style>

    .st-key-board {{
        width: 360px;
        max-width: 90vw;
        margin: 30px auto;
    }}

    .st-key-board [data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
        flex-wrap: nowrap !important;
    }}

    .st-key-board [data-testid="stColumn"] {{
        padding: 0 !important;
        margin: 0 !important;
        min-width: 33.333% !important;
        max-width: 33.333% !important;
        flex: 0 0 33.333% !important;
    }}

    .st-key-board [class*="st-key-cell_"] {{
        height: 120px !important;
        box-sizing: border-box !important;
    }}

    .st-key-board [class*="st-key-cell_"] .stButton {{
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
    }}

    .st-key-board [class*="st-key-cell_"] button {{
        width: 100% !important;
        height: 120px !important;
        min-height: 120px !important;

        padding: 0 !important;
        margin: 0 !important;

        border: none !important;
        border-radius: 0 !important;

        background: transparent !important;
        box-shadow: none !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        transition: background 0.15s ease;
    }}

    .st-key-board [class*="st-key-cell_"] button p {{
        font-size: 4rem !important;
        font-weight: 800 !important;
        line-height: 1 !important;

        margin: 0 !important;
        padding: 0 !important;
    }}

    .st-key-board [class*="st-key-cell_"] button:not(:disabled):hover {{
        background: rgba(128, 128, 128, 0.12) !important;
    }}

    .st-key-board button:disabled {{
        opacity: 1 !important;
        cursor: default !important;
    }}

    </style>
    """

    # Add all board-specific CSS to the SAME style block.
    rules = []

    for i in range(9):
        row, col = divmod(i, 3)

        border = ""

        if col < 2:
            border += (
                f"border-right: 4px solid {LINE_COLOR} !important;"
            )

        if row < 2:
            border += (
                f"border-bottom: 4px solid {LINE_COLOR} !important;"
            )

        if i in state.winning_line:
            border += (
                "background: rgba(46, 204, 113, 0.25) !important;"
            )

        rules.append(
            f"""
            .st-key-board .st-key-cell_{i} {{
                {border}
            }}
            """
        )

        if state.board[i]:
            color = X_COLOR if state.board[i] == "X" else O_COLOR

            rules.append(
                f"""
                .st-key-board .st-key-cell_{i} button p {{
                    color: {color} !important;
                }}
                """
            )

    css = css.replace(
        "</style>",
        "\n".join(rules) + "</style>",
    )

    return css


# ---------- App ----------

st.set_page_config(
    page_title="Tic Tac Toe",
    page_icon="❌",
    layout="centered",
)

if "board" not in st.session_state:
    new_game()


state = st.session_state

st.title("Tic Tac Toe")


# Status
if state.winner == "X":
    st.success("You win!")
elif state.winner == "O":
    st.error("The bot wins!")
elif state.draw:
    st.info("It's a draw!")
else:
    st.write("Your turn — you are **X**")


# Difficulty
st.radio(
    "Difficulty",
    ["Easy", "Hard"],
    index=1,
    horizontal=True,
    key="difficulty",
)


# CSS
st.markdown(
    board_css(state),
    unsafe_allow_html=True,
)


# Board
game_over = bool(state.winner or state.draw)

with st.container(key="board"):
    for row in range(3):
        columns = st.columns(3)

        for col in range(3):
            index = row * 3 + col

            with columns[col]:
                with st.container(key=f"cell_{index}"):
                    st.button(
                        state.board[index] or " ",
                        key=f"button_{index}",
                        on_click=play,
                        args=(index,),
                        disabled=(
                            bool(state.board[index])
                            or game_over
                        ),
                        use_container_width=True,
                    )


# New game
st.button(
    "New Game",
    on_click=new_game,
    use_container_width=True,
)
