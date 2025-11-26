�// === Application Configuration ===

const CONFIG = {
  // Gemini API Settings
  GEMINI: {
    API_ENDPOINT: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent',
    MODEL: 'gemini-2.0-flash-exp',
    
    // Model parameters
    TEMPERATURE: 0.7,        // Creativity vs. consistency (0-1)
    TOP_P: 0.9,              // Nucleus sampling
    TOP_K: 40,               // Top-k sampling
    MAX_OUTPUT_TOKENS: 2048, // Maximum response length
    
    // Safety settings (BLOCK_NONE for educational content)
    SAFETY_SETTINGS: [
      { category: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_NONE' },
      { category: 'HARM_CATEGORY_HATE_SPEECH', threshold: 'BLOCK_NONE' },
      { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold: 'BLOCK_NONE' },
      { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', threshold: 'BLOCK_NONE' }
    ]
  },

  // Subject-specific settings
  SUBJECTS: {
    SCIENCE: {
      id: 'science',
      name: 'Természettudomány',
      grades: '5-6. évfolyam',
      icon: '🔬',
      color: '#6366F1' // Indigo
    },
    GEOGRAPHY: {
      id: 'geography',
      name: 'Földrajz',
      grades: '7-8. évfolyam',
      icon: '🌍',
      color: '#10B981' // Green
    }
  },

  // Knowledge Tracing settings
  KNOWLEDGE_TRACING: {
    INITIAL_MASTERY: 0.5,           // Starting probability for unknown concepts
    MASTERY_THRESHOLD: 0.8,         // Consider "mastered" above this
    STRUGGLE_THRESHOLD: 0.3,        // Consider "struggling" below this
    
    // Bayesian update factors
    CORRECT_ANSWER_BOOST: 0.15,
    WRONG_ANSWER_PENALTY: -0.1,
    
    // Learning rate (how quickly mastery changes)
    LEARNING_RATE: 0.1
  },

  // Adaptive Engine settings
  ADAPTIVE: {
    // Zone of Proximal Development (ZPD) boundaries
    ZPD_MIN: 0.3,  // Below this: too easy (already mastered or forgotten)
    ZPD_MAX: 0.7,  // Above this: too hard (not ready yet)
    
    // Difficulty adjustment triggers
    DIFFICULTY_UP_STREAK: 3,    // Consecutive correct answers to increase difficulty
    DIFFICULTY_DOWN_STREAK: 2,  // Consecutive wrong answers to decrease difficulty
    
    // Scaffolding levels
    SCAFFOLDING_LEVELS: {
      NONE: 0,           // No help
      HINT: 1,           // Subtle hint
      GUIDED: 2,         // Step-by-step guidance
      DEMONSTRATION: 3   // Full demonstration with explanation
    }
  },

  // User interface settings
  UI: {
    CHAT_MAX_MESSAGES: 100,        // Maximum messages to keep in memory
    TYPING_INDICATOR_DELAY: 500,   // ms before showing "AI is typing..."
    AUTO_SCROLL_DELAY: 100,        // ms delay for smooth auto-scroll
    TOAST_DURATION: 3000           // Toast notification duration (ms)
  },

  // Storage keys (localStorage)
  STORAGE: {
    API_KEY: 'adaptive_learning_api_key',
    CURRENT_USER: 'adaptive_learning_current_user',
    USER_PROFILES: 'adaptive_learning_user_profiles',
    CHAT_HISTORY: 'adaptive_learning_chat_history',
    THEME: 'adaptive_learning_theme'
  },

  // Debug mode (set to false in production)
  DEBUG: true
};

// Freeze config to prevent accidental modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.GEMINI);
Object.freeze(CONFIG.SUBJECTS);
Object.freeze(CONFIG.KNOWLEDGE_TRACING);
Object.freeze(CONFIG.ADAPTIVE);
Object.freeze(CONFIG.UI);
Object.freeze(CONFIG.STORAGE);

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
�*cascade082mfile:///C:/Users/Tomi/Term%C3%A9szettudom%C3%A1ny,f%C3%B6ldrajz%20%C3%B6n%C3%A1ll%C3%B3%20modell/js/config.js