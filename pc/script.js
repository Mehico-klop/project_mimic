const rows = 10;
const cols = 4;

const tbody = document.querySelector("#commandTable tbody");

// создаём таблицу
for (let i = 0; i < rows; i++) {
    const tr = document.createElement("tr");
    for (let j = 0; j < cols; j++) {
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.type = "number";
        input.value = 0;
        td.appendChild(input);
        tr.appendChild(td);
    }
    tbody.appendChild(tr);
}

function collectData() {
    const data = [];
    tbody.querySelectorAll("tr").forEach(tr => {
        const row = [];
        tr.querySelectorAll("input").forEach(input => {
            row.push(Number(input.value));
        });
        data.push(row);
    });
    return data;
}

function sendSequence() {
    fetch("/api/upload_sequence", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            sequence: collectData()
        })
    });
}

function play() {
    fetch("/api/play", {method: "POST"});
}
