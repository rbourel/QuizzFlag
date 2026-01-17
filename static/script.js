document.addEventListener('DOMContentLoaded', () => {
    // Menu Elements
    const startMenu = document.getElementById('start-menu');
    const gameApp = document.getElementById('game-app');
    const startGameBtn = document.getElementById('start-game-btn');
    const homeBtn = document.getElementById('home-btn');
    const typeButtons = document.querySelectorAll('.toggle-btn[data-type]');
    const diffButtons = document.querySelectorAll('.toggle-btn[data-diff]');

    // Game Elements
    const questionText = document.getElementById('question-text');
    const flagImage = document.getElementById('flag-image');
    const capitalIcon = document.getElementById('capital-icon');
    const optionsContainer = document.getElementById('options-container');
    const inputContainer = document.getElementById('input-container');
    const answerInput = document.getElementById('answer-input');
    const submitAnswerBtn = document.getElementById('submit-answer-btn');
    
    const feedbackArea = document.getElementById('feedback-area');
    const feedbackMessage = document.getElementById('feedback-message');
    const nextBtn = document.getElementById('next-btn');
    const infoBtn = document.getElementById('info-btn');
    const streakCounter = document.getElementById('streak-counter');
    const loadingOverlay = document.getElementById('loading');
    
    // Modal elements
    const modal = document.getElementById('info-modal');
    const closeModal = document.getElementById('close-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');

    // State
    let currentStreak = 0;
    let isAnswered = false;
    let settings = {
        type: 'flag',
        difficulty: '4'
    };

    // --- Menu Logic ---

    typeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            typeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            settings.type = btn.dataset.type;
        });
    });

    diffButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            diffButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            settings.difficulty = btn.dataset.diff;
        });
    });

    startGameBtn.addEventListener('click', () => {
        startMenu.classList.add('hidden');
        gameApp.classList.remove('hidden');
        loadQuestion();
    });

    homeBtn.addEventListener('click', () => {
        gameApp.classList.add('hidden');
        startMenu.classList.remove('hidden');
        currentStreak = 0;
        streakCounter.textContent = '0';
    });


    // --- Game Logic ---

    const setLoading = (isLoading) => {
        if (isLoading) {
            loadingOverlay.classList.add('active');
        } else {
            loadingOverlay.classList.remove('active');
        }
    };

    const loadQuestion = async () => {
        if (window.nextQuestionTimeout) clearTimeout(window.nextQuestionTimeout);
        setLoading(true);
        isAnswered = false;
        feedbackArea.classList.add('hidden');
        answerInput.value = '';
        
        // Reset UI View
        optionsContainer.innerHTML = '';
        
        try {
            const query = new URLSearchParams(settings).toString();
            const response = await fetch(`/api/new-question?${query}`);
            const data = await response.json();
            
            if (data.error) {
                alert("Error: " + data.error);
                return;
            }

            // Setup Question Visual
            if (data.type === 'flag') {
                flagImage.src = '/static/' + data.image;
                flagImage.classList.remove('hidden');
                capitalIcon.classList.add('hidden');
            } else {
                flagImage.classList.add('hidden');
                capitalIcon.classList.remove('hidden');
            }

            questionText.textContent = data.question_text;

            // Setup Answer Mode
            if (data.input_mode) {
                optionsContainer.classList.add('hidden');
                inputContainer.classList.remove('hidden');
                setTimeout(() => answerInput.focus(), 100);
            } else {
                inputContainer.classList.add('hidden');
                optionsContainer.classList.remove('hidden');
                
                // Adjust Grid for 8 items
                if (data.choices.length > 4) {
                    optionsContainer.classList.add('grid-8');
                } else {
                    optionsContainer.classList.remove('grid-8');
                }

                data.choices.forEach((choice, index) => {
                    const btn = document.createElement('button');
                    btn.className = 'option-btn';
                    btn.textContent = choice;
                    btn.onclick = () => checkAnswer({ index: index }, btn);
                    optionsContainer.appendChild(btn);
                });
            }

        } catch (error) {
            console.error(error);
            questionText.textContent = "Error loading question.";
        } finally {
            setLoading(false);
        }
    };

    const checkAnswer = async (payload, btnElement = null) => {
        if (isAnswered) return;
        isAnswered = true;
        setLoading(true);

        // Disable inputs
        const allBtns = optionsContainer.querySelectorAll('.option-btn');
        allBtns.forEach(b => b.disabled = true);
        
        try {
            const response = await fetch('/api/check-answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();

            if (result.correct) {
                if (btnElement) btnElement.classList.add('correct');
                else answerInput.style.borderColor = 'var(--success)';
                
                feedbackMessage.textContent = "Correct! 🎉";
                feedbackMessage.style.color = "var(--success)";
                currentStreak++;
            } else {
                if (btnElement) btnElement.classList.add('wrong');
                else answerInput.style.borderColor = 'var(--error)';
                
                feedbackMessage.innerHTML = `Wrong. It was <b>${result.correct_country}</b>.<br>Capital: ${result.correct_capital}`;
                feedbackMessage.style.color = "var(--error)";
                currentStreak = 0;
            }

            streakCounter.textContent = currentStreak;
            feedbackArea.classList.remove('hidden');

            // Auto-advance logic
            const delay = result.correct ? 1200 : 3500; // 1.2s for correct, 3.5s for wrong (to read info)
            
            // Clear any existing timeout to prevent double loading if user clicks "Next" manually
            if (window.nextQuestionTimeout) clearTimeout(window.nextQuestionTimeout);
            
            window.nextQuestionTimeout = setTimeout(() => {
                if (isAnswered && !modal.classList.contains('hidden')) {
                    // If user opened the info modal, don't auto-advance yet
                    // or we can wait until modal closes. For now, let's just 
                    // not auto-advance if modal is open.
                    return;
                }
                if (isAnswered) loadQuestion();
            }, delay);

        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // Text Input Submit
    submitAnswerBtn.addEventListener('click', () => {
        const text = answerInput.value.trim();
        if (text) checkAnswer({ text: text });
    });

    answerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const text = answerInput.value.trim();
            if (text) checkAnswer({ text: text });
        }
    });


    // --- Info Modal ---
    const showInfo = async () => {
        modal.classList.remove('hidden');
        modalContent.innerHTML = '<div class="spinner" style="margin: 0 auto;"></div>';
        
        try {
            const response = await fetch('/api/country-info');
            const data = await response.json();
            
            modalTitle.textContent = data.country;
            
            if (data.info) {
                let html = '<table>';
                for (const [key, value] of Object.entries(data.info)) {
                    html += `<tr><th>${key}</th><td>${value}</td></tr>`;
                }
                html += '</table>';
                modalContent.innerHTML = html;
            } else {
                modalContent.textContent = "No detailed information found.";
            }

        } catch (error) {
            modalContent.textContent = "Error loading info.";
        }
    };

    nextBtn.onclick = loadQuestion;
    infoBtn.onclick = showInfo;
    
    closeModal.onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    };
});