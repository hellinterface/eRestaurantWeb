
"use strict";

let timeOptions_start = [];
let tempString = "";
for (let i = 11; i <= 22; i++) {
    timeOptions_start.push(i + ":00");
    tempString += `<option value="${i}:00">${i}:00</option>`
}
timeInput_start.innerHTML = tempString;

let timeOptions_end = [];
tempString = "";
for (let i = 12; i <= 23; i++) {
    timeOptions_end.push(i + ":00");
    tempString += `<option value="${i}:00">${i}:00</option>`
}
timeInput_end.innerHTML = tempString;

timeInput_start.addEventListener('change', () => checkTables());
timeInput_end.addEventListener('change', () => checkTables());

function checkTables() {
    let timeStart = new Date(dateInput.value + " " + timeInput_start.value);
    timeStart = Math.floor(timeStart.getTime() / 1000);
    let timeEnd = new Date(dateInput.value + " " + timeInput_end.value);
    timeEnd = Math.floor(timeEnd.getTime() / 1000);
    let jsonString = JSON.stringify({time_start: timeStart, time_end: timeEnd});
    (async () => {
        const rawResponse = await fetch('/tables', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: jsonString
        });
        const content = await rawResponse.json();
      
        console.log(content);
        for (let i of tableCards) {
            i.setAttribute("disabled", "true");
        }
        for (let i of content) {
            let element = document.querySelector(`.tableCard[data-tableid="${i}"]`);
            if (element) element.setAttribute("disabled", "false");
        }
      })();
}

function submit() {
    let timeStart = new Date(dateInput.value + " " + timeInput_start.value);
    timeStart = Math.floor(timeStart.getTime() / 1000);
    let timeEnd = new Date(dateInput.value + " " + timeInput_end.value);
    timeEnd = Math.floor(timeEnd.getTime() / 1000);
    
    let cuisines = [];
    document.querySelectorAll('.cuisineCard.selected').forEach(element => {
        cuisines.push(parseInt(element.getAttribute('data-cuisineid')));
    });
    let selectedTableElement = document.querySelector('.tableCard.selected');
    selectedTable = parseInt(selectedTableElement.getAttribute('data-tableid'));

    let jsonString = JSON.stringify({time_start: timeStart, time_end: timeEnd, table_id: selectedTable, people_count: peopleCount, cuisine_ids: cuisines});
    (async () => {
        const rawResponse = await fetch('/create', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: jsonString
        });
        const content = await rawResponse.text();
      
        console.log(content);
      })();
}


document.querySelectorAll('.cuisineCard h3').forEach(element => {
    element.innerHTML = JSON.parse(element.innerText).join('\n');
});

document.querySelectorAll('.cuisineCard').forEach(element => {
    element.addEventListener('click', () => {
        element.classList.toggle('selected');
    })
});

let tableCards = [...document.querySelectorAll('.tableCard')];

tableCards.forEach(element => {
    element.addEventListener('click', () => {
        for (let i of tableCards) {
            if (i == element) i.classList.add('selected');
            else i.classList.remove('selected');
        }
    })
});