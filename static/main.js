
document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');

    const iniSuraInput = document.getElementById('ini_sura');
    const iniVerseInput = document.getElementById('ini_verse');
    const iniWordInput = document.getElementById('ini_word');
    const iniBlockInput = document.getElementById('ini_block');

    const endSuraInput = document.getElementById('end_sura');
    const endVerseInput = document.getElementById('end_verse');
    const endWordInput = document.getElementById('end_word');
    const endBlockInput = document.getElementById('end_block');

    const archigraphemes_output = document.getElementById('archigraphemesToggle').checked;
    const blocks_output = document.getElementById('blocksToggle').checked;
    const latin_output = document.getElementById('latinToggle').checked;

    const resultElement = document.getElementById('result');
    
    generateBtn.addEventListener('click', async function() {
        
        let ini_sura = parseInt(iniSuraInput.value);
        let ini_verse = parseInt(iniVerseInput.value);
        let ini_word = parseInt(iniWordInput.value);
        let ini_block = parseInt(iniBlockInput.value);

        let end_sura = parseInt(endSuraInput.value);
        let end_verse = parseInt(endVerseInput.value);
        let end_word = parseInt(endWordInput.value);
        let end_block = parseInt(endBlockInput.value);
        
        if (isNaN(ini_sura)) {
           ini_sura = 0; 
        }
        if (isNaN(ini_verse)) {
           ini_verse = 0; 
        }
        if (isNaN(ini_word)) {
           ini_word = 0; 
        }
        if (isNaN(ini_block)) {
           ini_block = 0; 
        }

        if (isNaN(end_sura)) {
           end_sura = 0; 
        }
        if (isNaN(end_verse)) {
           end_verse = 0; 
        }
        if (isNaN(end_word)) {
           end_word = 0; 
        }
        if (isNaN(end_block)) {
           end_block = 0; 
        }
        
        try {
            const response = await fetch(
                `/generate?` +
                `ini_sura=${ini_sura}&` + 
                `ini_verse=${ini_verse}&` + 
                `ini_word=${ini_word}&` + 
                `ini_block=${ini_block}&` + 

                `end_sura=${end_sura}&` +
                `end_verse=${end_verse}&` +
                `end_word=${end_word}&` +
                `end_block=${end_block}&` +

                `get_archigraphemes=${archigraphemes_output}&` +
                `get_blocks=${blocks_output}&` +
                `get_latin=${latin_output}`, {
                headers: {
                    'Authorization': 'Basic ' + btoa('admin:' + getPasswordFromStorage())
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Request failed');
            }
            
            const data = await response.json();
            resultElement.textContent = data.result;
            resultContainer.classList.remove('hidden');
        } catch (error) {
            // showError(error.message);
        }
    });
    
    // function showError(message) {
    //     errorMessage.textContent = message;
    //     errorContainer.classList.remove('hidden');
    // }
    
    function getPasswordFromStorage() {
        //FIXME
        // In a real app, you might want to implement a proper login flow
        // For this simple example, we'll prompt for password if not in sessionStorage
        let password = sessionStorage.getItem('master_password');
        if (!password) {
            password = prompt('Please enter the master password:');
            if (password) {
                sessionStorage.setItem('master_password', password);
            }
        }
        return password;
    }
});


document.getElementById('copyButton').addEventListener('click', function() {
    const textarea = document.getElementById('resultText');
    textarea.select();
    document.execCommand('copy');
    
    // visual feedback
    const originalText = this.textContent;
    this.textContent = 'Copied!';
    setTimeout(() => {
        this.textContent = originalText;
    }, 2000);
});

