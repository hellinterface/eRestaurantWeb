
"use strict";

headerAccountButton.addEventListener('click', () => {
    document.body.classList.toggle('accountMenuVisible');
});

function completeStringWithZeros(input, targetLength) {
    if (typeof input == 'number') input = input.toString();
    if (targetLength <= input.length) return input;
    let tempString = '';
    for (let i = 0; i < targetLength - input.length; i++) {
        tempString += '0';
    }
    return tempString + input;
}