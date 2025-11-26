�F// === Science Knowledge Graph (5-6. évfolyam) ===
// Structured representation of concepts and their relationships

const scienceKnowledgeGraph = {
    subject: 'science',
    grade: '5-6',

    // Nodes represent concepts
    nodes: [
        // Level 1: Alapfogalmak
        {
            id: 'anyag',
            name: 'Anyag',
            level: 1,
            prerequisites: [],
            description: 'Az anyag minden, ami helyet foglal és tömege van'
        },
        {
            id: 'halmazállapot',
            name: 'Halmazállapot',
            level: 1,
            prerequisites: ['anyag'],
            description: 'Az anyag három alapvető formája: szilárd, folyékony, gáznemű'
        },
        {
            id: 'hőmérséklet',
            name: 'Hőmérséklet',
            level: 1,
            prerequisites: ['anyag'],
            description: 'Az anyag melegségének mérőszáma'
        },

        // Level 2: Folyamatok
        {
            id: 'olvadás',
            name: 'Olvadás',
            level: 2,
            prerequisites: ['halmazállapot', 'hőmérséklet'],
            description: 'Szilárd anyag folyékony állapotba kerülése hő hatására'
        },
        {
            id: 'fagyás',
            name: 'Fagyás',
            level: 2,
            prerequisites: ['halmazállapot', 'hőmérséklet'],
            description: 'Folyékony anyag szilárd állapotba kerülése hő elvonása miatt'
        },
        {
            id: 'párolgás',
            name: 'Párolgás',
            level: 2,
            prerequisites: ['halmazállapot', 'hőmérséklet'],
            description: 'Folyékony anyag gáznemű állapotba kerülése'
        },
        {
            id: 'forrás',
            name: 'Forrás',
            level: 2,
            prerequisites: ['párolgás'],
            description: 'Gyors párolgás az anyag belsejében is, forráspontnál'
        },
        {
            id: 'kondenzáció',
            name: 'Kondenzáció (lecsapódás)',
            level: 2,
            prerequisites: ['párolgás'],
            description: 'Gáznemű anyag folyékony állapotba kerülése hűlés miatt'
        },
        {
            id: 'szublimáció',
            name: 'Szublimáció',
            level: 3,
            prerequisites: ['halmazállapot'],
            description: 'Szilárd anyag közvetlenül gáznemű állapotba kerülése'
        },

        // Level 2: Oldódás (NEM olvadás!)
        {
            id: 'oldat',
            name: 'Oldat',
            level: 2,
            prerequisites: ['anyag'],
            description: 'Két vagy több anyag homogén elegye'
        },
        {
            id: 'oldódás',
            name: 'Oldódás',
            level: 2,
            prerequisites: ['oldat'],
            description: 'Egy anyag (oldott anyag) szétoszlása másik anyagban (oldószer)'
        },
        {
            id: 'oldhatóság',
            name: 'Oldhatóság',
            level: 3,
            prerequisites: ['oldódás', 'hőmérséklet'],
            description: 'Mennyi anyag oldható adott mennyiségű oldószerben'
        },

        // Level 3: Víz körforgása
        {
            id: 'víz_körforgása',
            name: 'A víz körforgása',
            level: 3,
            prerequisites: ['párolgás', 'kondenzáció', 'halmazállapot'],
            description: 'A víz folyamatos mozgása a természetben'
        },
        {
            id: 'csapadék',
            name: 'Csapadék',
            level: 3,
            prerequisites: ['víz_körforgása', 'kondenzáció'],
            description: 'Eső, hó, jégeső - víz különböző formái'
        },

        // Level 2: Részecske-modell
        {
            id: 'részecske',
            name: 'Részecske (molekula/atom)',
            level: 2,
            prerequisites: ['anyag'],
            description: 'Az anyagot felépítő apró részek'
        },
        {
            id: 'részecske_mozgás',
            name: 'Részecskék mozgása',
            level: 2,
            prerequisites: ['részecske', 'hőmérséklet'],
            description: 'A részecskék állandó mozgásban vannak, a hőmérséklettől függ a sebességük'
        },

        // Level 3: Energia
        {
            id: 'hő',
            name: 'Hő (hőenergia)',
            level: 3,
            prerequisites: ['részecske_mozgás', 'hőmérséklet'],
            description: 'A részecskék mozgási energiája'
        },
        {
            id: 'hővezetés',
            name: 'Hővezetés',
            level: 3,
            prerequisites: ['hő'],
            description: 'A hőenergia terjedése egyik helyről a másikra'
        }
    ],

    // Edges represent relationships
    edges: [
        { from: 'anyag', to: 'halmazállapot', type: 'has_property' },
        { from: 'anyag', to: 'hőmérséklet', type: 'has_property' },
        { from: 'halmazállapot', to: 'olvadás', type: 'changes_via' },
        { from: 'halmazállapot', to: 'fagyás', type: 'changes_via' },
        { from: 'halmazállapot', to: 'párolgás', type: 'changes_via' },
        { from: 'párolgás', to: 'víz_körforgása', type: 'part_of' },
        { from: 'kondenzáció', to: 'víz_körforgása', type: 'part_of' },
        { from: 'részecske_mozgás', to: 'halmazállapot', type: 'explains' },
        { from: 'hőmérséklet', to: 'részecske_mozgás', type: 'controls' }
    ],

    // Common misconceptions
    misconceptions: [
        {
            id: 'oldódás_vs_olvadás',
            incorrect: 'A cukor elolvad a vízben',
            correct: 'A cukor oldódik a vízben',
            explanation: 'Az olvadás halmazállapot-változás (szilárd→folyékony) hő hatására. Az oldódás pedig egy anyag szétoszlása másik anyagban.',
            intervention: 'socratic_contrast',
            relatedConcepts: ['oldódás', 'olvadás']
        },
        {
            id: 'párolgás_forrás',
            incorrect: 'A párolgás csak forraláskor történik',
            correct: 'A párolgás folyamatosan zajlik minden hőmérsékleten',
            explanation: 'A tócsa kiszárad forralás nélkül is. A párolgás a felszínről történik, a forrás pedig az anyag belsejéből is.',
            intervention: 'everyday_example',
            relatedConcepts: ['párolgás', 'forrás']
        },
        {
            id: 'levegő_anyag',
            incorrect: 'A levegő nem anyag, mert nem látom',
            correct: 'A levegő is anyag, gáznemű halmazállapotban',
            explanation: 'Az anyagnak nem kell láthatónak lennie. A levegőnek tömege van és helyet foglal.',
            intervention: 'demonstration',
            relatedConcepts: ['anyag', 'halmazállapot']
        },
        {
            id: 'szilárd_részecske',
            incorrect: 'A szilárd anyagok részecskéi nem mozognak',
            correct: 'Minden halmazállapotban mozognak a részecskék',
            explanation: 'A szilárd anyagokban a részecskék a helyükön rezegnek. Mozgásuk lassabb, mint folyadékban vagy gázban, de mozognak.',
            intervention: 'simulation',
            relatedConcepts: ['részecske_mozgás', 'halmazállapot']
        },
        {
            id: 'forrás_buborék',
            incorrect: 'A forró vízben levegő buborékok vannak',
            correct: 'A forrásban lévő vízben vízgőz buborékok vannak',
            explanation: 'A víz forrásakor a vízmolekulák gáznemű állapotba kerülnek, nem levegő szabadul fel.',
            intervention: 'clarification',
            relatedConcepts: ['forrás', 'párolgás']
        }
    ],

    // Helper method: Get concept by ID
    getConcept(id) {
        return this.nodes.find(node => node.id === id);
    },

    // Helper method: Get prerequisites for a concept
    getPrerequisites(conceptId) {
        const concept = this.getConcept(conceptId);
        return concept ? concept.prerequisites : [];
    },

    // Helper method: Get concepts that depend on this one
    getDependents(conceptId) {
        return this.nodes.filter(node =>
            node.prerequisites.includes(conceptId)
        );
    },

    // Helper method: Find misconception by pattern
    findMisconception(userMessage) {
        for (const misc of this.misconceptions) {
            // Simple keyword matching (can be enhanced)
            if (userMessage.toLowerCase().includes(misc.incorrect.toLowerCase().substring(0, 15))) {
                return misc;
            }
        }
        return null;
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = scienceKnowledgeGraph;
}
�F*cascade082�file:///C:/Users/Tomi/Term%C3%A9szettudom%C3%A1ny,f%C3%B6ldrajz%20%C3%B6n%C3%A1ll%C3%B3%20modell/subjects/science/knowledge-graph.js