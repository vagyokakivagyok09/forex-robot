Îƒ// =====================================================
// GAME STATE
// =====================================================

const gameState = {
    currentScreen: 'intro-screen',
    unlockedDigits: [false, false, false, false, false],
    codeDigits: ['?', '?', '?', '?', '?'],
    correctCode: '21265'
};

// =====================================================
// NAVIGATION & UI
// =====================================================

function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    // Show target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
        gameState.currentScreen = screenId;
    }

    // Update progress bar visibility
    const progressBar = document.getElementById('progress-bar');
    if (screenId === 'intro-screen' || screenId === 'victory-screen') {
        progressBar.style.display = 'none';
    } else {
        progressBar.style.display = 'flex';
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

function startGame() {
    showScreen('main-menu');
    updateMainMenu();
}

function restartGame() {
    // Reset game state
    gameState.unlockedDigits = [false, false, false, false, false];
    gameState.codeDigits = ['?', '?', '?', '?', '?'];

    // Reset all inputs
    for (let i = 1; i <= 5; i++) {
        const input = document.getElementById(`answer-${i}`);
        if (input) input.value = '';

        const feedback = document.getElementById(`feedback-${i}`);
        if (feedback) {
            feedback.classList.remove('show', 'correct', 'incorrect');
        }
    }

    // Reset final code input
    const finalInput = document.getElementById('final-code');
    if (finalInput) finalInput.value = '';

    const finalFeedback = document.getElementById('final-feedback');
    if (finalFeedback) {
        finalFeedback.classList.remove('show', 'correct', 'incorrect');
    }

    // Reset scenario selection
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelectorAll('input[name="scenario"]').forEach(radio => {
        radio.checked = false;
    });

    // Reset quiz answers
    quizAnswers.fill(null);
    document.querySelectorAll('.btn-quiz').forEach(btn => btn.classList.remove('selected'));
    document.querySelectorAll('.quiz-item').forEach(item => item.classList.remove('correct-answer', 'wrong-answer'));
    const quizCheckBtn = document.getElementById('quiz-check-btn');
    if (quizCheckBtn) {
        quizCheckBtn.disabled = true;
        quizCheckBtn.classList.remove('btn-primary');
        quizCheckBtn.classList.add('btn-secondary');
    }
    const correctCountDisplay = document.getElementById('correct-count');
    if (correctCountDisplay) correctCountDisplay.textContent = '0';


    // Update UI
    updateCodeDisplay();

    // Return to intro
    showScreen('intro-screen');
}

// =====================================================
// MAIN MENU (HUB) LOGIC
// =====================================================

function selectStation(stationId) {
    if (stationId === 'final') {
        // Check if all digits are unlocked
        const allUnlocked = gameState.unlockedDigits.every(d => d === true);
        if (allUnlocked) {
            showScreen('final-screen');
        } else {
            alert('MÃ©g nem szerezted meg az Ã¶sszes kÃ³drÃ©szletet! Oldd meg a feladatokat!');
        }
        return;
    }

    const index = stationId - 1;
    // Station 1 is always open. Others depend on previous digit.
    let isLocked = false;
    if (index > 0) {
        if (!gameState.unlockedDigits[index - 1]) {
            isLocked = true;
        }
    }

    if (!isLocked) {
        showScreen(`station-${stationId}`);
    }
}

function updateMainMenu() {
    const stations = [1, 2, 3, 4, 5];
    stations.forEach(id => {
        const card = document.querySelector(`.mission-card[onclick="selectStation(${id})"]`);
        if (!card) return;

        const index = id - 1;
        // Check locked status
        let isLocked = false;
        if (index > 0 && !gameState.unlockedDigits[index - 1]) {
            isLocked = true;
        }

        // Check completed status
        const isCompleted = gameState.unlockedDigits[index];

        // Reset classes
        card.classList.remove('locked', 'active', 'completed');

        const statusText = card.querySelector('.card-status');

        if (isCompleted) {
            card.classList.add('completed');
            if (statusText) statusText.textContent = 'KÃ‰SZ';
        } else if (isLocked) {
            card.classList.add('locked');
            if (statusText) statusText.textContent = 'ZÃRVA';
        } else {
            card.classList.add('active');
            if (statusText) statusText.textContent = 'NYITVA';
        }
    });

    // Update Final Gate
    const finalCard = document.querySelector('.mission-card.final-gate');
    if (finalCard) {
        const allUnlocked = gameState.unlockedDigits.every(d => d === true);
        finalCard.classList.remove('locked', 'active');
        const statusText = finalCard.querySelector('.card-status');

        if (allUnlocked) {
            finalCard.classList.add('active');
            if (statusText) statusText.textContent = 'NYITVA';
        } else {
            finalCard.classList.add('locked');
            if (statusText) statusText.textContent = 'ZÃRVA';
        }
    }
}

// =====================================================
// HELPER FUNCTIONS
// =====================================================

function unlockDigit(index, digit) {
    gameState.unlockedDigits[index] = true;
    gameState.codeDigits[index] = digit;
    updateCodeDisplay();
    updateMainMenu(); // Update menu state
}

function updateCodeDisplay() {
    const slots = document.querySelectorAll('.code-slot');
    const finalSlots = document.querySelectorAll('.final-code-slot');

    slots.forEach((slot, index) => {
        if (gameState.unlockedDigits[index]) {
            slot.textContent = gameState.codeDigits[index];
            slot.classList.add('unlocked');

            // Add pop animation if just unlocked
            slot.classList.remove('pop-animation');
            void slot.offsetWidth; // trigger reflow
            slot.classList.add('pop-animation');
        } else {
            slot.textContent = '?';
            slot.classList.remove('unlocked', 'pop-animation');
        }
    });

    // Update final screen slots as well
    finalSlots.forEach((slot, index) => {
        if (gameState.unlockedDigits[index]) {
            slot.textContent = gameState.codeDigits[index];
            slot.classList.add('unlocked');
        } else {
            slot.textContent = '?';
            slot.classList.remove('unlocked');
        }
    });
}

function showFeedback(stationId, isCorrect, message) {
    const feedbackEl = document.getElementById(`feedback-${stationId}`);
    if (!feedbackEl) return;

    feedbackEl.textContent = message;
    feedbackEl.className = `feedback show ${isCorrect ? 'correct' : 'incorrect'}`;
}

// =====================================================
// STATION 1: A TÅ°Z HÃROMSZÃ–GE
// =====================================================

function checkStation1() {
    const input = document.getElementById('answer-1');
    const answer = input.value.trim().toLowerCase();

    if (answer === 'oxigÃ©n' || answer === 'oxigen') {
        unlockDigit(0, 2);
        showFeedback(1, true, 'âœ… Helyes! Az Ã©gÃ©shez oxigÃ©n szÃ¼ksÃ©ges. Megszerezted az elsÅ‘ szÃ¡mjegyet (2)!');
        setTimeout(() => showScreen('main-menu'), 2000);
    } else {
        showFeedback(1, false, 'âŒ Nem jÃ³ vÃ¡lasz. Gondolj arra, mi van a levegÅ‘ben, ami kell a tÅ±znek!');
    }
}

// =====================================================
// STATION 2: A HÅMÃ‰RÅ REJTÃ‰LYE
// =====================================================

function checkStation2() {
    const input = document.getElementById('answer-2');
    const answer = input.value.trim();

    if (answer === '1') {
        unlockDigit(1, 1);
        showFeedback(2, true, 'âœ… Helyes! Az ÃºjsÃ¡gpapÃ­r gyullad meg a legkÃ¶nnyebben (190Â°C). Megszerezted a mÃ¡sodik szÃ¡mjegyet (1)!');
        setTimeout(() => showScreen('main-menu'), 2000);
    } else {
        showFeedback(2, false, 'âŒ Nem jÃ³ vÃ¡lasz. NÃ©zd meg a tÃ¡blÃ¡zatot! Melyik a legalacsonyabb szÃ¡m? Annak az elsÅ‘ szÃ¡mjegye kell.');
    }
}

// =====================================================
// STATION 3: A VÃ‰SZHELYZET SZIMULÃTOR
// =====================================================

function selectScenario(id) {
    // Remove selected class from all cards
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selected class to clicked card
    const card = document.querySelector(`.scenario-card[onclick="selectScenario(${id})"]`);
    if (card) card.classList.add('selected');

    // Check the radio button
    const radio = document.getElementById(`scenario-${id}`);
    if (radio) radio.checked = true;
}

function checkStation3() {
    const selected = document.querySelector('input[name="scenario"]:checked');

    if (!selected) {
        showFeedback(3, false, 'âš ï¸ KÃ©rlek, vÃ¡lassz egy lehetÅ‘sÃ©get!');
        return;
    }

    if (selected.value === '2') {
        unlockDigit(2, 2);
        showFeedback(3, true, 'âœ… Helyes! Elektromos tÃ¼zet (kenyÃ©rpirÃ­tÃ³) TILOS vÃ­zzel oltani! Megszerezted a harmadik szÃ¡mjegyet (2)!');
        setTimeout(() => showScreen('main-menu'), 2000);
    } else {
        showFeedback(3, false, 'âŒ VeszÃ©lyes dÃ¶ntÃ©s! Melyik esetben okozhat Ã¡ramÃ¼tÃ©st a vÃ­z?');
    }
}

// =====================================================
// STATION 4: A BIZTONSÃGI SZÃ‰F
// =====================================================

function checkStation4() {
    const input = document.getElementById('answer-4');
    const answer = input.value.trim();

    // 104 + 105 + 107 = 316 -> Last digit is 6
    if (answer === '6') {
        unlockDigit(3, 6);
        showFeedback(4, true, 'âœ… Helyes! A szÃ¡mok Ã¶sszege 316, az utolsÃ³ szÃ¡mjegy a 6. Megszerezted a negyedik szÃ¡mjegyet (6)!');
        setTimeout(() => showScreen('main-menu'), 2000);
    } else {
        showFeedback(4, false, 'âŒ Nem jÃ³ vÃ¡lasz. SzÃ¡mold Ãºjra: 104 + 105 + 107 = ? Mi az utolsÃ³ szÃ¡mjegy?');
    }
}

// =====================================================
// STATION 5: AZ IGAZSÃG DETEKTORA
// =====================================================

// Store user answers: index -> boolean (true/false)
const quizAnswers = new Array(10).fill(null);

function answerQuiz(btn, isTrue) {
    const quizItem = btn.closest('.quiz-item');
    const buttons = quizItem.querySelectorAll('.btn-quiz');
    const index = Array.from(document.querySelectorAll('.quiz-item')).indexOf(quizItem);

    // Update UI
    buttons.forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');

    // Store answer
    quizAnswers[index] = isTrue;

    // Check if all answered
    const allAnswered = quizAnswers.every(a => a !== null);
    const checkBtn = document.getElementById('quiz-check-btn');
    if (checkBtn) {
        checkBtn.disabled = !allAnswered;
        if (allAnswered) {
            checkBtn.classList.remove('btn-secondary');
            checkBtn.classList.add('btn-primary');
        }
    }
}

function checkStation5() {
    const quizItems = document.querySelectorAll('.quiz-item');
    let correctCount = 0;
    let allCorrect = true;

    quizItems.forEach((item, index) => {
        const isCorrectAnswer = item.dataset.correct === 'true';
        const userAnswer = quizAnswers[index];

        // Reset classes
        item.classList.remove('correct-answer', 'wrong-answer');

        if (userAnswer === isCorrectAnswer) {
            item.classList.add('correct-answer');
            correctCount++;
        } else {
            item.classList.add('wrong-answer');
            allCorrect = false;
        }
    });

    // Update counter display
    const counterDisplay = document.getElementById('correct-count');
    if (counterDisplay) counterDisplay.textContent = correctCount;

    if (allCorrect) {
        const finalDigit = 5;
        unlockDigit(4, finalDigit);
        showFeedback(5, true, 'âœ… ZseniÃ¡lis! Minden kÃ©rdÃ©sre helyesen vÃ¡laszoltÃ¡l. Megszerezted az utolsÃ³ szÃ¡mjegyet (5)!');

        setTimeout(() => {
            showScreen('main-menu'); // Return to main menu instead of final screen directly
        }, 2500);
    } else {
        showFeedback(5, false, `âŒ MÃ©g nem tÃ¶kÃ©letes. ${correctCount} / 10 vÃ¡lasz helyes. NÃ©zd Ã¡t a pirossal jelÃ¶lt kÃ©rdÃ©seket!`);
    }
}

// =====================================================
// FINAL CODE CHECK
// =====================================================

function checkFinalCode() {
    const input = document.getElementById('final-code');
    const feedback = document.getElementById('final-feedback');
    const answer = input.value.trim();

    if (answer === '') {
        feedback.textContent = 'âŒ KÃ©rlek, Ã­rd be az 5 szÃ¡mjegyÅ± kÃ³dot!';
        feedback.classList.remove('correct');
        feedback.classList.add('show', 'incorrect');
        return;
    }

    if (answer === gameState.correctCode) {
        feedback.textContent = 'âœ… Helyes kÃ³d! Az ajtÃ³ kinyÃ­lik...';
        feedback.classList.remove('incorrect');
        feedback.classList.add('show', 'correct');

        setTimeout(() => {
            showScreen('victory-screen');
        }, 2000);
    } else {
        feedback.textContent = 'âŒ Helytelen kÃ³d! EllenÅ‘rizd a megszerzett szÃ¡mjegyeket!';
        feedback.classList.remove('correct');
        feedback.classList.add('show', 'incorrect');

        // Shake animation
        input.style.animation = 'none';
        setTimeout(() => {
            input.style.animation = 'shake 0.5s';
        }, 10);
    }
}

// =====================================================
// EVENT LISTENERS
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize code display
    updateCodeDisplay();

    // Add Enter key support for inputs
    const inputs = ['answer-1', 'answer-2', 'answer-4', 'answer-5', 'final-code'];
    inputs.forEach((inputId, index) => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    if (inputId === 'final-code') {
                        checkFinalCode();
                    } else {
                        // Determine station number based on ID
                        const stationNum = parseInt(inputId.split('-')[1]);
                        if (stationNum === 1) checkStation1();
                        else if (stationNum === 2) checkStation2();
                        else if (stationNum === 4) checkStation4();
                        else if (stationNum === 5) checkStation5();
                    }
                }
            });
        }
    });

    // Prevent non-numeric input for number fields
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    });

    // Final code input formatting
    const finalCodeInput = document.getElementById('final-code');
    if (finalCodeInput) {
        finalCodeInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 5);
        });
    }

    // Ensure we start at the intro screen
    showScreen('intro-screen');
});

