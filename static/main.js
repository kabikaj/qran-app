
document.addEventListener('DOMContentLoaded', function() {

    const generateBtn = document.getElementById('generate-btn');
    const copyButton = document.getElementById('copyButton');
    const resultElement = document.getElementById('result');

    const iniSuraInput = document.getElementById('ini_sura');
    const iniVerseInput = document.getElementById('ini_verse');
    const iniWordInput = document.getElementById('ini_word');
    const iniBlockInput = document.getElementById('ini_block');

    const endSuraInput = document.getElementById('end_sura');
    const endVerseInput = document.getElementById('end_verse');
    const endWordInput = document.getElementById('end_word');
    const endBlockInput = document.getElementById('end_block');

    generateBtn.addEventListener('click', async function() {

        const archigraphemes_output = document.getElementById('archigraphemesToggle').checked;
        const blocks_output = document.getElementById('blocksToggle').checked;
        const latin_output = document.getElementById('latinToggle').checked;

        const ini_sura = iniSuraInput.value.trim();
        const ini_verse = iniVerseInput.value.trim();
        const ini_word = iniWordInput.value.trim();
        const ini_block = iniBlockInput.value.trim();
        const end_sura = endSuraInput.value.trim();
        const end_verse = endVerseInput.value.trim();
        const end_word = endWordInput.value.trim();
        const end_block = endBlockInput.value.trim();

        const params = new URLSearchParams();

        const addParamIfValid = (name, value) => {
            if (value !== '') {
                const num = parseInt(value);
                if (!isNaN(num)) {
                    params.append(name, num);
                }
            }
        };

        addParamIfValid('ini_sura', ini_sura);
        addParamIfValid('ini_verse', ini_verse);
        addParamIfValid('ini_word', ini_word);
        addParamIfValid('ini_block', ini_block);

        addParamIfValid('end_sura', end_sura);
        addParamIfValid('end_verse', end_verse);
        addParamIfValid('end_word', end_word);
        addParamIfValid('end_block', end_block);

        params.append('get_archigraphemes', archigraphemes_output);
        params.append('get_blocks', blocks_output);
        params.append('get_latin', latin_output);

        try {
            const response = await fetch(`/generate?${params.toString()}`, {
                headers: {
                    'Authorization': 'Basic ' + btoa('admin:' + getPasswordFromStorage())
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            resultElement.value = data.result;

            const hasArabic = /[\p{Script=Arabic}]/u.test(data.result);
            resultElement.classList.toggle('arabic-text', hasArabic);
            resultElement.classList.toggle('latin-text', !hasArabic);

        } catch (error) {
            console.error('Fetch error:', error);
            resultElement.value = `Error: ${error.message}`;

        }
    });
    
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

