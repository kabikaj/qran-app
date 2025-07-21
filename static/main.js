
//
// Copyright (c) 2025 Alicia González Martínez
//

document.addEventListener('DOMContentLoaded', function() {

    const extractBtn = document.getElementById('extract-btn');
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

    extractBtn.addEventListener('click', async function() {

        const archigraphemes_output = document.getElementById('archigraphemesToggle').checked;
        const blocks_output = document.getElementById('blocksToggle').checked;
        const latin_output = document.getElementById('latinToggle').checked;
        const show_verse_markers = document.getElementById('noVersesToggle').checked;

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

        params.append('get_archigraphemes', String(archigraphemes_output));
        params.append('get_blocks', String(blocks_output));
        params.append('get_latin', String(latin_output));
        params.append('show_verse_markers', String(show_verse_markers));

        try {
            let response = await fetch(`/extract?${params.toString()}`);

            if (response.status === 401) {
                //console.warn("Authentication failed. Retrying as guest...");
                const guestCredentials = btoa("guest:guest");
                response = await fetch(`/extract?${params.toString()}`, {
                    headers: {
                        Authorization: `Basic ${guestCredentials}`,
                    },
                });
            }
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();

            if (data.alert?.trim()) {
                showAlert(data.alert);
            }

            resultElement.value = data.result;

            const hasArabic = /[\p{Script=Arabic}]/u.test(data.result);
            resultElement.classList.toggle('arabic-text', hasArabic);
            resultElement.classList.toggle('latin-text', !hasArabic);

        } catch (error) {
            console.error('Fetch error:', error);
            resultElement.value = `Error: ${error.message}`;

        }
    });

});





function showAlert(message) {
  const alert = document.getElementById('alert');
  const messageEl = document.getElementById('alert-message');
  
  messageEl.textContent = message;
  alert.classList.remove('hidden');
  
  setTimeout(() => alert.classList.add('hidden'), 5000);
}



document.getElementById('copyButton').addEventListener('click', function() {
    const textarea = document.getElementById('result');
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(textarea.value)
            .then(() => {
                // visual feedback
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
                // Fallback to old method if modern API fails
                fallbackCopyText(textarea);
            });
    } else {
        // fallback for older browsers
        fallbackCopyText(textarea);
    }
});

// fallback method using deprecated execCommand
function fallbackCopyText(textarea) {
    textarea.select();
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            // visual feedback
            const copyButton = document.getElementById('copyButton');
            const originalText = copyButton.textContent;
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = originalText;
            }, 2000);
        } else {
            console.error('Fallback copy method failed');
        }
    } catch (err) {
        console.error('Error in fallback copy method: ', err);
    }
}




const helpToggle = document.getElementById('helpToggle');
const helpSection = document.getElementById('helpSection');
const closeHelp = document.getElementById('closeHelp');

helpToggle.addEventListener('click', () => {
    helpSection.classList.remove('hidden');
    helpToggle.classList.add('hidden');
});

closeHelp.addEventListener('click', () => {
    helpSection.classList.add('hidden');
    helpToggle.classList.remove('hidden');
});



//
// nagivate to previous and next suras
//

const upArrow = document.getElementById('prevSurah');
const downArrow = document.getElementById('nextSurah');
const resultElement = document.getElementById('result');


function findArabicSuras(text) {
  const regex = /صُورِة/g;
  const positions = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    positions.push(match.index);
  }
  return positions;
}

function findLatinSuras(text) {
  const regex = /\b(\d+):1\b/g;
  const positions = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    positions.push(match.index);
  }
  return positions;
}

function navigateToSura(direction) {
  const text = resultElement.value;
  const cursorPos = resultElement.selectionStart;
  const is_latin = document.getElementById('latinToggle').checked;
  let positions = [];

  if (is_latin) {
    positions = findLatinSuras(text);
  }
  else {
    positions = findArabicSuras(text);
  }
  
  if (positions.length === 0) return;

  let targetPos = 0; // default to beginning

  if (direction === 'prev_sura') {
    for (let i = positions.length - 1; i >= 0; i--) {
      if (positions[i] < cursorPos) {
        targetPos = positions[i];
        break;
      }
    }
  } else {
    for (let i = 0; i < positions.length; i++) {
      if (positions[i] > cursorPos) {
        targetPos = positions[i];
        break;
      }
    }
    // if at end, go the start
    if (targetPos <= cursorPos) targetPos = positions[0];
  }

  // scroll to the target position
  resultElement.focus();
  resultElement.setSelectionRange(targetPos, targetPos);

  // scroll calculation
  const textareaRect = resultElement.getBoundingClientRect();
  const charWidth = textareaRect.width / (resultElement.cols || 40);
  const visibleChars = textareaRect.width / charWidth;
  const visibleLines = textareaRect.height / parseInt(getComputedStyle(resultElement).lineHeight);
    
  const targetLine = Math.floor(targetPos / visibleChars);
  resultElement.scrollTop = targetLine * parseInt(getComputedStyle(resultElement).lineHeight);


}

upArrow.addEventListener('click', () => navigateToSura('prev_sura'));
downArrow.addEventListener('click', () => navigateToSura('next_sura'));


