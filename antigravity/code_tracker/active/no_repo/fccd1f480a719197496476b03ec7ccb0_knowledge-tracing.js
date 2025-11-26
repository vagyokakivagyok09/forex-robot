�R// === Knowledge Tracing System ===
// Tracks student's concept-level mastery using Bayesian Knowledge Tracing

class KnowledgeTracer {
    constructor(studentId) {
        this.studentId = studentId;
        this.conceptMastery = {};      // { 'concept_id': probability }
        this.interactionHistory = [];  // [{ concept, correct, timestamp }]
        this.learningStyle = null;     // 'visual' | 'auditory' | 'kinesthetic'
        this.consecutiveCorrect = {};  // Track streaks
        this.consecutiveWrong = {};
    }

    /**
     * Initialize concept mastery from knowledge graph
     */
    initializeFromKnowledgeGraph(knowledgeGraph) {
        knowledgeGraph.nodes.forEach(node => {
            if (!this.conceptMastery[node.id]) {
                this.conceptMastery[node.id] = CONFIG.KNOWLEDGE_TRACING.INITIAL_MASTERY;
            }
        });
    }

    /**
     * Update mastery after student interaction
     */
    updateMastery(concept, wasCorrect, questionDifficulty = 'medium') {
        const currentMastery = this.conceptMastery[concept] || CONFIG.KNOWLEDGE_TRACING.INITIAL_MASTERY;

        // Bayesian Knowledge Tracing update
        let change = 0;

        if (wasCorrect) {
            // Correct answer increases mastery
            change = CONFIG.KNOWLEDGE_TRACING.CORRECT_ANSWER_BOOST;

            // Harder questions boost more
            if (questionDifficulty === 'hard') {
                change *= 1.5;
            }

            // Track streak
            this.consecutiveCorrect[concept] = (this.consecutiveCorrect[concept] || 0) + 1;
            this.consecutiveWrong[concept] = 0;

        } else {
            // Wrong answer decreases mastery
            change = CONFIG.KNOWLEDGE_TRACING.WRONG_ANSWER_PENALTY;

            // Track streak
            this.consecutiveWrong[concept] = (this.consecutiveWrong[concept] || 0) + 1;
            this.consecutiveCorrect[concept] = 0;
        }

        // Apply learning rate
        change *= CONFIG.KNOWLEDGE_TRACING.LEARNING_RATE;

        // Update mastery (keep between 0 and 1)
        let newMastery = currentMastery + change;
        newMastery = Math.max(0, Math.min(1, newMastery));

        this.conceptMastery[concept] = newMastery;

        // Record interaction
        this.interactionHistory.push({
            concept: concept,
            correct: wasCorrect,
            difficulty: questionDifficulty,
            masteryBefore: currentMastery,
            masteryAfter: newMastery,
            timestamp: Date.now()
        });

        if (CONFIG.DEBUG) {
            console.log(`Mastery updated: ${concept} ${currentMastery.toFixed(2)} → ${newMastery.toFixed(2)} (${wasCorrect ? '✓' : '✗'})`);
        }

        return newMastery;
    }

    /**
     * Get mastery level for a concept
     */
    getMastery(concept) {
        return this.conceptMastery[concept] || CONFIG.KNOWLEDGE_TRACING.INITIAL_MASTERY;
    }

    /**
     * Get all concepts within ZPD (Zone of Proximal Development)
     */
    getConceptsInZPD() {
        const zpd = [];

        for (const [concept, mastery] of Object.entries(this.conceptMastery)) {
            if (mastery >= CONFIG.ADAPTIVE.ZPD_MIN && mastery <= CONFIG.ADAPTIVE.ZPD_MAX) {
                zpd.push({ concept, mastery });
            }
        }

        // Sort by mastery (prioritize concepts closer to mastery threshold)
        zpd.sort((a, b) => b.mastery - a.mastery);

        return zpd;
    }

    /**
     * Get mastered concepts
     */
    getMasteredConcepts() {
        const mastered = [];

        for (const [concept, mastery] of Object.entries(this.conceptMastery)) {
            if (mastery >= CONFIG.KNOWLEDGE_TRACING.MASTERY_THRESHOLD) {
                mastered.push({ concept, mastery });
            }
        }

        return mastered;
    }

    /**
     * Get concepts student is struggling with
     */
    getStrugglingConcepts() {
        const struggling = [];

        for (const [concept, mastery] of Object.entries(this.conceptMastery)) {
            if (mastery < CONFIG.KNOWLEDGE_TRACING.STRUGGLE_THRESHOLD) {
                struggling.push({ concept, mastery });
            }
        }

        // Prioritize by how many wrong answers in a row
        struggling.sort((a, b) => {
            const streakA = this.consecutiveWrong[a.concept] || 0;
            const streakB = this.consecutiveWrong[b.concept] || 0;
            return streakB - streakA;
        });

        return struggling;
    }

