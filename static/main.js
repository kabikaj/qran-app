
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
            const response = await fetch(`/extract?${params.toString()}`);
            
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





function showAlert(message) {
  const alert = document.getElementById('alert');
  const messageEl = document.getElementById('alert-message');
  
  messageEl.textContent = message;
  alert.classList.remove('hidden');
  
  setTimeout(() => alert.classList.add('hidden'), 5000);
}



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
  const regex = /(1:1|2:1|3:1|4:1|5:1|6:1|7:1|8:1|9:1|10:1|11:1|12:1|13:1|14:1|15:1|16:1|17:1|18:1|19:1|20:1|21:1|22:1|23:1|24:1|25:1|26:1|27:1|28:1|29:1|30:1|31:1|32:1|33:1|34:1|35:1|36:1|37:1|38:1|39:1|40:1|41:1|42:1|43:1|44:1|45:1|46:1|47:1|48:1|49:1|50:1|51:1|52:1|53:1|54:1|55:1|56:1|57:1|58:1|59:1|60:1|61:1|62:1|63:1|64:1|65:1|66:1|67:1|68:1|69:1|70:1|71:1|72:1|73:1|74:1|75:1|76:1|77:1|78:1|79:1|80:1|81:1|82:1|83:1|84:1|85:1|86:1|87:1|88:1|89:1|90:1|91:1|92:1|93:1|94:1|95:1|96:1|97:1|98:1|99:1|100:1|101:1|102:1|103:1|104:1|105:1|106:1|107:1|108:1|109:1|110:1|111:1|112:1|113:1|114:1)[^\d]/g;
  const positions = [];
  let match;
  while ((match = regex.exec(text)) !== null) {
    positions.push(match.index);
  }
  return positions;
}

function navigateToPoint(direction) {
  const text = resultElement.value;
  const cursorPos = resultElement.selectionStart;
  const is_latin = document.getElementById('latinToggle').checked;

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
  
  // scroll the textarea to make the sura visible
  const lineHeight = parseInt(getComputedStyle(resultElement).lineHeight);
  const linesToScroll = Math.floor(resultElement.scrollTop / lineHeight);
  const targetLine = Math.floor(targetPos / (resultElement.cols || 40)); // rough estimate
  resultElement.scrollTop = (targetLine - linesToScroll) * lineHeight;
}

upArrow.addEventListener('click', () => navigateToPoint('prev_sura'));
downArrow.addEventListener('click', () => navigateToPoint('next_sura'));


