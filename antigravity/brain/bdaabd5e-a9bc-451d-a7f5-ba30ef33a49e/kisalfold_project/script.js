// Data
const tfQuestions = [
    { q: "A Kisalföld Magyarország északkeleti részén található.", a: false },
    { q: "A Kisalföld három ország területére nyúlik át: Magyarország, Szlovákia, Ausztria.", a: true },
    { q: "A Szigetköz a Duna és a Rába között helyezkedik el.", a: false },
    { q: "A Hanság régen hatalmas mocsárvilág volt, amit lecsapoltak.", a: true },
    { q: "A Marcal-medence a Kisalföld északi, hegyvidéki része.", a: false }
];

const mcQuestions = [
    { q: "Melyik két folyó hordaléka alakította ki főleg a Kisalföldet?", options: ["Duna, Tisza", "Duna, Rába", "Rába, Dráva"], a: 1 },
    { q: "Melyik tájegység található a Duna és a Mosoni-Duna között?", options: ["Csallóköz", "Szigetköz", "Rábaköz"], a: 1 },
    { q: "Melyik földtörténeti korban formálta a szél a kavicsos-homokos teraszokat?", options: ["Holocén", "Pleisztocén", "Miocén"], a: 1 },
    { q: "Melyik medence híres a mocsarairól és a Fertő tóról?", options: ["Győri-medence", "Marcal-medence", "Fertő-Hanság-medence"], a: 2 },
    { q: "Hol található a Csallóköz nagyobb része?", options: ["Magyarország", "Ausztria", "Szlovákia"], a: 2 }
];

// Init
document.addEventListener('DOMContentLoaded', () => {
    renderTF();
    renderMC();
    initDragAndDrop();
});

// Render True/False
function renderTF() {
    const container = document.getElementById('tf-questions');
    tfQuestions.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'question-item';
        div.innerHTML = `
            <p>${index + 1}. ${item.q}</p>
            <div class="options">
                <button onclick="checkTF(${index}, true, this)">Igaz</button>
                <button onclick="checkTF(${index}, false, this)">Hamis</button>
            </div>
            <div class="feedback" id="tf-feedback-${index}"></div>
        `;
        container.appendChild(div);
    });
}

function checkTF(index, answer, btn) {
    const correct = tfQuestions[index].a === answer;
    const feedback = document.getElementById(`tf-feedback-${index}`);
    const buttons = btn.parentElement.querySelectorAll('button');

    buttons.forEach(b => b.disabled = true);

    if (correct) {
        btn.classList.add('correct');
        feedback.textContent = "Helyes! ✅";
        feedback.style.color = "var(--success)";
    } else {
        btn.classList.add('incorrect');
        feedback.textContent = "Sajnos nem. ❌";
        feedback.style.color = "var(--error)";
    }
}

// Render Multiple Choice
function renderMC() {
    const container = document.getElementById('mc-questions');
    mcQuestions.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'question-item';
        let buttonsHtml = '';
        item.options.forEach((opt, optIndex) => {
            buttonsHtml += `<button onclick="checkMC(${index}, ${optIndex}, this)">${opt}</button>`;
        });

        div.innerHTML = `
            <p>${index + 1}. ${item.q}</p>
            <div class="options">
                ${buttonsHtml}
            </div>
            <div class="feedback" id="mc-feedback-${index}"></div>
        `;
        container.appendChild(div);
    });
}

function checkMC(qIndex, optIndex, btn) {
    const correct = mcQuestions[qIndex].a === optIndex;
    const feedback = document.getElementById(`mc-feedback-${qIndex}`);
    const buttons = btn.parentElement.querySelectorAll('button');

    buttons.forEach(b => b.disabled = true);

    if (correct) {
        btn.classList.add('correct');
        feedback.textContent = "Helyes! ✅";
        feedback.style.color = "var(--success)";
    } else {
        btn.classList.add('incorrect');
        // Highlight correct answer
        buttons[mcQuestions[qIndex].a].classList.add('correct');
        feedback.textContent = "Nem talált. ❌";
        feedback.style.color = "var(--error)";
    }
}

// Logic Problem
function checkLogic() {
    const input = document.getElementById('logic-answer').value.toLowerCase();
    const feedback = document.getElementById('logic-feedback');

    // Keywords to look for
    const hasSzigetkoz = input.includes('szigetköz');
    const hasCsallokoz = input.includes('csallóköz') || input.includes('szlovákia');

    if (hasSzigetkoz && hasCsallokoz) {
        feedback.textContent = "Tökéletes! Áthaladt a Szigetközön és megérkezett a Csallóközbe (Szlovákiába). 🏆";
        feedback.style.color = "var(--success)";
    } else if (hasSzigetkoz) {
        feedback.textContent = "Részben jó! A Szigetközön valóban áthaladt, de hová érkezett?";
        feedback.style.color = "orange";
    } else {
        feedback.textContent = "Próbáld újra! Nézd meg a térképet: Győr -> Mosoni-Duna -> ? -> Duna -> ?";
        feedback.style.color = "var(--error)";
    }
}

// Drag and Drop
function initDragAndDrop() {
    const draggables = document.querySelectorAll('.draggable');
    const dropZones = document.querySelectorAll('.drop-zone');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', () => {
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging');
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            if (!zone.hasChildNodes()) {
                zone.classList.add('drag-over');
            }
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });

        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('drag-over');

            const draggable = document.querySelector('.dragging');
            if (!draggable) return;

            const zoneRegion = zone.getAttribute('data-region');
            const itemRegion = draggable.getAttribute('data-id');

            if (zoneRegion === itemRegion) {
                // Correct match
                zone.appendChild(draggable);
                zone.classList.add('correct');
                draggable.setAttribute('draggable', 'false');
                draggable.style.cursor = 'default';
            } else {
                // Incorrect match animation
                zone.classList.add('incorrect');
                setTimeout(() => zone.classList.remove('incorrect'), 500);
            }
        });
    });
}
