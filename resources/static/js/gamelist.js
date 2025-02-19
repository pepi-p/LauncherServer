const server_url = `${window.location.protocol}//${window.location.host}`;
// const socket = new WebSocket(`ws://${window.location.host}/ws`);

function initUpdateData() {
    const url = server_url + `/api/search`;
        fetch(url)
            .then(response => response.json())
            .then(data => data.forEach(item => addGameList(item.id, item.title)))
            .catch(error => console.error('Error:', error));
}

function addGameList(id, title) {
    const game_item = document.getElementById('game_item');
    const new_item = game_item.cloneNode(true);
    new_item.style = "";
    new_item.id = "game_" + id;
    const children = new_item.children[0].children;
    children[0].textContent = id;
    children[1].textContent = title;
    const edit_btn = new_item.children[1];
    edit_btn.id = "btn_" + id;
    edit_btn.addEventListener("click", () => window.location.href = `${server_url}/web/register?id=${encodeURIComponent(id)}`);
    const del_btn = new_item.children[2];
    del_btn.addEventListener("click", () => deleteGame(id));
    const list = document.getElementById('game_list');
    list.appendChild(new_item);
}

initUpdateData();

function deleteGame(id) {
    const url = server_url + `/api/delete?id=${encodeURIComponent(id)}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(_ => location.reload())
    .catch(error => console.error('Error:', error));
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("create_btn").addEventListener("click", () => window.location.href = server_url + '/web/register');
})