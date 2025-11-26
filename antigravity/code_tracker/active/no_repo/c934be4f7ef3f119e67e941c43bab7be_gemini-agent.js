�~// === Gemini AI Agent - Agentic AI Core ===
// Implements Planning, Tool Use, Self-Correction, and Persistence

class GeminiAgent {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.conversationHistory = [];
        this.currentSubject = null;
        this.studentProfile = null;
        this.systemPrompt = null;
    }

    /**
     * Initialize the agent with subject and student context
     */
    async initialize(subject, studentProfile) {
        this.currentSubject = subject;
        this.studentProfile = studentProfile;
        this.systemPrompt = this.buildSystemPrompt(subject);

        if (CONFIG.DEBUG) {
            console.log('Agent initialized:', { subject, studentProfile });
        }
    }

    /**
     * Build subject-specific system prompt (Prompt Engineering)
     */
    buildSystemPrompt(subject) {
        const basePrompt = `Te egy AI tanári asszisztens vagy, aki az Agentic AI paradigma szerint működik.

**Az Antigravity Paradigma 4 Pillére:**

1. **PLANNING (Tervezés)**: Mielőtt válaszolsz, tervezd meg a tanítási stratégiát.
   - Milyen módszert használsz? (Szókratészi kérdés, közvetlen magyarázat, analógia, vizualizáció?)
   - Milyen előismereteket feltételezel?
   - Mi a pedagógiai cél?

2. **TOOL USE (Eszközhasználat)**: Jelezd, ha külső eszközre van szükség.
   - Szimuláció indítása: [TOOL: SIMULATION <név>]
   - Vizualizáció generálás: [TOOL: VISUALIZATION <típus>]
   - Tudásgráf lekérdezés: [TOOL: KNOWLEDGE_GRAPH <fogalom>]

3. **SELF-CORRECTION (Önellenőrzés)**: Válaszolás előtt ellenőrizd:
   - Megfelelő a nyelvi szint? (5-8. osztály)
   - Pontos a szakmai tartalom?
   - Pedagógiailag hatékony? (nem túl közvetlen válasz?)

4. **PERSISTENCE (Memória)**: Emlékezz a diák:
   - Korábbi válaszaira és tévhiteire
   - Tanulási stílusára (vizuális/auditív/kinetikus)
   - Elsajátított fogalmaira`;

        const subjectSpecific = subject === 'science'
            ? this.getSciencePrompt()
            : this.getGeographyPrompt();

        return `${basePrompt}\n\n${subjectSpecific}`;
    }

    /**
     * Science-specific prompt (5-6. évfolyam)
     */
    getSciencePrompt() {
        return `**TANTÁRGY: Természettudomány (5-6. évfolyam)**

**OBJECTIVE**: Segítsd a diákot a természettudományos fogalmak (anyagok, halmazállapotok, folyamatok) megértésében a NAT 2020 szerint.

**CONSTRAINTS**:
- SOHA ne add meg a választ közvetlenül
- Használj rávezető kérdéseket (Szókratészi módszer)
- Ha tévhitet (misconception) észlelsz, NE javítsd ki azonnal
  1. Kérd meg, magyarázza el, miért gondolja így
  2. Adj ellenpéldát vagy analógiát
  3. Vezess rá a helyes megoldásra
- Használj mindennapi példákat (konyha, otthon, iskola)
- Fogalmakat fokozatosan építsd fel (egyszerűtől a bonyolulthoz)

**TONE**: Barátságos, lelkes, bátorító, kíváncsi (mint egy nagy testvér vagy mentor)

**GYAKORI TÉVHITEK** (figyelj rájuk):
- "A cukor elolvad a teában" → oldódás vs. olvadás
- "A párolgás csak forraláskor történik" → folyamatos folyamat
- "A levegő nem anyag" → gáz is anyag
- "A szilárd anyagok részecskéi nem mozognak" → mindig mozognak

**PÉLDA INTERAKCIÓK**:

Diák: "A cukor elolvad a vízben."
AI: "Érdekes! Mondd, ha egy darab vajat teszel hideg vízbe, az is eltűnik, mint a cukor?"
(Szókratészi kontrasztálás)

Diák: "Nem értem, miért párolognak a tócsák."
AI: "Képzeld el, hogy a vízmolekulák kis labdák, amik ugrálnak. Melyik labda tud kiugrani a papírdobozból: a lassú vagy a gyors?"
(Analógia + mikroszintű modell)`;
    }

    /**
     * Geography-specific prompt (7-8. évfolyam)
     */
    getGeographyPrompt() {
        return `**TANTÁRGY: Földrajz (7-8. évfolyam)**

**OBJECTIVE**: Fejleszd a diák térbeli intelligenciáját, rendszerszemléletét és a természeti-társadalmi folyamatok összekapcsolásának képességét.

**CONSTRAINTS**:
- Hozz létre kapcsolatokat természeti és társadalmi jelenségek között (ok-okozat)
- Használj VALÓS, AKTUÁLIS példákat (magyar városok, KSH adatok, hírek)
- Tedd SZEMÉLYESSÉ (diák városa, környezete)
- Ösztönözd a kritikai gondolkodást ("Szerinted mi történne, ha...?")
- Használj több skálát: lokális → regionális → globális
- Hangsúlyozd a földrajzi folyamatok időbeliségét (múlt-jelen-jövő)

**TONE**: Szakértő, de közérthető; objektív, de engedd meg a vitát

**TOOLS**:
- Korfák és demográfiai adatok
- Térképek (domborzat, klíma, gazdaság)
- Statisztikák és grafikonok
- Szerepjátékok (pl. "Te vagy a polgármester...")

**PEDAGÓGIAI MÓDSZEREK**:

1. **Helyi → Globális**:
   "Debrecenben hogyan változott a népesség 50 év alatt? Most nézzük meg Japánt..."

2. **Döntési szimul ációk**:
   "Te vagy a pénzügyminiszter. A korfa alapján az ország elöregedik. 3 választási lehetőséged van..."

3. **Ok-okozati térképezés**:
   "A születésszám csökken → kevesebb óvoda kell → pedagógusokat elbocsátanak → ..."

**PÉLDA INTERAKCIÓK**:

Diák: "Nem értem ezt a korfát."
AI: "Hol élsz? Indítsunk egy felfedezést a saját városod adataiból! [TOOL: VISUALIZATION korfa_magyarorszag]"

Diák: "Miért fontos ez?"
AI: "Képzeld el, hogy 2040-ben Te fizetsz nyugdíjat a nagyszüle идnek. De a korfából látszik, hogy 2 nyugdíjas jut majd minden dolgozóra. Szerinted kijön a matek?"`;
    }

    /**
     * PLANNING MODULE: Create a teaching strategy before responding
     */
    async planResponse(userMessage, context) {
        const plan = {
            method: null,          // 'socratic' | 'direct' | 'analogy' | 'simulation'
            difficulty: 'medium',  // 'easy' | 'medium' | 'hard'
            scaffolding: 0,        // 0-3 (none to full demonstration)
            misconceptionDetected: null,
            requiredTools: [],
            pedagogicalGoal: null
        };

        // Detect current understanding level
        const conceptMastery = this.getConceptMastery(userMessage);

        // Detect misconceptions
        plan.misconceptionDetected = this.detectMisconception(userMessage);

        // Choose method based on context
        if (plan.misconceptionDetected) {
            plan.method = 'socratic';  // Use questions to guide discovery
            plan.pedagogicalGoal = 'Correct misconception without demotivating';
        } else if (conceptMastery < CONFIG.ADAPTIVE.ZPD_MIN) {
            plan.method = 'simulation';  // Too hard, need scaffolding
            plan.scaffolding = 2;
            plan.requiredTools = ['VISUALIZATION'];
            plan.pedagogicalGoal = 'Build prerequisites with visual support';
        } else if (conceptMastery > CONFIG.ADAPTIVE.ZPD_MAX) {
            plan.method = 'challenge';  // Too easy, level up
            plan.difficulty = 'hard';
            plan.pedagogicalGoal = 'Extend knowledge with advanced concepts';
        } else {
            plan.method = 'guided';  // In ZPD, perfect for learning
            plan.pedagogicalGoal = 'Guide through discovery in ZPD';
        }

        if (CONFIG.DEBUG) {
            console.log('Teaching plan:', plan);
        }

        return plan;
    }

    /**
     * TOOL USE: Detect and prepare tool calls
     */
    detectToolNeeds(message, plan) {
        const tools = [];

        // Check if simulation would help
        if (message.match(/(nem értem|mi történik|hogyan|miért)/i)) {
            if (this.currentSubject === 'science') {
                tools.push({ type: 'SIMULATION', target: 'particle_model' });
            } else {
                tools.push({ type: 'VISUALIZATION', target: 'population_pyramid' });
            }
        }

        // Check if knowledge graph lookup needed
        const concepts = this.extractConcepts(message);
        if (concepts.length > 0) {
            tools.push({ type: 'KNOWLEDGE_GRAPH', target: concepts[0] });
        }

        return tools;
    }

    /**
     * SELF-CORRECTION: Validate response before sending
     */
    async validateResponse(response) {
        const issues = [];

        // Check 1: Language complexity (should be age-appropriate)
        const complexWords = this.countComplexWords(response);
        if (complexWords > 5) {
            issues.push('Too many complex words for grade level');
        }

        // Check 2: Not giving direct answer (for problem-solving questions)
        if (response.match(/^(A válasz:|A megoldás:|Ez azért van, mert:)/i)) {
            issues.push('Too direct, should use Socratic method');
        }

        // Check 3: Length (too short = not helpful, too long = overwhelming)
        const wordCount = response.split(/\s+/).length;
        if (wordCount < 20) {
            issues.push('Response too short');
        } else if (wordCount > 150) {
            issues.push('Response too long, risk of cognitive overload');
        }

        if (CONFIG.DEBUG && issues.length > 0) {
            console.warn('Response validation issues:', issues);
        }

        return {
            valid: issues.length === 0,
            issues: issues
        };
    }

    /**
     * PERSISTENCE: Manage conversation history and context
     */
    addToHistory(role, content) {
        this.conversationHistory.push({
            role: role,  // 'user' or 'model'
            parts: [{ text: content }],
            timestamp: Date.now()
        });

        // Keep only last N messages to avoid token limits
        if (this.conversationHistory.length > CONFIG.UI.CHAT_MAX_MESSAGES) {
            this.conversationHistory = this.conversationHistory.slice(-CONFIG.UI.CHAT_MAX_MESSAGES);
        }
    }

    /**
     * Main entry point: Generate AI response
     */
    async generateResponse(userMessage) {
        try {
            // Step 1: PLANNING
            const plan = await this.planResponse(userMessage, this.studentProfile);

            // Step 2: TOOL USE (detect needs)
            const tools = this.detectToolNeeds(userMessage, plan);

            // Step 3: Build API request
            const requestBody = this.buildGeminiRequest(userMessage, plan);

            // Step 4: Call Gemini API
            const response = await this.callGeminiAPI(requestBody);

            // Step 5: SELF-CORRECTION (validate before returning)
            const validation = await this.validateResponse(response);

            if (!validation.valid && CONFIG.DEBUG) {
                console.warn('Response needs improvement:', validation.issues);
            }

            // Step 6: PERSISTENCE (save to history)
            this.addToHistory('user', userMessage);
            this.addToHistory('model', response);

            return {
                text: response,
                tools: tools,
                plan: plan,
                validation: validation
            };

        } catch (error) {
            console.error('Error generating response:', error);
            throw error;
        }
    }

    /**
     * Build Gemini API request payload
     */
    buildGeminiRequest(userMessage, plan) {
        const contents = [
            {
                role: 'user',
                parts: [{ text: this.systemPrompt }]
            },
            {
                role: 'model',
                parts: [{ text: 'Értem. Készen állok a tanításra az Agentic AI paradigma szerint.' }]
            },
            ...this.conversationHistory,
            {
                role: 'user',
                parts: [{ text: userMessage }]
            }
        ];

        return {
            contents: contents,
            generationConfig: {
                temperature: CONFIG.GEMINI.TEMPERATURE,
                topP: CONFIG.GEMINI.TOP_P,
                topK: CONFIG.GEMINI.TOP_K,
                maxOutputTokens: CONFIG.GEMINI.MAX_OUTPUT_TOKENS
            },
            safetySettings: CONFIG.GEMINI.SAFETY_SETTINGS
        };
    }

    /**
     * Call Gemini API
     */
    async callGeminiAPI(requestBody) {
        const url = `${CONFIG.GEMINI.API_ENDPOINT}?key=${this.apiKey}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`Gemini API error: ${error.error?.message || response.statusText}`);
        }

        const data = await response.json();

        // Extract text from response
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

        if (!text) {
            throw new Error('No text in Gemini response');
        }

        return text;
    }

    /**
     * Helper: Get concept mastery from student profile
     */
    getConceptMastery(message) {
        const concepts = this.extractConcepts(message);
        if (concepts.length === 0 || !this.studentProfile) {
            return CONFIG.KNOWLEDGE_TRACING.INITIAL_MASTERY;
        }

        const concept = concepts[0];
        return this.studentProfile.conceptMastery?.[concept] || CONFIG.KNOWLEDGE_TRACING.INITIAL_MASTERY;
    }

    /**
     * Helper: Extract key concepts from message
     */
    extractConcepts(message) {
        // Simple keyword extraction (can be enhanced with NLP)
        const scienceKeywords = ['halmazállapot', 'oldódás', 'olvadás', 'párolgás', 'forrás', 'szilárd', 'folyékony', 'gáz', 'anyag', 'részecske'];
        const geographyKeywords = ['korfa', 'népesség', 'születés', 'halálozás', 'elöregedés', 'urbanizáció', 'migráció'];

        const keywords = this.currentSubject === 'science' ? scienceKeywords : geographyKeywords;

        return keywords.filter(keyword => message.toLowerCase().includes(keyword));
    }

    /**
     * Helper: Detect misconceptions
     */
    detectMisconception(message) {
        const misconceptions = {
            science: [
                { pattern: /cukor.*elolvad.*víz/i, type: 'oldódás_vs_olvadás' },
                { pattern: /levegő.*nem.*anyag/i, type: 'gáz_anyag' },
                { pattern: /szilárd.*nem.*mozog/i, type: 'részecske_mozgás' }
            ],
            geography: [
                { pattern: /korfa.*csak.*öregek/i, type: 'korfa_értelmezés' }
            ]
        };

        const relevant = misconceptions[this.currentSubject] || [];

        for (const misc of relevant) {
            if (message.match(misc.pattern)) {
                return misc.type;
            }
        }

        return null;
    }

    /**
     * Helper: Count complex words (for age-appropriateness check)
     */
    countComplexWords(text) {
        const complexWords = [
            'paradigma', 'komplex', 'absztrakt', 'szintetizál',
            'transzkripció', 'fotoszintézis', 'demográfiai', 'urbanizáció'
        ];

        let count = 0;
        complexWords.forEach(word => {
            if (text.toLowerCase().includes(word)) count++;
        });

        return count;
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        this.conversationHistory = [];
    }

    /**
     * Get conversation history (for persistence)
     */
    getHistory() {
        return this.conversationHistory;
    }

    /**
     * Load conversation history (from localStorage)
     */
    loadHistory(history) {
        this.conversationHistory = history || [];
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GeminiAgent;
}
�~*cascade082sfile:///C:/Users/Tomi/Term%C3%A9szettudom%C3%A1ny,f%C3%B6ldrajz%20%C3%B6n%C3%A1ll%C3%B3%20modell/js/gemini-agent.js