document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('songForm');
    const submitBtn = document.getElementById('submitBtn');
    const requestCodeBtn = document.getElementById('requestCodeBtn');
    const messageBox = document.getElementById('messageBox');
    const emailInput = document.getElementById('email');
    const codeInput = document.getElementById('code');
    
    loadStats();
    
    // Przycisk "Wyślij kod"
    if (requestCodeBtn) {
        requestCodeBtn.addEventListener('click', async function() {
            const email = emailInput.value.trim();
            
            if (!email) {
                showMessage('❌ Wprowadź adres email', 'error');
                return;
            }
            
            requestCodeBtn.disabled = true;
            requestCodeBtn.textContent = 'Wysyłanie... ⏳';
            
            try {
                const response = await fetch('/api/request-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('✅ ' + result.message + ' (sprawdź konsolę serwera)', 'success');
                    codeInput.disabled = false;
                    codeInput.focus();
                } else {
                    showMessage('❌ ' + result.message, 'error');
                }
            } catch (error) {
                showMessage('❌ Błąd połączenia z serwerem', 'error');
            } finally {
                requestCodeBtn.disabled = false;
                requestCodeBtn.textContent = 'Wyślij kod 📧';
            }
        });
    }
    
    // Formularz zgłoszenia
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Wysyłanie... ⏳';
        
        const formData = {
            email: emailInput.value.trim(),
            code: codeInput.value.trim(),
            artist: document.getElementById('artist').value,
            title: document.getElementById('title').value
        };
        
        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Pokaż sukces z informacją o piosence
                let message = result.message;
                
                if (result.track) {
                    message += `\n\n🎤 ${result.track.artist}\n🎵 ${result.track.title}`;
                    if (result.track.url) {
                        message += `\n\n🔗 Posłuchaj: ${result.track.url}`;
                    }
                }
                
                showMessage(message, 'success');
                form.reset();
                codeInput.disabled = true;
                loadStats();
            } else {
                showMessage('❌ ' + result.message, 'error');
            }
            
        } catch (error) {
            showMessage('❌ Błąd połączenia z serwerem', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Zgłoś piosenkę 🚀';
        }
    });
    
    function showMessage(message, type) {
        messageBox.innerHTML = message.replace(/\n/g, '<br>');
        messageBox.className = `message-box ${type}`;
        messageBox.style.display = 'block';
        
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 15000);
    }
    
    async function loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            if (stats.success) {
                document.getElementById('approvedCount').textContent = stats.today_approved;
                document.getElementById('rejectedCount').textContent = stats.today_rejected;
                document.getElementById('totalCount').textContent = stats.today_total;
            }
        } catch (error) {
            console.error('Błąd ładowania statystyk:', error);
        }
    }
});
