�]// === Adaptive Engine - The System's "Brain" ===
// Connects all components and makes real-time adaptive decisions

class AdaptiveEngine {
    constructor(geminiAgent, knowledgeTracer, knowledgeGraph) {
        this.ai = geminiAgent;
        this.tracer = knowledgeTracer;
        this.knowledgeGraph = knowledgeGraph;
        this.currentTopic = null;
        this.difficultyLevel = 'medium'; // 'easy' | 'medium' | 'hard'
    }

    /**
     * Main entry: Process student input and generate adaptive response
     */
    async processInput(userMessage) {
        try {
            // Step 1: Analyze input and update knowledge state
            const analysis = await this.analyzeInput(userMessage);

            // Step 2: Update difficulty based on performance
            this.updateDifficulty(analysis);

            // Step 3: Generate AI response with adaptive context
            const aiResponse = await this.ai.generateResponse(userMessage);

            // Step 4: Determine if scaffolding is needed
            const scaffolding = this.determineScaffolding(analysis);

            // Step 5: Select appropriate content delivery method
            const contentStrategy = this.selectContentStrategy(analysis, aiResponse);

            // Step 6: Update student profile
            if (analysis.answerEvaluation) {
                this.tracer.updateMastery(
                    analysis.concept,
                    analysis.answerEvaluation.correct,
                    this.difficultyLevel
                );
            }

            return {
                aiText: aiResponse.text,
                tools: aiResponse.tools,
                scaffolding: scaffolding,
                strategy: contentStrategy,
                analysis: analysis,
                recommendations: this.tracer.generateRecommendations()
            };

        } catch (error) {
            console.error('Adaptive engine error:', error);
            throw error;
        }
    }

    /**
     * Analyze student input
     */
    async analyzeInput(message) {
        const analysis = {
            concept: null,
            isQuestion: false,
            isAnswer: false,
            answerEvaluation: null,
            sentiment: 'neutral', // 'positive' | 'neutral' | 'frustrated'
            complexity: 0
        };

        // Detect if it's a question
        analysis.isQuestion = /\?|hogyan|miért|mi|milyen|mikor|meddig/i.test(message);

        // Extract primary concept
        const concepts = this.extractConcepts(message);
        if (concepts.length > 0) {
            analysis.concept = concepts[0];
        }

        // Detect sentiment (simple keyword-based)
        if (/nem értem|nehéz|bonyolult|zavart/i.test(message)) {
            analysis.sentiment = 'frustrated';
        } else if (/értem|könnyű|érdekes|klassz/i.test(message)) {
            analysis.sentiment = 'positive';
        }

        // TODO: If message is an answer to a previous question, evaluate it
        // This would require tracking pending questions

        if (CONFIG.DEBUG) {
            console.log('Input analysis:', analysis);
        }

        return analysis;
    }

    /**
     * Update difficulty level based on student performance
     */
    updateDifficulty(analysis) {
        if (!analysis.concept) return;

        const concept = analysis.concept;
        const correctStreak = this.tracer.consecutiveCorrect[concept] || 0;
        const wrongStreak = this.tracer.consecutiveWrong[concept] || 0;

        // Increase difficulty if student is doing well
        if (correctStreak >= CONFIG.ADAPTIVE.DIFFICULTY_UP_STREAK) {
            if (this.difficultyLevel === 'easy') {
                this.difficultyLevel = 'medium';
                if (CONFIG.DEBUG) console.log('🔼 Difficulty increased to medium');
            } else if (this.difficultyLevel === 'medium') {
                this.difficultyLevel = 'hard';
                if (CONFIG.DEBUG) console.log('🔼 Difficulty increased to hard');
            }
        }

        // Decrease difficulty if student is struggling
        if (wrongStreak >= CONFIG.ADAPTIVE.DIFFICULTY_DOWN_STREAK) {
            if (this.difficultyLevel === 'hard') {
                this.difficultyLevel = 'medium';
                if (CONFIG.DEBUG) console.log('🔽 Difficulty decreased to medium');
            } else if (this.difficultyLevel === 'medium') {
                this.difficultyLevel = 'easy';
                if (CONFIG.DEBUG) console.log('🔽 Difficulty decreased to easy');
            }
        }
    }

    /**
     * Determine appropriate scaffolding level
     */
    determineScaffolding(analysis) {
        if (!analysis.concept) {
            return { level: CONFIG.ADAPTIVE.SCAFFOLDING_LEVELS.NONE, reason: 'No concept detected' };
        }

        const mastery = this.tracer.getMastery(analysis.concept);
        const wrongStreak = this.tracer.consecutiveWrong[analysis.concept] || 0;

        // High scaffolding if struggling
        if (mastery < CONFIG.KNOWLEDGE_TRACING.STRUGGLE_THRESHOLD || wrongStreak >= 2) {
            return {
                level: CONFIG.ADAPTIVE.SCAFFOLDING_LEVELS.GUIDED,
                reason: 'Student struggling with concept',
                action: 'Provide step-by-step guidance with visual support'
            };
        }

        // Medium scaffolding if in ZPD
        if (mastery >= CONFIG.ADAPTIVE.ZPD_MIN && mastery <= CONFIG.ADAPTIVE.ZPD_MAX) {
            return {
                level: CONFIG.ADAPTIVE.SCAFFOLDING_LEVELS.HINT,
                reason: 'Student in ZPD',
                action: 'Provide subtle hints and Socratic questions'
            };
        }

        // No scaffolding if mastered
        if (mastery >= CONFIG.KNOWLEDGE_TRACING.MASTERY_THRESHOLD) {
            return {
                level: CONFIG.ADAPTIVE.SCAFFOLDING_LEVELS.NONE,
                reason: 'Concept mastered',
                action: 'Challenge with advanced questions'
            };
        }

        // Default: hint
        return {
            level: CONFIG.ADAPTIVE.SCAFFOLDING_LEVELS.HINT,
            reason: 'Default scaffolding',
            action: 'Provide hints as needed'
        };
    }

