document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatForm = document.getElementById('chatForm');
    const movieInput = document.getElementById('movieInput');
    const questionInput = document.getElementById('questionInput');
    const warningToggle = document.getElementById('showWarning');
    const messagesContainer = document.getElementById('messages');
    const submitButton = document.getElementById('submitButton');
    const warningModal = document.getElementById('warningModal');
    const showAnswerButton = document.getElementById('showAnswer');
    const cancelButton = document.getElementById('cancelButton');
    const suggestionsList = document.getElementById('suggestions');
    
    let currentResponse = null;
    let movies = [];
    
    // Fetch available movies on load
    fetchMovies();
    
    // Event listeners
    chatForm.addEventListener('submit', handleSubmit);
    movieInput.addEventListener('input', handleMovieInput);
    showAnswerButton.addEventListener('click', showSpoiler);
    cancelButton.addEventListener('click', cancelSpoiler);
    
    // Functions
    function fetchMovies() {
        fetch('/api/movies')
            .then(response => response.json())
            .then(data => {
                movies = data.movies;
            })
            .catch(error => console.error('Error fetching movies:', error));
    }
    
    function handleMovieInput() {
        const query = movieInput.value.toLowerCase();
        if (query.length < 2) {
            suggestionsList.innerHTML = '';
            suggestionsList.classList.add('hidden');
            return;
        }
        
        const filteredMovies = movies.filter(movie => 
            movie.title.toLowerCase().includes(query)
        );
        
        if (filteredMovies.length > 0) {
            suggestionsList.innerHTML = '';
            filteredMovies.forEach(movie => {
                const div = document.createElement('div');
                div.classList.add('suggestion');
                div.textContent = `${movie.title} (${movie.year})`;
                div.addEventListener('click', () => {
                    movieInput.value = movie.title;
                    suggestionsList.innerHTML = '';
                    suggestionsList.classList.add('hidden');
                });
                suggestionsList.appendChild(div);
            });
            suggestionsList.classList.remove('hidden');
        } else {
            suggestionsList.innerHTML = '';
            suggestionsList.classList.add('hidden');
        }
    }
    
    function handleSubmit(e) {
        e.preventDefault();
        
        const movie = movieInput.value.trim();
        const question = questionInput.value.trim();
        
        if (!movie || !question) {
            alert('Please enter both a movie title and a question');
            return;
        }
        
        // Add user message to chat
        addMessage('user', `Movie: ${movie}\nQuestion: ${question}`);
        
        // Disable submit button and show loading
        submitButton.disabled = true;
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('loading');
        loadingDiv.innerHTML = `
            <div class="loading-dots">
                <div></div>
                <div></div>
                <div></div>
            </div>
        `;
        messagesContainer.appendChild(loadingDiv);
        
        // Send request to API
        fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                movie,
                question,
                showWarning: warningToggle.checked
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            messagesContainer.removeChild(loadingDiv);
            
            if (data.error) {
                addMessage('bot', data.message || data.error);
            } else {
                currentResponse = data;
                
                if (data.showWarning) {
                    // Show warning modal
                    warningModal.classList.remove('hidden');
                } else {
                    // Show answer directly
                    addMessage('bot', data.answer);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messagesContainer.removeChild(loadingDiv);
            addMessage('bot', 'Sorry, something went wrong. Please try again.');
        })
        .finally(() => {
            submitButton.disabled = false;
            questionInput.value = '';
        });
    }
    
    function showSpoiler() {
        if (currentResponse) {
            addMessage('bot', currentResponse.answer);
            warningModal.classList.add('hidden');
            currentResponse = null;
        }
    }
    
    function cancelSpoiler() {
        warningModal.classList.add('hidden');
        addMessage('bot', 'Spoiler hidden. Ask another question if you\'d like.');
        currentResponse = null;
    }
    
    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${type}-message`);
        
        // Format message content with line breaks
        const formattedContent = content.replace(/\n/g, '<br>');
        messageDiv.innerHTML = formattedContent;
        
        messagesContainer.appendChild(messageDiv);
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});