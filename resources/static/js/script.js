const server_url = `${window.location.protocol}//${window.location.host}`;
const socket = new WebSocket(`ws://${window.location.host}/ws/web`);
let is_update = false; // 更新かどうか
let game_id; // ゲームのID

window.onload = function () {
    initUpdateData();

    const url_params = new URLSearchParams(window.location.search);
    const id = url_params.get('id');

    // id未指定 = クエリなしとみなし，中断する
    if (id == null) return;

    is_update = true;

    game_id = id;
    loadData(id);
}

function loadData(id) {
    const title_text = document.getElementById('title_text');
    const author_text = document.getElementById('author_text');
    const version_text = document.getElementById('version_text');
    const description_text = document.getElementById('description_text');

    const url = server_url + `/api/search?id=${encodeURIComponent(id)}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            title_text.value = data.title;
            author_text.value = data.author;
            version_text.value = data.version;
            description_text.value = data.description;
            Array.from(data.tags).forEach(tag => {
                toggleTagList(tag, true);
            });
        })
        .catch(error => console.error('Error:', error));
}

socket.onopen = function(event) {
    console.log('WebSocket is connected');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received broadcast:', data);

    // キーが同じ要素があれば，tag名を上書き，要素がなければ作成
    Object.keys(data).forEach(key => {
        const tag_item = document.getElementById(`tag_${key}`);
        if (tag_item == null) addTagList(key, data[key]);
        else {
            tag_item.children[0].value = data[key];
            tag_item.children[1].textContent = data[key];
        }
    });

    // 存在しないキーの要素があれば削除
    const tag_list = document.getElementById('tag_list');
    Array.from(tag_list.children).forEach(item => {
        let flg = true;
        Object.keys(data).forEach(key => {
            if (item.id == `tag_${key}`) flg = false;
        })
        if (flg) item.remove();
    });
}

function initUpdateData() {
    const url = server_url + '/api/tag';
    fetch(url)
        .then(response => response.json())
        .then(data => data.forEach(item => addTagList(item.id, item.tag)))
        .catch(error => console.error('Error:', error));
}

function addTagList(id, tag) {
    const tag_item = document.getElementById('tag_item');
    const new_item = tag_item.cloneNode(true);
    new_item.style = "";
    new_item.id = "tag_" + id;
    const children = new_item.children;
    children[0].value = tag;
    children[1].textContent = tag;
    children[2].id = "del_" + id;
    children[2].addEventListener("click", () => sendDelTag(id));
    const list = document.getElementById('tag_list');
    list.appendChild(new_item);
}

function toggleTagList(tag, flg) {
    const tag_checkboxes = document.querySelectorAll('#tag_list input[type="checkbox"]');
    const checked_tags = Array.from(tag_checkboxes).filter(checkbox => checkbox.value == tag);
    checked_tags[0].checked = flg;
}

function sendDelTag(id) {
    const url = server_url + `/api/tag/remove?id=${encodeURIComponent(id)}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json)
    .then(data => console.log('Success:', data))
    .catch(error => console.error('Error:', error));
}

document.addEventListener("DOMContentLoaded", function () {
    function sendNewTag() {
        const input_text = document.getElementById('tag_input_text');
        if (input_text.value == "") return;
        const url = server_url + `/api/tag?tag=${encodeURIComponent(input_text.value)}`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json)
        .then(data => console.log('Success:', data))
        .catch(error => console.error('Error:', error));
        input_text.value = "";
    }

    document.getElementById("tag_add_btn").addEventListener("click", sendNewTag);
})

document.addEventListener("DOMContentLoaded", function () {
    async function sendData() {
        const build_file = document.getElementById('build_file');
        const title_text = document.getElementById('title_text');
        const author_text = document.getElementById('author_text');
        const image_file = document.getElementById('image_file');
        const version_text = document.getElementById('version_text');
        const description_text = document.getElementById('description_text');

        build_file_exist = build_file.files.length > 0;
        image_file_exist = image_file.files.length > 0;

        console.log(`is_update: ${is_update}`);

        if (!is_update && (!build_file_exist || !image_file_exist)) {
            alert("ファイルが選択されていません！");
            return;
        }

        // タグの取得
        const tag_checkboxes = document.querySelectorAll('#tag_list input[type="checkbox"]');
        const checked_tags = Array.from(tag_checkboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);;

        // 日時
        const date = new Date();
        date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
        const str_date = date.toJSON()?.replace('T', ' ').slice(0, -5);

        // .exeの名前の取得
        let files;
        let exe_name;
        
        if (build_file_exist) {
            files = build_file.files;
            exe_names = Array.from(files).filter(file => {
                ext = file.name.split('.').pop().toLowerCase();
                return (ext == 'exe' && file.name != 'UnityCrashHandler64.exe')
            });
            exe_name = exe_names[0].name;
            console.log(exe_name);
        }

        let json_data =
        {
            "title": title_text.value,
            "author": author_text.value,
            "version": version_text.value,
            "description": description_text.value,
            "lastupdate": str_date,
            "tags": checked_tags
        }

        if (is_update) json_data["id"] = Number(game_id);
        if (build_file_exist) json_data["exeName"] = exe_name;
        else json_data["exeName"] = null;
        if (image_file_exist) json_data["imgName"] = image_file.files[0].name;
        else json_data["imgName"] = null;

        console.log(json_data);

        const formData = new FormData();
        formData.append("metadata", JSON.stringify(json_data));

        // zip圧縮
        if (build_file_exist) {
            const zip = new JSZip();
            const parent_dir = files[0].webkitRelativePath.split('/')[0];
            for (let i = 0; i < files.length; i++) {
                // 親ディレクトリを含めないパスを生成
                const relativePath = files[i].webkitRelativePath.replace(`${parent_dir}/`, '');
                zip.file(relativePath, files[i]);
            }

            const zipfile = await zip.generateAsync({ type: "blob" });
            formData.append("build_file", zipfile, `${title_text.value}.zip`);
        }

        if (image_file_exist) formData.append("image_file", image_file.files[0]);

        if (!is_update) {
            const url = server_url + '/api/upload';
            fetch(url, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(_ => window.location.href = server_url + '/web/list/')
            .catch(error => console.error('Error:', error));
        }
        else {
            const url = server_url + '/api/update';
            fetch(url, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(_ => window.location.href = server_url + '/web/list/')
            .catch(error => console.error('Error:', error));
        }
    }

    document.getElementById("submit_btn").addEventListener("click", sendData);
})