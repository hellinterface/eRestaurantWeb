
"use strict";

function createXselect(values) {
    let items = [];
    let container = document.createElement('div');
    container.className = "xSelect";
    for (let i of values) {
        let item = document.createElement('div');
        item.innerHTML = i;
        item.addEventListener('click', () => {
            for (let n of items) {
                if (item != n) n.classList.remove('selected');
                else n.classList.add('selected');
            }
            container.value = i;
        })
        container.appendChild(item);
        items.push(item);
    }
    items[0].click();
    return container;
}

let timeOptions_start = [];
for (let i = 11; i <= 22; i++) {
    timeOptions_start.push(i + ":00");
}

let timeOptions_end = [];
for (let i = 12; i <= 23; i++) {
    timeOptions_end.push(i + ":00");
}

let xSelect_timeStart = createXselect(timeOptions_start);
xSelect_timeStart.id = "newEntry_timeStartInput";
let xSelect_timeEnd = createXselect(timeOptions_end);
xSelect_timeEnd.id = "newEntry_timeEndInput";

newEntry_right.appendChild(xSelect_timeStart);
newEntry_right.appendChild(xSelect_timeEnd);


newEntry_submitButton.addEventListener('click', () => {
    let timeStart = new Date(newEntry_dateInput.value + " " + xSelect_timeStart.value);
    timeStart = Math.floor(timeStart.getTime() / 1000);
    let timeEnd = new Date(newEntry_dateInput.value + " " + xSelect_timeStart.value);
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
        const content = await rawResponse.text();
      
        console.log(content);
      })();
});

document.querySelectorAll('.newEntry_cuisineCard h3').forEach(element => {
    element.innerHTML = JSON.parse(element.innerText).join('\n');
});