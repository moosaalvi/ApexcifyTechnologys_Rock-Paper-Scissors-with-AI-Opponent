# 🤖 Adaptive AI: Rock, Paper, Scissors Game (Pygame Implementation)

> A stable, high-performance Graphical User Interface (GUI) based Rock, Paper, Scissors game featuring a learning AI opponent, developed as part of a technical internship task.

---

## 🎯 Project Overview & Goal

This project was completed as **Task 1** for the **[Your Internship/Company Name]** Internship program. The core goal was to implement the classic Rock, Paper, Scissors game but elevate it into a portfolio-grade application by integrating:

1.  **A highly stable and responsive UI/UX (Pixel-Perfect Design).**
2.  **A custom Adaptive AI opponent that learns player patterns.**

---

## ✨ Technical Highlights & Features

The following features demonstrate key programming and design skills:

### 🧠 Adaptive AI Logic
* **Dynamic Counter-Bias:** The AI maintains a dynamic probability to counter the player's most common move. This bias is actively adjusted based on the computer's **win/loss streak** to maintain a challenging and unpredictable gameplay loop.
* **Pattern Recognition (Basic):** The AI can detect basic looping patterns (e.g., repeating Rock-Paper) in the last two moves and attempts to break that cycle.
* **Data Structure Usage:** Utilizes Python's `collections.Counter` for efficient tracking of player history.

### 🎨 Pygame UI/UX Implementation
* **Responsive Buttons:** All interaction elements (`ROCK`, `PAPER`, `SCISSORS`) are implemented as reusable `Button` classes with hover and click states.
* **Visual Stability:** The UI was fine-tuned across several iterations to ensure **zero text overflow** issues (like the "UNMUTE" text) and consistent component alignment across all game states.
* **State Management:** Uses a clear state machine (`MENU`, `PLAYING`, `GAME_OVER`) to manage screen flow and logic.

### ⚙️ Architecture & Code Quality
* **Object-Oriented Programming (OOP):** The entire game is encapsulated within the `PygameRPS` class, promoting high modularity and maintenance.
* **Asset Management:** Includes dedicated loading for images and sound effects (`.png`, `.wav`).

---

## 🚀 Installation & Setup

To run this project locally, you need Python and the Pygame library.

### Prerequisites

* **Python 3.x**
* **Pygame** Library

### Quick Installation

```bash
# 1. Intall Pygame 
pip install pygame

# 2. Clone The Repository 
git clone [Your GitHub Link]
cd <repository-folder-name>

# 3. Run Game
python rps.py






Detail       |    Value
Developer    |    Moosa Alvi
Task,"Rock   |    Paper, Scissors Game with AI Opponent"
Organization |    Apexcify Technologies - Internship
Status       |    Completed and Deployed 
LinkedIn     |    https://www.linkedin.com/in/moosa-alvi-50b24a352/
