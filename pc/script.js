// ... существующий код для таблицы (адаптируйте на 3 колонки: depth, yaw, time)

const socket = io();  // SocketIO

socket.on('telemetry', function(data) {
    const telemetryDiv = document.getElementById('telemetry');
    telemetryDiv.innerHTML = `
        Глубина: ${data.depth} м<br>
        Давление: ${data.pressure} hPa<br>
        Yaw: ${data.yaw}°<br>
        Ток: ${data.current} A<br>
        Напряжение: ${data.voltage} V
    `;
});

// Кнопки (добавьте в HTML: <button onclick="startMission()">Запуск миссии</button> <button onclick="stopMission()">Экстренный стоп</button>)

function startMission() {
    fetch('/api/play', {method: 'POST'});
}

function stopMission() {
    fetch('/api/stop', {method: 'POST'});
}

function saveMission() {
    const data = {};
    const inputs = document.querySelectorAll('#commandTable input');
    inputs.forEach((input, idx) => {
        const row = Math.floor(idx / 3) + 1;
        const col = idx % 3;
        if (col === 0) data[`depth_${row}`] = input.value;
        if (col === 1) data[`yaw_${row}`] = input.value;
        if (col === 2) data[`time_${row}`] = input.value;
    });
    fetch('/save_mission', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
}

// Вызовите saveMission() перед стартом, если нужно