var gameDataFetcher = null;
var gameImage = null;
var gameData = null;

var setGameDataFetcher = () => {
    gameDataFetcher = setInterval(() => {
        fetch('/game_data')
        .then(response => response.json())
        .then(data => {
            gameData.innerHTML = JSON.stringify(data, undefined, 4);
            // console.log(JSON.stringify(data, undefined, 4));
        });
    }, 1000)
}

var clearGameDataFetcher = () => {
    console.log("Clearing")
    clearInterval(gameDataFetcher);
}

var startGame = (mode) => {
    fetch(
        '/start_game',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({gameMode: mode})
        })
        .then(response => gameImage.src = '/video_feed')
        .then(() => setGameDataFetcher())
}

var stopGame = () => {
    gameData.innerHTML = ""
    fetch(
        '/stop_game',
        {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
        })
        .then(response => {
            gameImage.src = '';
            clearGameDataFetcher();
        })
}

document.addEventListener('DOMContentLoaded', (event) => {
    gameImage = document.getElementById('gameImage');
    gameData = document.getElementById('gameData');
});
