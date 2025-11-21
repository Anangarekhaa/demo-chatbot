// Function to send the user's message
function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();
    if (userInput === '') return;

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const chatOutput = document.getElementById('chat-output');
        
        // Append user message
        appendMessage(`You: ${userInput}`, 'user');

        // Append bot response
        appendMessage(`Bot: ${data.response}`, 'bot');

        chatOutput.scrollTop = chatOutput.scrollHeight;
        document.getElementById('user-input').value = '';

        // Trigger learning process if the bot asks
        if (data.response.includes("Should I learn this?")) {
            handleLearning();
        }
    })
    .catch(err => console.error('Error:', err));
}

// Function to append messages to the chat box
function appendMessage(message, sender) {
    const chatOutput = document.getElementById("chat-output");
    const messageDiv = document.createElement("div");

    // Add CSS classes based on sender
    messageDiv.className = sender === "bot" ? "bot-message" : "user-message";
    messageDiv.textContent = message;

    chatOutput.appendChild(messageDiv);
    chatOutput.scrollTop = chatOutput.scrollHeight; // Auto scroll to bottom
}

// Function to handle learning new information
function handleLearning() {
    const input = prompt("Enter the information in 'key: value' format:");
    if (input && input.includes(":")) {
        const [key, value] = input.split(':').map(item => item.trim());
        teachNewInfo(key, value);
    }
}

// Function to teach the bot new information
function teachNewInfo(key, value) {
    if (!key || !value) return;

    fetch('/learn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: `${key}: ${value}` })
    })
    .then(res => res.json())
    .then(data => {
        appendMessage(`Bot: ${data.message}`, 'bot');
    })
    .catch(err => {
        console.error('Error in learning:', err);
        appendMessage("Bot: Sorry, I couldn't learn that new information.", 'bot');
    });
}

// Function to fetch weather
function getWeather() {
    const location = prompt("Enter location for weather:");
    if (!location) return;

    fetch(`/weather/${location}`)
    .then(response => response.json())
    .then(data => {
        console.log(data.weather);  // Check in browser console
        appendMessage(`Bot: ${data.weather}`, 'bot');
    })
    .catch(error => {
        console.error('Error in weather API:', error);
        appendMessage("Bot: Sorry, I couldn't fetch the weather.", 'bot');
    });
}




// Function to fetch latest news
function getNews() {
    fetch('/news')
    .then(response => response.json())
    .then(data => {
        appendMessage(`Bot: ${data.news}`, 'bot');
    })
    .catch(error => {
        console.error('Error in news API:', error);
        appendMessage("Bot: Sorry, I couldn't fetch the news.", 'bot');
    });
}

// Function to perform search using SerpAPI
function searchData() {
    const query = prompt("Enter what you want to search:");
    if (!query) return;

    fetch(`/search?query=${query}`)
    .then(response => response.json())
    .then(data => {
        appendMessage(`Bot: ${data.search_results}`, 'bot');
    })
    .catch(error => {
        console.error('Error in search API:', error);
        appendMessage("Bot: Sorry, I couldn't perform the search.", 'bot');
    });
}


