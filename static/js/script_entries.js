
"use strict";

// карточки с записями
var entryCards = document.querySelectorAll(".entries_entryContainer");

for (let card of entryCards) {
    let timeStart = new Date(parseInt(card.getAttribute('data-timestart')) * 1000); // конвертация времени начала
    let timeEnd = new Date(parseInt(card.getAttribute('data-timeend')) * 1000); // конвертация времени конца
    card.querySelector('.entries_entryDate').innerText = `${timeStart.getFullYear()}.${timeStart.getMonth()+1}.${timeStart.getDate()}`; // дата
    card.querySelector('.entries_entryTime').innerText = `${timeStart.getHours()}:00 - ${timeEnd.getHours()}:00`; // время
}

// удаление записи
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
        
        if (content.success == true) {
            document.querySelector(`.entries_entryContainer[entryID="${entryID}"]`).remove(); // удаление элемента
        }
      })();
}