    /**
     * Select content delivery strategy
     */
    selectContentStrategy(analysis, aiResponse) {
        const strategy = {
            method: 'text',  // 'text' | 'simulation' | 'visualization' | 'game'
            priority: 'explanation', // 'explanation' | 'question' | 'practice'
            visualSupport: false
        };

        // Check if AI requested tools
        if (aiResponse.tools && aiResponse.tools.length > 0) {
            const toolTypes = aiResponse.tools.map(t => t.type);

            if (toolTypes.includes('SIMULATION')) {
                strategy.method = 'simulation';
                strategy.visualSupport = true;
            } else if (toolTypes.includes('VISUALIZATION')) {
                strategy.method = 'visualization';
                strategy.visualSupport = true;
            }
        }

        // If student is frustrated, prioritize visual support
        if (analysis.sentiment === 'frustrated') {
            strategy.visualSupport = true;
            strategy.method = 'simulation';
        }

        // If student is bored (high mastery + positive), prioritize game
        if (analysis.sentiment === 'positive' && analysis.concept) {
            const mastery = this.tracer.getMastery(analysis.concept);
            if (mastery > 0.7) {
                strategy.method = 'game';
                strategy.priority = 'practice';
            }
        }

        return strategy;
    }

    /**
     * Calculate ZPD and recommend next topics
     */
    calculateZPD() {
        const zpd = this.tracer.getConceptsInZPD();

        if (zpd.length === 0) {
            // No concepts in ZPD - find prerequisites of higher-level concepts
            return this.findNextLearningPath();
        }

        return zpd.map(item => {
            // Enrich with knowledge graph information
            const node = this.knowledgeGraph.nodes.find(n => n.id === item.concept);
            return {
                ...item,
                level: node?.level,
                prerequisites: node?.prerequisites
            };
        });
    }

    /**
     * Find next learning path based on knowledge graph
     */
    findNextLearningPath() {
        const mastered = this.tracer.getMasteredConcepts().map(c => c.concept);
        const available = [];

        // Find concepts where all prerequisites are mastered
        this.knowledgeGraph.nodes.forEach(node => {
            const allPrereqsMastered = node.prerequisites.every(prereq =>
                mastered.includes(prereq)
            );

            const notYetMastered = !mastered.includes(node.id);

            if (allPrereqsMastered && notYetMastered) {
                available.push({
                    concept: node.id,
                    level: node.level,
                    mastery: this.tracer.getMastery(node.id)
                });
            }
        });

        // Sort by level (easier first)
        available.sort((a, b) => a.level - b.level);

        return available;
    }

    /**
     * Generate personalized learning session
     */
    async generateLearningSession(topic) {
        this.currentTopic = topic;

        const session = {
            topic: topic,
            objectives: [],
            activities: [],
            estimatedDuration: 0
        };

        // Find related concepts in knowledge graph
        const topicNode = this.knowledgeGraph.nodes.find(n => n.id === topic);
        if (!topicNode) {
            throw new Error(`Topic ${topic} not found in knowledge graph`);
        }

        // Set objectives based on mastery
        const mastery = this.tracer.getMastery(topic);

        if (mastery < 0.3) {
            session.objectives = ['Megismerni az alapfogalmakat', 'Vizuális modell megértése'];
            session.activities = ['simulation', 'guided_questions', 'practice_easy'];
            session.estimatedDuration = 20; // minutes
        } else if (mastery < 0.7) {
            session.objectives = ['Mélyebb összefüggések feltárása', 'Alkalmazás gyakorlása'];
            session.activities = ['discussion', 'problem_solving', 'practice_medium'];
            session.estimatedDuration = 15;
        } else {
            session.objectives = ['Magasabb szintű alkalmazás', 'Kritikai gondolkodás fejlesztése'];
            session.activities = ['challenge_problems', 'real_world_scenarios', 'game'];
            session.estimatedDuration = 10;
        }

        return session;
    }

    /**
     * Helper: Extract concepts from message
     */
    extractConcepts(message) {
        // Delegate to AI agent's method
        return this.ai.extractConcepts(message);
    }

    /**
     * Get current student state summary
     */
    getStudentState() {
        return {
            averageMastery: this.tracer.getAverageMastery(),
            recentAccuracy: this.tracer.getRecentAccuracy(),
            mastered: this.tracer.getMasteredConcepts().length,
            struggling: this.tracer.getStrugglingConcepts().length,
            zpd: this.tracer.getConceptsInZPD().length,
            difficultyLevel: this.difficultyLevel,
            learningStyle: this.tracer.learningStyle
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdaptiveEngine;
}
�]*cascade082vfile:///C:/Users/Tomi/Term%C3%A9szettudom%C3%A1ny,f%C3%B6ldrajz%20%C3%B6n%C3%A1ll%C3%B3%20modell/js/adaptive-engine.js