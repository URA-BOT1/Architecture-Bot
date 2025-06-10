// Configuration
// API_URL peut être défini dans config.js
const API_URL = window.API_URL || (
    window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : ''
);

// État de l'application
let isLoading = false;

// Éléments DOM
const chatBox = document.getElementById('chatBox');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');
const status = document.getElementById('status');
const totalQueriesSpan = document.getElementById('totalQueries');
const cacheHitsSpan = document.getElementById('cacheHits');
const processingTimeSpan = document.getElementById('processingTime');

// Vérifier la connexion au démarrage
checkConnection();
updateStats();

// Mettre à jour les stats toutes les 5 secondes
setInterval(updateStats, 5000);

async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        status.textContent = `✅ En ligne - Cache: ${data.cache}`;
        status.className = 'status online';
    } catch (error) {
        status.textContent = '❌ Hors ligne';
        status.className = 'status offline';
        console.error('Erreur de connexion:', error);
    }
}

async function updateStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats`);
        const data = await response.json();
        
        totalQueriesSpan.textContent = data.total_queries;
        cacheHitsSpan.textContent = data.cache_hits;
    } catch (error) {
        console.error('Erreur lors de la récupération des stats:', error);
    }
}

async function sendQuestion() {
    const question = questionInput.value.trim();
    
    if (!question || isLoading) return;
    
    isLoading = true;
    sendButton.disabled = true;
    
    // Ajouter la question de l'utilisateur
    addMessage(question, 'user');
    
    // Vider l'input
    questionInput.value = '';
    
    // Afficher un loader
    const loaderId = addLoader();
    
    try {
        const startTime = performance.now();
        
        const response = await fetch(`${API_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                commune: 'Montpellier' // Pour le test
            })
        });
        
        const endTime = performance.now();
        const processingTime = Math.round(endTime - startTime);
        
        if (!response.ok) {
            throw new Error(`Erreur serveur: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Retirer le loader
        removeLoader(loaderId);
        
        // Ajouter la réponse
        let messageContent = data.answer;
        if (data.cached) {
            messageContent += '\n<span class="cached-indicator">📦 Réponse depuis le cache</span>';
        }
        
        addMessage(messageContent, 'bot');
        
        // Afficher le temps de traitement
        processingTimeSpan.textContent = data.processing_time 
            ? `${Math.round(data.processing_time * 1000)}` 
            : processingTime;
        
        // Mettre à jour les stats
        updateStats();
        
    } catch (error) {
        removeLoader(loaderId);
        addMessage('❌ Désolé, une erreur est survenue. Veuillez réessayer.', 'bot');
        console.error('Erreur:', error);
    } finally {
        isLoading = false;
        sendButton.disabled = false;
        questionInput.focus();
    }
}

function addMessage(text, type) {
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    message.innerHTML = text;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addLoader() {
    const loader = document.createElement('div');
    loader.className = 'message bot-message';
    loader.id = `loader-${Date.now()}`;
    loader.innerHTML = '<div class="loader"></div> Recherche en cours...';
    chatBox.appendChild(loader);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loader.id;
}

function removeLoader(loaderId) {
    const loader = document.getElementById(loaderId);
    if (loader) loader.remove();
}

function askSuggestion(question) {
    questionInput.value = question;
    sendQuestion();
}

// Ajouter des exemples de questions après un délai
setTimeout(() => {
    addMessage(
        `📘 Je peux répondre à des questions comme :
        
• Quelle est la hauteur maximale autorisée en zone UB ?
• Puis-je construire une piscine en limite de propriété ?
• Combien de places de parking pour un immeuble de bureaux ?
• Quelle distance respecter par rapport à la voirie ?
• Ai-je besoin d'un permis de construire pour mon projet ?
        
N'hésitez pas à me poser vos questions !`,
        'bot'
    );
}, 1500);

// Raccourcis clavier
document.addEventListener('keydown', (e) => {
    // Ctrl+K pour focus sur l'input
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        questionInput.focus();
    }
    
    // Échap pour vider l'input
    if (e.key === 'Escape') {
        questionInput.value = '';
    }
});

// Gestion du focus
questionInput.focus();
