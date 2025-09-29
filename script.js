// Navigation Toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
}

// Recommendation Form Handling
document.addEventListener('DOMContentLoaded', () => {
    const recommendationForm = document.getElementById('recommendation-form');
    const resultSection = document.getElementById('result-section');

    if (recommendationForm) {
        initSliders();

        recommendationForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = recommendationForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Analyzing...';
            submitBtn.disabled = true;

            const loadingSpinner = document.getElementById('loading-spinner');
            loadingSpinner.classList.remove('hidden');

            const formData = {
                N: parseInt(document.getElementById('nitrogen').value),
                P: parseInt(document.getElementById('phosphorus').value),
                K: parseInt(document.getElementById('potassium').value),
                temperature: parseFloat(document.getElementById('temperature').value),
                humidity: parseFloat(document.getElementById('humidity').value),
                ph: parseFloat(document.getElementById('ph').value),
                rainfall: parseFloat(document.getElementById('rainfall').value)
            };

            try {
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    displayResultsInline(data);
                    sessionStorage.setItem('cropRecommendationResult', JSON.stringify(data));
                } else {
                    throw new Error(data.error || 'Server error occurred');
                }
            } catch (err) {
                alert('Error: ' + err.message);
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                loadingSpinner.classList.add('hidden');
            }
        });
    }

    // Display results on result page
    if (window.location.pathname.includes('result.html')) {
        const storedData = sessionStorage.getItem('cropRecommendationResult');
        if (storedData) displayResults(JSON.parse(storedData));
    }
});

// Slider initialization
function initSliders() {
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        const valueDisplay = slider.nextElementSibling;
        if (valueDisplay && valueDisplay.classList.contains('slider-value')) {
            valueDisplay.textContent = slider.value;
            slider.addEventListener('input', () => valueDisplay.textContent = slider.value);
        }
    });
}

// Display inline results
function displayResultsInline(data) {
    const resultContent = document.getElementById('result-content');
    resultContent.innerHTML = `
        <div class="result-header">
            <div class="crop-image-placeholder">🌱</div>
            <div>
                <h2>Recommended Crop: ${data.crop}</h2>
                <div class="confidence-badge">AI Confidence: ${data.confidence}%</div>
            </div>
        </div>
        <div class="crop-details">
            <h3>Crop Information</h3>
            <ul>
                <li>Best Season: ${data.season}</li>
                <li>Growth Duration: ${data.duration}</li>
                <li>Water Requirement: ${data.water_requirement}</li>
                <li>Soil Type: ${data.soil_type}</li>
            </ul>
        </div>
        <div class="growth-tips">
            <h3>Growth Tips</h3>
            <ul>${data.tips.map(t => `<li>${t}</li>`).join('')}</ul>
        </div>
    `;
    document.getElementById('result-section').classList.remove('hidden');
}

// Display on result page
function displayResults(data) {
    const resultContent = document.getElementById('result-content');
    resultContent.innerHTML = `
        <h2>Recommended Crop: ${data.crop}</h2>
        <p>Confidence: ${data.confidence}%</p>
        <p>Season: ${data.season}</p>
        <p>Growth Duration: ${data.duration}</p>
        <p>Water Requirement: ${data.water_requirement}</p>
        <p>Soil Type: ${data.soil_type}</p>
        <h3>Growth Tips</h3>
        <ul>${data.tips.map(t => `<li>${t}</li>`).join('')}</ul>
    `;
}

// PDF generation
async function generatePDFReport() {
    const resultData = sessionStorage.getItem('cropRecommendationResult');
    if (!resultData) return alert('No data found. Submit the form first.');

    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: resultData
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `crop_recommendation.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        alert('PDF generation failed: ' + err.message);
    }
}
// ---------------- Chatbot ----------------
document.addEventListener("DOMContentLoaded", () => {
    const chatbotBtn = document.getElementById("chatbot-button");
    const chatbot = document.getElementById("chatbot-container");
    const closeBtn = document.getElementById("chatbot-close");
    const sendBtn = document.getElementById("chatbot-send");
    const input = document.getElementById("chatbot-text");
    const messages = document.getElementById("chatbot-messages");

    if (!chatbotBtn || !chatbot) return;

    chatbotBtn.addEventListener("click", () => {
        chatbot.classList.toggle("hidden");
    });

    closeBtn.addEventListener("click", () => {
        chatbot.classList.add("hidden");
    });

    function addMessage(sender, text) {
        const msg = document.createElement("div");
        msg.className = sender === "user" ? "user-message" : "bot-message";
        msg.textContent = text;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    function getBotReply(question) {
        // Simple mock responses (English + Telugu)
        if (question.toLowerCase().includes("crop") || question.includes("పంట")) {
            return "🌱 You should try Rice or Wheat for this season. (ఈ సీజన్‌లో మీరు బియ్యం లేదా గోధుమలను ప్రయత్నించాలి)";
        }
        if (question.toLowerCase().includes("weather") || question.includes("వాతావరణం")) {
            return "☀️ The weather looks favorable for maize. (మొక్కజొన్నకు వాతావరణం అనుకూలంగా ఉంది)";
        }
        return "🤖 Sorry, I don’t understand. Please ask about crops or weather. (క్షమించండి, నేను అర్థం చేసుకోలేకపోతున్నాను. పంటలు లేదా వాతావరణం గురించి అడగండి)";
    }

    sendBtn.addEventListener("click", () => {
        const text = input.value.trim();
        if (!text) return;
        addMessage("user", "👤 " + text);
        input.value = "";
        setTimeout(() => {
            addMessage("bot", getBotReply(text));
        }, 800);
    });

    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendBtn.click();
    });
});

