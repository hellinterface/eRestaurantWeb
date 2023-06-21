
"use strict";

var entryCards = document.querySelectorAll(".entries_entryContainer");

for (let card of entryCards) {
    let timeStart = new Date(parseInt(card.getAttribute('data-timestart')) * 1000);
    let timeEnd = new Date(parseInt(card.getAttribute('data-timeend')) * 1000);
    card.querySelector('.entries_entryDate').innerText = `${timeStart.getFullYear()}.${timeStart.getMonth()}.${timeStart.getDate()}`;
    card.querySelector('.entries_entryTime').innerText = `${timeStart.getHours()}:00 - ${timeEnd.getHours()}:00`;
}