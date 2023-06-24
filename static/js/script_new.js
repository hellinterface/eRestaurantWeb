
"use strict";

// заполнение элемента селект времени начала
let timeOptions_start = [];
let tempString = "";
for (let i = 11; i <= 22; i++) {
    timeOptions_start.push(i + ":00");
    tempString += `<option value="${i}:00">${i}:00</option>`
}
timeInput_start.innerHTML = tempString;

// заполнение элемента селект времени конца
let timeOptions_end = [];
tempString = "";
for (let i = 12; i <= 23; i++) {
    timeOptions_end.push(i + ":00");
    tempString += `<option value="${i}:00">${i}:00</option>`
}
timeInput_end.innerHTML = tempString;

// обновление доступных опций в селекте времени конца
function updateTimeEndOptions() {
    if (timeInput_end.options.selectedIndex <= timeInput_start.options.selectedIndex) {
        timeInput_end.options.selectedIndex = timeInput_start.options.selectedIndex;
    }
    for (let i in timeInput_end.options) {
        if (i < timeInput_start.options.selectedIndex) timeInput_end.options[i].setAttribute("disabled", "true");
        else timeInput_end.options[i].removeAttribute("disabled");
    }
}

// проверка свободныъ столиков
function checkTables() {
    // проверка на корректность полей
    if (timeInput_start.checkValidity() == false) return;
    if (timeInput_end.checkValidity() == false) return;
    if (peopleCountInput.checkValidity() == false) return;

    // время начала
    let timeStart = new Date(dateInput.value + " " + timeInput_start.value);
    console.log(timeStart);
    timeStart = Math.floor(timeStart.getTime() / 1000);
    // время конца
    let timeEnd = new Date(dateInput.value + " " + timeInput_end.value);
    console.log(timeEnd);
    timeEnd = Math.floor(timeEnd.getTime() / 1000);
    // число людей
    let peopleCount = parseInt(peopleCountInput.value);
    let jsonString = JSON.stringify({time_start: timeStart, time_end: timeEnd, people_count: peopleCount});
    // отправление объекта
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
      
        // получение ответа
        console.log(content);
        console.log(tableCards);
        for (let i of tableCards) {
            i.setAttribute("disabled", "true");
        }
        for (let i of content) {
            let element = document.querySelector(`.tableCard[data-tableid="${i}"]`);
            if (element) element.removeAttribute("disabled");
        }
        let currentSelectedTable = document.querySelector(`.tableCard.selected`);
        if (currentSelectedTable.getAttribute("disabled") == 'true') {
            let element = document.querySelector(`.tableCard[data-tableid="${content[0]}"]`);
            if (element) element.click();
        }
      })();
}

// отправка финальной записи
function submit() {
    // проверка полей на корректность
    if (timeInput_start.checkValidity() == false) return;
    if (timeInput_end.checkValidity() == false) return;
    if (peopleCountInput.checkValidity() == false) return;

    // время начала
    let timeStart = new Date(dateInput.value + " " + timeInput_start.value);
    timeStart = Math.floor(timeStart.getTime() / 1000);
    // время конца
    let timeEnd = new Date(dateInput.value + " " + timeInput_end.value);
    timeEnd = Math.floor(timeEnd.getTime() / 1000);
    // число людей
    let peopleCount = parseInt(peopleCountInput.value);
    
    // создание массива с выбранными кухнями
    let cuisines = [];
    document.querySelectorAll('.cuisineCard.selected').forEach(element => {
        cuisines.push(parseInt(element.getAttribute('data-cuisineid')));
    });
    console.log(cuisines);
    // выбранный столик
    let selectedTableElement = document.querySelector('.tableCard.selected');
    let selectedTable = parseInt(selectedTableElement.getAttribute('data-tableid'));

    // объект для отправки
    let objectToSend = {
        time_start: timeStart, 
        time_end: timeEnd, 
        table_id: selectedTable, 
        people_count: peopleCount, 
        cuisine_ids: cuisines
    };
    
    let editEntryID = new URLSearchParams(window.location.search).get("entryID");
    let admin_usernameInput = document.getElementById("adminUsernameInput");
    if (window.location.pathname == "/edit" && editEntry) { // идёт редактирование, пользователь не админ
        objectToSend.id = editEntryID;
    }
    if (admin_usernameInput) { // идёт редактирование, пользователь админ
        if (admin_usernameInput.checkValidity() == false) return;
        objectToSend.for_username = admin_usernameInput.value;
    }
    
    // отправление запроса
    (async () => {
        const rawResponse = await fetch('/apply', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(objectToSend)
        });
        const content = await rawResponse.text();
      
        console.log(content);
        window.location.href = "/";
      })();
}

let tableCards;

document.addEventListener('DOMContentLoaded', () => {

    newEntry_submitButton.addEventListener('click', () => submit());

    document.querySelectorAll('.cuisineCard h3').forEach(element => {
        element.innerHTML = JSON.parse(element.innerText).join('\n');
    });
    
    document.querySelectorAll('.cuisineCard').forEach(element => {
        element.addEventListener('click', () => {
            element.classList.toggle('selected');
        })
    });
    
    tableCards = [...document.querySelectorAll('.tableCard')];
    
    tableCards.forEach(element => {
        element.addEventListener('click', () => {
            for (let i of tableCards) {
                if (i == element) i.classList.add('selected');
                else i.classList.remove('selected');
            }
        })
    });

    if (window.editEntry) {
        for (let element of document.querySelectorAll('.cuisineCard')) {
            if (editEntry.cuisine_ids.includes(parseInt(element.getAttribute("data-cuisineid")))) element.classList.add('selected');
            else element.classList.remove('selected');
        }
        let dateStart = new Date(editEntry.time_start * 1000);
        let dateEnd = new Date(editEntry.time_end * 1000);
        let mm = completeStringWithZeros(dateStart.getMonth(), 2);
        let dd = completeStringWithZeros(dateStart.getDate(), 2);
        let dateString = `${dateStart.getFullYear()}-${mm}-${dd}`
        dateInput.setAttribute("min", dateString);
        dateInput.setAttribute("max", dateString);
        dateInput.value = dateString;
        peopleCountInput.value = editEntry.people_count;
        timeInput_start.options.selectedIndex = dateStart.getHours() - 11;
        timeInput_end.options.selectedIndex = dateEnd.getHours() - 12;
        document.querySelector(`.tableCard[data-tableid="${editEntry.table_id}"]`).classList.add('selected');
    }
    else {
        tableCards[0].classList.add('selected');
    }

    dateInput.addEventListener('input', () => checkTables());
    timeInput_start.addEventListener('input', () => {
        checkTables();
        updateTimeEndOptions();
    });
    timeInput_end.addEventListener('input', () => checkTables());
    peopleCountInput.addEventListener('input', () => checkTables());
    
    checkTables();
    updateTimeEndOptions();
})