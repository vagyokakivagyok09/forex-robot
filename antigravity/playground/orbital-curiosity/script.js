const questions = [
    {
        question: "Mi Magyarország fővárosa?",
        options: ["Debrecen", "Pécs", "Budapest", "Szeged"],
        correct: 2
    },
    {
        question: "Melyik évben volt az államalapítás?",
        options: ["896", "1000", "1222", "1848"],
        correct: 1
    },
    {
        question: "Ki írta a Himnuszt?",
        options: ["Vörösmarty Mihály", "Petőfi Sándor", "Arany János", "Kölcsey Ferenc"],
        correct: 3
    },
    {
        question: "Hány megye van Magyarországon?",
        options: ["19", "20", "22", "18"],
        correct: 0
    },
    {
        question: "Melyik a legnagyobb tó Magyarországon?",
        options: ["Velencei-tó", "Fertő-tó", "Balaton", "Tisza-tó"],
        correct: 2
    }
];

let currentQuestionIndex = 0;
let score = 0;

// DOM Elements
const startScreen = document.getElementById('start-screen');
const quizScreen = document.getElementById('quiz-screen');
const resultScreen = document.getElementById('result-screen');

const startBtn = document.getElementById('start-btn');
const restartBtn = document.getElementById('restart-btn');

const questionCounter = document.getElementById('question-counter');
const scoreDisplay = document.getElementById('score-display');
const progressBar = document.getElementById('progress-bar');
const questionText = document.getElementById('question-text');
const optionsContainer = document.getElementById('options-container');

const finalScore = document.getElementById('final-score');
const resultMessage = document.getElementById('result-message');

// Event Listeners
startBtn.addEventListener('click', startQuiz);
restartBtn.addEventListener('click', restartQuiz);

function startQuiz() {
    startScreen.classList.add('hidden');
    startScreen.classList.remove('active');

    quizScreen.classList.remove('hidden');
    // Small delay to allow display:block to apply before opacity transition
    setTimeout(() => {
        quizScreen.classList.add('active');
    }, 10);

    currentQuestionIndex = 0;
    score = 0;
    loadQuestion();
}

function loadQuestion() {
    const currentQuestion = questions[currentQuestionIndex];

    // Update stats
    questionCounter.textContent = `${currentQuestionIndex + 1} / ${questions.length}`;
    scoreDisplay.textContent = `Pontszám: ${score}`;

    // Update progress bar
    const progress = ((currentQuestionIndex) / questions.length) * 100;
    progressBar.style.width = `${progress}%`;

    // Set question text
    questionText.textContent = currentQuestion.question;

    // Generate options
    optionsContainer.innerHTML = '';
    currentQuestion.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.classList.add('option-btn');
        button.textContent = option;
        button.addEventListener('click', () => selectOption(index));
        optionsContainer.appendChild(button);
    });
}

function selectOption(selectedIndex) {
    const currentQuestion = questions[currentQuestionIndex];
    const buttons = optionsContainer.querySelectorAll('.option-btn');

    // Disable all buttons
    buttons.forEach(btn => btn.disabled = true);

    // Check answer
    if (selectedIndex === currentQuestion.correct) {
        buttons[selectedIndex].classList.add('correct');
        score++;
        scoreDisplay.textContent = `Pontszám: ${score}`;
    } else {
        buttons[selectedIndex].classList.add('wrong');
        // Show correct answer
        buttons[currentQuestion.correct].classList.add('correct');
    }

    // Update progress bar to next step visually
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    progressBar.style.width = `${progress}%`;

    // Wait and go to next question
    setTimeout(() => {
        currentQuestionIndex++;
        if (currentQuestionIndex < questions.length) {
            loadQuestion();
        } else {
            showResult();
        }
    }, 1500);
}

function showResult() {
    quizScreen.classList.remove('active');
    quizScreen.classList.add('hidden');

    resultScreen.classList.remove('hidden');
    setTimeout(() => {
        resultScreen.classList.add('active');
    }, 10);

    finalScore.textContent = score;

    // Update circle gradient based on score percentage
    const percentage = (score / questions.length) * 100;
    const circle = document.querySelector('.score-circle');
    circle.style.background = `conic-gradient(var(--primary-color) ${percentage}%, rgba(255, 255, 255, 0.05) ${percentage}%)`;

    // Custom message
    if (score === questions.length) {
        resultMessage.textContent = "Tökéletes! Zseni vagy! 🏆";
    } else if (score >= questions.length / 2) {
        resultMessage.textContent = "Szép munka! 👍";
    } else {
        resultMessage.textContent = "Gyakorolj még kicsit! 💪";
    }
}

function restartQuiz() {
    resultScreen.classList.remove('active');
    resultScreen.classList.add('hidden');

    startScreen.classList.remove('hidden');
    setTimeout(() => {
        startScreen.classList.add('active');
    }, 10);
}