// =====================================================
// KEYBOARD SHORTCUTS (Optional Easter Egg)
// =====================================================

document.addEventListener('keydown', (e) => {
    // Press 'R' to restart (only on victory screen)
    if (e.key === 'r' && gameState.currentScreen === 'victory-screen') {
        restartGame();
    }
});
í *cascade08íô*cascade08ô‰ *cascade08‰*cascade08º *cascade08º»*cascade08»‹ *cascade08‹*cascade08û *cascade08ûû*cascade08ûÑ *cascade08ÑÑ*cascade08ÑÌ *cascade08ÌÒ*cascade08ÒÕ *cascade08ÕÖ*cascade08Ö× *cascade08×İ*cascade08İñ *cascade08ñò*cascade08òó *cascade08óø*cascade08ø *cascade08› *cascade08›*cascade08¢ *cascade08¢£*cascade08£¤ *cascade08¤­*cascade08­Ö *cascade08ÖØ*cascade08ØÙ *cascade08ÙÛ*cascade08Ûİ *cascade08İæ*cascade08æè *cascade08èé*cascade08é£	 *cascade08£	¤	*cascade08¤	ÿ> *cascade08ÿ>í?*cascade08í?ó? *cascade08ó?ı?*cascade08ı?ş? *cascade08ş?·@*cascade08·@¸@ *cascade08¸@¿@*cascade08¿@À@ *cascade08À@Î@*cascade08Î@Ï@ *cascade08Ï@Ú@*cascade08Ú@İ@ *cascade08İ@¤A*cascade08¤A¦A *cascade08¦A©A*cascade08©AªA *cascade08ªAâA*cascade08âAãA *cascade08ãAøA*cascade08øAùA *cascade08ùAúA*cascade08úAûA *cascade08ûA†B*cascade08†B‡B *cascade08‡BB*cascade08BŸB *cascade08ŸB B*cascade08 B£B *cascade08£BÜB*cascade08ÜBİB *cascade08İB›C*cascade08›CœC *cascade08œC±C*cascade08±C²C *cascade08²C÷C*cascade08÷CøC *cascade08øCûC*cascade08ûCüC *cascade08üC‚E*cascade08‚EƒE *cascade08ƒE‡F*cascade08‡F‰F *cascade08‰FæF*cascade08æFçF *cascade08çFèF*cascade08èFéF *cascade08éFúF*cascade08úFûF *cascade08ûFŒG*cascade08ŒGG *cascade08G¯G*cascade08¯G°G *cascade08°GÕG*cascade08ÕGÖG *cascade08ÖGëG*cascade08ëGìG*cascade08ìGíG *cascade08íGŠH*cascade08ŠH‹H *cascade08‹HÂH*cascade08ÂHÃH *cascade08ÃHÅH*cascade08ÅHÆH *cascade08ÆHÉH*cascade08ÉHÊH *cascade08ÊHÍH*cascade08ÍHÎH *cascade08ÎHØH*cascade08ØHÙH *cascade08ÙHâH*cascade08âHãH *cascade08ãHùH*cascade08ùHúH *cascade08úH˜I*cascade08˜I™I *cascade08™II*cascade08IŸI *cascade08ŸIÔI*cascade08ÔIÕI *cascade08ÕIäI*cascade08äIåI*cascade08åIŠJ*cascade08ŠJ‹J *cascade08‹JJ*cascade08JŸJ *cascade08ŸJªJ*cascade08ªJ«J *cascade08«J¬J*cascade08¬J­J *cascade08­J¹J*cascade08¹JºJ *cascade08ºJ»J*cascade08»JÁJ *cascade08ÁJ„K*cascade08„KK *cascade08K¢K*cascade08¢K¤K *cascade08¤K±K*cascade08±K²K *cascade08²K£L*cascade08£L¤L *cascade08¤L‚M*cascade08‚MƒM *cascade08ƒMM*cascade08MM *cascade08M M*cascade08 M¡M *cascade08¡M¢M*cascade08¢M£M *cascade08£M®M*cascade08®M¯M *cascade08¯M½M*cascade08½M¾M *cascade08¾M¼N*cascade08¼N¾N *cascade08¾N¿N*cascade08¿NÀN *cascade08ÀNÏN*cascade08ÏNĞN *cascade08ĞNÒN*cascade08ÒNÓN *cascade08ÓNúN*cascade08úNûN *cascade08ûN†O*cascade08†O‡O *cascade08‡O£P*cascade08£P¤P *cascade08¤PÉQ*cascade08ÉQÊQ *cascade08ÊQàQ*cascade08àQáQ *cascade08áQëQ*cascade08ëQìQ *cascade08ìQôQ*cascade08ôQõQ *cascade08õQ‚R*cascade08‚R„R *cascade08„R±R*cascade08±R²R *cascade08²RÖR*cascade08ÖR×R *cascade08×RˆS*cascade08ˆS‰S *cascade08‰S¬S*cascade08¬S­S *cascade08­SäS*cascade08äSåS *cascade08åS™T*cascade08™T›T *cascade08›T®T*cascade08®T¯T *cascade08¯TÏT*cascade08ÏTĞT *cascade08ĞT§U*cascade08§U«U *cascade08«U°U*cascade08°U²U *cascade08²U¹U*cascade08¹UºU *cascade08ºUóU*cascade08óUôU *cascade08ôUùV*cascade08ùVúV *cascade08úV¯Z*cascade08¯Z³Z *cascade08³ZÉƒ*cascade08ÉƒÎƒ *cascade082=file:///C:/Users/Tomi/Oktat%C3%A1s/fire-escape-room/script.js