    /**
     * Detect learning style based on interaction patterns
     */
    detectLearningStyle() {
        // Analyze which type of questions/interactions led to better performance
        const visualScore = 0;
        const auditoryScore = 0;
        const kinestheticScore = 0;

        // TODO: Implement ML-based detection
        // For now, default to visual (most common for STEM subjects)

        this.learningStyle = 'visual';
        return this.learningStyle;
    }

    /**
     * Generate student performance report
     */
    generateReport() {
        const report = {
            studentId: this.studentId,
            totalConcepts: Object.keys(this.conceptMastery).length,
            mastered: this.getMasteredConcepts().length,
            inProgress: this.getConceptsInZPD().length,
            struggling: this.getStrugglingConcepts().length,
            averageMastery: this.getAverageMastery(),
            totalInteractions: this.interactionHistory.length,
            recentAccuracy: this.getRecentAccuracy(10),
            learningCurve: this.getLearningCurve(),
            recommendations: this.generateRecommendations()
        };

        return report;
    }

    /**
     * Get average mastery across all concepts
     */
    getAverageMastery() {
        const values = Object.values(this.conceptMastery);
        if (values.length === 0) return 0;

        const sum = values.reduce((a, b) => a + b, 0);
        return sum / values.length;
    }

    /**
     * Get recent accuracy (last N interactions)
     */
    getRecentAccuracy(n = 10) {
        const recent = this.interactionHistory.slice(-n);
        if (recent.length === 0) return 0;

        const correct = recent.filter(i => i.correct).length;
        return correct / recent.length;
    }

    /**
     * Get learning curve data for visualization
     */
    getLearningCurve() {
        const curve = [];
        let runningTotal = 0;
        let count = 0;

        this.interactionHistory.forEach((interaction, index) => {
            runningTotal += interaction.masteryAfter;
            count++;

            // Sample every 5th interaction to avoid too many data points
            if (index % 5 === 0) {
                curve.push({
                    x: index,
                    y: runningTotal / count,
                    timestamp: interaction.timestamp
                });
            }
        });

        return curve;
    }

    /**
     * Generate personalized learning recommendations
     */
    generateRecommendations() {
        const recommendations = [];

        // Recommendation 1: Focus areas
        const struggling = this.getStrugglingConcepts();
        if (struggling.length > 0) {
            recommendations.push({
                type: 'focus',
                priority: 'high',
                message: `Érdemes gyakorolni: ${struggling.slice(0, 3).map(c => c.concept).join(', ')}`,
                concepts: struggling.slice(0, 3).map(c => c.concept)
            });
        }

        // Recommendation 2: Ready for challenge
        const zpd = this.getConceptsInZPD();
        if (zpd.length > 0 && zpd[0].mastery > 0.65) {
            recommendations.push({
                type: 'challenge',
                priority: 'medium',
                message: `Készen állsz nehezebb feladatokra: ${zpd[0].concept}`,
                concepts: [zpd[0].concept]
            });
        }

        // Recommendation 3: Streak bonus
        const streaks = Object.entries(this.consecutiveCorrect)
            .filter(([_, count]) => count >= 3)
            .sort((a, b) => b[1] - a[1]);

        if (streaks.length > 0) {
            recommendations.push({
                type: 'achievement',
                priority: 'low',
                message: `Szép! ${streaks[0][1]} helyes válasz egymás után: ${streaks[0][0]} 🎯`,
                concepts: [streaks[0][0]]
            });
        }

        // Recommendation 4: Learning style
        if (!this.learningStyle) {
            this.detectLearningStyle();
        }

        if (this.learningStyle === 'visual') {
            recommendations.push({
                type: 'style',
                priority: 'medium',
                message: 'Vizuális típus vagy - használd a szimulációkat!',
                action: 'enable_visualizations'
            });
        }

        return recommendations;
    }

    /**
     * Export data for persistence (localStorage)
     */
    export() {
        return {
            studentId: this.studentId,
            conceptMastery: this.conceptMastery,
            interactionHistory: this.interactionHistory,
            learningStyle: this.learningStyle,
            consecutiveCorrect: this.consecutiveCorrect,
            consecutiveWrong: this.consecutiveWrong,
            lastUpdated: Date.now()
        };
    }

    /**
     * Import data from storage
     */
    import(data) {
        if (!data) return;

        this.studentId = data.studentId;
        this.conceptMastery = data.conceptMastery || {};
        this.interactionHistory = data.interactionHistory || [];
        this.learningStyle = data.learningStyle;
        this.consecutiveCorrect = data.consecutiveCorrect || {};
        this.consecutiveWrong = data.consecutiveWrong || {};
    }

    /**
     * Reset all progress (for testing or new subject)
     */
    reset() {
        this.conceptMastery = {};
        this.interactionHistory = [];
        this.consecutiveCorrect = {};
        this.consecutiveWrong = {};
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeTracer;
}
�R*cascade082xfile:///C:/Users/Tomi/Term%C3%A9szettudom%C3%A1ny,f%C3%B6ldrajz%20%C3%B6n%C3%A1ll%C3%B3%20modell/js/knowledge-tracing.js