
"use strict";

var entryCards = document.querySelectorAll(".entries_entryContainer");

for (let card of entryCards) {
    let timeStart = new Date(parseInt(card.getAttribute('data-timestart')) * 1000);
    let timeEnd = new Date(parseInt(card.getAttribute('data-timeend')) * 1000);
    card.querySelector('.entries_entryDate').innerText = `${timeStart.getFullYear()}.${timeStart.getMonth()}.${timeStart.getDate()}`;
    card.querySelector('.entries_entryTime').innerText = `${timeStart.getHours()}:00 - ${timeEnd.getHours()}:00`;
}

function deleteEntry(entryID) {
    (async () => {
        const rawResponse = await fetch('/delete', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: entryID
        });
        const content = await rawResponse.json();
      
        console.log(content);
        
      })();
}